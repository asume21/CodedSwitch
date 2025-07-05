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

// Generate lyrics API endpoint
app.post('/api/generate-lyrics', async (req, res) => {
  try {
    const { style, topic, userPlan } = req.body;
    
    // In production, integrate with your actual AI lyric generation
    // For now, return demo lyrics based on style and topic
    const demoLyrics = generateDemoLyrics(style, topic);
    
    res.json({
      success: true,
      lyrics: demoLyrics,
      style: style,
      topic: topic,
      generatedAt: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error generating lyrics:', error);
    res.status(500).json({ error: 'Failed to generate lyrics' });
  }
});

// Helper function to generate demo lyrics
function generateDemoLyrics(style, topic) {
  const topicText = topic || 'technology';
  
  const lyricsByStyle = {
    'boom-bap': `[Verse 1]
Yo, I'm spitting rhymes about ${topicText}, keeping it real
Breaking down concepts, that's how I feel
From the streets to the code, I'm making the deal
CodedSwitch style, that's the appeal

[Hook]
${topicText}, that's the name
Breaking down barriers, playing the game
From hip-hop to tech, I bridge the gap
Making music and code, that's the rap`,

    'trap': `[Intro]
Yeah, yeah, ${topicText} in the building
Let's go!

[Verse 1]
808s hitting hard like my ${topicText} innovation
Stack overflow, but I keep the dedication
Trap beats and algorithms, that's my combination
Breaking down barriers, that's my foundation

[Hook]
${topicText}, that's the wave
Making moves, that's the way
From trap to tech, I'm here to stay
${topicText}, that's the way`,

    'drill': `[Intro]
${topicText}, drill time
Let's go!

[Verse 1]
Drilling through the ${topicText}, breaking down the walls
Stack overflow, but I never fall
From UK to US, I'm making the call
${topicText}, that's the protocol

[Hook]
Drill time, ${topicText}
Breaking down the code, that's the fix
From drill to tech, I'm making the mix
${topicText}, that's the drill`,

    'melodic': `[Intro]
Oh, oh, oh
${topicText}

[Verse 1]
Melodic flows like the ${topicText} I write
Making music and tech, shining so bright
From Python to JavaScript, I translate the light
${topicText}, making everything right

[Hook]
Oh, ${topicText}, that's the way
Making music and code, every day
From melodic to tech, I'm here to stay
${topicText}, that's the way`,

    'uk-drill': `[Intro]
${topicText}, UK drill
Let's go!

[Verse 1]
UK drill, that's the style
Breaking down ${topicText}, going the extra mile
From London to the world, I'm making the file
${topicText}, that's the profile

[Hook]
UK drill, ${topicText}
Breaking down the code, that's the fix
From UK to tech, I'm making the mix
${topicText}, that's the drill`,

    'experimental': `[Intro]
Experimental, ${topicText}
Let's go!

[Verse 1]
Experimental flows, breaking the mold
Making ${topicText} and tech, that's the goal
From avant-garde to algorithm, I'm in control
${topicText}, that's the role

[Hook]
Experimental, ${topicText}
Breaking down the code, that's the fix
From experimental to tech, I'm making the mix
${topicText}, that's the experimental`,

    'coding-rap': `[Intro]
Coding rap, ${topicText}
Let's go!

[Verse 1]
Coding rap, that's the style
Breaking down ${topicText}, going the extra mile
From Python to JavaScript, I'm making the file
${topicText}, that's the profile

[Hook]
Coding rap, ${topicText}
Breaking down the code, that's the fix
From coding to tech, I'm making the mix
${topicText}, that's the coding rap`
  };

  return lyricsByStyle[style] || lyricsByStyle['boom-bap'];
}

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