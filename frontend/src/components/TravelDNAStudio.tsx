import React from 'react';
import { Save } from 'lucide-react';
import { TravelDNA, Persona, User } from '../types';
import { RadarChart } from './RadarChart';

interface TravelDNAStudioProps {
  dna: TravelDNA;
  onChange: (newDna: TravelDNA) => void;
  personas: Persona[];
  user: User | null;
  onSaveToProfile: () => void;
  savingProfile: boolean;
}

const DNA_FIELDS: Array<{ key: keyof TravelDNA; label: string; desc: string }> = [
  { key: 'cost_sensitivity', label: 'Cost Sensitivity', desc: 'Price elasticity vs monetary budget' },
  { key: 'time_sensitivity', label: 'Time Sensitivity', desc: 'Disutility of total travel duration' },
  { key: 'reliability_sensitivity', label: 'Reliability Sensitivity', desc: 'Aversion to arrival delay variance' },
  { key: 'comfort_preference', label: 'Comfort Preference', desc: 'Valuation of premium berths & cabin class' },
  { key: 'transfer_tolerance', label: 'Transfer Tolerance', desc: 'Willingness to endure layovers vs direct routes' },
  { key: 'departure_time_flexibility', label: 'Departure Flexibility', desc: 'Willingness to travel during off-peak hours' },
  { key: 'sustainability_preference', label: 'Sustainability Preference', desc: 'Aversion to transit carbon emissions (CO₂)' },
];

export const TravelDNAStudio: React.FC<TravelDNAStudioProps> = ({
  dna,
  onChange,
  personas,
  user,
  onSaveToProfile,
  savingProfile,
}) => {
  const handleSliderChange = (key: keyof TravelDNA, value: number) => {
    onChange({
      ...dna,
      [key]: Math.round(value * 100) / 100,
    });
  };

  const handleReset = () => {
    onChange({
      cost_sensitivity: 0.50,
      time_sensitivity: 0.50,
      reliability_sensitivity: 0.50,
      comfort_preference: 0.50,
      transfer_tolerance: 0.50,
      departure_time_flexibility: 0.50,
      sustainability_preference: 0.50,
    });
  };

  return (
    <div className="glass-card" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 800 }}>7-D Travel DNA</h2>
          <p style={{ fontSize: '0.8rem', color: '#9ca3af' }}>Continuous latent passenger psychographics</p>
        </div>
        <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }} onClick={handleReset}>
          Reset
        </button>
      </div>

      {/* Archetype Preset Chips */}
      <div style={{ marginBottom: '16px' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase' }}>
          Calibrated Archetypes
        </span>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
          {personas.map((p) => (
            <button
              key={p.persona_name}
              type="button"
              className="btn btn-secondary"
              style={{ padding: '4px 8px', fontSize: '0.75rem', borderRadius: '12px' }}
              onClick={() => onChange(p.travel_dna)}
            >
              {p.persona_name}
            </button>
          ))}
        </div>
      </div>

      {/* Radar Chart */}
      <div style={{ margin: '10px 0 16px' }}>
        <RadarChart dna={dna} size={250} />
      </div>

      {/* Continuous Sliders */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {DNA_FIELDS.map((field) => (
          <div key={field.key}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '2px' }}>
              <span style={{ fontWeight: 600 }}>{field.label}</span>
              <span style={{ fontFamily: 'monospace', fontWeight: 700, color: '#06b6d4' }}>
                {Number(dna[field.key] ?? 0.5).toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={dna[field.key] ?? 0.5}
              onChange={(e) => handleSliderChange(field.key, parseFloat(e.target.value))}
              className="dna-slider"
            />
          </div>
        ))}
      </div>

      {/* Save to user profile action */}
      {user && (
        <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <button
            type="button"
            className="btn btn-outline"
            style={{ width: '100%', fontSize: '0.85rem' }}
            onClick={onSaveToProfile}
            disabled={savingProfile}
          >
            {savingProfile ? (
              'Saving...'
            ) : (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                <Save size={14} /> Save as Default DNA Profile
              </span>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

