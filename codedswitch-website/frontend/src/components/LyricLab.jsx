import React, { useState, useEffect } from 'react';
import './LyricLab.css';

const LyricLab = ({ userPlan = 'free', onUsageUpdate }) => {
  const [selectedStyle, setSelectedStyle] = useState('boom-bap');
  const [topic, setTopic] = useState('');
  const [generatedLyrics, setGeneratedLyrics] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [userSubscription, setUserSubscription] = useState(null);
  const [userUsage, setUserUsage] = useState(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [loading, setLoading] = useState(true);

  const rapStyles = [
    { id: 'boom-bap', name: 'Boom Bap', description: 'Classic 90s hip-hop style' },
    { id: 'trap', name: 'Trap', description: 'Modern trap with heavy 808s' },
    { id: 'drill', name: 'Drill', description: 'Aggressive UK drill style' },
    { id: 'melodic', name: 'Melodic Rap', description: 'Melodic and singing rap' },
    { id: 'uk-drill', name: 'UK Drill', description: 'British drill style' },
    { id: 'experimental', name: 'Experimental', description: 'Avant-garde rap' },
    { id: 'coding-rap', name: 'Coding Rap', description: 'Tech and programming themes' }
  ];

  useEffect(() => {
    fetchUserSubscription();
  }, []);

  const fetchUserSubscription = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/user/subscription?userId=anonymous`);
      const data = await response.json();
      setUserSubscription(data.subscription);
      setUserUsage(data.usage);
    } catch (error) {
      console.error('Error fetching subscription:', error);
      // Fallback to free plan
      setUserSubscription({
        plan: 'free',
        name: 'Free',
        monthlyLyrics: 5,
        features: ['5 Lyric Generations per Month', 'Basic Code Translation', 'Community Support']
      });
      setUserUsage({
        lyricsGenerated: 0,
        lastReset: new Date().toISOString().slice(0, 7)
      });
    } finally {
      setLoading(false);
    }
  };

  const canGenerate = () => {
    if (!userSubscription || !userUsage) return false;
    return userUsage.lyricsGenerated < userSubscription.monthlyLyrics;
  };

  const generateLyrics = async () => {
    if (!topic.trim()) {
      alert('Please enter a topic for your lyrics!');
      return;
    }

    if (!canGenerate()) {
      setShowUpgradeModal(true);
      return;
    }

    setIsGenerating(true);

    try {
      // API call to your backend
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/generate-lyrics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          style: selectedStyle,
          topic: topic,
          userId: 'anonymous'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedLyrics(data.lyrics);
        
        // Update usage from response
        if (data.usage) {
          setUserUsage(data.usage);
        }
        
        if (onUsageUpdate) {
          onUsageUpdate(data.usage?.lyricsGenerated || 0);
        }
      } else if (response.status === 403) {
        const errorData = await response.json();
        if (errorData.upgradeRequired) {
          setShowUpgradeModal(true);
        } else {
          throw new Error(errorData.message || 'Failed to generate lyrics');
        }
      } else {
        throw new Error('Failed to generate lyrics');
      }
    } catch (error) {
      console.error('Error generating lyrics:', error);
      alert(error.message || 'Failed to generate lyrics. Please try again.');
    }

    setIsGenerating(false);
  };

  const generateDemoLyrics = () => {
    const demoLyrics = {
      'boom-bap': `[Verse 1]
Yo, I'm spitting rhymes like a coding machine
Breaking down algorithms, keeping it clean
From Python to JavaScript, I translate the flow
Making beats and bars, watch the code glow

[Hook]
CodedSwitch, that's the name
Breaking down languages, playing the game
From hip-hop to tech, I bridge the gap
Making music and code, that's the rap`,

      'trap': `[Intro]
Yeah, yeah, CodedSwitch in the building
Let's go!

[Verse 1]
808s hitting hard like my code compilation
Stack overflow, but I keep the innovation
Trap beats and algorithms, that's my combination
Breaking down barriers, that's my dedication

[Hook]
CodedSwitch, that's the wave
Making moves, that's the way
From trap to tech, I'm here to stay
CodedSwitch, that's the way`,

      'drill': `[Intro]
CodedSwitch, drill time
Let's go!

[Verse 1]
Drilling through the code, breaking down the walls
Stack overflow, but I never fall
From UK to US, I'm making the call
CodedSwitch, that's the protocol

[Hook]
Drill time, CodedSwitch
Breaking down the code, that's the fix
From drill to tech, I'm making the mix
CodedSwitch, that's the drill`,

      'melodic': `[Intro]
Oh, oh, oh
CodedSwitch

[Verse 1]
Melodic flows like the code I write
Making music and tech, shining so bright
From Python to JavaScript, I translate the light
CodedSwitch, making everything right

[Hook]
Oh, CodedSwitch, that's the way
Making music and code, every day
From melodic to tech, I'm here to stay
CodedSwitch, that's the way`,

      'uk-drill': `[Intro]
CodedSwitch, UK drill
Let's go!

[Verse 1]
UK drill, that's the style
Breaking down code, going the extra mile
From London to the world, I'm making the file
CodedSwitch, that's the profile

[Hook]
UK drill, CodedSwitch
Breaking down the code, that's the fix
From UK to tech, I'm making the mix
CodedSwitch, that's the drill`,

      'experimental': `[Intro]
Experimental, CodedSwitch
Let's go!

[Verse 1]
Experimental flows, breaking the mold
Making music and tech, that's the goal
From avant-garde to algorithm, I'm in control
CodedSwitch, that's the role

[Hook]
Experimental, CodedSwitch
Breaking down the code, that's the fix
From experimental to tech, I'm making the mix
CodedSwitch, that's the experimental`,

      'coding-rap': `[Intro]
Coding rap, CodedSwitch
Let's go!

[Verse 1]
Coding rap, that's the style
Breaking down algorithms, going the extra mile
From Python to JavaScript, I'm making the file
CodedSwitch, that's the profile

[Hook]
Coding rap, CodedSwitch
Breaking down the code, that's the fix
From coding to tech, I'm making the mix
CodedSwitch, that's the coding rap`
    };

    return demoLyrics[selectedStyle] || demoLyrics['boom-bap'];
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedLyrics);
    alert('Lyrics copied to clipboard!');
  };

  const downloadLyrics = () => {
    const blob = new Blob([generatedLyrics], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `codedswitch-lyrics-${selectedStyle}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="lyric-lab">
        <div className="loading">Loading Lyric Lab...</div>
      </div>
    );
  }

  return (
    <div className="lyric-lab">
      <div className="lyric-lab-header">
        <h2>🎤 Lyric Lab</h2>
        <p>AI-powered lyric generation with 7 different rap styles</p>
        
        <div className="usage-info">
          <span className="usage-text">
            Monthly Usage: {userUsage?.lyricsGenerated || 0} / {userSubscription?.monthlyLyrics || 5}
          </span>
          {userSubscription?.plan === 'free' && (
            <button 
              className="upgrade-btn"
              onClick={() => setShowUpgradeModal(true)}
            >
              Upgrade to Pro
            </button>
          )}
        </div>
      </div>

      <div className="lyric-lab-content">
        <div className="lyric-controls">
          <div className="style-selector">
            <label>Rap Style:</label>
            <select 
              value={selectedStyle} 
              onChange={(e) => setSelectedStyle(e.target.value)}
            >
              {rapStyles.map(style => (
                <option key={style.id} value={style.id}>
                  {style.name} - {style.description}
                </option>
              ))}
            </select>
          </div>

          <div className="topic-input">
            <label>Topic/Theme:</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter your topic (e.g., 'coding', 'success', 'technology')"
            />
          </div>

          <button 
            className="generate-btn"
            onClick={generateLyrics}
            disabled={isGenerating || !canGenerate()}
          >
            {isGenerating ? 'Generating...' : 'Generate Lyrics'}
          </button>
        </div>

        {generatedLyrics && (
          <div className="lyrics-output">
            <div className="lyrics-header">
              <h3>Generated Lyrics ({rapStyles.find(s => s.id === selectedStyle)?.name})</h3>
              <div className="lyrics-actions">
                <button onClick={copyToClipboard} className="action-btn">
                  📋 Copy
                </button>
                <button onClick={downloadLyrics} className="action-btn">
                  💾 Download
                </button>
              </div>
            </div>
            <div className="lyrics-content">
              <pre>{generatedLyrics}</pre>
            </div>
          </div>
        )}
      </div>

      {showUpgradeModal && (
        <div className="modal-overlay">
          <div className="upgrade-modal">
            <h3>🚀 Upgrade Your Plan!</h3>
            <p>You've reached your monthly limit of {userSubscription?.monthlyLyrics || 5} lyrics.</p>
            <p>Upgrade to unlock more generations and advanced features!</p>
            <div className="modal-actions">
              <button 
                className="upgrade-btn"
                onClick={() => {
                  setShowUpgradeModal(false);
                  // Navigate to pricing page
                  window.location.href = '/pricing';
                }}
              >
                View Plans
              </button>
              <button 
                className="cancel-btn"
                onClick={() => setShowUpgradeModal(false)}
              >
                Maybe Later
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LyricLab; 