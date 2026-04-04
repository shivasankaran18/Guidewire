# LaborGuard — Adversarial Fraud Defense Strategy

## Overview

LaborGuard employs a multi-layered fraud defense system designed to catch both individual fraud and coordinated ring attacks, while maintaining a worker-friendly appeals process.

## 7-Signal Fraud Detection

Each claim is scored across 7 independent signals:

| # | Signal | What it Detects | Weight |
|---|--------|----------------|--------|
| 1 | **Velocity Anomaly** | GPS speed > 120 km/h (impossible for bike) | 25% |
| 2 | **Zone Mismatch** | Claiming in zone where worker hasn't been active | 20% |
| 3 | **Device Risk** | Rooted device, mock GPS, emulator detection | 15% |
| 4 | **Altitude Anomaly** | Zero altitude variance = sitting at desk (GPS spoof) | 10% |
| 5 | **Cell Tower Mismatch** | GPS location vs cell tower distance > 15km | 10% |
| 6 | **Motion Absence** | Accelerometer shows no physical motion | 10% |
| 7 | **Order Absence** | No orders on platform during claimed working time | 10% |

## Three-Tier Classification

```
Score 0–30  → 🟢 GREEN — Auto-approve, instant UPI payout
Score 31–60 → 🟡 AMBER — Soft verify, one-tap worker confirm
Score 61–100 → 🔴 RED  — Hold for review, manual in 2hrs
```

## DBSCAN Fraud Ring Detection

Coordinated fraud ring detection using density-based clustering:

- **Spatial clustering**: Multiple claims within 100m radius
- **Timing synchronization**: Claims filed within 30 seconds
- **IP correlation**: Multiple workers sharing IP subnet
- **Registration surge**: > 10 new accounts from same area/day
- **Home zone diversity**: Ring members from vastly different home zones

### Ring Response Protocol
1. Detect cluster → Flag all members
2. Freeze affected accounts
3. Admin alert with evidence dashboard
4. Two-admin co-sign required for > ₹1000 overrides
5. Report to legal if network confirmed

## Trust Score System

```
Base Score: 50 / 100
+ 3 points per clean claim (max from claims: +30)
- 15 points per fraud strike
Verified Partner: score ≥ 80
```

### Strike Policy
| Strike | Action |
|--------|--------|
| 1st | Warning — no penalty |
| 2nd | Premium increases next week |
| 3rd | Account suspended + legal report |

## False Positive Recovery

- **₹50 goodwill credit** for reversed false positives
- **One-tap appeal** within 48 hours
- **Manual review** within 2 hours guaranteed
- Trust score recovery on successful appeal

## Anti-Gaming Measures

1. **Device fingerprinting**: One device = one account
2. **Replay guard**: Nonce + timestamp deduplication
3. **Probation period**: 2-week monitoring for new accounts
4. **Movement DNA**: Baseline behavioral patterns detect anomalies
5. **Cross-platform verification**: Zomato/Swiggy order data validation
