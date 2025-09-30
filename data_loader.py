"""
Data loader for fetching and updating scam/sanctions lists
"""
import json
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set, List
import config

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles fetching and caching of scam/sanctions data"""
    
    def __init__(self):
        self.last_updated = {}
        self.data_cache = {
            "sanctions": {"ethereum": set(), "bitcoin": set(), "polygon": set(), "bsc": set()},
            "scams": {"ethereum": set(), "bitcoin": set(), "polygon": set(), "bsc": set()},
            "phishing_domains": set(),
            "mixer_contracts": config.MIXER_CONTRACTS.copy()
        }
        
    def needs_update(self, source: str, max_age_hours: int = 24) -> bool:
        """Check if data source needs refresh"""
        if source not in self.last_updated:
            return True
        age = datetime.now() - self.last_updated[source]
        return age > timedelta(hours=max_age_hours)
    
    def fetch_ofac_sanctions(self) -> Dict[str, Set[str]]:
        """Fetch OFAC sanctioned crypto addresses"""
        logger.info("Fetching OFAC sanctions list...")
        
        sanctions = {"ethereum": set(), "bitcoin": set(), "polygon": set(), "bsc": set()}
        
        try:
            # Use OpenSanctions US OFAC SDN dataset
            response = requests.get(
                "https://data.opensanctions.org/datasets/latest/us_ofac_sdn/entities.ftm.json",
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Parse the JSON Lines format (one JSON object per line)
            for line in response.text.strip().split('\n'):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if isinstance(entry, dict) and "properties" in entry:
                        props = entry["properties"]
                        # Look for cryptocurrency wallet addresses
                        crypto_addrs = props.get("cryptoWallets", []) + props.get("address", [])
                        for addr in crypto_addrs:
                            addr = str(addr).lower().strip()
                            if addr.startswith("0x") and len(addr) == 42:
                                sanctions["ethereum"].add(addr)
                                sanctions["polygon"].add(addr)
                                sanctions["bsc"].add(addr)
                            elif addr.startswith(("1", "3", "bc1", "bc1q")):
                                sanctions["bitcoin"].add(addr)
                except json.JSONDecodeError:
                    continue
            
            # Also try the direct OFAC GitHub mirror
            try:
                response2 = requests.get(
                    "https://raw.githubusercontent.com/0xB10C/ofac-sanctioned-digital-currency-addresses/master/sanctioned_addresses_BTC.txt",
                    timeout=config.REQUEST_TIMEOUT
                )
                if response2.status_code == 200:
                    for line in response2.text.strip().split('\n'):
                        addr = line.strip().lower()
                        if addr and not addr.startswith("#"):
                            sanctions["bitcoin"].add(addr)
                
                response3 = requests.get(
                    "https://raw.githubusercontent.com/0xB10C/ofac-sanctioned-digital-currency-addresses/master/sanctioned_addresses_ETH.txt",
                    timeout=config.REQUEST_TIMEOUT
                )
                if response3.status_code == 200:
                    for line in response3.text.strip().split('\n'):
                        addr = line.strip().lower()
                        if addr and not addr.startswith("#") and addr.startswith("0x"):
                            sanctions["ethereum"].add(addr)
                            sanctions["polygon"].add(addr)
                            sanctions["bsc"].add(addr)
            except:
                pass
            
            self.last_updated["ofac"] = datetime.now()
            logger.info(f"Loaded OFAC: {len(sanctions['ethereum'])} ETH, {len(sanctions['bitcoin'])} BTC addresses")
            return sanctions
            
        except Exception as e:
            logger.error(f"Failed to fetch OFAC data: {e}")
            return sanctions
    
    def fetch_cryptoscamdb(self) -> Dict[str, Set[str]]:
        """Fetch CryptoScamDB addresses and domains"""
        logger.info("Fetching CryptoScamDB...")
        
        scams = {"ethereum": set(), "bitcoin": set(), "polygon": set(), "bsc": set()}
        domains = set()
        
        try:
            # Try the new API endpoint
            response = requests.get(
                "https://api.cryptoscamdb.org/v1/addresses",
                timeout=config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "result" in data:
                    for entry in data["result"]:
                        if isinstance(entry, dict):
                            addr = entry.get("address", "").lower().strip()
                            if addr.startswith("0x") and len(addr) == 42:
                                scams["ethereum"].add(addr)
                                scams["polygon"].add(addr)
                                scams["bsc"].add(addr)
                            elif addr.startswith(("1", "3", "bc1")):
                                scams["bitcoin"].add(addr)
            
            logger.info(f"Loaded CryptoScamDB addresses: {len(scams['ethereum'])} ETH, {len(scams['bitcoin'])} BTC")
            
        except Exception as e:
            logger.warning(f"Failed to fetch CryptoScamDB addresses: {e}")
        
        try:
            # Fetch phishing domains
            response = requests.get(
                "https://api.cryptoscamdb.org/v1/scams",
                timeout=config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "result" in data:
                    for entry in data["result"]:
                        if isinstance(entry, dict):
                            # Get domain
                            domain = entry.get("domain", "").lower().strip()
                            if domain:
                                domains.add(domain)
                            # Get URL and extract domain
                            url = entry.get("url", "").lower().strip()
                            if url:
                                domain = url.replace("http://", "").replace("https://", "").split("/")[0]
                                if domain:
                                    domains.add(domain)
            
            logger.info(f"Loaded {len(domains)} phishing domains")
            
        except Exception as e:
            logger.warning(f"Failed to fetch CryptoScamDB domains: {e}")
        
        # Load our curated list of known scams
        self._load_curated_scams(scams, domains)
        
        self.last_updated["cryptoscamdb"] = datetime.now()
        return scams, domains
    
    def _load_curated_scams(self, scams: Dict[str, Set[str]], domains: set):
        """Load curated list of known scam addresses and domains"""
        # Known Ethereum scams (high-profile cases)
        known_eth_scams = [
            "0xd882cfc20f52f2599d84b8e8d58c7fb62cfe344b",  # PlusToken scam
            "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",  # Bitconnect
            "0x957cd4ff9b3894fc78b5134a8dc72b032ffbc464",  # SaveTheKids scam
        ]
        
        # Known Bitcoin scams
        known_btc_scams = [
            "1Jn9fT5LqWNqnMWwXBSfXPpAbvfNZRJqJv",  # Reported scam
            "1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3",  # Reported scam
        ]
        
        # Known phishing domains
        known_phishing_domains = [
            "metamask-secure.com",
            "binance-promo.com",
            "coinbase-support.net",
            "uniswap-v4.com",
            "opensea-nft.net",
        ]
        
        for addr in known_eth_scams:
            scams["ethereum"].add(addr.lower())
            scams["polygon"].add(addr.lower())
            scams["bsc"].add(addr.lower())
        
        for addr in known_btc_scams:
            scams["bitcoin"].add(addr.lower())
        
        for domain in known_phishing_domains:
            domains.add(domain.lower())
        
        logger.info(f"Added curated scams: {len(known_eth_scams)} ETH, {len(known_btc_scams)} BTC, {len(known_phishing_domains)} domains")
    
    def load_all_data(self):
        """Load all data sources"""
        logger.info("Loading all data sources...")
        
        # Fetch OFAC sanctions
        if self.needs_update("ofac"):
            sanctions = self.fetch_ofac_sanctions()
            for chain in config.SUPPORTED_CHAINS:
                self.data_cache["sanctions"][chain].update(sanctions.get(chain, set()))
        
        # Fetch CryptoScamDB
        if self.needs_update("cryptoscamdb"):
            scams, domains = self.fetch_cryptoscamdb()
            for chain in config.SUPPORTED_CHAINS:
                self.data_cache["scams"][chain].update(scams.get(chain, set()))
            self.data_cache["phishing_domains"] = domains
        
        # Save to disk for faster startup
        self.save_cache()
        
        logger.info("Data loading complete")
        return self.get_stats()
    
    def save_cache(self):
        """Save data cache to disk"""
        cache_file = config.SOURCES_DIR / "data_cache.json"
        
        # Convert sets to lists for JSON serialization
        serializable = {
            "sanctions": {k: list(v) for k, v in self.data_cache["sanctions"].items()},
            "scams": {k: list(v) for k, v in self.data_cache["scams"].items()},
            "phishing_domains": list(self.data_cache["phishing_domains"]),
            "mixer_contracts": self.data_cache["mixer_contracts"],
            "last_updated": {k: v.isoformat() for k, v in self.last_updated.items()}
        }
        
        with open(cache_file, 'w') as f:
            json.dump(serializable, f, indent=2)
        
        logger.info(f"Data cache saved to {cache_file}")
    
    def load_cache(self):
        """Load data cache from disk"""
        cache_file = config.SOURCES_DIR / "data_cache.json"
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Convert lists back to sets
            self.data_cache["sanctions"] = {k: set(v) for k, v in cached["sanctions"].items()}
            self.data_cache["scams"] = {k: set(v) for k, v in cached["scams"].items()}
            self.data_cache["phishing_domains"] = set(cached["phishing_domains"])
            self.data_cache["mixer_contracts"] = cached["mixer_contracts"]
            
            # Parse timestamps
            for k, v in cached.get("last_updated", {}).items():
                self.last_updated[k] = datetime.fromisoformat(v)
            
            logger.info("Data cache loaded from disk")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return False
    
    def is_sanctioned(self, address: str, chain: str) -> bool:
        """Check if address is on sanctions list"""
        return address.lower() in self.data_cache["sanctions"].get(chain, set())
    
    def is_scam(self, address: str, chain: str) -> bool:
        """Check if address is on scam list"""
        return address.lower() in self.data_cache["scams"].get(chain, set())
    
    def is_mixer(self, address: str, chain: str) -> bool:
        """Check if address is a known mixer contract"""
        return address.lower() in [m.lower() for m in self.data_cache["mixer_contracts"].get(chain, [])]
    
    def is_phishing_domain(self, domain: str) -> bool:
        """Check if domain is on phishing list"""
        return domain.lower() in self.data_cache["phishing_domains"]
    
    def get_stats(self) -> Dict:
        """Get statistics about loaded data"""
        return {
            "sanctions": {k: len(v) for k, v in self.data_cache["sanctions"].items()},
            "scams": {k: len(v) for k, v in self.data_cache["scams"].items()},
            "phishing_domains": len(self.data_cache["phishing_domains"]),
            "mixer_contracts": {k: len(v) for k, v in self.data_cache["mixer_contracts"].items()},
            "last_updated": {k: v.isoformat() for k, v in self.last_updated.items()}
        }


# Global data loader instance
data_loader = DataLoader()
