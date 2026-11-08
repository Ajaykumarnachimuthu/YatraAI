import React from 'react';
import { X, Sliders, Sparkles, Check } from 'lucide-react';
import { TravelDNA } from '../types';
import { RadarChart } from './RadarChart';

interface AdvancedDNAModalProps {
  isOpen: boolean;
  onClose: () => void;
  travelDna: TravelDNA;
  onChangeDNA: (dna: TravelDNA) => void;
}

const DIMENSIONS: Array<{
  key: keyof TravelDNA;
  label: string;
  desc: string;
}> = [
    { key: 'cost_sensitivity', label: 'Cost Sensitivity', desc: 'Price minimization priority' },
    { key: 'time_sensitivity', label: 'Time Sensitivity', desc: 'Transit speed urgency' },
    { key: 'reliability_sensitivity', label: 'Reliability Sensitivity', desc: 'Punctuality & delay avoidance' },
    { key: 'comfort_preference', label: 'Comfort Preference', desc: '1AC/2AC berths & private taxis' },
    { key: 'transfer_tolerance', label: 'Transfer Tolerance', desc: 'Willingness to change transit legs' },
    { key: 'departure_time_flexibility', label: 'Departure Flexibility', desc: 'Schedule adaptation flexibility' },
    { key: 'sustainability_preference', label: 'Eco Preference', desc: 'Lower carbon footprint priority' },
  ];

export const AdvancedDNAModal: React.FC<AdvancedDNAModalProps> = ({
  isOpen,
  onClose,
  travelDna,
  onChangeDNA,
}) => {
  if (!isOpen) return null;

  const handleChange = (key: keyof TravelDNA, val: number) => {
    onChangeDNA({ ...travelDna, [key]: val });
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content glass-card" style={{ maxWidth: '640px', width: '92%' }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={20} className="text-cyan" />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              Advanced Travel DNA Studio
            </h2>
          </div>
          <button type="button" onClick={onClose} className="modal-close-btn">
            <X size={20} />
          </button>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '18px' }}>
          Calibrated 7-dimensional behavioral coordinates passed to the HistGradientBoosting ML model.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          {/* Sliders */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {DIMENSIONS.map((dim) => {
              const val = travelDna[dim.key] ?? 0.5;
              return (
                <div key={dim.key}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    <span>{dim.label}</span>
                    <span style={{ color: 'var(--action-primary)' }}>{(val * 100).toFixed(0)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={val}
                    className="custom-range-slider"
                    onChange={(e) => handleChange(dim.key, parseFloat(e.target.value))}
                  />
                </div>
              );
            })}
          </div>

          {/* Radar Chart */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <RadarChart dna={travelDna} size={240} />
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '6px' }}>
              Normalized Attribute Surface
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px', paddingTop: '14px', borderTop: '1px solid var(--border-default)' }}>
          <button type="button" className="btn btn-primary" onClick={onClose}>
            <Check size={16} />
            <span>Apply Sensitivities</span>
          </button>
        </div>
      </div>
    </div>
  );
};

