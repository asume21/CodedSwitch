# Payment Setup Guide for CodedSwitch

## 1. Stripe Account Setup

### Create Stripe Account
1. Go to [stripe.com](https://stripe.com) and create an account
2. Complete your business verification
3. Add your business information and bank account for payouts

### Get Your API Keys
1. Go to [Stripe Dashboard > Developers > API Keys](https://dashboard.stripe.com/apikeys)
2. Copy your **Publishable Key** (starts with `pk_live_`)
3. Copy your **Secret Key** (starts with `sk_live_`)
4. **IMPORTANT**: Never share your secret key publicly!

## 2. Webhook Setup

### Create Webhook Endpoint
1. Go to [Stripe Dashboard > Developers > Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Set endpoint URL to: `https://your-domain.com/api/webhook`
4. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the **Webhook Secret** (starts with `whsec_`)

## 3. Environment Variables

### Backend (.env file)
Create a `.env` file in your backend directory:

```env
# Server Configuration
PORT=5000
NODE_ENV=production

# Frontend URL (for CORS and redirects)
FRONTEND_URL=https://your-domain.com

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_live_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### Render Environment Variables
In your Render dashboard, add these environment variables:
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `FRONTEND_URL`

## 4. Product Setup in Stripe

### Create Products
1. Go to [Stripe Dashboard > Products](https://dashboard.stripe.com/products)
2. Create products for each plan:
   - **Basic Plan** ($9.99/month)
   - **Professional Plan** ($19.99/month)
   - **Enterprise Plan** ($49.99/month)

### Set Up Recurring Pricing
1. For each product, set up recurring pricing
2. Choose "Recurring price" with monthly billing
3. Set the price to match your plans

## 5. Legal Requirements

### Terms of Service & Privacy Policy
You need these for legal compliance:
- Terms of Service
- Privacy Policy
- Refund Policy

### Tax Configuration
1. Set up tax rates in Stripe if required
2. Configure tax collection for your jurisdiction

## 6. Testing

### Test Mode
Before going live:
1. Use test keys (start with `sk_test_` and `pk_test_`)
2. Test the complete payment flow
3. Test webhook handling
4. Test subscription management

### Test Cards
Use these test card numbers:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- 3D Secure: `4000 0025 0000 3155`

## 7. Go Live Checklist

- [ ] Stripe account verified
- [ ] API keys switched to live mode
- [ ] Webhook endpoint configured
- [ ] Products created in Stripe
- [ ] Environment variables set
- [ ] Legal documents in place
- [ ] Testing completed
- [ ] Domain SSL certificate active

## 8. Monitoring

### Stripe Dashboard
Monitor these metrics:
- Payment success/failure rates
- Subscription metrics
- Revenue analytics
- Dispute handling

### Webhook Monitoring
- Check webhook delivery status
- Monitor for failed webhook attempts
- Set up alerts for critical events

## 9. Security Best Practices

1. **Never commit API keys to git**
2. Use environment variables
3. Enable webhook signature verification
4. Implement proper error handling
5. Use HTTPS everywhere
6. Regular security audits

## 10. Support & Documentation

### Stripe Resources
- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Support](https://support.stripe.com)
- [Stripe Community](https://community.stripe.com)

### Your Implementation
- Webhook endpoint: `/api/webhook`
- Checkout endpoint: `/api/create-checkout-session`
- Subscription management: `/api/user/subscription`

## Quick Start Commands

```bash
# Test the payment flow locally
cd codedswitch-website/backend
npm install
npm start

# Test webhook locally (using ngrok)
ngrok http 5000
# Then update webhook URL in Stripe dashboard
```

## Troubleshooting

### Common Issues
1. **Webhook not receiving events**: Check endpoint URL and signature verification
2. **Payment failing**: Verify API keys and product setup
3. **CORS errors**: Check FRONTEND_URL environment variable
4. **Subscription not updating**: Verify webhook event handling

### Debug Mode
Add this to your backend for debugging:
```javascript
console.log('Stripe event received:', event.type);
console.log('Event data:', event.data.object);
``` 