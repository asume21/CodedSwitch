import React from 'react'
import './About.css'

const About = () => {
  const items = [
    {
      icon: '💻',
      title: 'CODE (Programming)',
      description:
        'Advanced AI-powered code translation between programming languages. Seamlessly convert Python to JavaScript, Java to C++, and more with intelligent analysis and optimization.'
    },
    {
      icon: '🎤',
      title: 'CODE (Lyrics/Bars)',
      description:
        'Revolutionary AI lyric generation with 7 different rap styles. From Boom Bap to Trap, Drill to Melodic Rap—create professional lyrics with intelligent rhyme suggestions and flow analysis.'
    },
    {
      icon: '🔄',
      title: 'CODE-SWITCHING (Linguistic)',
      description:
        "Seamlessly switch between different modes, languages, and styles. The platform adapts to your needs, whether you're coding, writing lyrics, or analyzing music production."
    },
    {
      icon: '🚀',
      title: 'Revolutionary Features',
      description:
        'AI Code Translation, Lyric Lab, Beat Analysis, Security Scanning, and more—breaking new ground for developers and musicians alike.'
    },
    {
      icon: '🌟',
      title: 'The Vision',
      description:
        'CodedSwitch represents the fusion of programming, music and AI. Empowering creators to push boundaries and turn imagination into reality.'
    }
  ]

  return (
    <section className="about-timeline-section">
      <h2>🎯 The CodedSwitch Story</h2>
      <div className="timeline">
        {items.map((item, index) => (
          <div
            key={index}
            className={`timeline-container ${index % 2 === 0 ? 'left' : 'right'}`}
          >
            <div className="timeline-content">
              <div className="timeline-icon">{item.icon}</div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default About
