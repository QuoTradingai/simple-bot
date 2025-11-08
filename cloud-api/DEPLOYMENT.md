# QuoTrading Cloud API - Render Deployment Guide

## 🚀 Quick Deployment to Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub account

### Step 2: Create PostgreSQL Database
1. Click **"New +"** → **"PostgreSQL"**
2. Name: `quotrading-db`
3. Region: Choose closest to your users
4. Plan: **Free** (for testing) or **Starter $7/mo** (production)
5. Click **"Create Database"**
6. **Copy the Internal Database URL** (starts with `postgresql://`)

### Step 3: Deploy API Service
1. Click **"New +"** → **"Web Service"**
2. Connect your `simple-bot` GitHub repository
3. Configure:
   - **Name:** `quotrading-api`
   - **Region:** Same as database
   - **Branch:** `main`
   - **Root Directory:** `cloud-api`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free (for testing) or Starter $7/mo (production)

### Step 4: Set Environment Variables
In your Render web service dashboard, add these environment variables:

1. **DATABASE_URL**
   - Value: Paste the Internal Database URL from Step 2
   
2. **STRIPE_SECRET_KEY**
   - Get from: https://dashboard.stripe.com/apikeys
   - Value: `sk_test_...` (test mode) or `sk_live_...` (live mode)
   
3. **STRIPE_WEBHOOK_SECRET**
   - Get from: https://dashboard.stripe.com/webhooks
   - Create webhook endpoint: `https://your-render-url.onrender.com/api/v1/webhooks/stripe`
   - Events to listen for:
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_failed`
   - Value: `whsec_...`
   
4. **API_SECRET_KEY**
   - Generate random secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Value: Your generated secret

### Step 5: Deploy
1. Click **"Create Web Service"**
2. Wait 2-3 minutes for deployment
3. Your API will be live at: `https://quotrading-api.onrender.com`

### Step 6: Test Your API
```bash
# Health check
curl https://quotrading-api.onrender.com/

# Register a test user
curl -X POST https://quotrading-api.onrender.com/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Response will include your API key
```

---

## 📊 Pricing Tiers

### Basic - $99/month
- Max 3 contracts per trade
- 1 broker account
- Email support

### Pro - $199/month
- Max 10 contracts per trade
- 3 broker accounts
- Priority email support
- Advanced analytics

### Enterprise - $499/month
- Max 25 contracts per trade
- 10 broker accounts
- 24/7 phone support
- Custom integrations
- Dedicated account manager

---

## 🔧 API Endpoints

### User Registration
```http
POST /api/v1/users/register
Content-Type: application/json

{
  "email": "user@example.com"
}

Response:
{
  "success": true,
  "email": "user@example.com",
  "api_key": "quo_xxxxxxxxxxxxxxxx",
  "message": "Registration successful!"
}
```

### License Validation (Bot uses this)
```http
POST /api/v1/license/validate
Content-Type: application/json

{
  "email": "user@example.com",
  "api_key": "quo_xxxxxxxxxxxxxxxx"
}

Response:
{
  "valid": true,
  "email": "user@example.com",
  "subscription_status": "active",
  "subscription_tier": "pro",
  "subscription_end": "2025-12-08T00:00:00",
  "max_contract_size": 10,
  "max_accounts": 3,
  "message": "License valid - subscription active"
}
```

### Create Subscription
```http
POST /api/v1/subscriptions/create
Content-Type: application/json

{
  "email": "user@example.com",
  "tier": "pro",
  "payment_method_id": "pm_xxxxxxxxxxxxxxxx"
}
```

### Get User Info
```http
GET /api/v1/users/{email}

Response:
{
  "email": "user@example.com",
  "subscription_status": "active",
  "subscription_tier": "pro",
  "subscription_end": "2025-12-08T00:00:00",
  "max_contract_size": 10,
  "max_accounts": 3,
  "last_login": "2025-11-08T12:00:00",
  "total_logins": 42,
  "created_at": "2025-01-01T00:00:00"
}
```

---

## 🔐 Security Notes

1. **HTTPS Only:** Render provides free SSL certificates
2. **Admin Key:** `QUOTRADING_ADMIN_MASTER_2025` bypasses all checks (use carefully!)
3. **API Keys:** Generated as `quo_` + 32 random characters
4. **Webhook Verification:** Stripe signatures are verified
5. **Rate Limiting:** Add in production (use fastapi-limiter)

---

## 📈 Monitoring

**Render Dashboard Shows:**
- API uptime
- Request volume
- Error rates
- Database connections
- Memory/CPU usage

**Stripe Dashboard Shows:**
- Active subscriptions
- Revenue
- Failed payments
- Churn rate

---

## 🐛 Troubleshooting

### API Won't Start
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure DATABASE_URL uses `postgresql://` not `postgres://`

### Database Connection Failed
- Check DATABASE_URL is the **Internal Database URL**
- Verify database is in same region as API
- Check database is running (not paused)

### Stripe Webhooks Not Working
- Verify STRIPE_WEBHOOK_SECRET is correct
- Check webhook URL matches your Render URL
- Ensure webhook events are properly configured

### License Validation Fails
- Verify user exists in database
- Check API key matches exactly (case-sensitive)
- Ensure subscription status is "active"
- Check subscription_end date is in future

---

## 🚀 Going Live

1. **Switch Stripe to Live Mode:**
   - Get live API keys from Stripe dashboard
   - Update STRIPE_SECRET_KEY in Render
   - Create new webhook with live keys

2. **Upgrade Render Plans:**
   - Database: Starter ($7/mo minimum)
   - API: Starter ($7/mo minimum)
   - Total: ~$15/mo for production

3. **Custom Domain (Optional):**
   - Add custom domain in Render
   - Point DNS to Render
   - SSL certificate auto-generated

4. **Update Bot:**
   - Change QUOTRADING_API_URL to production URL
   - Test with real subscriptions
   - Monitor error logs

---

## 💡 Next Steps

1. **Deploy to Render** (follow steps above)
2. **Update bot launcher** to call your API
3. **Create Stripe products** for each tier
4. **Build customer dashboard** (optional)
5. **Set up email notifications** (optional)
