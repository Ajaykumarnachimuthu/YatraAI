import React, { useState } from 'react';
import {
  Clock,
  MapPin,
  Train,
  Plane,
  Bus,
  Car,
  Footprints,
  ShieldCheck,
  AlertTriangle,
  Info,
  Bookmark,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Leaf,
  IndianRupee,
  X,
  Lightbulb,
} from 'lucide-react';
import { MultimodalJourney, MultimodalLeg } from '../types';

interface JourneyTimelineProps {
  journey: MultimodalJourney | null;
  onSaveTrip: (journey: MultimodalJourney) => void;
  isSaved?: boolean;
  onClose?: () => void;
}

export const JourneyTimeline: React.FC<JourneyTimelineProps> = ({
  journey,
  onSaveTrip,
  isSaved = false,
  onClose,
}) => {
  const [expandedLegIndex, setExpandedLegIndex] = useState<number | null>(null);
  const [showFareBreakdown, setShowFareBreakdown] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState(false);

  if (!journey) {
    return (
      <div className="timeline-slide-over glass-card">
        <div className="timeline-slide-over-header">
          <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Journey Inspector</span>
          {onClose && (
            <button type="button" onClick={onClose} className="modal-close-btn" title="Close">
              <X size={18} />
            </button>
          )}
        </div>
        <div className="timeline-slide-over-body" style={{ textAlign: 'center', padding: '36px 16px', color: 'var(--text-muted)' }}>
          <Info size={32} style={{ margin: '0 auto 12px auto', color: 'var(--action-primary)' }} />
          <h4 style={{ color: 'var(--text-primary)', marginBottom: '6px' }}>Select a Journey to View Timeline</h4>
          <p style={{ fontSize: '0.85rem' }}>
            Explore complete door-to-door transit legs, connection buffers, and Connection Guardian protection.
          </p>
        </div>
      </div>
    );
  }

  const handleSave = () => {
    onSaveTrip(journey);
    setSaveSuccessMsg(true);
    setTimeout(() => setSaveSuccessMsg(false), 3000);
  };

  const getLegIcon = (mode: string) => {
    switch (mode) {
      case 'Flight':
        return <Plane size={15} style={{ color: '#0284c7' }} />;
      case 'Rail':
        return <Train size={15} style={{ color: '#4f46e5' }} />;
      case 'Metro':
        return <Train size={15} style={{ color: '#059669' }} />;
      case 'Bus':
        return <Bus size={15} style={{ color: '#ea580c' }} />;
      case 'Cab':
        return <Car size={15} style={{ color: '#d97706' }} />;
      default:
        return <Footprints size={15} style={{ color: '#64748b' }} />;
    }
  };

  const getGuardianColor = (status: string) => {
    switch (status) {
      case 'SAFE':
        return { bg: '#ecfdf5', border: '#a7f3d0', text: '#059669' };
      case 'TIGHT':
        return { bg: '#fffbeb', border: '#fde68a', text: '#d97706' };
      default:
        return { bg: '#fef2f2', border: '#fecaca', text: '#dc2626' };
    }
  };

  const guardianTheme = getGuardianColor(journey.connection_guardian?.status || 'SAFE');

  return (
    <div className="timeline-slide-over">
      {/* Detail Header Bar */}
      <div className="timeline-slide-over-header">
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="timeline-rank-badge">#{journey.rank}</span>
            <h3 className="timeline-journey-title" style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              {journey.title}
            </h3>
          </div>
          <div className="timeline-journey-subtitle" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            <span>{journey.multimodal_type}</span>
            <span>•</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
              <Clock size={12} /> {journey.total_duration_hours}h total
            </span>
            <span>•</span>
            <span style={{ color: 'var(--action-primary)', fontWeight: 700 }}>
              ₹{journey.total_fare_inr.toLocaleString('en-IN')}
            </span>
          </div>
        </div>

        {/* Action Controls & Close */}
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => setShowFareBreakdown(!showFareBreakdown)}
            title="Inspect Fare Breakdown"
          >
            <IndianRupee size={13} />
            <span>Fares</span>
          </button>

          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={handleSave}
            title="Save Journey to My Trips"
          >
            {isSaved || saveSuccessMsg ? (
              <>
                <CheckCircle size={13} />
                <span>Saved!</span>
              </>
            ) : (
              <>
                <Bookmark size={13} />
                <span>Save</span>
              </>
            )}
          </button>

          {onClose && (
            <button
              type="button"
              className="modal-close-btn"
              onClick={onClose}
              title="Close Timeline Inspector"
              style={{ marginLeft: '4px' }}
            >
              <X size={18} />
            </button>
          )}
        </div>
      </div>

      {/* Body Area */}
      <div className="timeline-slide-over-body">
        {/* Connection Guardian Protection Banner */}
        {journey.connection_guardian && (
          <div
            className="connection-guardian-box"
            style={{
              background: guardianTheme.bg,
              borderColor: guardianTheme.border,
              borderWidth: '1px',
              borderStyle: 'solid',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '16px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
              <div style={{ color: guardianTheme.text, marginTop: '2px' }}>
                <ShieldCheck size={20} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 800, color: guardianTheme.text, textTransform: 'uppercase' }}>
                    Connection Guardian: {journey.connection_guardian.status} Buffer ({journey.connection_guardian.buffer_minutes}m)
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Risk: {(journey.connection_guardian.risk_score * 100).toFixed(0)}%
                  </span>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: '1.4' }}>
                  {journey.connection_guardian.explanation}
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                  <Lightbulb size={13} style={{ color: 'var(--semantic-warning)', flexShrink: 0 }} />
                  <span><strong>Contingency:</strong> {journey.connection_guardian.backup_alternative}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px', fontStyle: 'italic' }}>
                  <ShieldCheck size={12} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
                  <span>{journey.connection_guardian.data_authenticity_notice}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Fare Breakdown Drawer (if open) */}
        {showFareBreakdown && (
          <div className="fare-breakdown-card" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border-default)', borderRadius: '8px', padding: '12px', marginBottom: '16px' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '8px' }}>
              Door-to-Door Fare Breakdown
            </div>
            <table className="fare-table" style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-default)', textAlign: 'left', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '4px 6px' }}>Leg</th>
                  <th style={{ padding: '4px 6px' }}>Mode</th>
                  <th style={{ padding: '4px 6px' }}>Provider</th>
                  <th style={{ padding: '4px 6px', textAlign: 'right' }}>Fare</th>
                </tr>
              </thead>
              <tbody>
                {journey.legs?.map((leg, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '6px' }}>Leg {leg.leg_index}</td>
                    <td style={{ padding: '6px' }}>{leg.mode}</td>
                    <td style={{ padding: '6px' }}>{leg.carrier || leg.provider || leg.service_identifier}</td>
                    <td style={{ padding: '6px', textAlign: 'right', fontWeight: 600 }}>₹{leg.fare_inr.toLocaleString('en-IN')}</td>
                  </tr>
                ))}
                <tr style={{ borderTop: '2px solid var(--border-strong)', fontWeight: 800 }}>
                  <td colSpan={3} style={{ padding: '8px 6px' }}>Total Door-to-Door Fare</td>
                  <td style={{ padding: '8px 6px', textAlign: 'right', color: 'var(--action-primary)', fontSize: '0.95rem' }}>
                    ₹{journey.total_fare_inr.toLocaleString('en-IN')}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {/* Expandable Chronological Timeline Sequence */}
        <div className="timeline-sequence">
          {journey.legs?.map((leg, idx) => {
            const isExpanded = expandedLegIndex === idx;

            return (
              <div key={idx} className="timeline-leg-item">
                {/* Timeline Connector Line & Pin */}
                <div className="timeline-node-track">
                  <div className="timeline-mode-avatar">
                    {getLegIcon(leg.mode)}
                  </div>
                  {idx < journey.legs.length - 1 && <div className="timeline-track-line" />}
                </div>

                {/* Leg Content Card */}
                <div className="timeline-leg-content glass-card">
                  {/* Leg Summary Row */}
                  <div
                    className="timeline-leg-summary"
                    onClick={() => setExpandedLegIndex(isExpanded ? null : idx)}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className="leg-time-tag">{leg.departure_time}</span>
                        <span className="leg-route-title">
                          {leg.departure_location} ➔ {leg.arrival_location}
                        </span>
                      </div>
                      <div className="leg-provider-info">
                        <strong>{leg.carrier || leg.provider}</strong> • {leg.service_identifier} ({leg.service_tier})
                      </div>
                    </div>

                    <div style={{ textAlign: 'right', marginRight: '8px' }}>
                      <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.88rem' }}>
                        ₹{leg.fare_inr}
                      </div>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                        {leg.duration_hours}h • {leg.distance_km} km
                      </div>
                    </div>

                    <button type="button" className="leg-toggle-btn">
                      {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                    </button>
                  </div>

                  {/* Expandable Details Body */}
                  {isExpanded && (
                    <div className="leg-expanded-details">
                      <div className="leg-details-grid">
                        <div>
                          <span className="detail-meta-label">Departure</span>
                          <div className="detail-meta-val">{leg.departure_location}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Time: {leg.departure_time}</div>
                        </div>

                        <div>
                          <span className="detail-meta-label">Arrival</span>
                          <div className="detail-meta-val">{leg.arrival_location}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Time: {leg.arrival_time}</div>
                        </div>

                        <div>
                          <span className="detail-meta-label">Carbon Footprint</span>
                          <div className="detail-meta-val" style={{ color: 'var(--semantic-success)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Leaf size={12} /> {leg.carbon_kg} kg CO₂
                          </div>
                        </div>

                        <div>
                          <span className="detail-meta-label">Punctuality</span>
                          <div className="detail-meta-val">
                            {leg.historical_punctuality
                              ? `${(leg.historical_punctuality * 100).toFixed(0)}% on-time`
                              : 'Standard urban schedule'}
                          </div>
                        </div>
                      </div>

                      {/* Terminal Guidance */}
                      {leg.terminal_guidance && (
                        <div className="terminal-guidance-pill" style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
                          <Info size={13} style={{ color: 'var(--action-primary)', marginTop: '2px', flexShrink: 0 }} />
                          <span><strong>Transit Note:</strong> {leg.terminal_guidance}</span>
                        </div>
                      )}

                      {/* Transfer Waiting buffer if followed by another leg */}
                      {leg.transfer_wait_minutes && leg.transfer_wait_minutes > 0 && (
                        <div className="transfer-buffer-pill" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Clock size={13} style={{ color: 'var(--semantic-warning)', flexShrink: 0 }} />
                          <span>Transfer buffer: <strong>{leg.transfer_wait_minutes} minutes</strong></span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
