"""
Risk scoring engine for wallet address analysis
"""
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class RiskScorer:
    """Calculates risk scores based on multiple signals"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
    
    def calculate_risk(
        self,
        chain: str,
        address: str,
        domain: Optional[str] = None,
        tx_data: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate comprehensive risk score for an address
        
        Returns:
            {
                "scam_flag": bool,
                "risk_score": int (0-100),
                "label": str,
                "reasons": List[str],
                "signals": Dict,
                "sources": Dict
            }
        """
        address = address.lower()
        score = 0
        reasons = []
        signals = {}
        
        # Check sanctions list (+80)
        if self.data_loader.is_sanctioned(address, chain):
            score += config.SCORING["sanctions_listed"]
            reasons.append("Address is on OFAC sanctions list")
            signals["sanctions_listed"] = True
        
        # Check scam list (+80)
        if self.data_loader.is_scam(address, chain):
            score += config.SCORING["scam_listed"]
            reasons.append("Address found in scam database")
            signals["scam_listed"] = True
        
        # Check if address is a mixer contract (+40)
        if self.data_loader.is_mixer(address, chain):
            score += config.SCORING["mixer_interaction"]
            reasons.append("Address is a known mixer contract (e.g., Tornado Cash)")
            signals["mixer_contract"] = True
        
        # Check phishing domain if provided (+15)
        if domain and self.data_loader.is_phishing_domain(domain):
            score += config.SCORING["phishing_domain"]
            reasons.append(f"Associated domain '{domain}' is on phishing list")
            signals["phishing_domain"] = domain
        
        # Analyze transaction data if provided
        if tx_data:
            tx_signals = self._analyze_transactions(tx_data, chain)
            score += tx_signals["score"]
            reasons.extend(tx_signals["reasons"])
            signals.update(tx_signals["signals"])
        
        # Determine label based on score
        label = self._get_label(score)
        scam_flag = score >= 51  # High-risk or above
        
        return {
            "scam_flag": scam_flag,
            "risk_score": min(score, 100),  # Cap at 100
            "label": label,
            "reasons": reasons if reasons else ["No risk signals detected"],
            "signals": signals,
            "sources": self.data_loader.get_stats()
        }
    
    def _analyze_transactions(self, tx_data: Dict, chain: str) -> Dict:
        """Analyze transaction patterns for suspicious behavior"""
        score = 0
        reasons = []
        signals = {}
        
        # Check for interactions with flagged addresses
        if "from_addresses" in tx_data:
            flagged_from = []
            for addr in tx_data["from_addresses"]:
                addr = addr.lower()
                if self.data_loader.is_sanctioned(addr, chain) or self.data_loader.is_scam(addr, chain):
                    flagged_from.append(addr[:10] + "...")
            
            if flagged_from:
                score += config.SCORING["inbound_from_flagged"]
                reasons.append(f"Received funds from {len(flagged_from)} flagged address(es)")
                signals["inbound_from_flagged"] = {
                    "count": len(flagged_from),
                    "addresses": flagged_from
                }
        
        # Check for mixer interactions
        if "interacted_with" in tx_data:
            mixer_interactions = []
            for addr in tx_data["interacted_with"]:
                addr = addr.lower()
                if self.data_loader.is_mixer(addr, chain):
                    mixer_interactions.append(addr[:10] + "...")
            
            if mixer_interactions:
                score += config.SCORING["mixer_interaction"]
                reasons.append(f"Interacted with mixer contract(s)")
                signals["mixer_interactions"] = mixer_interactions
        
        # Dusting pattern detection
        if "dust_pattern" in tx_data and tx_data["dust_pattern"]:
            score += config.SCORING["dusting_pattern"]
            reasons.append("Dusting attack pattern detected (many small inbound transactions)")
            signals["dusting_pattern"] = True
        
        # New address with large inflows
        if "age_days" in tx_data and "large_inflows" in tx_data:
            if tx_data["age_days"] < 7 and tx_data["large_inflows"]:
                score += config.SCORING["new_with_large_inflows"]
                reasons.append("New address with suspicious large inflows")
                signals["new_with_large_inflows"] = True
        
        # Age bonus (old addresses with clean history)
        if "age_days" in tx_data and tx_data["age_days"] > 365:
            if score < 20:  # Only apply bonus if otherwise clean
                score += config.SCORING["age_bonus"]
                reasons.append("Established address with clean history")
                signals["age_bonus"] = True
        
        return {
            "score": score,
            "reasons": reasons,
            "signals": signals
        }
    
    def _get_label(self, score: int) -> str:
        """Convert score to risk label"""
        for label, (min_score, max_score) in config.RISK_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return label
        return "likely-scam"  # Default for >100
    
    def bulk_check(self, addresses: List[Tuple[str, str]]) -> List[Dict]:
        """
        Check multiple addresses in bulk
        
        Args:
            addresses: List of (chain, address) tuples
        
        Returns:
            List of risk results
        """
        results = []
        for chain, address in addresses:
            try:
                result = self.calculate_risk(chain, address)
                result["address"] = address
                result["chain"] = chain
                results.append(result)
            except Exception as e:
                logger.error(f"Error checking {chain}:{address}: {e}")
                results.append({
                    "chain": chain,
                    "address": address,
                    "error": str(e)
                })
        
        return results
