import React, { useEffect, useState } from 'react';
import { Compass, ArrowRight, Plane, Train, Bus, ShieldCheck, Sparkles } from 'lucide-react';
import { PopularCorridor } from '../types';
import { api } from '../services/api';

interface ExploreViewProps {
  onSelectCorridor: (origin: string, destination: string) => void;
}

export const ExploreView: React.FC<ExploreViewProps> = ({ onSelectCorridor }) => {
  const [corridors, setCorridors] = useState<PopularCorridor[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      const data = await api.getPopularCorridors();
      setCorridors(data);
      setIsLoading(false);
    };
    load();
  }, []);

  return (
    <div className="explore-view-container">
      {/* Banner */}
      <div className="page-header-banner glass-card">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Compass size={22} className="text-cyan" />
            <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              Explore Major Multimodal Corridors
            </h1>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Explore high-speed rail, air-transit bridges, and road-rail combinations connecting India's metropolitan clusters.
          </p>
        </div>
      </div>

      {/* Corridor Cards Grid */}
      <div className="explore-grid">
        {corridors.map((c) => (
          <div key={c.id} className="corridor-explore-card glass-card">
            <div className="corridor-card-header">
              <div>
                <span className="corridor-route-badge">
                  {c.origin} ➔ {c.destination}
                </span>
                <h3 className="corridor-title" style={{ marginTop: '6px' }}>
                  {c.title}
                </h3>
              </div>
              <span className="corridor-dist-pill">{c.distance_km} km</span>
            </div>

            <div className="corridor-card-body">
              <div style={{ display: 'flex', gap: '6px', margin: '10px 0' }}>
                {c.modes.map((m, idx) => (
                  <span key={idx} className="corridor-mode-pill">
                    {m === 'Flight' ? <Plane size={12} /> : m === 'Rail' ? <Train size={12} /> : <Bus size={12} />}
                    <span>{m}</span>
                  </span>
                ))}
              </div>

              <div className="corridor-stat-row">
                <span style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>Transit Speed:</span>
                <strong style={{ color: 'var(--text-primary)', fontSize: '0.85rem' }}>{c.fastest_time}</strong>
              </div>

              <div className="corridor-stat-row">
                <span style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>Starting Fares:</span>
                <strong style={{ color: 'var(--semantic-success)', fontSize: '0.95rem', fontWeight: 800 }}>From ₹{c.lowest_fare.toLocaleString('en-IN')}</strong>
              </div>

              <div style={{ marginTop: '12px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Connected Hubs:</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '6px' }}>
                  {c.popular_landmarks.map((l, idx) => (
                    <span key={idx} className="landmark-tag">
                      {l}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="corridor-card-footer">
              <button
                type="button"
                className="btn btn-primary btn-sm"
                style={{ width: '100%' }}
                onClick={() => onSelectCorridor(c.origin, c.destination)}
              >
                <span>Plan This Corridor on Map</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

