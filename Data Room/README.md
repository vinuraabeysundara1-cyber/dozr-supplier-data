# DOZR Analytics & Documentation

This repository contains DOZR analytics, API configurations, and session documentation.

---

## Quick Start for Team Members

### 1. Clone the Repository
```bash
git clone https://github.com/vinuraabeysundara1-cyber/DOZR.git
cd DOZR
```

### 2. Pull Latest Updates
```bash
git pull origin main
```

### 3. View Analysis Files
All analysis is saved as Markdown files - viewable on GitHub or any text editor.

---

## Folder Structure

```
DOZR/
├── CLAUDE.md                 # API connection configs (Google Ads, Metabase, GA4)
├── Config/                   # API credentials (DO NOT SHARE)
│
├── Session Logs/             # Claude session summaries
│   └── YYYY-MM-DD_Topic.md
│
├── Email Analysis/           # OMS, Supplier, Margin analysis
│   ├── OMS_vs_Manual_Orders_Analysis.md
│   ├── DOZR_Margin_Report_Analysis.md
│   └── ...
│
├── Google Ads Analysis/      # Campaign performance reports
│   └── ...
│
├── Google Ads Suppliers/     # Supplier research
│   └── ...
│
└── Scripts/                  # Automation scripts
```

---

## Available Data Sources

| Source | Status | What's Available |
|--------|--------|------------------|
| **Google Ads API** | ✅ Connected | Campaign performance, keywords, conversions |
| **Metabase API** | ✅ Connected | MongoDB queries, margin reports, OMS data |
| **Google Analytics** | 🔄 Pending | Sessions, users, landing pages, conversions |

---

## Key Reports

### OMS & Orders
- `Email Analysis/OMS_vs_Manual_Orders_Analysis.md` - OMS vs Manual fulfillment breakdown
- `Email Analysis/DOZR_Margin_Report_Analysis.md` - Full margin report with supplier/equipment data

### Google Ads
- `Google Ads Analysis/DOZR_Campaign_Performance_14Day_Feb2026.md` - Recent campaign performance
- `Google Ads Analysis/DOZR_Expansion_Campaigns_Audit_Feb2026.md` - Expansion campaign audit

---

## How to Use This Repo

### For Analysts (Vinura)
1. Run Claude sessions and save findings
2. Use Session Log template for progress tracking
3. Push updates: `git add . && git commit -m "message" && git push`

### For Team Members
1. Pull latest: `git pull origin main`
2. Browse Markdown files for analysis
3. Check Session Logs for recent work

### For Developers
1. See `CLAUDE.md` for API connection instructions
2. Check `Scripts/` for automation tools

---

## Contact

- **Primary Analyst:** Vinura Abeysundara
- **API Support:** Andrew Ladouceur

---

*Last updated: February 13, 2026*
