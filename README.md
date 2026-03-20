# 🛡️ GigShield

### AI-Powered Parametric Income Protection for Gig Delivery Workers

> _A zero-touch platform that automatically detects disruptions, verifies claims
> with multi-signal fraud intelligence, and pays delivery workers before they
> even realize they've lost income._

![Phase](https://img.shields.io/badge/Phase-1%20Seed-green)
![Hackathon](https://img.shields.io/badge/Hackathon-Guidewire%20DEVTrails%202026-blue)
![Stack](https://img.shields.io/badge/Stack-React%20%7C%20FastAPI%20%7C%20Supabase%20%7C%20XGBoost-orange)

---

## 📌 Table of Contents

- [The Problem](#-the-problem)
- [Our Solution](#-our-solution)
- [Persona](#-persona)
- [How It Works](#-how-it-works)
- [Weekly Premium Model](#-weekly-premium-model)
- [Parametric Triggers](#-parametric-triggers)
- [Earnings DNA Payout](#-earnings-dna-payout)
- [Adversarial Defense & Anti-Spoofing Strategy](#-adversarial-defense--anti-spoofing-strategy)
- [Cybersecurity Features](#-cybersecurity-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [File Structure](#-file-structure)
- [Team](#-team)

---

## 🔴 The Problem

India has **12+ million gig delivery workers**. They are the invisible backbone
of our digital economy — yet they have no financial safety net.

**Meet Ravi** — a Zomato delivery partner in Chennai earning ₹700/day.  
When Cyclone Fengal floods his zone, Zomato suspends deliveries.  
Ravi loses **₹2,000 in 3 days** with zero recourse.

| What Ravi Needs                             | What Exists Today             |
| ------------------------------------------- | ----------------------------- |
| Income protection for lost wages            | ❌ Not covered by any insurer |
| Automatic claim when disaster hits          | ❌ Weeks of paperwork         |
| Coverage that matches his week-to-week life | ❌ Only annual/monthly plans  |
| Protection from weather he can't control    | ❌ Bears full loss alone      |

Gig workers are classified as "independent contractors" — excluded from ESIC,
PF, and every safety net that exists. **GigShield fixes this.**

---

## 💡 Our Solution

GigShield is an **AI-powered parametric income protection platform** exclusively
for food delivery partners (Zomato/Swiggy).

```
ENROLL → MONITOR → TRIGGER → VERIFY → PAY
   ↑          ↑           ↑          ↑        ↑
Weekly    Real-time   Parametric  AI Fraud  Instant
Premium   Zone Watch  Event Fire  Defense   UPI Pay
```

**Parametric insurance** means payouts are triggered automatically when a
pre-defined event occurs — no claim filing, no paperwork, no waiting.  
When it rains beyond a threshold in Ravi's zone → money hits his UPI. Period.

---

## 👤 Persona

**Food Delivery Partners — Zomato & Swiggy**  
Tier-1 Indian cities: Chennai, Bengaluru, Mumbai, Hyderabad, Delhi

| Attribute               | Detail                        |
| ----------------------- | ----------------------------- |
| Average daily earnings  | ₹600–800/day                  |
| Average weekly earnings | ₹4,500–5,500/week             |
| Work pattern            | 10–12 hrs/day, 6 days/week    |
| Income dependency       | 100% gig, no secondary income |
| Tech profile            | Basic Android, UPI-enabled    |

---

## ⚙️ How It Works

### 1. Worker Onboarding

- Ravi registers with his Zomato Worker ID (verified via mock platform API)
- Masked Aadhaar KYC (last 4 digits only — never stored in full)
- Selfie liveness check — prevents fake account farms
- Device fingerprint locked to account — One Device = One Account
- AI generates his initial risk profile from zone flood history + pollution index

### 2. Weekly Coverage Activation

- Every Monday, Ravi receives a personalized premium notification
- He picks Basic / Standard / Premium plan and pays via UPI
- Coverage is active from that moment through Sunday

### 3. Real-Time Monitoring

- GigShield silently monitors 5 parametric triggers for his zone 24/7
- No action needed from Ravi

### 4. Automatic Claim + Payout

- Trigger fires → fraud check runs → payout hits UPI
- Ravi gets a notification. That's all he ever sees.

---

## 💰 Weekly Premium Model

**Algorithm: XGBoost Regression**

Dynamic weekly premium calculated every Monday per worker:

| Input Feature                        | Example                     |
| ------------------------------------ | --------------------------- |
| Zone flood/waterlog history (3yr)    | Velachery = High Risk       |
| IMD weather forecast for next 7 days | Heavy rain predicted        |
| AQI / pollution index forecast       | Severe week ahead           |
| Historical curfew/strike frequency   | Anna Nagar = 2 strikes/year |
| Worker's average weekly earnings     | ₹5,000 baseline             |
| Worker tenure on platform            | New vs veteran              |
| Past claim history                   | >2 claims/month = flag      |

**Output:** ₹29 – ₹75/week per worker  
**Sub-zone precision:** Priced at 500m polygon level, not city-wide  
Velachery Zone 4B and Anna Nagar Zone 2A have different premiums even
in the same city on the same week.

**Monday Nudge Example:**

> _"⚠️ High flood risk this week in your zone (78%). Your coverage:
> ₹2,000. Premium: ₹59. Tap to renew."_

---

## ⚡ Parametric Triggers

5 automated triggers monitored in real-time — no human intervention:

| Trigger                   | API Source      | Threshold                  |
| ------------------------- | --------------- | -------------------------- |
| Heavy Rainfall            | OpenWeatherMap  | > 80mm/hr in zone          |
| Flood / Waterlogging      | IMD Alert API   | Red alert issued           |
| Severe Heat               | OpenWeatherMap  | > 43°C sustained           |
| Severe AQI                | AQICN API       | AQI > 400 (Hazardous)      |
| Platform Order Suspension | Zomato Mock API | Orders down > 2hrs in zone |

**Triple-Source Cross-Validation:**  
All three independent sources (weather API + IMD + platform activity) must
agree before auto-approval. A fraudster cannot fake three independent
real-world data sources simultaneously.

| Sources Agreeing | Action                          |
| ---------------- | ------------------------------- |
| All 3 agree      | ✅ Auto-approve, instant payout |
| 2 agree          | ⚠️ Soft verify, minor delay     |
| Only 1           | 🔴 Hold for review              |

---

## 🧬 Earnings DNA Payout

Most parametric platforms pay a **flat amount** (₹500 per disruption day, same
for everyone). GigShield pays what the worker **actually lost.**

```
Payout = (Worker's Avg Earnings for that Day/Time slot)
         × (Disruption Hours / Working Hours)
         × Coverage Multiplier
```

**Example:**

- Ravi earns more on Friday evenings (festival orders) than Monday mornings
- A flood on Friday evening = 3× the financial loss of a Monday morning flood
- GigShield's Earnings DNA profile captures this time-weighted pattern
- His Friday evening payout reflects his actual loss, not a generic average

**Weekly Payout Cap:** 2× weekly premium × plan multiplier

---

## 🛡️ Adversarial Defense & Anti-Spoofing Strategy

> _500 delivery partners. Fake GPS. Real payouts. A coordinated fraud ring
> just drained a platform's liquidity pool. Simple GPS verification is dead._

### The Threat Model

A syndicate of 500 workers organizes via Telegram. Using GPS spoofing apps,
they fake their locations into a red-alert flood zone while sitting safely
at home — triggering mass false payouts and draining the liquidity pool.

---

### 1. Differentiating Genuine Workers from Bad Actors

Simple GPS coordinate check is insufficient. GigShield analyzes **7 independent
signals simultaneously** to build a Fraud Risk Score (0–100):

| Signal                        | What It Checks                                             | Fraud Indicator                                    |
| ----------------------------- | ---------------------------------------------------------- | -------------------------------------------------- |
| **Movement Velocity**         | Speed between consecutive GPS pings                        | >120 km/h between pings = impossible for a bike    |
| **Location History Match**    | Does claimed zone match last 30 days of delivery routes?   | Never delivered here before = suspicious           |
| **Device Fingerprint**        | Is device rooted? Is mock GPS app installed?               | Emulator/spoof app detected = Red flag             |
| **GPS Altitude Consistency**  | Altitude variance during claimed delivery                  | Flat/static altitude = phone sitting still at home |
| **Cell Tower vs GPS Match**   | Does cell tower location match GPS coordinates?            | >15km mismatch = spoofing likely                   |
| **Accelerometer / Gyroscope** | Is the phone physically moving?                            | Zero motion during "active delivery" = fraud       |
| **Platform Order Logs**       | Did Zomato show any orders accepted/rejected in that zone? | No order activity = no physical presence           |

**Fraud Risk Score:**

- **0–30 → Green:** Auto-approve, instant UPI payout
- **31–60 → Amber:** Soft verification (one-tap confirm + order log cross-check)
- **61–100 → Red:** Payout held, manual review within 2 hours

**Journey Signature Check:**  
Every active worker builds a movement signature over 4 weeks (speed, stop
patterns, route shapes). A stationary phone at home has a completely different
signature from a moving delivery bike. The system compares live movement against
this personal baseline before every claim approval.

**Geofence Consistency Check:**  
If Ravi claims he was trapped in Velachery Zone 4B during the flood, the system
checks: _"Was he in or near that zone in the 2 hours before the trigger fired?"_  
If yes → Green. If he teleported from Adyar 10 minutes before → Amber.

---

### 2. Detecting Coordinated Fraud Rings

Individual anomaly detection fails against organized syndicates. GigShield
adds a **group-level behavioral intelligence layer** using:

**Algorithm: Isolation Forest + DBSCAN Clustering**

The system looks for these coordinated fraud signatures:

**Spatio-Temporal Clustering:**
50+ workers simultaneously claiming from the exact same 100m radius, despite
historically working in completely different areas of the city. This is
statistically impossible in genuine disruptions — workers are naturally
distributed across zones. A tight cluster = coordinated fraud ring.

**Device & IP Correlation:**
Multiple accounts logging claims from the same IP subnet, same device IMEI
prefix, or same hardware fingerprint batch. A single operator running 50
fake accounts will share infrastructure signatures.

**Claim Timing Synchronization:**
Claims filed within seconds of each other across many accounts = bot-like
coordination, not organic human behavior. Genuine workers claim at random
intervals; fraud rings trigger simultaneously.

**Pre-Event Registration Surge:**
A sudden spike of new account registrations in one specific zone in the week
before a forecasted red-alert weather event = pre-planned fraud preparation.

**Earn/Claim Ratio Anomaly:**
Workers who never claimed for months then suddenly claim every trigger event
in the highest-payout zones = behavioral anomaly flagged by Isolation Forest.

**When a Ring is Detected:**
The entire DBSCAN cluster is flagged simultaneously — not just individual
members. Pool payouts for the cluster are frozen pending review. Genuine
workers outside the cluster are unaffected.

---

### 3. UX Balance — Protecting Honest Workers

The hardest design challenge: **don't punish Ravi because a fraudster lives
in his zone.**

**Three-Tier Response System:**

| Tier     | Fraud Score | Worker Experience                                                        |
| -------- | ----------- | ------------------------------------------------------------------------ |
| 🟢 Green | 0–30        | Instant UPI payout, no friction                                          |
| 🟡 Amber | 31–60       | One-tap confirmation + order log check. Small delay, transparent message |
| 🔴 Red   | 61–100      | Payout held. Clear explanation + appeal button. Manual review in 2 hrs   |

**Handling Genuine Network Drops in Bad Weather:**  
If Ravi's GPS drops during a flood (the very event he's protected from):

- System uses **last known zone + accelerometer data + order log timestamps**
  instead of live GPS
- GPS signal loss during a verified weather event is NOT treated as fraud
- He never gets penalized for his phone losing signal in a storm

**Trust Score System:**

- Every worker builds a Trust Score (0–100) based on clean claim history
- Trust Score > 80 = "Verified Partner" badge + fast-track approval lane
- High-trust workers auto-approved even on Amber signals
- New workers have 2-week conservative probation period

**Strike Policy:**

- 1st suspicious event → Warning notification, no penalty
- 2nd confirmed anomaly → Premium increases next week
- 3rd confirmed fraud → Account suspended + legal report filed

**False Positive Reversal:**  
Worker can appeal any flagged claim within 48 hours via one-tap appeal button.
If appeal succeeds → immediate payout + ₹50 goodwill credit. No honest
worker is ever permanently punished by a false positive.

**Claim Confidence Score (Shown to Worker):**  
Instead of a cold "Approved" or "Rejected", Ravi sees:

> _"Your claim was verified with 94% confidence based on weather data,
> your zone history, and platform activity."_

---

## 🔐 Cybersecurity Features

### Authentication

- OTP-based login via SMS — no passwords, familiar to gig workers
- JWT tokens with 24-hour expiry on all API calls
- Role-based access control: Worker / Admin / Super Admin

### Data Security

- All PII encrypted at rest with AES-256
- All communication over HTTPS / TLS 1.3
- UPI IDs stored as hashed references — never in plaintext
- Supabase Row Level Security — workers access only their own data

### Claims API Security

- Every claim request signed with worker token + device fingerprint hash
- Nonce + timestamp deduplication — replay attacks rejected silently
- Parametric trigger events cross-validated before processing
- Immutable SHA-256 audit log for every claim state change

### Fraud System Security

- Fraud scores computed server-side only — never exposed to client
- Fraudsters cannot reverse-engineer detection thresholds
- Device fingerprinting disclosed in ToS, compliant with IT Act 2000

### Infrastructure

- All routes behind Nginx reverse proxy
- DDoS protection via Cloudflare free tier
- All secrets in environment variables — never hardcoded
- Admin panel protected by 2FA (TOTP)
- Second admin co-sign required for manual overrides above ₹1,000

---

## 🧰 Tech Stack

| Layer            | Technology                                 |
| ---------------- | ------------------------------------------ |
| Frontend         | React + Tailwind CSS + Vite                |
| Backend          | Python FastAPI                             |
| Database         | Supabase (PostgreSQL + Row Level Security) |
| ML — Pricing     | XGBoost Regression                         |
| ML — Fraud       | Isolation Forest + DBSCAN Clustering       |
| Weather Triggers | OpenWeatherMap API (free tier)             |
| AQI Triggers     | AQICN API                                  |
| Payment Mock     | Razorpay Test Mode / UPI Simulator         |
| Security         | JWT, AES-256, HTTPS, Cloudflare            |
| Hosting          | Vercel (frontend) + Railway (backend)      |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     WORKER (Ravi)                        │
│              React Frontend (Vercel)                     │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS / JWT
┌────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend (Railway)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  Auth    │ │ Policies │ │  Claims  │ │  Triggers │  │
│  └──────────┘ └──────────┘ └──────────┘ └─────┬─────┘  │
│  ┌─────────────────────────────────────────────▼──────┐ │
│  │              Services Layer                        │ │
│  │  Premium Engine │ Fraud Detector │ Ring Detector   │ │
│  │  Payout Engine  │ Trust Score    │ Zone Engine     │ │
│  │  Audit Logger   │ Notification   │ Trigger Monitor │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │                ML Layer                          │   │
│  │  XGBoost (Premium) │ Isolation Forest (Fraud)    │   │
│  │  DBSCAN (Ring Detection) │ Drift Monitor         │   │
│  └──────────────────────────────────────────────────┘   │
└────────────┬────────────────────────┬───────────────────┘
             │                        │
┌────────────▼──────┐    ┌────────────▼────────────────┐
│ Supabase           │    │ External APIs               │
│ PostgreSQL + RLS   │    │ OpenWeatherMap │ IMD Mock    │
│ Audit Log (SHA256) │    │ AQICN │ Zomato Mock         │
│ pgcrypto (AES-256) │    │ Razorpay Sandbox            │
└───────────────────┘    └─────────────────────────────┘
```

---

## 📁 File Structure

```
gigshield/
├── README.md
├── .env.example
├── .gitignore
├── .github/workflows/ci.yml
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── context/
│   │   └── utils/
├── backend/
│   ├── api/
│   ├── services/
│   ├── ml/
│   ├── middleware/
│   ├── models/
│   └── config/
├── database/
│   ├── schema.sql
│   ├── rls_policies.sql
│   └── migrations/
├── mock-apis/
├── tests/
├── scripts/
├── docs/
│   ├── architecture.md
│   ├── adversarial_defense.md
│   ├── premium_model.md
│   └── zone_mapping.md
└── demo/
```

_Built for Guidewire DEVTrails University Hackathon 2026 🚀_  
_Theme: Seed • Scale • Soar_
