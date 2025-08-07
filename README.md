# ⚡ Lightning Digital Marketplace

## 🎯 Project Overview
A production-ready Lightning commerce platform built with step-by-step learning progression.

**Current Stage**: Stage 1 - Foundation Setup  
**Goal**: Basic Flask app connected to Polar Lightning

## 🌳 Branch Structure & Learning Progression

```
main (production-ready final application)
├── stage-1-foundation (basic Flask + Polar) ← YOU ARE HERE
├── stage-2-commerce (product catalog + payments) 
├── stage-3-realtime (WebSocket + live updates)
├── stage-4-production (real APIs + deployment)
└── stage-5-advanced (analytics + business features)
```

## 🚀 Quick Start - Stage 1

### Prerequisites
- Python 3.7+
- Polar Lightning Network running
- Virtual environment

### Setup
```bash
# 1. Create virtual environment
python3 -m venv lightning_marketplace_env
source lightning_marketplace_env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.template .env
# Edit .env with your Polar node details

# 4. Run the application
python app.py

# 5. Visit http://localhost:5000
```

## 📋 Stage 1 Learning Objectives

- ✅ Flask application setup and routing
- ✅ Environment variable management
- ✅ Polar Lightning node connection
- ✅ Basic Lightning API integration
- ✅ Clean project structure

## 📁 Current File Structure

```
Lightning-Digital-Marketplace/
├── README.md                   # This overview
├── requirements.txt            # Python dependencies
├── .env.template              # Environment template
├── .gitignore                 # Git ignore patterns
├── app.py                     # Main Flask application
├── config.py                  # Configuration management
├── services/
│   └── polar_service.py       # Polar Lightning integration
├── templates/
│   ├── base.html             # Base HTML template
│   └── index.html            # Home page
├── static/
│   └── style.css             # Basic styling
```

## 🎯 Stage 1 Success Criteria

- [ ] Flask app runs successfully
- [ ] Connects to Polar Lightning node
- [ ] Basic routing works
- [ ] Environment variables loaded
- [ ] Clean, professional UI foundation

## 🔄 Next Stage Preview

**Stage 2: Commerce Core** will add:
- Product catalog with sample digital products
- Shopping cart functionality  
- Lightning invoice generation
- QR code display for payments
- Basic payment verification

---

**Ready to build the future of Lightning commerce? Let's start coding!** ⚡🚀

