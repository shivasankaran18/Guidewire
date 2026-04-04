# LaborGuard — System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Tailwind)               │
│    Landing → Onboarding → Worker Dashboard → Admin Dashboard     │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS / JWT
┌───────────────────────────▼─────────────────────────────────────┐
│                     FASTAPI BACKEND (Python)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐     │
│  │ Auth API  │  │Policy API│  │Claims API│  │  Admin API    │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘     │
│       │              │              │               │             │
│  ┌────▼──────────────▼──────────────▼───────────────▼──────────┐ │
│  │                     SERVICE LAYER                             │ │
│  │  Premium Engine │ Payout Engine │ Fraud Detector │ Ring Det  │ │
│  │  Trigger Monitor│ Trust Score   │ Zone Engine    │ Audit Log │ │
│  └────────────────────────┬─────────────────────────────────────┘ │
│                           │                                       │
│  ┌────────────────────────▼─────────────────────────────────────┐ │
│  │                      ML LAYER                                 │ │
│  │  XGBoost Premium │ Isolation Forest │ DBSCAN Rings │ Earn DNA│ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│              DATABASE (Supabase / PostgreSQL / SQLite)             │
│  workers │ policies │ claims │ triggers │ payouts │ audit_log     │
│  zones   │ fraud_rings │ otp_codes │ movement_signatures          │
│                        + Row Level Security (RLS)                  │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Claim Lifecycle
```
Weather Event → Trigger Monitor → Triple-source validation
     → Auto-create claim → Fraud detection (7 signals)
     → Tier classification (GREEN/AMBER/RED)
     → GREEN: auto-approve + instant UPI
     → AMBER: soft verify (one-tap confirm)
     → RED: hold for 2hr manual review
     → Payout via Razorpay mock
     → Audit log (SHA-256 hash chain)
```

### Premium Calculation
```
Zone risk factors + Worker history + Weather forecast
     → XGBoost regression model
     → Feature importance weighting
     → Dynamic premium (₹29–75/week)
     → Plan tier multiplier (Basic/Standard/Premium)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Tailwind CSS, Recharts, Framer Motion |
| Backend | FastAPI (Python), Uvicorn, async SQLAlchemy |
| ML | XGBoost, Scikit-learn, NumPy/Pandas |
| Database | Supabase (prod), SQLite (dev) |
| Auth | JWT (HS256), OTP-based login |
| Security | AES-256 at rest, SHA-256 audit chain, RLS |
| External APIs | Mock (Weather, IMD, AQICN, Zomato, Razorpay) |

## Security Architecture

1. **Authentication**: OTP → JWT (24hr expiry)
2. **Authorization**: Role-based (Worker / Admin / Super Admin)
3. **Data Protection**: Aadhaar stored as last-4 + SHA-256 hash
4. **Audit Trail**: Immutable SHA-256 hash chain — tampering detected
5. **Device Security**: One device per account, GPS spoof detection
6. **Anti-Replay**: Nonce + timestamp deduplication
7. **Rate Limiting**: Per-IP and per-user throttling
