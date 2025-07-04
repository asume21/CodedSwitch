import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [pricingPlans, setPricingPlans] = useState([])
  const [loading, setLoading] = useState(false)
  const [paymentStatus, setPaymentStatus] = useState(null)
  const [activeTab, setActiveTab] = useState('home')

  useEffect(() => {
    fetchPricing()
  }, [])

  const fetchPricing = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/pricing')
      const data = await response.json()
      setPricingPlans(data.plans)
    } catch (error) {
      console.error('Error fetching pricing:', error)
    }
  }

  const handlePayment = async (plan) => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:5000/api/create-payment-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: plan.price })
      })
      const data = await response.json()
      
      // Simulate payment success for demo
      setTimeout(() => {
        setPaymentStatus('success')
        setLoading(false)
      }, 2000)
    } catch (error) {
      console.error('Payment error:', error)
      setLoading(false)
    }
  }

  const downloadApp = () => {
    // Simulate download
    const link = document.createElement('a')
    link.href = '#'
    link.download = 'CodedSwitch.exe'
    link.click()
  }

  return (
    <div className="App">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-brand">
            <img 
              src="/codedswitch_logo.png" 
              alt="CodedSwitch AI Godfather Logo" 
              className="coded-logo-navbar" 
            />
            <h1>CodedSwitch</h1>
          </div>
          <div className="nav-menu">
            <button 
              className={`nav-link ${activeTab === 'home' ? 'active' : ''}`}
              onClick={() => setActiveTab('home')}
            >
              Home
            </button>
            <button 
              className={`nav-link ${activeTab === 'about' ? 'active' : ''}`}
              onClick={() => setActiveTab('about')}
            >
              About
            </button>
            <button 
              className={`nav-link ${activeTab === 'features' ? 'active' : ''}`}
              onClick={() => setActiveTab('features')}
            >
              Features
            </button>
            <button 
              className={`nav-link ${activeTab === 'pricing' ? 'active' : ''}`}
              onClick={() => setActiveTab('pricing')}
            >
              Pricing
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'home' && (
          <div className="hero-section">
            <div className="hero-content">
              <img 
                src="/codedswitch_logo.png" 
                alt="CodedSwitch AI Godfather Logo" 
                className="coded-logo" 
              />
              <h1 className="hero-title">
                🎤 CodedSwitch
                <span className="hero-subtitle">The World's First AI Coding Rapper Platform</span>
              </h1>
              <p className="hero-description">
                Revolutionary triple entendre platform combining AI code translation, 
                intelligent lyric generation, and seamless mode switching.
              </p>
              <div className="hero-buttons">
                <button className="btn-primary" onClick={() => setActiveTab('features')}>
                  Explore Features
                </button>
                <button className="btn-secondary" onClick={() => setActiveTab('pricing')}>
                  Get Started
                </button>
              </div>
            </div>
            <div className="hero-visual">
              <div className="platform-preview">
                <div className="code-window">
                  <div className="window-header">
                    <span>💻 Code Translation</span>
                  </div>
                  <div className="code-content">
                    <pre>Python → JavaScript</pre>
                  </div>
                </div>
                <div className="lyric-window">
                  <div className="window-header">
                    <span>🎤 Lyric Lab</span>
                  </div>
                  <div className="lyric-content">
                    <pre>AI Rap Generation</pre>
                  </div>
                </div>
                <div className="beat-window">
                  <div className="window-header">
                    <span>🎧 Beat Analysis</span>
                  </div>
                  <div className="beat-content">
                    <pre>Lyrics → Beat Suggestions</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'about' && (
          <div className="about-section">
            <div className="about-content">
              <h2>🎯 The CodedSwitch Story</h2>
              
              <div className="story-section">
                <h3>🔥 The Triple Entendre Revolution</h3>
                <p>
                  CodedSwitch isn't just another AI platform—it's a revolutionary concept that 
                  combines three powerful meanings into one groundbreaking tool:
                </p>
                
                <div className="entendre-grid">
                  <div className="entendre-card">
                    <h4>💻 CODE (Programming)</h4>
                    <p>Advanced AI-powered code translation between programming languages. 
                    Seamlessly convert Python to JavaScript, Java to C++, and more with 
                    intelligent analysis and optimization.</p>
                  </div>
                  
                  <div className="entendre-card">
                    <h4>🎤 CODE (Lyrics/Bars)</h4>
                    <p>Revolutionary AI lyric generation with 7 different rap styles. 
                    From Boom Bap to Trap, Drill to Melodic Rap—create professional 
                    lyrics with intelligent rhyme suggestions and flow analysis.</p>
                  </div>
                  
                  <div className="entendre-card">
                    <h4>🔄 CODE-SWITCHING (Linguistic)</h4>
                    <p>Seamlessly switch between different modes, languages, and styles. 
                    The platform adapts to your needs, whether you're coding, writing lyrics, 
                    or analyzing music production.</p>
                  </div>
                </div>
              </div>

              <div className="innovation-section">
                <h3>🚀 Revolutionary Features</h3>
                <div className="innovation-grid">
                  <div className="innovation-item">
                    <h4>🎧 World's First Beat Analysis</h4>
                    <p>Analyze your lyrics and get AI-powered beat suggestions including BPM, 
                    drum patterns, instrumentation, and production notes. This has NEVER been done before!</p>
                  </div>
                  
                  <div className="innovation-item">
                    <h4>🛡️ Blockchain IP Protection</h4>
                    <p>Protect your lyrics and code on Story Protocol blockchain. 
                    Automated licensing and royalty management for your creative work.</p>
                  </div>
                  
                  <div className="innovation-item">
                    <h4>🎤 Professional Vocal Coaching</h4>
                    <p>Get AI-powered vocal delivery guides, breath marks, emphasis points, 
                    and studio recording tips for optimal performance.</p>
                  </div>
                  
                  <div className="innovation-item">
                    <h4>🔒 Advanced Security Scanning</h4>
                    <p>Built-in vulnerability scanning for your code with detailed 
                    analysis and automated fix suggestions.</p>
                  </div>
                </div>
              </div>

              <div className="vision-section">
                <h3>🌟 The Vision</h3>
                <p>
                  CodedSwitch represents the future of creative technology—where programming, 
                  music, and AI converge to create something truly revolutionary. It's not just 
                  a tool; it's a complete creative ecosystem that empowers developers, musicians, 
                  and creators to push the boundaries of what's possible.
                </p>
                <p>
                  From the coding rapper who writes bars about debugging to the producer who 
                  needs the perfect beat for their lyrics, CodedSwitch is the platform that 
                  makes the impossible possible.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'features' && (
          <div className="features-section">
            <h2>🎯 Complete Feature Overview</h2>
            
            <div className="features-grid">
              <div className="feature-category">
                <h3>💻 AI Code Translation</h3>
                <ul>
                  <li>Multi-language translation (Python, JavaScript, Java, C++, PHP)</li>
                  <li>Intelligent code optimization</li>
                  <li>Real-time syntax highlighting</li>
                  <li>Translation insights and best practices</li>
                  <li>Auto-save and version control</li>
                </ul>
              </div>

              <div className="feature-category">
                <h3>🎤 AI Lyric Lab</h3>
                <ul>
                  <li>7 different rap styles (Boom Bap, Trap, Drill, Melodic, UK Drill, Experimental, Coding Rap)</li>
                  <li>Real-time rhyme suggestions</li>
                  <li>Flow analysis and rhythm checking</li>
                  <li>Rhyme scheme visualization</li>
                  <li>Professional statistics (syllables, timing, etc.)</li>
                </ul>
              </div>

              <div className="feature-category">
                <h3>🎧 Revolutionary Beat Analysis</h3>
                <ul>
                  <li>AI-powered beat suggestions based on lyrics</li>
                  <li>BPM recommendations</li>
                  <li>Drum pattern suggestions</li>
                  <li>Instrumentation recommendations</li>
                  <li>Vocal mix style guidance</li>
                  <li>Reference track suggestions</li>
                </ul>
              </div>

              <div className="feature-category">
                <h3>🛡️ Security & Protection</h3>
                <ul>
                  <li>Advanced vulnerability scanning</li>
                  <li>Code security analysis</li>
                  <li>Automated fix suggestions</li>
                  <li>Story Protocol blockchain integration</li>
                  <li>IP protection and licensing</li>
                </ul>
              </div>

              <div className="feature-category">
                <h3>🤖 AI Assistant</h3>
                <ul>
                  <li>Intelligent chatbot for coding help</li>
                  <li>Context-aware responses</li>
                  <li>Code debugging assistance</li>
                  <li>Best practice recommendations</li>
                  <li>Real-time problem solving</li>
                </ul>
              </div>

              <div className="feature-category">
                <h3>🎵 Music Production</h3>
                <ul>
                  <li>Vocal delivery coaching</li>
                  <li>Breath mark suggestions</li>
                  <li>Studio recording tips</li>
                  <li>Professional export options</li>
                  <li>Beat studio integration</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'pricing' && (
          <div className="pricing-section">
            <h2>💰 Pricing Plans</h2>
            <p className="pricing-subtitle">Choose the perfect plan for your creative journey</p>
            
            <div className="pricing-grid">
              {pricingPlans.map((plan, index) => (
                <div key={index} className={`pricing-card ${plan.popular ? 'popular' : ''}`}>
                  {plan.popular && <div className="popular-badge">Most Popular</div>}
                  <h3>{plan.name}</h3>
                  <div className="price">
                    <span className="currency">$</span>
                    <span className="amount">{plan.price}</span>
                    <span className="period">/month</span>
                  </div>
                  <ul className="features-list">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex}>{feature}</li>
                    ))}
                  </ul>
                  <button 
                    className={`btn-pricing ${plan.popular ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => handlePayment(plan)}
                    disabled={loading}
                  >
                    {loading ? 'Processing...' : 'Get Started'}
                  </button>
                </div>
              ))}
            </div>

            {paymentStatus === 'success' && (
              <div className="success-message">
                <h3>🎉 Payment Successful!</h3>
                <p>Welcome to CodedSwitch! You can now download the full application.</p>
                <button className="btn-primary" onClick={downloadApp}>
                  Download CodedSwitch
                </button>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>🚀 CodedSwitch</h4>
            <p>The world's first AI coding rapper platform</p>
          </div>
          <div className="footer-section">
            <h4>Features</h4>
            <ul>
              <li>AI Code Translation</li>
              <li>Lyric Generation</li>
              <li>Beat Analysis</li>
              <li>Security Scanning</li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Support</h4>
            <ul>
              <li>Documentation</li>
              <li>API Reference</li>
              <li>Community</li>
              <li>Contact</li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 CodedSwitch. The future of creative coding and music production.</p>
        </div>
      </footer>
    </div>
  )
}

export default App 