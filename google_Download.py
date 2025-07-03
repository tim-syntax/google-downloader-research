import os
import time
import random
import urllib.parse
import requests
import shutil

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager

# ---------- Settings ----------

# List of keywords for each field
fields_keywords = {
'english_security' : [ 
    "International cybersecurity governance",
    "ENISA cybersecurity certification framework",
    "NIST Cybersecurity Framework (CSF) implementation",
    "ISO/IEC 27001 information security standard",
    "FIRST Common Vulnerability Scoring System (CVSS)",
    "ITU-T cybersecurity recommendations SG17",
    "Cloud Security Alliance (CSA) STAR program",
    "Software Bill of Materials (SBOM) policy",
    "AI security risk management framework",
    "Operational Technology (OT) security standards IEC 62443",
    "Cybersecurity policy and regulation trends",
    "Geopolitics of cyberspace and digital sovereignty",
    "EU Cybersecurity Act (CSA) impact analysis",
    "Zero Trust Architecture NIST SP 800-207",
    "Post-Quantum Cryptography (PQC) standardization",
    "Global Cybersecurity Index (GCI) report",
    "APCERT incident response cooperation",
    "Cyber sovereignty vs multistakeholder model",
    "NIS2 Directive implementation guide",
    "Traffic Light Protocol (TLP) for information sharing",
]

}

# Maximum number of PDFs to download per keyword
MAX_PDF = 200

# Base folder to save the PDFs
SAVE_DIR = os.path.join(os.getcwd(), 'downloaded_pdfs')
os.makedirs(SAVE_DIR, exist_ok=True)

# --------------------------------

# Generate random User-Agent
ua = UserAgent()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-agent={ua.random}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
# chrome_options.add_argument("--headless")  # If needed, use Headless

# Run the browser
svc = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=svc, options=chrome_options)


# Random wait
def random_sleep(a=2, b=5):
    time.sleep(random.uniform(a, b))

# Check if the robot is detected
def is_robot_detected(driver):
    page_text = driver.page_source.lower()
    return ("unusual traffic" in page_text or
            "i'm not a robot" in page_text or
            "automated queries" in page_text)

# Save the PDF
def save_pdf(url, save_path):
    try:
        response = requests.get(url, timeout=15, stream=True)
        if response.status_code == 200:
            # Extract the original file name
            original_filename = url.split('/')[-1]
            original_filename = urllib.parse.unquote(original_filename)  # Decode
            final_path = os.path.join(save_path, original_filename)

            if not os.path.exists(final_path):  # Avoid duplicates
                with open(final_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                print(f"✅ Saved: {final_path}")
            else:
                print(f"⚠️ Already exists: {final_path}")
        else:
            print(f"⚠️ Download failed: {url}")
    except Exception as e:
        print(f"❗ Request failed: {url} - {e}")

# ▶ Keyword-based work
for field, keywords in fields_keywords.items():
    print(f"\n📂 Field work started: {field}")

    # Create the field folder
    field_folder = os.path.join(SAVE_DIR, field.replace(' ', '_'))
    os.makedirs(field_folder, exist_ok=True)

    for keyword in keywords:
        print(f"\n🔍 Search started: {keyword}")

        search_query = f"{keyword} filetype:pdf"
        base_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"

        pdf_urls = set()
        page_num = 0

        while len(pdf_urls) < MAX_PDF:
            target_url = base_url + f"&start={page_num * 10}"
            driver.get(target_url)

            # Check if the robot is detected
            if is_robot_detected(driver):
                print("🚨 Robot detected! Please manually resolve the issue.")
                
                # After manually resolving the issue, continue automatically
                input("Enter after manually resolving the robot issue...")

                print("✅ Restart after manual processing")

                # After manually resolving the issue, continue automatically
                continue  # Continue (handle the page with robot detection)

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a")))

            except:
                print("❗ Page loading failed")
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_sleep(2, 4)

            links = driver.find_elements(By.CSS_SELECTOR, "a")
            for link in links:
                href = link.get_attribute('href')
                if href and href.endswith('.pdf'):
                    pdf_urls.add(href)

            print(f"Current collected PDF links: {len(pdf_urls)}")

            page_num += 1
            random_sleep(3, 6)

            if page_num > 3:
                print("❗ Too many pages searched, stopping.")
                break

        print(f"Total {len(pdf_urls)} PDF links collected. Download started!")

        # Create the keyword folder
        keyword_folder = os.path.join(field_folder, keyword.replace(' ', '_'))
        os.makedirs(keyword_folder, exist_ok=True)

        for pdf_url in pdf_urls:
            save_pdf(pdf_url, keyword_folder)

        random_sleep(5, 10)

driver.quit()
print("\n🎉 All work completed!")
