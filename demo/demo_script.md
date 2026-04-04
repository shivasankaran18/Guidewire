# LaborGuard — Demo Script

## Step-by-Step Video Walkthrough (3–5 Minutes)

### Scene 1: The Problem (30 sec)
> "Meet Ravi. A Zomato delivery partner in Chennai earning ₹700/day. When Cyclone Fengal hits, deliveries stop. Ravi loses ₹2,000 in 3 days — with zero recourse."
- Show Landing page hero
- Highlight the problem statement

### Scene 2: Worker Onboarding (45 sec)
> "LaborGuard fixes this. Ravi signs up in 60 seconds."
1. Click **"Get Protected"** on landing page
2. Enter phone → Receive OTP (demo mode shows OTP)
3. Platform ID verification (mock Zomato check)
4. Masked Aadhaar (only last 4 digits — privacy first)
5. Zone selection → Show **CHN-VEL-4B** (Velachery, Chennai)
6. Liveness check → Verified

### Scene 3: Premium & Coverage (45 sec)
> "Dynamic premium priced by AI. ₹29–75/week based on Ravi's zone risk."
1. Navigate to **Policy Page**
2. Show 3 tiers: Basic / Standard / Premium
3. Highlight **Standard Shield** (recommended)
4. Show AI pricing: ₹59/week → Coverage: ₹6,300
5. Click **Activate** → UPI payment → Confirmed

### Scene 4: Parametric Trigger (60 sec)
> "Now watch what happens when it rains."
1. Navigate to **Dashboard** → Show "All Clear" status
2. **Simulate trigger**: Call `/api/triggers/simulate/CHN-VEL-4B/HEAVY_RAIN`
3. Zone Alert turns **orange** → "HEAVY RAIN Alert: 95.5mm/hr"
4. Show triple-source validation: 3/3 sources agree
5. Claim created automatically → Fraud check runs
6. **🟢 GREEN tier** → Auto-approved
7. Show payout: **₹1,120 sent to ravi****@upi**
8. Total time: ~8 seconds from trigger to payout

### Scene 5: Fraud Defense Demo (45 sec)
> "But what about fraud? LaborGuard catches it."
1. Switch to **Admin Dashboard**
2. Show KPI overview (52 workers, 38 active policies)
3. Click **Review Queue** → Show AMBER/RED claims
4. Show 7-signal fraud analysis (GPS velocity, zone mismatch, etc.)
5. Show **DBSCAN Fraud Ring** detection panel
6. Ring of 7 accounts, 85% confidence, spatial + timing + IP correlation
7. Admin clicks **Freeze Ring Accounts**

### Scene 6: Admin Power (30 sec)
> "Full visibility. Full control. Full audit trail."
1. Show **Predictive Risk Map** → Next week's zone forecasts
2. Show **Worker Trust Table** → Scores, strikes, verified partners
3. Show **Immutable Audit Log** → SHA-256 hash chain verified
4. Show **Liquidity Meter** → Pool health (green)

### Scene 7: Closing (15 sec)
> "LaborGuard. From trigger to payout in under 10 seconds. Zero paperwork. AI-powered. Built on Guidewire."
- Show flow: ENROLL → MONITOR → TRIGGER → VERIFY → PAY
- Theme: Seed • Scale • Soar

---

## Demo Credentials

| Account | Login Method |
|---------|-------------|
| Worker (Ravi Kumar) | Click "Demo as Ravi (Worker)" |
| Admin (Priya) | Click "Demo as Admin" |

## Key API Calls for Demo

```bash
# Simulate heavy rain trigger
POST /api/triggers/simulate/CHN-VEL-4B/HEAVY_RAIN

# Simulate flood trigger
POST /api/triggers/simulate/MUM-AND-1A/FLOOD

# Simulate AQI crisis
POST /api/triggers/simulate/DEL-CON-1A/AQI
```
