# LaborGuard — Pitch Deck Outline

> **Note**: This file serves as the pitch deck content outline.
> For the final presentation, export to PDF/PPTX format.

---

## Slide 1: Title
**LaborGuard** 🛡️
*AI-Powered Parametric Income Protection for Gig Delivery Workers*
- Team TechNova
- Guidewire DEVTrails University Hackathon 2026
- Theme: Seed • Scale • Soar

---

## Slide 2: The Problem
- 12M+ gig delivery workers in India
- Zero income safety net (no ESIC, no PF, no insurance)
- Weather disruptions → lost earnings → debt spiral
- **Ravi's Story**: ₹700/day lost × 3 days = ₹2,100 gone during Cyclone Fengal

---

## Slide 3: Our Solution
- **Parametric insurance**: No claim forms, no paperwork
- **5 automated triggers**: Rain, Flood, Heat, AQI, Platform Suspension
- **AI-powered fraud defense**: 7-signal detection + DBSCAN ring detection
- **Instant UPI payouts**: Money arrives in under 10 seconds

---

## Slide 4: How It Works
```
ENROLL → MONITOR → TRIGGER → VERIFY → PAY
(₹29/wk)  (24/7)   (auto)   (AI)    (UPI)
```

---

## Slide 5: Technical Architecture
- React + Tailwind frontend
- FastAPI backend with async architecture
- XGBoost premium pricing model
- Isolation Forest fraud detection
- Supabase database with RLS
- Mock external APIs (Weather, IMD, AQICN, Zomato, Razorpay)

---

## Slide 6: AI/ML Models
| Model | Algorithm | Purpose |
|-------|-----------|---------|
| Premium Pricing | XGBoost Regression | ₹29–75 dynamic pricing |
| Fraud Detection | Isolation Forest | 7-signal anomaly scoring |
| Ring Detection | DBSCAN Clustering | Coordinated fraud groups |
| Earnings DNA | Time-weighted patterns | Fair payout calculation |

---

## Slide 7: Security & Trust
- SHA-256 immutable audit trail
- One device per account enforcement
- GPS spoof detection (velocity + altitude + cell tower)
- 3-strike fraud policy
- AES-256 encryption at rest
- DPDPA compliant (masked Aadhaar)

---

## Slide 8: Market Opportunity
- TAM: 12M gig workers × ₹50/week = ₹31,200 Cr/year
- SAM: 2M workers in 5 cities = ₹5,200 Cr/year
- SOM: 200K workers Year 1 = ₹520 Cr/year

---

## Slide 9: Demo Highlights
1. Worker onboarding (60 seconds)
2. Trigger → Claim → Payout (8 seconds)
3. Fraud ring detection (DBSCAN live)
4. Admin dashboard (full visibility)

---

## Slide 10: Roadmap
- **Seed**: MVP with 5 cities, mock APIs, demo-ready
- **Scale**: Real API integrations, mobile app, 20 cities
- **Soar**: Multi-platform (Uber, Ola), IRDAI sandbox, cross-border
