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

// Store successful payments and user subscriptions (in production, use a database)
const successfulPayments = new Set();
const userSubscriptions = new Map();
const userUsage = new Map();

// Subscription plans
const SUBSCRIPTION_PLANS = {
  free: {
    name: 'Free',
    price: 0,
    monthlyLyrics: 5,
    features: ['5 Lyric Generations per Month', 'Basic Code Translation', 'Community Support']
  },
  basic: {
    name: 'Basic',
    price: 9.99,
    monthlyLyrics: 50,
    features: ['50 Lyric Generations per Month', 'Advanced Code Translation', 'Email Support', 'Priority Features']
  },
  pro: {
    name: 'Professional',
    price: 19.99,
    monthlyLyrics: 200,
    features: ['200 Lyric Generations per Month', 'All Code Translation Features', 'Priority Support', 'Beat Studio Access', 'AI Assistant']
  },
  enterprise: {
    name: 'Enterprise',
    price: 49.99,
    monthlyLyrics: 1000,
    features: ['Unlimited Lyric Generations', 'All Features', 'Dedicated Support', 'Custom Integrations', 'API Access']
  }
};

// Helper function to get user usage
function getUserUsage(userId) {
  if (!userUsage.has(userId)) {
    userUsage.set(userId, {
      lyricsGenerated: 0,
      lastReset: new Date().toISOString().slice(0, 7) // YYYY-MM format
    });
  }
  
  const usage = userUsage.get(userId);
  const currentMonth = new Date().toISOString().slice(0, 7);
  
  // Reset usage if it's a new month
  if (usage.lastReset !== currentMonth) {
    usage.lyricsGenerated = 0;
    usage.lastReset = currentMonth;
  }
  
  return usage;
}

// Helper function to get user subscription
function getUserSubscription(userId) {
  return userSubscriptions.get(userId) || { plan: 'free', ...SUBSCRIPTION_PLANS.free };
}

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'CodedSwitch API is running' });
});

// Get subscription plans
app.get('/api/subscription-plans', (req, res) => {
  res.json({
    plans: Object.entries(SUBSCRIPTION_PLANS).map(([id, plan]) => ({
      id,
      ...plan
    }))
  });
});

// Get user subscription status
app.get('/api/user/subscription', (req, res) => {
  const userId = req.query.userId || 'anonymous';
  const subscription = getUserSubscription(userId);
  const usage = getUserUsage(userId);
  
  res.json({
    subscription,
    usage,
    canGenerateLyrics: usage.lyricsGenerated < subscription.monthlyLyrics
  });
});

// Create subscription checkout session
app.post('/api/create-checkout-session', async (req, res) => {
  try {
    const { planId, userId, successUrl, cancelUrl } = req.body;
    
    if (!SUBSCRIPTION_PLANS[planId]) {
      return res.status(400).json({ error: 'Invalid plan' });
    }
    
    if (!stripe) {
      // Simulate checkout for development
      const mockSession = {
        id: 'cs_mock_' + Date.now(),
        url: successUrl || 'http://localhost:3000/success'
      };
      
      res.json({ sessionId: mockSession.id, url: mockSession.url });
      return;
    }
    
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: `CodedSwitch ${SUBSCRIPTION_PLANS[planId].name} Plan`,
              description: `Monthly subscription for ${SUBSCRIPTION_PLANS[planId].name} plan`,
            },
            unit_amount: Math.round(SUBSCRIPTION_PLANS[planId].price * 100), // Convert to cents
          },
          quantity: 1,
        },
      ],
      mode: 'subscription',
      success_url: successUrl || `${process.env.FRONTEND_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: cancelUrl || `${process.env.FRONTEND_URL}/pricing`,
      metadata: {
        userId: userId || 'anonymous',
        planId: planId
      }
    });

    res.json({ sessionId: session.id, url: session.url });
  } catch (error) {
    console.error('Error creating checkout session:', error);
    res.status(500).json({ error: 'Failed to create checkout session' });
  }
});

// Handle subscription webhook (for production)
app.post('/api/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  if (!stripe) {
    return res.status(200).json({ received: true });
  }
  
  const sig = req.headers['stripe-signature'];
  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle the event
  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object;
      const userId = session.metadata.userId;
      const planId = session.metadata.planId;
      
      // Update user subscription
      userSubscriptions.set(userId, {
        plan: planId,
        ...SUBSCRIPTION_PLANS[planId],
        subscribedAt: new Date().toISOString(),
        stripeCustomerId: session.customer
      });
      
      console.log(`User ${userId} subscribed to ${planId} plan`);
      break;
      
    case 'customer.subscription.deleted':
      const subscription = event.data.object;
      // Handle subscription cancellation
      console.log('Subscription cancelled:', subscription.id);
      break;
      
    default:
      console.log(`Unhandled event type ${event.type}`);
  }

  res.json({ received: true });
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

// Generate lyrics API endpoint with usage tracking
app.post('/api/generate-lyrics', async (req, res) => {
  try {
    const { style, topic, userId } = req.body;
    
    // Get user subscription and usage
    const subscription = getUserSubscription(userId || 'anonymous');
    const usage = getUserUsage(userId || 'anonymous');
    
    // Check if user can generate more lyrics
    if (usage.lyricsGenerated >= subscription.monthlyLyrics) {
      return res.status(403).json({
        error: 'Monthly limit reached',
        message: `You've reached your monthly limit of ${subscription.monthlyLyrics} lyric generations.`,
        upgradeRequired: true,
        currentPlan: subscription.name,
        usage: usage
      });
    }
    
    // In production, integrate with your actual AI lyric generation
    // For now, return demo lyrics based on style and topic
    const demoLyrics = generateDemoLyrics(style, topic);
    
    // Update usage
    usage.lyricsGenerated += 1;
    userUsage.set(userId || 'anonymous', usage);
    
    res.json({
      success: true,
      lyrics: demoLyrics,
      style: style,
      topic: topic,
      generatedAt: new Date().toISOString(),
      usage: {
        ...usage,
        remaining: subscription.monthlyLyrics - usage.lyricsGenerated
      }
    });
  } catch (error) {
    console.error('Error generating lyrics:', error);
    res.status(500).json({ error: 'Failed to generate lyrics' });
  }
});

// Translate code API endpoint
app.post('/api/translate-code', async (req, res) => {
  try {
    const { sourceCode, sourceLanguage, targetLanguage, userId } = req.body;
    
    if (!sourceCode || !sourceLanguage || !targetLanguage) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }
    
    // Get user subscription and usage
    const subscription = getUserSubscription(userId || 'anonymous');
    const usage = getUserUsage(userId || 'anonymous');
    
    // Check if user can translate more code (different limit for code translation)
    const codeTranslationLimit = subscription.plan === 'free' ? 10 : 100;
    if (usage.codeTranslations >= codeTranslationLimit) {
      return res.status(403).json({
        error: 'Monthly limit reached',
        message: `You've reached your monthly limit of ${codeTranslationLimit} code translations.`,
        upgradeRequired: true,
        currentPlan: subscription.name,
        usage: usage
      });
    }
    
    // In production, integrate with your actual AI code translation service
    // For now, return demo translation
    const translatedCode = generateDemoCodeTranslation(sourceCode, sourceLanguage, targetLanguage);
    
    // Update usage
    usage.codeTranslations = (usage.codeTranslations || 0) + 1;
    userUsage.set(userId || 'anonymous', usage);
    
    res.json({
      success: true,
      translatedCode: translatedCode,
      sourceLanguage: sourceLanguage,
      targetLanguage: targetLanguage,
      translatedAt: new Date().toISOString(),
      usage: {
        ...usage,
        remaining: codeTranslationLimit - usage.codeTranslations
      }
    });
  } catch (error) {
    console.error('Error translating code:', error);
    res.status(500).json({ error: 'Failed to translate code' });
  }
});

// Helper function to generate demo code translation
function generateDemoCodeTranslation(sourceCode, sourceLanguage, targetLanguage) {
  const translations = {
    'python-javascript': (code) => {
      return code
        .replace(/def /g, 'function ')
        .replace(/if /g, 'if (')
        .replace(/:/g, ') {')
        .replace(/print\(/g, 'console.log(')
        .replace(/range\(/g, 'Array.from({length: ')
        .replace(/\)/g, '}, (_, i) => i)')
        .replace(/for /g, 'for (let ')
        .replace(/ in /g, ' of ')
        .replace(/return /g, 'return ')
        .replace(/def /g, 'function ')
        .replace(/None/g, 'null')
        .replace(/True/g, 'true')
        .replace(/False/g, 'false');
    },
    'javascript-python': (code) => {
      return code
        .replace(/function /g, 'def ')
        .replace(/console\.log\(/g, 'print(')
        .replace(/let /g, '')
        .replace(/const /g, '')
        .replace(/var /g, '')
        .replace(/for \(let /g, 'for ')
        .replace(/ of /g, ' in ')
        .replace(/null/g, 'None')
        .replace(/true/g, 'True')
        .replace(/false/g, 'False')
        .replace(/;/g, '')
        .replace(/{/g, ':')
        .replace(/}/g, '');
    },
    'python-java': (code) => {
      return `public class Main {
    ${code
      .replace(/def /g, 'public static ')
      .replace(/print\(/g, 'System.out.println(')
      .replace(/range\(/g, 'IntStream.range(0, ')
      .replace(/for /g, 'for (int ')
      .replace(/ in /g, ' = 0; ')
      .replace(/:/g, ' < ')
      .replace(/None/g, 'null')
      .replace(/True/g, 'true')
      .replace(/False/g, 'false')
    }
    
    public static void main(String[] args) {
        // Your code here
    }
}`;
    }
  };
  
  const key = `${sourceLanguage}-${targetLanguage}`;
  const translator = translations[key];
  
  if (translator) {
    return translator(sourceCode);
  }
  
  // Fallback translation
  return `// Translation from ${sourceLanguage} to ${targetLanguage}
// Demo translation - connect to AI service for real translation

${sourceCode}`;
}

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