import React, { useState, useEffect } from 'react';
import { Sliders, Sparkles, UserCheck, Shield, Save, Check } from 'lucide-react';
import { TravelDNA, Persona, User } from '../types';
import { RadarChart } from './RadarChart';
import { api } from '../services/api';

interface TravelProfileViewProps {
  currentDNA: TravelDNA;
  onUpdateDNA: (dna: TravelDNA) => void;
  user: User | null;
}

const DNA_FIELDS: Array<{
  key: keyof TravelDNA;
  label: string;
  description: string;
  lowLabel: string;
  highLabel: string;
}> = [
    {
      key: 'cost_sensitivity',
      label: 'Cost Sensitivity',
      description: 'Importance of minimizing ticket fare vs spending for speed or comfort',
      lowLabel: 'Budget Flexible',
      highLabel: 'Price Conscious',
    },
    {
      key: 'time_sensitivity',
      label: 'Time Sensitivity',
      description: 'Urgency of reaching destination quickly door-to-door',
      lowLabel: 'Leisurely Pace',
      highLabel: 'Express Only',
    },
    {
      key: 'reliability_sensitivity',
      label: 'Reliability Sensitivity',
      description: 'Tolerance for delays, missed connections, or unpredictable transit',
      lowLabel: 'Flexible',
      highLabel: 'Guaranteed On-Time',
    },
    {
      key: 'comfort_preference',
      label: 'Comfort Preference',
      description: 'Preference for 1AC/2AC berths, business class, and direct taxi links',
      lowLabel: 'Standard Transit',
      highLabel: 'Premium Luxury',
    },
    {
      key: 'transfer_tolerance',
      label: 'Transfer Tolerance',
      description: 'Willingness to change transit modes or trains at junctions',
      lowLabel: 'Dislikes Transfers',
      highLabel: 'Multi-Leg Explorer',
    },
    {
      key: 'departure_time_flexibility',
      label: 'Departure Flexibility',
      description: 'Flexibility to adjust schedule to match optimal transit schedules',
      lowLabel: 'Strict Schedule',
      highLabel: 'Highly Flexible',
    },
    {
      key: 'sustainability_preference',
      label: 'Eco & Sustainability',
      description: 'Preference for electric rail and urban transit to cut carbon emissions',
      lowLabel: 'Mode Agnostic',
      highLabel: 'Carbon Minimalist',
    },
  ];

export const TravelProfileView: React.FC<TravelProfileViewProps> = ({
  currentDNA,
  onUpdateDNA,
  user,
}) => {
  const [dna, setDna] = useState<TravelDNA>(currentDNA);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [activePersonaName, setActivePersonaName] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    const loadPersonas = async () => {
      try {
        const p = await api.getPersonas();
        setPersonas(p);
      } catch { }
    };
    loadPersonas();
  }, []);

  const handleSliderChange = (key: keyof TravelDNA, value: number) => {
    const updated = { ...dna, [key]: value };
    setDna(updated);
    setActivePersonaName(null);
    onUpdateDNA(updated);
  };

  const handleSelectPersona = (persona: Persona) => {
    setDna(persona.travel_dna);
    setActivePersonaName(persona.persona_name);
    onUpdateDNA(persona.travel_dna);
  };

  const handleSaveToProfile = async () => {
    if (user) {
      try {
        await api.updateTravelDNA(dna);
      } catch { }
    }
    localStorage.setItem('yatra_travel_dna', JSON.stringify(dna));
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2500);
  };

  return (
    <div className="travel-profile-container">
      {/* Banner */}
      <div className="page-header-banner glass-card">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={22} className="text-cyan" />
            <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              7-Dimensional Travel DNA Profile
            </h1>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Calibrated behavioral parameters powering Yātrā AI's machine learning personalization engine.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-primary"
          onClick={handleSaveToProfile}
        >
          {isSaved ? <Check size={16} /> : <Save size={16} />}
          <span>{isSaved ? 'Preferences Saved!' : 'Save DNA Preferences'}</span>
        </button>
      </div>

      {/* Main Two-Column Layout */}
      <div className="profile-two-column" style={{ marginTop: '20px' }}>
        {/* Left: Persona Presets & Radar Visualizer */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Persona Archetypes Selector */}
          <div className="glass-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <Sparkles size={16} className="text-cyan" />
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Calibrated Persona Archetypes
              </h3>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
              Select a research-calibrated traveler archetype derived from empirical choice behavior models:
            </p>

            <div className="personas-list">
              {personas.map((p) => {
                const isActive = activePersonaName === p.persona_name;
                return (
                  <button
                    key={p.persona_name}
                    type="button"
                    className={`persona-pill-btn ${isActive ? 'active' : ''}`}
                    onClick={() => handleSelectPersona(p)}
                  >
                    <span>{p.persona_name}</span>
                    {isActive && <Check size={14} className="text-cyan" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Radar Chart Visualizer */}
          <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
              Travel DNA Attribute Polygon
            </h3>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Normalized sensitivity coordinates [0.0 - 1.0]
            </span>

            <div style={{ marginTop: '16px' }}>
              <RadarChart dna={dna} size={280} />
            </div>
          </div>
        </div>

        {/* Right: 7-Dimensional Sliders */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Fine-Tune Individual Sensitivities
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Adjust the exact mathematical weights passed to the HistGradientBoosting ML model:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
            {DNA_FIELDS.map((field) => {
              const val = dna[field.key] ?? 0.5;
              return (
                <div key={field.key} className="slider-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <label style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {field.label}
                    </label>
                    <span className="slider-val-badge">
                      {(val * 100).toFixed(0)}%
                    </span>
                  </div>

                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '2px 0 8px 0' }}>
                    {field.description}
                  </p>

                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.02"
                    value={val}
                    className="custom-range-slider"
                    onChange={(e) => handleSliderChange(field.key, parseFloat(e.target.value))}
                  />

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>{field.lowLabel}</span>
                    <span>{field.highLabel}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

