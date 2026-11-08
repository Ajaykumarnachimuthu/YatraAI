import React, { useState } from 'react';
import {
  Zap,
  Coins,
  ShieldCheck,
  Sparkles,
  ArrowRightLeft,
  Leaf,
  Scale,
  Sliders,
} from 'lucide-react';

interface PreferenceSelectorProps {
  primaryPreference: string;
  secondaryPreference: string | null;
  onSelectPrimary: (pref: string) => void;
  onSelectSecondary: (pref: string | null) => void;
  onOpenAdvancedDNA: () => void;
}

interface PreferenceOption {
  id: string;
  label: string;
  tagline: string;
  icon: React.ReactNode;
  color: string;
}

const PREFERENCES: PreferenceOption[] = [
  {
    id: 'fastest',
    label: 'Fastest Journey',
    tagline: 'Minimizes total door-to-door transit time',
    icon: <Zap size={16} />,
    color: '#0284c7', // Sky 600
  },
  {
    id: 'cheapest',
    label: 'Cheapest Journey',
    tagline: 'Prioritizes lowest total journey fare',
    icon: <Coins size={16} />,
    color: '#059669', // Emerald 600
  },
  {
    id: 'most_reliable',
    label: 'Most Reliable',
    tagline: 'Safe transfer buffers & punctuality',
    icon: <ShieldCheck size={16} />,
    color: '#4f46e5', // Indigo 600
  },
  {
    id: 'maximum_comfort',
    label: 'Maximum Comfort',
    tagline: 'AC sleeper/first tier & direct taxis',
    icon: <Sparkles size={16} />,
    color: '#d97706', // Amber 600
  },
  {
    id: 'minimum_transfers',
    label: 'Min Transfers',
    tagline: 'Simplest routes with fewest legs',
    icon: <ArrowRightLeft size={16} />,
    color: '#7c3aed', // Violet 600
  },
  {
    id: 'eco_friendly',
    label: 'Eco-Friendly',
    tagline: 'Lowest carbon footprint (rail/metro)',
    icon: <Leaf size={16} />,
    color: '#16a34a', // Green 600
  },
  {
    id: 'balanced',
    label: 'Balanced Journey',
    tagline: 'Harmonious speed, cost & reliability',
    icon: <Scale size={16} />,
    color: '#0284c7', // Sky 600
  },
];

export const PreferenceSelector: React.FC<PreferenceSelectorProps> = ({
  primaryPreference,
  secondaryPreference,
  onSelectPrimary,
  onSelectSecondary,
  onOpenAdvancedDNA,
}) => {
  return (
    <div className="preference-selector-container glass-card" style={{ padding: '14px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div>
          <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Travel Style Priorities
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '6px' }}>
            Guides ML ranking
          </span>
        </div>

        {/* Advanced DNA Button */}
        <button
          type="button"
          className="advanced-dna-btn"
          onClick={onOpenAdvancedDNA}
          title="Open calibrated Travel DNA sensitivities & persona archetypes"
        >
          <Sliders size={13} />
          <span>Advanced DNA</span>
        </button>
      </div>

      {/* Primary Preference Cards Grid */}
      <div className="preference-cards-grid">
        {PREFERENCES.map((pref) => {
          const isSelected = primaryPreference.toLowerCase() === pref.id;
          return (
            <button
              key={pref.id}
              type="button"
              className={`pref-card ${isSelected ? 'active' : ''}`}
              onClick={() => onSelectPrimary(pref.id)}
            >
              <div className="pref-card-header">
                <span className="pref-icon" style={{ color: isSelected ? pref.color : 'var(--text-secondary)' }}>
                  {pref.icon}
                </span>
                <span className="pref-name">{pref.label}</span>
                {isSelected && <span className="pref-active-dot" style={{ background: pref.color }} />}
              </div>
              <div className="pref-tagline">{pref.tagline}</div>
            </button>
          );
        })}
      </div>

      {/* Secondary Preference Toggle Row */}
      <div className="secondary-pref-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            Secondary Priority:
          </span>
          <select
            className="secondary-pref-select"
            value={secondaryPreference || ''}
            onChange={(e) => onSelectSecondary(e.target.value || null)}
          >
            <option value="">None (Single Priority)</option>
            {PREFERENCES.filter((p) => p.id !== primaryPreference.toLowerCase()).map((p) => (
              <option key={p.id} value={p.id}>
                + {p.label}
              </option>
            ))}
          </select>
        </div>

        {secondaryPreference && (
          <span className="secondary-pill">
            Dual Priority: <strong>{primaryPreference}</strong> + <strong>{secondaryPreference}</strong>
          </span>
        )}
      </div>
    </div>
  );
};

