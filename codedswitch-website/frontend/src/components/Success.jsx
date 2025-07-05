import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import './Success.css';

const Success = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      // In a real app, you'd verify the session with your backend
      // For now, we'll simulate a successful subscription
      setTimeout(() => {
        setSubscription({
          plan: 'Professional',
          features: [
            '200 Lyric Generations per Month',
            'All Code Translation Features',
            'Priority Support',
            'Beat Studio Access',
            'AI Assistant'
          ]
        });
        setLoading(false);
      }, 2000);
    } else {
      setLoading(false);
    }
  }, [searchParams]);

  if (loading) {
    return (
      <div className="success-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Setting up your subscription...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="success-container">
      <div className="success-card">
        <div className="success-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        
        <h1>Welcome to CodedSwitch!</h1>
        <p className="success-message">
          Your subscription has been activated successfully. You now have access to all premium features.
        </p>

        {subscription && (
          <div className="subscription-details">
            <h3>Your {subscription.plan} Plan Includes:</h3>
            <ul>
              {subscription.features.map((feature, index) => (
                <li key={index}>
                  <span className="checkmark">✓</span>
                  {feature}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="next-steps">
          <h3>What's Next?</h3>
          <div className="steps-grid">
            <div className="step">
              <div className="step-number">1</div>
              <h4>Try Lyric Lab</h4>
              <p>Generate AI-powered lyrics with your new increased limits</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h4>Explore Code Translation</h4>
              <p>Translate code between different programming languages</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h4>Access Beat Studio</h4>
              <p>Create professional beats with AI assistance</p>
            </div>
          </div>
        </div>

        <div className="action-buttons">
          <button 
            className="primary-btn"
            onClick={() => window.location.href = '/'}
          >
            Start Creating
          </button>
          <button 
            className="secondary-btn"
            onClick={() => window.location.href = '/pricing'}
          >
            View All Features
          </button>
        </div>

        <div className="support-info">
          <p>
            Need help? Contact us at{' '}
            <a href="mailto:support@codedswitch.com">support@codedswitch.com</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Success; 