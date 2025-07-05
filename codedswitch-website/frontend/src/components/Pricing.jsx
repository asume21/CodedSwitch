import React, { useState, useEffect } from 'react';
import './Pricing.css';

const Pricing = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/subscription-plans`);
      const data = await response.json();
      setPlans(data.plans);
    } catch (error) {
      console.error('Error fetching plans:', error);
      // Fallback plans if API fails
      setPlans([
        {
          id: 'free',
          name: 'Free',
          price: 0,
          monthlyLyrics: 5,
          features: ['5 Lyric Generations per Month', 'Basic Code Translation', 'Community Support']
        },
        {
          id: 'basic',
          name: 'Basic',
          price: 9.99,
          monthlyLyrics: 50,
          features: ['50 Lyric Generations per Month', 'Advanced Code Translation', 'Email Support', 'Priority Features']
        },
        {
          id: 'pro',
          name: 'Professional',
          price: 19.99,
          monthlyLyrics: 200,
          features: ['200 Lyric Generations per Month', 'All Code Translation Features', 'Priority Support', 'Beat Studio Access', 'AI Assistant']
        },
        {
          id: 'enterprise',
          name: 'Enterprise',
          price: 49.99,
          monthlyLyrics: 1000,
          features: ['Unlimited Lyric Generations', 'All Features', 'Dedicated Support', 'Custom Integrations', 'API Access']
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId) => {
    if (planId === 'free') {
      alert('You are already on the free plan!');
      return;
    }

    setCheckoutLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          planId,
          userId: 'anonymous', // In production, use actual user ID
          successUrl: `${window.location.origin}/success`,
          cancelUrl: `${window.location.origin}/pricing`
        }),
      });

      const data = await response.json();
      
      if (data.url) {
        // Redirect to Stripe checkout
        window.location.href = data.url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
      alert('Failed to start checkout. Please try again.');
    } finally {
      setCheckoutLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="pricing-container">
        <div className="loading">Loading pricing plans...</div>
      </div>
    );
  }

  return (
    <div className="pricing-container">
      <div className="pricing-header">
        <h1>Choose Your CodedSwitch Plan</h1>
        <p>Unlock the full potential of AI-powered code translation and music creation</p>
      </div>

      <div className="pricing-grid">
        {plans.map((plan) => (
          <div 
            key={plan.id} 
            className={`pricing-card ${plan.id === 'pro' ? 'featured' : ''} ${selectedPlan === plan.id ? 'selected' : ''}`}
            onClick={() => setSelectedPlan(plan.id)}
          >
            {plan.id === 'pro' && <div className="featured-badge">Most Popular</div>}
            
            <div className="plan-header">
              <h3>{plan.name}</h3>
              <div className="price">
                <span className="currency">$</span>
                <span className="amount">{plan.price}</span>
                <span className="period">/month</span>
              </div>
              <p className="lyrics-limit">{plan.monthlyLyrics} Lyric Generations</p>
            </div>

            <div className="plan-features">
              <ul>
                {plan.features.map((feature, index) => (
                  <li key={index}>
                    <span className="checkmark">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            <button
              className={`subscribe-btn ${plan.id === 'free' ? 'free' : ''}`}
              onClick={(e) => {
                e.stopPropagation();
                handleSubscribe(plan.id);
              }}
              disabled={checkoutLoading}
            >
              {checkoutLoading && selectedPlan === plan.id ? (
                'Processing...'
              ) : plan.id === 'free' ? (
                'Current Plan'
              ) : (
                'Subscribe Now'
              )}
            </button>
          </div>
        ))}
      </div>

      <div className="pricing-footer">
        <div className="guarantee">
          <h4>30-Day Money-Back Guarantee</h4>
          <p>Not satisfied? Get a full refund within 30 days, no questions asked.</p>
        </div>
        
        <div className="security">
          <h4>Secure Payment</h4>
          <p>All payments are processed securely through Stripe with SSL encryption.</p>
        </div>
      </div>
    </div>
  );
};

export default Pricing; 