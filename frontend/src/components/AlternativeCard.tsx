import React from 'react';
import { Plane, Train, Bookmark, Check } from 'lucide-react';
import { ItineraryItem } from '../types';

interface AlternativeCardProps {
  itinerary: ItineraryItem;
  onSelectJourney: (itinerary: ItineraryItem) => void;
  onSaveTrip: (itinerary: ItineraryItem) => void;
  selected: boolean;
  saved: boolean;
}

export const AlternativeCard: React.FC<AlternativeCardProps> = ({
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
        padding: '18px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        gap: '14px',
        border: selected ? '1.5px solid #10b981' : undefined,
      }}
    >
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: 800, fontSize: '0.9rem', color: '#9ca3af' }}>
            #{itinerary.rank}
          </span>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: isFlight ? 'rgba(6, 182, 212, 0.15)' : 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: isFlight ? '#06b6d4' : '#6366f1',
            }}
          >
            {isFlight ? <Plane size={18} /> : <Train size={18} />}
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>
              {itinerary.carrier} ({itinerary.service_identifier})
            </div>
            <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
              {itinerary.service_tier} • {itinerary.departure_window}
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.7rem', color: '#9ca3af', textTransform: 'uppercase' }}>Match</span>
          <div style={{ fontWeight: 800, color: '#06b6d4' }}>{matchPct}%</div>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', textAlign: 'center', background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '8px' }}>
        <div>
          <span style={{ fontSize: '0.7rem', color: '#9ca3af' }}>Fare</span>
          <div style={{ fontWeight: 700, color: '#10b981', fontSize: '0.95rem' }}>
            ₹{itinerary.cost_inr.toLocaleString()}
          </div>
        </div>
        <div>
          <span style={{ fontSize: '0.7rem', color: '#9ca3af' }}>Duration</span>
          <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>
            {itinerary.duration_hours.toFixed(1)}h
          </div>
        </div>
        <div>
          <span style={{ fontSize: '0.7rem', color: '#9ca3af' }}>Punctuality</span>
          <div style={{ fontWeight: 700, color: '#f59e0b', fontSize: '0.95rem' }}>
            {Math.round(itinerary.historical_punctuality_rate * 100)}%
          </div>
        </div>
      </div>

      {/* Reasons preview */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
        {itinerary.feature_reasons.slice(0, 2).map((r, i) => (
          <span key={i} style={{ fontSize: '0.72rem', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '4px', color: '#9ca3af' }}>
            ✓ {r}
          </span>
        ))}
      </div>

      {/* Card Footer Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <button
          type="button"
          className="btn btn-secondary"
          style={{ padding: '6px 10px', fontSize: '0.75rem' }}
          onClick={() => onSaveTrip(itinerary)}
          disabled={saved}
        >
          {saved ? <Check size={14} /> : <Bookmark size={14} />}
          {saved ? 'Saved' : 'Save'}
        </button>

        <button
          type="button"
          className="btn btn-outline"
          style={{ padding: '6px 12px', fontSize: '0.75rem' }}
          onClick={() => onSelectJourney(itinerary)}
          disabled={selected}
        >
          {selected ? 'Selected' : 'Select Alternative'}
        </button>
      </div>
    </div>
  );
};

