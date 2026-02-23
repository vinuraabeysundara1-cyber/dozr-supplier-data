# DOZR Project

## API Connection Instructions

**When the user asks to connect to Google Ads or Metabase, use these configurations automatically.**

---

### Google Ads API

**Config File:** `Data Room/Config/google-ads.yaml` (relative to DOZR folder)

**How to Connect:**
```python
from google.ads.googleads.client import GoogleAdsClient
import os

# Get the config path relative to DOZR folder
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data Room/Config/google-ads.yaml")
# Or use absolute path:
# config_path = "/Users/vinuraabeysundara/Desktop/DOZR/Data Room/Config/google-ads.yaml"

client = GoogleAdsClient.load_from_storage(config_path)
```

**Simple Connection (use this):**
```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/Desktop/DOZR/Data Room/Config/google-ads.yaml")
```

**DOZR Account ID:** `8531896842` (use this for all queries)

**All Accessible Accounts:**
| Account ID | Name | Use For |
|------------|------|---------|
| 8531896842 | DOZR US LIMITED | Main account - use this |
| 1956839602 | Dozr | Inactive |
| 3685639058 | Hardly Ever Worn It | Other client |
| 4188996035 | Italist Manager Account | MCC |

**Example Query - Get Campaign Performance:**
```python
from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta

client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/Desktop/DOZR/Data Room/Config/google-ads.yaml")
ga_service = client.get_service("GoogleAdsService")
customer_id = "8531896842"

query = """
    SELECT
        campaign.name,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE campaign.status = 'ENABLED'
        AND segments.date DURING LAST_30_DAYS
    ORDER BY metrics.cost_micros DESC
"""

response = ga_service.search(customer_id=customer_id, query=query)
for row in response:
    print(f"{row.campaign.name}: ${row.metrics.cost_micros/1000000:.2f} spend, {row.metrics.conversions:.0f} conversions")
```

---

### Metabase API

**Instance:** `https://starry-bolt.metabaseapp.com`
**API Key:** `mb_XRBKMlQkz3Waw1jpgaNUVIYM+nEkF2bCexU1sUI0Uks=`
**Database:** Production MongoDB (DOZR)

**How to Connect:**
```python
import urllib.request
import json

METABASE_URL = "https://starry-bolt.metabaseapp.com"
METABASE_KEY = "mb_XRBKMlQkz3Waw1jpgaNUVIYM+nEkF2bCexU1sUI0Uks="

def metabase_request(endpoint, method="GET", data=None):
    url = f"{METABASE_URL}{endpoint}"
    headers = {"x-api-key": METABASE_KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()
    return json.loads(urllib.request.urlopen(req).read())
```

**Available Collections:**
- `accounts` - Customer accounts
- `supplierrequests` - OMS supplier requests
- `contacts` - Contact information
- `categories` - Equipment categories

**Example Query - Get Recent Orders:**
```python
# Run a native MongoDB query via Metabase
query_data = {
    "database": 2,  # MongoDB database ID
    "native": {
        "query": '{"collection": "supplierrequests", "limit": 100}',
        "template-tags": {}
    },
    "type": "native"
}
result = metabase_request("/api/dataset", method="POST", data=query_data)
```

---

## Quick Commands

When user says **"connect to Google Ads"** or **"pull Google Ads data"**:
1. Use the GoogleAdsClient with the yaml config
2. Query customer_id = "8531896842"
3. Return the requested metrics

When user says **"connect to Metabase"** or **"query Metabase"**:
1. Use the Metabase API with the key above
2. Query the MongoDB database
3. Return the requested data

---

## Project Structure

```
DOZR/
├── Email Analysis/           # OMS data, Marketo analysis
│   ├── Marketo_Email_Analysis.md
│   ├── DOZR_Email_Marketing_Summary.pdf
│   ├── oms_complete_supplier_list.csv/md
│   └── oms_booked_orders_90days.csv/md
├── Google Ads Analysis/      # Google Ads performance data
│   ├── Reports/              # PDF reports
│   └── Data/                 # JSON data exports
├── Google Ads Suppliers/     # Supplier research
├── Scripts/                  # Automation scripts
│   ├── api/                  # API query scripts
│   ├── analysis/             # Analysis scripts
│   └── reports/              # Report generation
└── Config/                   # Configuration files
```

---

## Key Metrics (Feb 2026)

### Email Marketing (Marketo)
- **Contacts:** 164,271 (89.7% marketable)
- **Avg Delivery Rate:** 91%
- **Avg Open Rate:** 27-35%

### OMS Performance (Last 90 Days)
- **Requests Sent:** 2,681
- **Book Rate:** 10.8%
- **Response Rate:** 20.7%
- **Total Suppliers:** 914

### Google Ads (DOZR US - Last 30 Days)
- **Spend:** ~$77,000 CAD
- **Clicks:** ~9,300
- **Conversions:** ~1,360
- **Conversion Value:** ~$355,000
