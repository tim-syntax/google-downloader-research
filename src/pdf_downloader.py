import os
import time
import random
import urllib.parse
import requests
import shutil
import logging
from typing import Set, List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager

from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFDownloader:
    """Main class for downloading PDFs from Google search results"""
    
    def __init__(self, config: Config = None, status_callback=None):
        self.config = config or Config()
        self.driver = None
        self.ua = UserAgent() if self.config.USER_AGENT_ROTATION else None
        self.download_path = self.config.get_download_path()
        self.status_callback = status_callback
        self.should_resume = False
        self.should_stop = False
        
    def resume_download(self):
        """Set flag to resume download after CAPTCHA"""
        self.should_resume = True
        logger.info("🔄 Resume flag set - download will continue")
    
    def stop_download(self):
        """Set flag to stop download"""
        self.should_stop = True
        logger.info("🛑 Stop flag set - download will be terminated")
        
        # Close the browser if it's open
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🔒 Browser closed due to stop request")
            except Exception as e:
                logger.warning(f"⚠️ Error closing browser: {e}")
    
    def _is_browser_responsive(self) -> bool:
        """Check if the browser is still responsive"""
        try:
            if not self.driver:
                return False
            # Try to get the current URL to check if browser is responsive
            self.driver.current_url
            return True
        except Exception:
            return False
    
    def _handle_browser_closure(self):
        """Handle unexpected browser closure"""
        if self.status_callback:
            self.status_callback({
                'is_running': False,
                'captcha_detected': False,
                'captcha_message': None,
                'download_paused': False,
                'error': 'Download process stopped - browser was closed unexpectedly'
            })
        logger.error("🚨 Browser was closed unexpectedly - download process stopped")
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Initialize and configure Chrome WebDriver"""
        chrome_options = ChromeOptions()
        
        if self.config.USER_AGENT_ROTATION:
            chrome_options.add_argument(f"user-agent={self.ua.random}")
        
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if self.config.HEADLESS_MODE:
            chrome_options.add_argument("--headless")
        
        # Additional options for better performance
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        svc = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=svc, options=chrome_options)
        
        # Execute script to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _random_sleep(self, min_time: float = None, max_time: float = None):
        """Random sleep to avoid detection"""
        min_t = min_time or self.config.MIN_SLEEP_TIME
        max_t = max_time or self.config.MAX_SLEEP_TIME
        time.sleep(random.uniform(min_t, max_t))
    
    def _is_robot_detected(self, driver: webdriver.Chrome) -> bool:
        """Check if the robot is detected by Google"""
        page_text = driver.page_source.lower()
        detection_phrases = [
            "unusual traffic",
            "i'm not a robot",
            "automated queries",
            "captcha",
            "verify you're human"
        ]
        return any(phrase in page_text for phrase in detection_phrases)
    
    def _handle_captcha_detection(self, driver: webdriver.Chrome) -> bool:
        """Handle CAPTCHA detection and wait for resolution"""
        if self.status_callback:
            # Update status to indicate CAPTCHA detected
            self.status_callback({
                'captcha_detected': True,
                'captcha_message': 'CAPTCHA detected! Please solve it manually and click Resume.',
                'download_paused': True
            })
            
            # Wait for CAPTCHA to be resolved
            while True:
                # Check if user wants to resume
                if self.should_resume:
                    self.should_resume = False
                    self.status_callback({
                        'captcha_detected': False,
                        'captcha_message': None,
                        'download_paused': False
                    })
                    logger.info("✅ Download resumed by user")
                    return True
                
                # Check if CAPTCHA is still present
                if not self._is_robot_detected(driver):
                    # CAPTCHA resolved automatically, update status
                    self.status_callback({
                        'captcha_detected': False,
                        'captcha_message': None,
                        'download_paused': False
                    })
                    logger.info("✅ CAPTCHA resolved automatically, continuing download")
                    return True
                
                # Wait a bit before checking again
                time.sleep(2)
        else:
            # Fallback to console input for CLI usage
            logger.warning("🚨 Robot detected! Please manually resolve the issue.")
            input("Press Enter after manually resolving the robot issue...")
            logger.info("✅ Continuing after manual resolution")
            return True
    
    def _save_pdf(self, url: str, save_path: str) -> bool:
        """Download and save a PDF file"""
        try:
            response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT, stream=True)
            if response.status_code == 200:
                # Extract the original file name
                original_filename = url.split('/')[-1]
                original_filename = urllib.parse.unquote(original_filename)
                final_path = os.path.join(save_path, original_filename)
                
                if not os.path.exists(final_path):  # Avoid duplicates
                    with open(final_path, 'wb') as f:
                        shutil.copyfileobj(response.raw, f)
                    logger.info(f"✅ Saved: {final_path}")
                    return True
                else:
                    logger.info(f"⚠️ Already exists: {final_path}")
                    return False
            else:
                logger.warning(f"⚠️ Download failed: {url} - Status: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❗ Request failed: {url} - {e}")
            return False
    
    def _search_pdf_urls(self, keyword: str, max_pdfs: int = None) -> Set[str]:
        """Search for PDF URLs using Google search"""
        max_pdfs = max_pdfs or self.config.MAX_PDF_PER_KEYWORD
        pdf_urls = set()
        page_num = 0
        
        search_query = f"{keyword} filetype:pdf"
        base_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        
        logger.info(f"🔍 Searching for: {keyword}")
        
        while len(pdf_urls) < max_pdfs and page_num < self.config.MAX_PAGES_PER_SEARCH:
            # Check if download should be stopped
            if self.should_stop:
                logger.info("🛑 Download stopped by user")
                return pdf_urls
            
            target_url = base_url + f"&start={page_num * 10}"
            
            try:
                self.driver.get(target_url)
                
                # Check if browser is still responsive
                if not self._is_browser_responsive():
                    self._handle_browser_closure()
                    return pdf_urls
                
                # Check for robot detection
                if self._is_robot_detected(self.driver):
                    self._handle_captcha_detection(self.driver)
                    continue
                
                # Wait for page to load
                WebDriverWait(self.driver, self.config.PAGE_LOAD_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a"))
                )
                
                # Scroll to load more content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self._random_sleep(2, 4)
                
                # Extract PDF links
                links = self.driver.find_elements(By.CSS_SELECTOR, "a")
                for link in links:
                    href = link.get_attribute('href')
                    if href and href.endswith('.pdf'):
                        pdf_urls.add(href)
                
                logger.info(f"📄 Found {len(pdf_urls)} PDF links so far")
                
                page_num += 1
                self._random_sleep(3, 6)
                
            except Exception as e:
                logger.error(f"❗ Error on page {page_num}: {e}")
                break
        
        logger.info(f"📊 Total PDF links collected: {len(pdf_urls)}")
        return pdf_urls
    
    def download_pdfs_for_keyword(self, keyword: str, field_name: str, max_pdfs: int = None) -> Dict[str, any]:
        """Download PDFs for a specific keyword"""
        max_pdfs = max_pdfs or self.config.MAX_PDF_PER_KEYWORD
        
        # Check if browser is still responsive
        if not self._is_browser_responsive():
            self._handle_browser_closure()
            return {
                'keyword': keyword,
                'field': field_name,
                'error': 'Browser was closed unexpectedly'
            }
        
        # Create directories
        field_folder = os.path.join(self.download_path, field_name.replace(' ', '_'))
        keyword_folder = os.path.join(field_folder, keyword.replace(' ', '_'))
        os.makedirs(keyword_folder, exist_ok=True)
        
        # Search for PDF URLs
        pdf_urls = self._search_pdf_urls(keyword, max_pdfs)
        
        # Download PDFs
        downloaded_count = 0
        failed_count = 0
        
        for pdf_url in pdf_urls:
            if self._save_pdf(pdf_url, keyword_folder):
                downloaded_count += 1
            else:
                failed_count += 1
        
        return {
            'keyword': keyword,
            'field': field_name,
            'total_urls_found': len(pdf_urls),
            'downloaded_count': downloaded_count,
            'failed_count': failed_count,
            'save_path': keyword_folder
        }
    
    def download_pdfs_for_field(self, field_name: str, keywords: List[str], max_pdfs_per_keyword: int = None) -> List[Dict[str, any]]:
        """Download PDFs for all keywords in a field"""
        logger.info(f"📂 Starting downloads for field: {field_name}")
        
        results = []
        for keyword in keywords:
            # Check if download should be stopped
            if self.should_stop:
                logger.info("🛑 Download stopped by user")
                break
                
            try:
                result = self.download_pdfs_for_keyword(keyword, field_name, max_pdfs_per_keyword)
                results.append(result)
                self._random_sleep(5, 10)  # Longer pause between keywords
            except Exception as e:
                logger.error(f"❗ Error processing keyword '{keyword}': {e}")
                results.append({
                    'keyword': keyword,
                    'field': field_name,
                    'error': str(e)
                })
        
        return results
    
    def download_all_pdfs(self, fields_keywords: Dict[str, List[str]] = None) -> Dict[str, List[Dict[str, any]]]:
        """Download PDFs for all fields and keywords"""
        fields_keywords = fields_keywords or self.config.get_fields_keywords()
        
        try:
            self.driver = self._setup_driver()
            logger.info("🚀 Starting PDF download process")
            
            all_results = {}
            
            for field_name, keywords in fields_keywords.items():
                # Check if download should be stopped
                if self.should_stop:
                    logger.info("🛑 Download stopped by user")
                    break
                
                # Check if browser is still responsive
                if not self._is_browser_responsive():
                    self._handle_browser_closure()
                    break
                    
                logger.info(f"📂 Processing field: {field_name}")
                results = self.download_pdfs_for_field(field_name, keywords)
                all_results[field_name] = results
            
            if self.should_stop:
                logger.info("🛑 Download process terminated")
            else:
                logger.info("🎉 All downloads completed!")
            return all_results
            
        except Exception as e:
            logger.error(f"❗ Fatal error: {e}")
            raise
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("🔒 Browser closed")
                except Exception as e:
                    logger.warning(f"⚠️ Error closing browser: {e}")
    
    def download_single_keyword(self, keyword: str, field_name: str = "custom", max_pdfs: int = None) -> Dict[str, any]:
        """Download PDFs for a single keyword"""
        try:
            self.driver = self._setup_driver()
            return self.download_pdfs_for_keyword(keyword, field_name, max_pdfs)
        finally:
            if self.driver:
                self.driver.quit() 