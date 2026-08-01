import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/SkillBasedMatching.css';

const SkillBasedMatching = () => {
  const [allSkills, setAllSkills] = useState([]);
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [matchedProviders, setMatchedProviders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedProvider, setExpandedProvider] = useState(null);
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    fetchAllSkills();
  }, []);

  const fetchAllSkills = async () => {
    try {
      const response = await axios.get('/api/skills', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAllSkills(response.data);
    } catch (error) {
      console.error('Error fetching skills:', error);
    }
  };

  const toggleSkillSelection = (skillId) => {
    setSelectedSkills(prev =>
      prev.includes(skillId)
        ? prev.filter(id => id !== skillId)
        : [...prev, skillId]
    );
  };

  const handleMatchProviders = async () => {
    if (selectedSkills.length === 0) {
      alert('Please select at least one skill');
      return;
    }

    setLoading(true);
    try {
      const skillsParam = selectedSkills.join(',');
      const response = await axios.get(
        `/api/skills/match?skills=${skillsParam}&limit=20&min_rating=3.0`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMatchedProviders(response.data);
    } catch (error) {
      console.error('Error matching providers:', error);
      alert('Failed to find matching providers');
    } finally {
      setLoading(false);
    }
  };

  const getPercentileLabel = (percentile) => {
    if (percentile >= 95) return '🏆 Top 5%';
    if (percentile >= 90) return '⭐ Top 10%';
    if (percentile >= 75) return '✨ Highly Skilled';
    if (percentile >= 50) return '👍 Above Average';
    return '📈 Getting Started';
  };

  const getScoreColor = (score) => {
    if (score >= 85) return '#27ae60'; // green
    if (score >= 70) return '#f39c12'; // orange
    return '#e74c3c'; // red
  };

  return (
    <div className="skill-matching-container">
      <div className="matching-header">
        <h1>🎯 Smart Provider Matching</h1>
        <p>Find experts, not just ratings. Match based on specific skills.</p>
      </div>

      {/* Skills Selection */}
      <section className="skills-selection">
        <h2>Step 1: Select Required Skills</h2>
        <div className="skills-grid">
          {allSkills.map(skill => (
            <button
              key={skill.id}
              className={`skill-chip ${selectedSkills.includes(skill.id) ? 'selected' : ''}`}
              onClick={() => toggleSkillSelection(skill.id)}
              title={skill.description}
            >
              {skill.icon && <span className="skill-icon">{skill.icon}</span>}
              <span className="skill-name">{skill.name}</span>
              {selectedSkills.includes(skill.id) && <span className="checkmark">✓</span>}
            </button>
          ))}
        </div>

        <div className="selection-summary">
          <p>{selectedSkills.length} skill(s) selected</p>
          <button
            className="btn btn-primary"
            onClick={handleMatchProviders}
            disabled={loading || selectedSkills.length === 0}
          >
            {loading ? 'Finding Expert Providers...' : 'Find Matching Providers'}
          </button>
        </div>
      </section>

      {/* Matched Providers */}
      {matchedProviders.length > 0 && (
        <section className="matched-providers">
          <h2>Step 2: Choose Your Expert</h2>
          <p className="results-info">{matchedProviders.length} providers found</p>

          <div className="providers-list">
            {matchedProviders.map((provider, idx) => (
              <div
                key={idx}
                className={`provider-card ${expandedProvider === idx ? 'expanded' : ''}`}
              >
                <div className="card-header">
                  <div className="rank-badge">#{idx + 1}</div>
                  <div className="provider-info">
                    <h3>{provider.provider_name}</h3>
                    <div className="expertise-labels">
                      {provider.expertise_labels.map((label, i) => (
                        <span key={i} className="expertise-badge">{label}</span>
                      ))}
                    </div>
                  </div>
                  <div className="match-score">
                    <div
                      className="score-circle"
                      style={{
                        background: `conic-gradient(
                          ${getScoreColor(provider.match_score)} 0deg,
                          ${getScoreColor(provider.match_score)} ${provider.match_score * 3.6}deg,
                          #ecf0f1 ${provider.match_score * 3.6}deg
                        )`
                      }}
                    >
                      <span className="score-value">{provider.match_score.toFixed(0)}</span>
                    </div>
                    <p className="score-label">Match Score</p>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedProvider === idx && (
                  <div className="card-details">
                    <div className="skills-breakdown">
                      <h4>Skill Details:</h4>
                      {provider.skills.map((skill, i) => (
                        <div key={i} className="skill-detail">
                          <div className="skill-header">
                            <span className="skill-name">Skill {i + 1}</span>
                            <span className={`percentile ${skill.percentile >= 75 ? 'excellent' : skill.percentile >= 50 ? 'good' : ''}`}>
                              {getPercentileLabel(skill.percentile)}
                            </span>
                          </div>
                          <div className="skill-metrics">
                            <p>⭐ Rating: <strong>{skill.rating.toFixed(1)}/5</strong></p>
                            <p>📊 Percentile: <strong>Top {100 - skill.percentile}%</strong></p>
                            <p>✅ Completed: <strong>{skill.completed_jobs} jobs</strong></p>
                            {skill.verified && <p className="verified">✓ Verified Expert</p>}
                          </div>
                          <div className="rating-bar">
                            <div
                              className="rating-fill"
                              style={{ width: `${skill.rating * 20}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="card-actions">
                      <button className="btn btn-secondary">Request Quote</button>
                      <button className="btn btn-primary">Book Now</button>
                    </div>
                  </div>
                )}

                {/* Collapse/Expand Button */}
                <button
                  className="expand-btn"
                  onClick={() => setExpandedProvider(expandedProvider === idx ? null : idx)}
                >
                  {expandedProvider === idx ? '▼ Hide Details' : '▶ Show Details'}
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* No Results */}
      {!loading && selectedSkills.length > 0 && matchedProviders.length === 0 && (
        <div className="no-results">
          <p>No providers found for the selected skills. Try different skills or lower the rating requirement.</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && selectedSkills.length === 0 && matchedProviders.length === 0 && (
        <div className="empty-state">
          <p>Select skills above to find matching expert providers</p>
        </div>
      )}
    </div>
  );
};

export default SkillBasedMatching;
