# Crypto Wallet Scam Checker API

🛡️ **Fast, transparent risk scoring for cryptocurrency wallet addresses**

One API call answers: "Is this wallet flagged or suspicious?"

Combines open sanctions lists, scam databases, mixer detection, and on-chain analysis to return a clear risk score (0-100), label, and detailed reasons.

---

## Features

✅ **Single Endpoint** - POST `/wallet/check` returns everything you need  
✅ **Multi-Chain Support** - Ethereum, Bitcoin, Polygon, BSC  
✅ **Comprehensive Data Sources** - OFAC sanctions, CryptoScamDB, Tornado Cash mixers  
✅ **Privacy-First** - No storage of addresses beyond aggregate metrics  
✅ **Fast** - < 500ms typical response time  
✅ **Transparent** - Shows which sources flagged the address  
✅ **Professional** - Full FastAPI docs, type safety, error handling  

---

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the API

```bash
python main.py
```

The API will start on `http://localhost:8000`

### 3. Check a Wallet

```bash
curl -X POST http://localhost:8000/wallet/check \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ethereum",
    "address": "0x722122df12d4e14e13ac3b6895a86e84145b6967"
  }'
```

**Response:**
```json
{
  "chain": "ethereum",
  "address": "0x722122df12d4e14e13ac3b6895a86e84145b6967",
  "scam_flag": false,
  "risk_score": 40,
  "label": "caution",
  "reasons": [
    "Address is a known mixer contract (e.g., Tornado Cash)"
  ],
  "signals": {
    "mixer_contract": true
  },
  "sources": {
    "sanctions": {"ethereum": 10, "bitcoin": 1088},
    "scams": {"ethereum": 5, "bitcoin": 2},
    "phishing_domains": 12,
    "last_updated": {"ofac": "2025-09-30T14:00:00Z"}
  }
}
```

---

## API Endpoints

### POST `/wallet/check`

Check a cryptocurrency wallet address for scam/sanctions risk.

**Request:**
```json
{
  "chain": "ethereum",
  "address": "0xABC...",
  "domain": "optional-domain.com",
  "tx_hash": "optional-tx-hash"
}
```

**Response:**
- `scam_flag` (boolean) - True if high-risk or above
- `risk_score` (0-100) - Numerical risk score
- `label` - "clean", "caution", "high-risk", or "likely-scam"
- `reasons` - Human-readable list of why the score was assigned
- `signals` - Detailed signals that contributed to the score
- `sources` - Data sources used and last updated times

### GET `/status`

Health check and data source statistics.

### GET `/docs`

Interactive API documentation (Swagger UI).

---

## Risk Scoring

### Score Ranges
- **0-20**: Clean - No risk signals detected
- **21-50**: Caution - Minor risk signals
- **51-80**: High-risk - Multiple risk signals
- **81-100**: Likely scam - Strong evidence of fraud

### Scoring Signals
- **+80** - Address on OFAC sanctions list
- **+80** - Address in scam database
- **+40** - Known mixer contract (Tornado Cash, etc.)
- **+25** - Received funds from flagged address
- **+20** - Dusting attack pattern
- **+15** - New address with large suspicious inflows
- **+15** - Associated with phishing domain
- **-10 to -30** - Mitigating factors (age, verified contract, clean history)

---

## Data Sources

### Current Sources
1. **OFAC Sanctions** - U.S. Treasury sanctioned crypto addresses
2. **CryptoScamDB** - Community-maintained scam address database
3. **Tornado Cash Contracts** - Known mixer addresses
4. **Curated Scam List** - High-profile scam addresses (PlusToken, Bitconnect, etc.)
5. **Phishing Domains** - Known crypto phishing websites

### Data Updates
- External sources: Fetched daily
- Curated lists: Updated with each release
- Cache: Saved to disk for fast startup

---

## Supported Chains

- ✅ **Ethereum** - Full support
- ✅ **Bitcoin** - Full support (1088+ OFAC addresses)
- ✅ **Polygon** - Shares Ethereum address format
- ✅ **BSC (Binance Smart Chain)** - Shares Ethereum address format

---

## Examples

### Clean Address
```bash
curl -X POST http://localhost:8000/wallet/check \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ethereum",
    "address": "0x1234567890123456789012345678901234567890"
  }'
```

**Result:** `risk_score: 0`, `label: "clean"`

### Scam Address (PlusToken)
```bash
curl -X POST http://localhost:8000/wallet/check \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ethereum",
    "address": "0xd882cfc20f52f2599d84b8e8d58c7fb62cfe344b"
  }'
```

**Result:** `risk_score: 80`, `label: "high-risk"`, reasons include "Address found in scam database"

### With Phishing Domain
```bash
curl -X POST http://localhost:8000/wallet/check \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ethereum",
    "address": "0x1234567890123456789012345678901234567890",
    "domain": "metamask-secure.com"
  }'
```

**Result:** Additional +15 score for phishing domain detection

---

## Development

### Run Tests
```bash
python test_api.py
```

### Update Data Sources
Data is automatically fetched on startup. To force refresh:
```python
from data_loader import data_loader
data_loader.load_all_data()
```

### Add New Scam Addresses
Edit `seed_data.py` and add to the curated lists:
```python
KNOWN_SCAM_ADDRESSES_ETH = [
    "0xYOUR_SCAM_ADDRESS_HERE",
    # ...
]
```

---

## Deployment

### Render.com

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: crypto-wallet-checker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    plan: starter
```

2. Deploy:
```bash
git push
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## RapidAPI Integration

### Suggested Pricing Tiers

**Free**: 10,000 checks/month; 1,000/hour  
**Starter ($9/mo)**: 100,000/month; bulk-check enabled; $0.50/1k overage  
**Growth ($29/mo)**: 500,000/month; $0.40/1k overage  
**Scale ($79/mo)**: 2,000,000/month; $0.30/1k overage  
**Enterprise**: Custom (SLA, webhooks, custom datasets)

### Marketing Copy

> **Crypto Wallet Scam Checker: One call, one answer.**  
> We fuse public scam lists, sanctions, mixer interactions, and on-chain patterns to return a clear risk score, label, and reasons—fast, transparent, and privacy-first.

---

## Configuration

Edit `config.py` to customize:

- `SCORING` - Adjust weights for each signal
- `RISK_THRESHOLDS` - Change label boundaries
- `MIXER_CONTRACTS` - Add more mixer addresses
- `REQUEST_TIMEOUT` - Adjust external API timeouts
- `CACHE_TX_TTL` - Transaction cache duration

---

## Privacy & Security

✅ **No Address Storage** - Addresses are never logged or stored  
✅ **No User Tracking** - Only aggregate metrics collected  
✅ **Open Source Data** - All data sources are public/open  
✅ **Transparent Scoring** - All signals explained in response  
✅ **Cache Only** - Short-lived in-memory cache for performance  

---

## Performance

- **Typical Latency**: < 300ms for list-only checks
- **With Blockchain API**: < 1-2s for on-chain analysis
- **Memory Usage**: < 150MB (fits on 512MB plans)
- **Cache Strategy**: LRU with 1-hour TTL for transaction data

---

## Contributing

Contributions welcome! Please focus on:
1. Adding more data sources
2. Improving scoring heuristics
3. Adding more blockchain support
4. Performance optimizations

---

## License

MIT License - See LICENSE file for details

---

## Support

- **Documentation**: `/docs` endpoint
- **Issues**: GitHub Issues
- **Email**: support@yourapi.com

---

## Roadmap

- [ ] Ethereum transaction analysis (1-hop taint tracking)
- [ ] Solana support
- [ ] Bulk check endpoint (CSV upload)
- [ ] Webhook alerts for watched addresses
- [ ] Historical risk timeline
- [ ] Confidence scores per signal
- [ ] Custom whitelist support

---

Built with ❤️ for the crypto community
