# Deployment Guide

## Deploying to Render.com

### Method 1: GitHub Integration (Recommended)

1. **Push to GitHub:**
```bash
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/crypto-wallet-checker-api.git
git branch -M main
git push -u origin main
```

2. **Connect to Render:**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Click "Create Web Service"

3. **Deploy:**
   - Render will automatically build and deploy
   - Wait 3-5 minutes for first deployment
   - Your API will be live at: `https://crypto-wallet-checker-api.onrender.com`

### Method 2: Manual Deploy

1. **Install Render CLI:**
```bash
npm install -g render
```

2. **Login:**
```bash
render login
```

3. **Deploy:**
```bash
render deploy
```

---

## Deployment Configuration

The `render.yaml` file includes:
- **Plan:** Starter ($7/mo) - sufficient for 100k+ requests/month
- **Region:** Oregon (can change to nearest your users)
- **Workers:** 1 (increase for higher traffic)
- **Python:** 3.11
- **Auto-deploy:** Enabled on push to main

### Environment Variables (Optional)

Add these in Render Dashboard → Environment:
- `ETHERSCAN_API_KEY` - For Ethereum transaction analysis (optional)
- `BITCOIN_ABUSE_API_KEY` - For Bitcoin abuse reports (optional)
- `LOG_LEVEL` - Set to `DEBUG` for verbose logs

---

## Post-Deployment Testing

1. **Test Health:**
```bash
curl https://YOUR_APP.onrender.com/
```

2. **Test Wallet Check:**
```bash
curl -X POST https://YOUR_APP.onrender.com/wallet/check \
  -H "Content-Type: application/json" \
  -d '{"chain": "ethereum", "address": "0x722122df12d4e14e13ac3b6895a86e84145b6967"}'
```

3. **Check Status:**
```bash
curl https://YOUR_APP.onrender.com/status
```

---

## Listing on RapidAPI

### Step 1: Prep

Your API is already RapidAPI-ready! It follows best practices:
- ✅ Clear, RESTful endpoints
- ✅ JSON request/response
- ✅ Proper error handling (422, 500)
- ✅ OpenAPI/Swagger docs at `/docs`

### Step 2: Create RapidAPI Listing

1. **Sign up:** https://rapidapi.com/provider
2. **Add API:**
   - Name: "Crypto Wallet Scam Checker"
   - Base URL: `https://YOUR_APP.onrender.com`
   - Import from Swagger: `https://YOUR_APP.onrender.com/openapi.json`

3. **Configure Endpoints:**
   - POST `/wallet/check` - Main endpoint
   - GET `/status` - Health check (free tier)

4. **Set Pricing:**
```
Free Tier:
  - 10,000 requests/month
  - 1,000 requests/hour
  - Hard limit

Starter ($9/mo):
  - 100,000 requests/month
  - 5,000 requests/hour
  - Overage: $0.50 per 1,000 requests
  - Features: Bulk check enabled

Growth ($29/mo):
  - 500,000 requests/month
  - 10,000 requests/hour
  - Overage: $0.40 per 1,000 requests

Scale ($79/mo):
  - 2,000,000 requests/month
  - 20,000 requests/hour
  - Overage: $0.30 per 1,000 requests

Enterprise (Custom):
  - Custom limits
  - SLA guarantees
  - Dedicated support
  - Custom data sources
```

### Step 3: Marketing

**Title:**
> Crypto Wallet Scam Checker - Detect Fraudulent Addresses Fast

**Description:**
> One API call answers: "Is this wallet flagged or suspicious?" Combines OFAC sanctions, scam databases, mixer detection, and on-chain patterns to return a clear risk score (0-100), label, and detailed reasons. Multi-chain support (ETH, BTC, Polygon, BSC). Privacy-first, transparent, and lightning fast.

**Tags:**
- cryptocurrency
- blockchain
- scam-detection
- security
- compliance
- sanctions
- ethereum
- bitcoin

**Categories:**
- Financial
- Security
- Data

### Step 4: Test & Publish

1. Test all endpoints in RapidAPI console
2. Add code examples (curl, JavaScript, Python)
3. Write comprehensive documentation
4. Submit for review
5. Publish!

---

## Monitoring

### Render Dashboard
- **Metrics:** CPU, Memory, Response Times
- **Logs:** Real-time application logs
- **Alerts:** Set up email alerts for downtime

### Custom Monitoring

Add to your application:
```python
# Track request counts
from collections import Counter
request_counter = Counter()

@app.middleware("http")
async def count_requests(request: Request, call_next):
    request_counter[request.url.path] += 1
    return await call_next(request)
```

---

## Scaling

### When to Upgrade

**Starter → Standard ($25/mo):**
- Response times > 1s
- Memory usage > 400MB consistently
- Traffic > 10k requests/day

**Add More Instances:**
- Set `instances: 2` in render.yaml
- Render will auto-load-balance

### Performance Tips

1. **Cache Aggressively:**
   - Current: 1-hour TTL on transaction data
   - Consider Redis for multi-instance caching

2. **Rate Limit:**
   - Add slowapi rate limiting (already included!)
   - Prevent abuse

3. **CDN:**
   - Add Cloudflare in front of Render
   - Cache static responses

---

## Maintenance

### Daily Updates

Data sources auto-update on startup. To force refresh:
```python
# Add admin endpoint (protect with API key!)
@app.post("/admin/refresh-data")
async def refresh_data(api_key: str):
    if api_key != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(403)
    data_loader.load_all_data()
    return {"status": "refreshed"}
```

### Adding New Scam Addresses

1. Edit `seed_data.py`
2. Add addresses to curated lists
3. Commit and push
4. Render auto-deploys

### Updating Dependencies

```bash
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
git commit -am "Update dependencies"
git push
```

---

## Troubleshooting

### Build Fails
- Check Python version in `runtime.txt`
- Verify all dependencies in `requirements.txt`
- Check Render build logs

### High Memory Usage
- Reduce cache sizes in `config.py`
- Lower `CACHE_TX_TTL`
- Upgrade to Standard plan

### Slow Responses
- Check external API timeouts
- Add caching layer (Redis)
- Increase workers in `render.yaml`

### Data Not Loading
- Check data source URLs (may change)
- Verify network access from Render
- Check logs for HTTP errors

---

## Support

- **Issues:** GitHub Issues
- **Email:** your-email@domain.com
- **Docs:** `/docs` endpoint
- **Status:** https://status.render.com

---

## Estimated Costs

| Traffic/Month | Render Plan | Cost | RapidAPI Revenue | Net Profit |
|---------------|-------------|------|------------------|------------|
| <10k          | Free        | $0   | $0               | $0         |
| 100k          | Starter     | $7   | $50-100          | $43-93     |
| 500k          | Starter     | $7   | $200-400         | $193-393   |
| 1M+           | Standard    | $25  | $500-1000        | $475-975   |

**Goal:** Get to 500k requests/month = ~$300/mo profit! 🚀

---

Good luck with your API! 🎉
