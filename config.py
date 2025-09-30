"""
Configuration for Crypto Wallet Checker API
"""
import os
from pathlib import Path
from typing import Dict

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SOURCES_DIR = DATA_DIR / "sources"
CACHE_DIR = DATA_DIR / "cache"

# Ensure directories exist
SOURCES_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API Settings
API_VERSION = "1.0.0"
API_NAME = "Crypto Wallet Scam Checker"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Rate limiting
RATE_LIMIT_FREE = "1000/hour"
RATE_LIMIT_STARTER = "5000/hour"

# Cache settings
CACHE_TX_TTL = 3600  # 1 hour for transaction data
CACHE_ADDRESS_TTL = 900  # 15 minutes for address checks

# External API keys (optional, from environment)
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
BITCOIN_ABUSE_API_KEY = os.getenv("BITCOIN_ABUSE_API_KEY", "")

# Data source URLs
DATA_SOURCES = {
    "ofac": "https://data.opensanctions.org/contrib/ofac/crypto_addresses.json",
    "cryptoscamdb": "https://raw.githubusercontent.com/CryptoScamDB/blacklist/master/data/urls.json",
    "cryptoscamdb_addresses": "https://raw.githubusercontent.com/CryptoScamDB/blacklist/master/data/addresses.json",
}

# Supported chains
SUPPORTED_CHAINS = ["ethereum", "bitcoin", "polygon", "bsc"]

# Risk score thresholds
RISK_THRESHOLDS = {
    "clean": (0, 20),
    "caution": (21, 50),
    "high-risk": (51, 80),
    "likely-scam": (81, 100)
}

# Scoring weights
SCORING = {
    "sanctions_listed": 80,
    "scam_listed": 80,
    "mixer_interaction": 40,
    "inbound_from_flagged": 25,
    "dusting_pattern": 20,
    "new_with_large_inflows": 15,
    "phishing_domain": 15,
    "high_risk_exchange": 10,
    "clean_history_bonus": -10,
    "verified_contract_bonus": -20,
    "age_bonus": -10
}

# Known mixer contracts (Ethereum mainnet)
MIXER_CONTRACTS = {
    "ethereum": [
        "0x722122df12d4e14e13ac3b6895a86e84145b6967",  # Tornado Cash: 0.1 ETH
        "0xdd4c48c0b24039969fc16d1cdf626eab821d3384",  # Tornado Cash: 1 ETH
        "0x07687e702b410fa43f4cb4af7fa097918ffd2730",  # Tornado Cash: 10 ETH
        "0x23773e65ed146a459791799d01336db287f25334",  # Tornado Cash: 100 ETH
    ],
    "polygon": [],
    "bsc": []
}

# Etherscan API endpoints
ETHERSCAN_ENDPOINTS = {
    "ethereum": "https://api.etherscan.io/api",
    "polygon": "https://api.polygonscan.com/api",
    "bsc": "https://api.bscscan.com/api"
}

# Blockchain explorer APIs
BLOCKCHAIN_APIS = {
    "bitcoin": "https://blockchain.info/rawaddr/",
    "ethereum": "https://api.etherscan.io/api"
}

# Request timeouts
REQUEST_TIMEOUT = 10  # seconds for external API calls
CHAIN_API_TIMEOUT = 5  # seconds for blockchain API calls

# Privacy settings
STORE_ADDRESSES = False  # Never store addresses
LOG_ADDRESSES = False  # Never log full addresses (only first 8 chars for debugging)
RETENTION_SECONDS = 0  # Zero retention policy
