import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the PDF Downloader application"""
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    # Download settings
    MAX_PDF_PER_KEYWORD = int(os.getenv('MAX_PDF_PER_KEYWORD', '200'))
    MAX_PAGES_PER_SEARCH = int(os.getenv('MAX_PAGES_PER_SEARCH', '3'))
    
    # Timing settings (in seconds)
    MIN_SLEEP_TIME = float(os.getenv('MIN_SLEEP_TIME', '2'))
    MAX_SLEEP_TIME = float(os.getenv('MAX_SLEEP_TIME', '5'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '10'))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '15'))
    
    # Browser settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    USER_AGENT_ROTATION = os.getenv('USER_AGENT_ROTATION', 'True').lower() == 'true'
    
    # File storage
    BASE_DOWNLOAD_DIR = os.getenv('BASE_DOWNLOAD_DIR', 'downloads')
    
    # Default keywords by field
    DEFAULT_FIELDS_KEYWORDS = {
        'english_security': [
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
        ],
        'cybersecurity': [
            "Cybersecurity best practices",
            "Network security protocols",
            "Data protection regulations",
            "Incident response procedures",
            "Threat intelligence analysis",
        ],
        'artificial_intelligence': [
            "AI ethics and governance",
            "Machine learning security",
            "AI bias and fairness",
            "Autonomous systems safety",
            "AI regulation frameworks",
        ]
    }
    
    @classmethod
    def get_fields_keywords(cls) -> Dict[str, List[str]]:
        """Get keywords configuration, allowing for environment variable override"""
        # You can override keywords via environment variable in the future
        return cls.DEFAULT_FIELDS_KEYWORDS
    
    @classmethod
    def get_download_path(cls) -> str:
        """Get the base download directory path"""
        download_path = os.path.join(os.getcwd(), cls.BASE_DOWNLOAD_DIR)
        os.makedirs(download_path, exist_ok=True)
        return download_path 