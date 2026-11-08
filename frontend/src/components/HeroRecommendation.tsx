import React, { useState } from 'react';
import { Plane, Train, CheckCircle2, Bookmark, Check, ShieldCheck, Clock, IndianRupee, Leaf } from 'lucide-react';
import { ItineraryItem, User } from '../types';

interface HeroRecommendationProps {
  itinerary: ItineraryItem;
  sessionId: number;
  user: User | null;
  onSelectJourney: (itinerary: ItineraryItem) => void;
  onSaveTrip: (itinerary: ItineraryItem) => void;
  selected: boolean;
  saved: boolean;
}

export const HeroRecommendation: React.FC<HeroRecommendationProps> = ({
  itinerary,
  onSelectJourney,
  onSaveTrip,
  selected,
  saved,
}) => {
  const isFlight = itinerary.mode === 'Flight';
  const matchPct = Math.round(itinerary.ml_personalization_score * 100);

  return (
    <div
      className="glass-card"
      style={{
        padding: '24px',
        marginBottom: '24px',
        border: '1.5px solid rgba(99, 102, 241, 0.4)',
        background: 'linear-gradient(180deg, rgba(30, 27, 75, 0.4) 0%, rgba(17, 24, 39, 0.8) 100%)',
      }}
    >
      {/* Header Badge Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="pill pill-indigo" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
            ★ CHAMPION RECOMMENDATION (RANK #1)
          </span>
          {itinerary.preference_threshold_met && (
            <span className="pill pill-emerald" style={{ fontSize: '0.75rem' }}>
              <ShieldCheck size={14} /> Decision Threshold Met (τ ≥ 0.30)
            </span>
          )}
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.75rem', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            ML Preference Match
          </span>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#06b6d4' }}>
            {matchPct}%
          </div>
        </div>
      </div>

      {/* Main Service Info Row */}
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '20px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            style={{
              width: '52px',
              height: '52px',
              borderRadius: '12px',
              background: isFlight ? 'rgba(6, 182, 212, 0.15)' : 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: isFlight ? '#06b6d4' : '#6366f1',
            }}
          >
            {isFlight ? <Plane size={28} /> : <Train size={28} />}
          </div>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>
              {itinerary.carrier} ({itinerary.service_identifier})
            </h3>
            <p style={{ color: '#9ca3af', fontSize: '0.9rem' }}>
              {itinerary.service_tier} • {itinerary.departure_window} • {itinerary.transfer_count === 0 ? 'Direct Non-Stop' : `${itinerary.transfer_count} Transfer(s)`}
            </p>
          </div>
        </div>

        {/* Primary Metrics */}
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#9ca3af', textTransform: 'uppercase' }}>Fare</span>
            <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#10b981', display: 'flex', alignItems: 'center' }}>
              ₹{itinerary.cost_inr.toLocaleString()}
            </div>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: '#9ca3af', textTransform: 'uppercase' }}>Duration</span>
            <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>
              {itinerary.duration_hours.toFixed(1)} hrs
            </div>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: '#9ca3af', textTransform: 'uppercase' }}>Punctuality</span>
            <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f59e0b' }}>
              {Math.round(itinerary.historical_punctuality_rate * 100)}%
            </div>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: '#9ca3af', textTransform: 'uppercase' }}>Carbon</span>
            <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#06b6d4' }}>
              {itinerary.carbon_estimate_kg.toFixed(1)} kg
            </div>
          </div>
        </div>
      </div>

      {/* Feature-Grounded Reasons */}
      <div style={{ marginBottom: '20px' }}>
        <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', marginBottom: '8px', display: 'block' }}>
          Why Yatra AI Champion Recommends This:
        </span>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {itinerary.feature_reasons.map((reason, idx) => (
            <span key={idx} className="pill pill-cyan" style={{ fontSize: '0.82rem', padding: '5px 12px' }}>
              ✓ {reason}
            </span>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '16px' }}>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => onSaveTrip(itinerary)}
          disabled={saved}
        >
          {saved ? <Check size={16} /> : <Bookmark size={16} />}
          {saved ? 'Saved to Trips' : 'Save Itinerary'}
        </button>

        <button
          type="button"
          className="btn btn-primary"
          onClick={() => onSelectJourney(itinerary)}
          disabled={selected}
        >
          {selected ? <CheckCircle2 size={18} /> : null}
          {selected ? 'Journey Selected (Feedback Logged)' : 'Select This Journey'}
        </button>
      </div>
    </div>
  );
};

