import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="config/.env", override=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def validate_config():
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        raise ValueError("OPENAI_API_KEY environment variable not set. Please update config/.env before proceeding.")


# Flask configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Database configuration
DB_DIRECTORY = os.getenv("DB_DIRECTORY", "./data/chroma_db")

# Knowledge base configuration
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "./data/knowledge_base")

# Rank configuration
RANKS = {
    1: {"name": "Security Novice", "threshold": 0},
    2: {"name": "Security Apprentice", "threshold": 100},
    3: {"name": "Security Adept", "threshold": 250},
    4: {"name": "Security Expert", "threshold": 500},
    5: {"name": "Security Master", "threshold": 1000}
}

# Topic configuration
TOPICS = {
    "phishing": {
        "rank": 1,
        "keywords": ["phishing", "scam", "fake email", "suspicious link"]
    },
    "passwords": {
        "rank": 1,
        "keywords": ["password", "credentials", "authentication", "login"]
    },
    "basic_security": {
        "rank": 1,
        "keywords": ["basic security", "security basics", "fundamental", "security 101"]
    },
    "malware": {
        "rank": 1,
        "keywords": ["malware", "virus", "trojan", "spyware", "ransomware"]
    },
    "social_engineering": {
        "rank": 1,
        "keywords": ["social engineering", "manipulation", "pretexting", "baiting"]
    },
    "data_protection": {
        "rank": 2,
        "keywords": ["data protection", "data privacy", "data security", "pii"]
    },
    "email_security": {
        "rank": 2,
        "keywords": ["email security", "secure email", "email protection"]
    },
    "device_security": {
        "rank": 2,
        "keywords": ["device security", "mobile security", "endpoint security"]
    },
    "secure_browsing": {
        "rank": 2,
        "keywords": ["secure browsing", "safe browsing", "browser security"]
    },
    "network_security": {
        "rank": 3,
        "keywords": ["network", "wifi", "router", "firewall", "vpn", "network security"]
    },
    "encryption": {
        "rank": 3,
        "keywords": ["encryption", "encrypt", "cipher", "cryptography"]
    },
    "authentication": {
        "rank": 3,
        "keywords": ["authentication", "mfa", "2fa", "two-factor", "multi-factor"]
    },
    "security_policies": {
        "rank": 3,
        "keywords": ["security policy", "security policies", "policy", "compliance"]
    },
    "incident_response": {
        "rank": 4,
        "keywords": ["incident", "breach", "attack", "response", "compromise"]
    },
    "security_audits": {
        "rank": 4,
        "keywords": ["audit", "security audit", "assessment", "evaluation"]
    },
    "risk_assessment": {
        "rank": 4,
        "keywords": ["risk", "risk assessment", "vulnerability assessment"]
    },
    "compliance": {
        "rank": 4,
        "keywords": ["compliance", "gdpr", "hipaa", "pci", "regulatory"]
    },
    "penetration_testing": {
        "rank": 5,
        "keywords": ["penetration testing", "pentest", "ethical hacking"]
    },
    "advanced_threats": {
        "rank": 5,
        "keywords": ["advanced threat", "apt", "sophisticated attack", "zero day"]
    },
    "security_architecture": {
        "rank": 5,
        "keywords": ["security architecture", "defense in depth", "secure design"]
    },
    "zero_trust": {
        "rank": 5,
        "keywords": ["zero trust", "zero trust architecture", "trust but verify"]
    }
}

# LLM Configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")