# LaborGuard — API Reference

Base URL: `http://localhost:8000/api`

## Authentication

### POST `/auth/send-otp`
Send OTP to phone number.
```json
{ "phone": "+919876543210" }
→ { "message": "OTP sent. Demo OTP: 123456", "expires_in_seconds": 300 }
```

### POST `/auth/verify-otp`
Verify OTP and get JWT token.
```json
{ "phone": "+919876543210", "otp": "123456" }
→ { "access_token": "eyJ...", "worker_id": "uuid", "role": "WORKER", "name": "Ravi Kumar" }
```

### POST `/auth/register`
Register new worker.
```json
{ "phone": "+919876543210", "name": "Ravi Kumar", "platform": "zomato", "platform_worker_id": "ZW123456" }
```

### POST `/auth/demo-login`
Quick demo worker login (no OTP needed).

### POST `/auth/demo-admin-login`
Quick demo admin login.

---

## Policies

### GET `/policies/plans`
Get available plan tiers with pricing.

### GET `/policies/current`
Get worker's current active policy.

### POST `/policies/activate`
Activate weekly coverage.
```json
{ "plan_tier": "STANDARD", "upi_reference": "UPI_REF123" }
```

### GET `/policies/history`
Get worker's past policies.

---

## Claims

### GET `/claims/`
Get all claims for current worker.

### GET `/claims/{claim_id}`
Get specific claim detail.

### POST `/claims/auto-claim/{trigger_id}`
Auto-create claim from a trigger event. Runs fraud detection.

### POST `/claims/appeal/{claim_id}`
Appeal a rejected/held claim.
```json
{ "reason": "I was actively delivering during this time" }
```

---

## Triggers

### GET `/triggers/status`
Real-time trigger status for worker's zone.

### GET `/triggers/history`
Trigger event history.

### POST `/triggers/simulate/{zone_code}/{trigger_type}`
Simulate a trigger (demo). Types: `HEAVY_RAIN`, `FLOOD`, `HEAT`, `AQI`, `ORDER_SUSPENSION`

---

## Workers

### GET `/workers/profile`
Get current worker profile.

### PUT `/workers/profile`
Update profile.

### GET `/workers/trust-score`
Get trust score breakdown.

### GET `/workers/earnings-dna`
Get Earnings DNA 7×24 heatmap.

### GET `/workers/notifications`
Get worker notifications.

---

## Payouts

### GET `/payouts/`
Get all payouts for current worker.

### GET `/payouts/{payout_id}`
Get specific payout detail.

### POST `/payouts/process/{claim_id}` (Admin)
Manually process a payout.

---

## Admin (requires ADMIN role)

### GET `/admin/dashboard`
Admin overview with KPIs.

### GET `/admin/claims/review`
Claims pending manual review (AMBER/RED tier).

### POST `/admin/claims/{claim_id}/resolve`
Approve or reject a claim.
```json
{ "action": "APPROVE", "notes": "Verified via manual check" }
```

### GET `/admin/fraud-rings`
Detected fraud rings.

### GET `/admin/workers`
All workers list.

---

## Mock APIs

| Endpoint | Source |
|----------|--------|
| `GET /mock/weather/current` | OpenWeatherMap |
| `GET /mock/weather/forecast` | OpenWeatherMap |
| `GET /mock/imd/alerts` | IMD |
| `GET /mock/imd/flood-status` | IMD |
| `GET /mock/aqicn/feed` | AQICN |
| `GET /mock/zomato/verify-worker` | Zomato |
| `GET /mock/zomato/order-activity` | Zomato |
| `GET /mock/zomato/zone-status` | Zomato |
| `POST /mock/razorpay/pay` | Razorpay |
| `POST /mock/razorpay/collect` | Razorpay |
