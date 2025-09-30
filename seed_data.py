"""
Seed data with known sanctioned and scam addresses for immediate use
"""

# Tornado Cash sanctioned addresses (OFAC)
TORNADO_CASH_ADDRESSES = [
    "0x722122df12d4e14e13ac3b6895a86e84145b6967",  # 0.1 ETH
    "0xdd4c48c0b24039969fc16d1cdf626eab821d3384",  # 1 ETH
    "0x07687e702b410fa43f4cb4af7fa097918ffd2730",  # 10 ETH
    "0x23773e65ed146a459791799d01336db287f25334",  # 100 ETH
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b",  # 1000 ETH
    "0xd4b88df4d29f5cedd6857912842cff3b20c8cfa3",  # 5000 ETH
    "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf",  # 50000 ETH
]

# Additional OFAC sanctioned crypto addresses
OFAC_SANCTIONED_ETH = [
    "0x8576acc5c05d6ce88f4e49bf65bdf0c62f91353c",  # Lazarus Group
    "0x098b716b8aaf21512996dc57eb0615e2383e2f96",  # North Korea
    "0x  722122df12d4e14e13ac3b6895a86e84145b6967",  # Tornado Cash
]

# High-profile scam addresses
KNOWN_SCAM_ADDRESSES_ETH = [
    "0xd882cfc20f52f2599d84b8e8d58c7fb62cfe344b",  # PlusToken scam
    "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",  # Bitconnect
    "0x957cd4ff9b3894fc78b5134a8dc72b032ffbc464",  # SaveTheKids scam
    "0xe93381fb4c4f14bda253907b18fad305d799241a",  # Fake ICO
    "0x75c8e1a4d77d78dca19c4d6ed9360f7e20b0f17c",  # Phishing attack
]

KNOWN_SCAM_ADDRESSES_BTC = [
    "1Jn9fT5LqWNqnMWwXBSfXPpAbvfNZRJqJv",
    "1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3",
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Satoshi's address (for testing)
]

# Known phishing domains
PHISHING_DOMAINS = [
    "metamask-secure.com",
    "metamask-wallet.com",
    "binance-promo.com",
    "binance-support.net",
    "coinbase-support.net",
    "coinbase-verify.com",
    "uniswap-v4.com",
    "uniswap-protocol.net",
    "opensea-nft.net",
    "opensea-support.com",
    "pancakeswap-finance.com",
    "1inch-exchange.net",
]

# High-risk exchange deposit addresses (examples - simplified)
HIGH_RISK_EXCHANGES = [
    "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be",  # Binance cold wallet (for testing interaction)
]

def get_all_sanctioned_addresses():
    """Get all sanctioned addresses"""
    return {
        "ethereum": set([addr.lower() for addr in TORNADO_CASH_ADDRESSES + OFAC_SANCTIONED_ETH]),
        "bitcoin": set(),
        "polygon": set([addr.lower() for addr in TORNADO_CASH_ADDRESSES + OFAC_SANCTIONED_ETH]),
        "bsc": set([addr.lower() for addr in TORNADO_CASH_ADDRESSES + OFAC_SANCTIONED_ETH]),
    }

def get_all_scam_addresses():
    """Get all known scam addresses"""
    return {
        "ethereum": set([addr.lower() for addr in KNOWN_SCAM_ADDRESSES_ETH]),
        "bitcoin": set([addr.lower() for addr in KNOWN_SCAM_ADDRESSES_BTC]),
        "polygon": set([addr.lower() for addr in KNOWN_SCAM_ADDRESSES_ETH]),
        "bsc": set([addr.lower() for addr in KNOWN_SCAM_ADDRESSES_ETH]),
    }

def get_all_phishing_domains():
    """Get all known phishing domains"""
    return set([domain.lower() for domain in PHISHING_DOMAINS])
