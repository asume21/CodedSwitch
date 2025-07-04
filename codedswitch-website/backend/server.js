require('dotenv').config();
const express = require('express');
const cors = require('cors');

// Initialize Stripe only if API key is available
let stripe;
try {
  if (process.env.STRIPE_SECRET_KEY && process.env.STRIPE_SECRET_KEY !== 'sk_test_placeholder_key_for_development') {
    stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
    console.log('✅ Stripe initialized successfully');
  } else {
    console.log('⚠️  Stripe API key not configured. Payment features will be simulated.');
  }
} catch (error) {
  console.log('⚠️  Stripe not available. Payment features will be simulated.');
}

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Store successful payments (in production, use a database)
const successfulPayments = new Set();

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'CodedSwitch API is running' });
});

// Create payment intent for subscription
app.post('/api/create-payment-intent', async (req, res) => {
  try {
    const { amount, currency = 'usd' } = req.body;
    
    if (!stripe) {
      // Simulate payment for development
      const mockPaymentIntent = {
        id: 'pi_mock_' + Date.now(),
        client_secret: 'pi_mock_secret_' + Date.now(),
        status: 'requires_payment_method'
      };
      
      res.json({
        clientSecret: mockPaymentIntent.client_secret
      });
      return;
    }
    
    const paymentIntent = await stripe.paymentIntents.create({
      amount: amount * 100, // Convert to cents
      currency,
      metadata: {
        product: 'CodedSwitch Subscription'
      }
    });

    res.json({
      clientSecret: paymentIntent.client_secret
    });
  } catch (error) {
    console.error('Error creating payment intent:', error);
    res.status(500).json({ error: 'Failed to create payment intent' });
  }
});

// Handle successful payment
app.post('/api/payment-success', async (req, res) => {
  try {
    const { paymentIntentId } = req.body;
    
    if (!stripe) {
      // Simulate successful payment for development
      successfulPayments.add(paymentIntentId);
      res.json({ 
        success: true, 
        message: 'Payment successful! You can now download CodedSwitch.',
        downloadUrl: '/api/download'
      });
      return;
    }
    
    // Verify payment with Stripe
    const paymentIntent = await stripe.paymentIntents.retrieve(paymentIntentId);
    
    if (paymentIntent.status === 'succeeded') {
      successfulPayments.add(paymentIntentId);
      res.json({ 
        success: true, 
        message: 'Payment successful! You can now download CodedSwitch.',
        downloadUrl: '/api/download'
      });
    } else {
      res.status(400).json({ error: 'Payment not completed' });
    }
  } catch (error) {
    console.error('Error handling payment success:', error);
    res.status(500).json({ error: 'Failed to verify payment' });
  }
});

// Secure download endpoint
app.get('/api/download', (req, res) => {
  const { paymentId } = req.query;
  
  if (!paymentId || !successfulPayments.has(paymentId)) {
    return res.status(403).json({ 
      error: 'Access denied. Please complete payment first.' 
    });
  }
  
  // In production, serve the actual file
  // For now, return a success message
  res.json({ 
    success: true, 
    message: 'Download access granted!',
    downloadLink: 'https://your-actual-download-link.com/codedswitch.zip'
  });
});

// Get pricing information
app.get('/api/pricing', (req, res) => {
  res.json({
    plans: [
      {
        id: 'basic',
        name: 'Basic',
        price: 9.99,
        features: [
          'Full CodedSwitch Access',
          'Basic Support',
          '30-day Money Back Guarantee'
        ]
      },
      {
        id: 'pro',
        name: 'Professional',
        price: 19.99,
        features: [
          'Full CodedSwitch Access',
          'Priority Support',
          'Advanced Features',
          '30-day Money Back Guarantee'
        ]
      }
    ]
  });
});

app.listen(PORT, () => {
  console.log(`CodedSwitch API server running on port ${PORT}`);
}); 