import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import './App.css'
import LyricLab from './components/LyricLab'
import CodeTranslator from './components/CodeTranslator'
import Pricing from './components/Pricing'
import Success from './components/Success'

function AppContent() {
  const [pricingPlans, setPricingPlans] = useState([])
  const [loading, setLoading] = useState(false)
  const [paymentStatus, setPaymentStatus] = useState(null)
  const [navOpen, setNavOpen] = useState(false)
  const [userPlan, setUserPlan] = useState('free') // Track user subscription
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    fetchPricing()
  }, [])

  const fetchPricing = async () => {
    try {
      const response = await fetch('./pricing.json')
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

  const isActive = (path) => location.pathname === path

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
          <button 
              className="nav-toggle" 
              onClick={() => setNavOpen(!navOpen)}
            >
              &#9776;
            </button>
            <div className={`nav-menu ${navOpen ? 'open' : ''}`}>
            <button 
              className={`nav-link ${isActive('/') ? 'active' : ''}`}
              onClick={() => navigate('/')}
            >
              Home
            </button>
            <button 
              className={`nav-link ${isActive('/about') ? 'active' : ''}`}
              onClick={() => navigate('/about')}
            >
              About
            </button>
            <button 
              className={`nav-link ${isActive('/features') ? 'active' : ''}`}
              onClick={() => navigate('/features')}
            >
              Features
            </button>
            <button 
              className={`nav-link ${isActive('/pricing') ? 'active' : ''}`}
              onClick={() => navigate('/pricing')}
            >
              Pricing
            </button>
            <button 
              className={`nav-link ${isActive('/code-translator') ? 'active' : ''}`}
              onClick={() => navigate('/code-translator')}
            >
              Code Translator
            </button>
            <button 
              className={`nav-link ${isActive('/lyric-lab') ? 'active' : ''}`}
              onClick={() => navigate('/lyric-lab')}
            >
              Lyric Lab
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={
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
                  <button className="btn-primary" onClick={() => navigate('/features')}>
                    Explore Features
                  </button>
                  <button className="btn-secondary" onClick={() => navigate('/pricing')}>
                    Get Started
                  </button>
                </div>
              </div>
              <div className="hero-visual">
                <div className="platform-preview">
                  <div className="code-window interactive-window" onClick={() => navigate('/features')}>
                    <div className="window-header">
                      <span>💻 Code Translation</span>
                    </div>
                    <div className="code-content">
                      <pre>Python → JavaScript</pre>
                    </div>
                  </div>
                  <div className="lyric-window interactive-window" onClick={() => navigate('/features')}>
                    <div className="window-header">
                      <span>🎤 Lyric Lab</span>
                    </div>
                    <div className="lyric-content">
                      <pre>AI Rap Generation</pre>
                    </div>
                  </div>
                  <div className="beat-window interactive-window" onClick={() => navigate('/pricing')}>
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
          } />
          
          <Route path="/about" element={
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

              <div className="demo-section">
                <h3>🎬 Live Demos</h3>
                <div className="demo-grid">
                  <div className="demo-card" onClick={() => navigate('/code-translator')}>
                    <div className="demo-header">
                      <h4>💻 Code Translation Demo</h4>
                      <span className="demo-badge">Try Now</span>
                    </div>
                    <div className="demo-content">
                      <div className="code-preview">
                        <div className="code-block">
                          <span className="lang-label">Python</span>
                          <pre>{`def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)`}</pre>
                        </div>
                        <div className="arrow">→</div>
                        <div className="code-block">
                          <span className="lang-label">JavaScript</span>
                          <pre>{`function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}`}</pre>
                        </div>
                      </div>
                      <p>Click to try the full AI-powered code translator</p>
                    </div>
                  </div>

                  <div className="demo-card" onClick={() => navigate('/lyric-lab')}>
                    <div className="demo-header">
                      <h4>🎤 Lyric Generation Demo</h4>
                      <span className="demo-badge">Try Now</span>
                    </div>
                    <div className="demo-content">
                      <div className="lyric-preview">
                        <div className="style-tag">Trap Style</div>
                        <div className="lyric-example">
                          <p>"808s hitting hard like my code compilation<br/>
                          Stack overflow, but I keep the innovation<br/>
                          Trap beats and algorithms, that's my combination"</p>
                        </div>
                      </div>
                      <p>Click to generate your own AI-powered lyrics</p>
                    </div>
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
                    <div className="feature-demo">
                      <div className="beat-suggestion">
                        <strong>Suggested Beat:</strong> 140 BPM, Trap, Heavy 808s
                      </div>
                    </div>
                  </div>
                  
                  <div className="innovation-item">
                    <h4>🛡️ Blockchain IP Protection</h4>
                    <p>Protect your lyrics and code on Story Protocol blockchain. 
                    Automated licensing and royalty management for your creative work.</p>
                    <div className="feature-demo">
                      <div className="blockchain-status">
                        <span className="status-dot">●</span> IP Protected on Blockchain
                      </div>
                    </div>
                  </div>
                  
                  <div className="innovation-item">
                    <h4>🎤 Professional Vocal Coaching</h4>
                    <p>Get AI-powered vocal delivery guides, breath marks, emphasis points, 
                    and studio recording tips for optimal performance.</p>
                    <div className="feature-demo">
                      <div className="vocal-tips">
                        <strong>Vocal Tips:</strong> Emphasize "compilation" at 0:45
                      </div>
                    </div>
                  </div>
                  
                  <div className="innovation-item">
                    <h4>🔒 Advanced Security Scanning</h4>
                    <p>Built-in vulnerability scanning for your code with detailed 
                    analysis and automated fix suggestions.</p>
                    <div className="feature-demo">
                      <div className="security-scan">
                        <span className="scan-status">✓</span> No vulnerabilities found
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="demo-showcase">
                <h3>🎬 Interactive Demo Showcase</h3>
                <div className="showcase-grid">
                  <div className="showcase-item">
                    <div className="showcase-icon">💻</div>
                    <h4>Code Translation</h4>
                    <p>See AI translate code between 5+ languages instantly</p>
                    <button className="showcase-btn" onClick={() => navigate('/code-translator')}>
                      Try Code Translator
                    </button>
                  </div>
                  
                  <div className="showcase-item">
                    <div className="showcase-icon">🎤</div>
                    <h4>Lyric Generation</h4>
                    <p>Generate rap lyrics in 7 different styles with AI</p>
                    <button className="showcase-btn" onClick={() => navigate('/lyric-lab')}>
                      Try Lyric Lab
                    </button>
                  </div>
                  
                  <div className="showcase-item">
                    <div className="showcase-icon">🎧</div>
                    <h4>Beat Analysis</h4>
                    <p>Get AI-powered beat suggestions for your lyrics</p>
                    <div className="coming-soon">Coming Soon</div>
                  </div>
                  
                  <div className="showcase-item">
                    <div className="showcase-icon">🛡️</div>
                    <h4>Security Scanner</h4>
                    <p>Scan your code for vulnerabilities automatically</p>
                    <div className="coming-soon">Coming Soon</div>
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
          } />

          <Route path="/features" element={
            <div className="features-section">
              <h2>🎯 Complete Feature Overview</h2>
              
              <div className="features-hero">
                <div className="hero-demo">
                  <h3>🚀 Try It Now</h3>
                  <div className="demo-buttons">
                    <button className="demo-btn primary" onClick={() => navigate('/code-translator')}>
                      💻 Code Translator
                    </button>
                    <button className="demo-btn secondary" onClick={() => navigate('/lyric-lab')}>
                      🎤 Lyric Lab
                    </button>
                  </div>
                </div>
              </div>
              
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
                  <div className="feature-example">
                    <div className="example-header">Quick Example:</div>
                    <div className="code-example">
                      <div className="code-side">
                        <span className="lang-tag">Python</span>
                        <pre>{`def greet(name):
    return f"Hello, {name}!"`}</pre>
                      </div>
                      <div className="arrow">→</div>
                      <div className="code-side">
                        <span className="lang-tag">JavaScript</span>
                        <pre>{`function greet(name) {
    return \`Hello, \${name}!\`;
}`}</pre>
                      </div>
                    </div>
                  </div>
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
                  <div className="feature-example">
                    <div className="example-header">Style Preview:</div>
                    <div className="lyric-example">
                      <div className="style-badge">Trap Style</div>
                      <div className="lyric-preview">
                        "808s hitting hard like my code compilation<br/>
                        Stack overflow, but I keep the innovation<br/>
                        Trap beats and algorithms, that's my combination"
                      </div>
                    </div>
                  </div>
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
                  <div className="feature-example">
                    <div className="example-header">Beat Analysis:</div>
                    <div className="beat-analysis">
                      <div className="analysis-item">
                        <strong>BPM:</strong> 140
                      </div>
                      <div className="analysis-item">
                        <strong>Style:</strong> Trap
                      </div>
                      <div className="analysis-item">
                        <strong>Drums:</strong> Heavy 808s, Hi-hats
                      </div>
                    </div>
                  </div>
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
                  <div className="feature-example">
                    <div className="example-header">Security Scan:</div>
                    <div className="security-status">
                      <span className="status-icon">✓</span>
                      <span className="status-text">No vulnerabilities found</span>
                    </div>
                  </div>
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
                  <div className="feature-example">
                    <div className="example-header">AI Chat:</div>
                    <div className="chat-preview">
                      <div className="chat-message">
                        <strong>You:</strong> How do I optimize this function?
                      </div>
                      <div className="chat-response">
                        <strong>AI:</strong> Consider using memoization for better performance...
                      </div>
                    </div>
                  </div>
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
                  <div className="feature-example">
                    <div className="example-header">Vocal Tips:</div>
                    <div className="vocal-tips">
                      <div className="tip-item">
                        <strong>Breath:</strong> Take breath at 0:45
                      </div>
                      <div className="tip-item">
                        <strong>Emphasis:</strong> Stress "compilation"
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="features-cta">
                <h3>Ready to Get Started?</h3>
                <p>Join thousands of developers and musicians using CodedSwitch</p>
                <div className="cta-buttons">
                  <button className="cta-btn primary" onClick={() => navigate('/pricing')}>
                    View Pricing Plans
                  </button>
                  <button className="cta-btn secondary" onClick={() => navigate('/code-translator')}>
                    Try Code Translator
                  </button>
                </div>
              </div>
            </div>
          } />
          
          <Route path="/pricing" element={<Pricing />} />
          
          <Route path="/code-translator" element={
            <div className="code-translator-section">
              <CodeTranslator 
                userSubscription={userSubscription}
              />
            </div>
          } />
          
          <Route path="/lyric-lab" element={
            <div className="lyric-lab-section">
              <LyricLab 
                userPlan={userPlan} 
                onUsageUpdate={(usage) => {
                  console.log('Lyric usage updated:', usage);
                  // Here you can add logic to sync with backend
                }}
              />
            </div>
          } />
          
          <Route path="/success" element={<Success />} />
        </Routes>
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
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App; 