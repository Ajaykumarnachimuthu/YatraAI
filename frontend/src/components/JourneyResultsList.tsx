import React, { useState } from 'react';
import {
  Sparkles,
  Clock,
  IndianRupee,
  ShieldCheck,
  Leaf,
  GitCommit,
  ChevronRight,
  Filter,
  CheckCircle2,
  Train,
  Plane,
  Bus,
  Car,
  Footprints,
  Info,
} from 'lucide-react';
import { MultimodalJourney } from '../types';

interface JourneyResultsListProps {
  journeys: MultimodalJourney[];
  selectedJourneyId: string | null;
  onSelectJourney: (id: string) => void;
  primaryPreference: string;
  onOpenTimeline?: () => void;
}

export const JourneyResultsList: React.FC<JourneyResultsListProps> = ({
  journeys,
  selectedJourneyId,
  onSelectJourney,
  primaryPreference,
  onOpenTimeline,
}) => {
  // Filters state
  const [modeFilter, setModeFilter] = useState<'All' | 'Flight' | 'Rail' | 'Bus'>('All');
  const [maxTransfers, setMaxTransfers] = useState<number | 'Any'>('Any');
  const [expandedReasonId, setExpandedReasonId] = useState<string | null>(null);

  // Filter journeys
  const filteredJourneys = journeys.filter((j) => {
    if (modeFilter !== 'All') {
      const hasMode = j.legs?.some((leg) => leg.mode === modeFilter);
      if (!hasMode) return false;
    }
    if (maxTransfers !== 'Any') {
      if (j.transfer_count > maxTransfers) return false;
    }
    return true;
  });

  const getLegIcon = (mode: string) => {
    switch (mode) {
      case 'Flight':
        return <Plane size={13} style={{ color: '#0284c7' }} />;
      case 'Rail':
        return <Train size={13} style={{ color: '#4f46e5' }} />;
      case 'Metro':
        return <Train size={13} style={{ color: '#059669' }} />;
      case 'Bus':
        return <Bus size={13} style={{ color: '#ea580c' }} />;
      case 'Cab':
        return <Car size={13} style={{ color: '#d97706' }} />;
      default:
        return <Footprints size={13} style={{ color: '#64748b' }} />;
    }
  };

  return (
    <div className="journey-results-panel">
      {/* Search Filter Strip */}
      <div className="journey-filter-strip">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Filter size={14} className="text-secondary" />
          <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Filter:
          </span>
        </div>

        {/* Mode Filter Buttons */}
        <div className="filter-button-group">
          {(['All', 'Flight', 'Rail', 'Bus'] as const).map((mode) => (
            <button
              key={mode}
              className={`filter-pill-btn ${modeFilter === mode ? 'active' : ''}`}
              onClick={() => setModeFilter(mode)}
            >
              {mode === 'All' ? 'All Modes' : `${mode}+`}
            </button>
          ))}
        </div>

        {/* Transfers Filter */}
        <select
          className="filter-select"
          value={String(maxTransfers)}
          onChange={(e) => setMaxTransfers(e.target.value === 'Any' ? 'Any' : Number(e.target.value))}
        >
          <option value="Any">Transfers: Any</option>
          <option value="1">Max 1 Transfer</option>
          <option value="2">Max 2 Transfers</option>
          <option value="0">Direct Only (0)</option>
        </select>
      </div>

      {/* Results Header Count */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '12px 4px 8px 4px' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          {filteredJourneys.length} Recommended Multimodal Journeys
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--action-primary)', fontWeight: 600 }}>
          Sorted by: {primaryPreference}
        </span>
      </div>

      {/* Journeys List */}
      <div className="journeys-cards-container">
        {filteredJourneys.length === 0 ? (
          <div className="glass-card" style={{ padding: '28px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <p style={{ fontWeight: 600 }}>No journeys match the active filters.</p>
            <button
              className="btn btn-secondary"
              style={{ marginTop: '10px', fontSize: '0.8rem' }}
              onClick={() => {
                setModeFilter('All');
                setMaxTransfers('Any');
              }}
            >
              Reset Filters
            </button>
          </div>
        ) : (
          filteredJourneys.map((j) => {
            const isSelected = selectedJourneyId === j.journey_id;
            const isTopRanked = j.rank === 1;
            const isReasonsOpen = expandedReasonId === j.journey_id;

            return (
              <div
                key={j.journey_id}
                className={`journey-card glass-card ${isSelected ? 'selected-card' : ''}`}
                onClick={() => {
                  onSelectJourney(j.journey_id);
                  if (onOpenTimeline) onOpenTimeline();
                }}
              >
                {/* Card Top Row: Rank & Badge */}
                <div className="journey-card-top">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className={`journey-rank-badge ${isTopRanked ? 'rank-champion' : ''}`}>
                      #{j.rank}
                    </span>
                    <span className="recommendation-badge-pill">
                      {j.recommendation_badge}
                    </span>
                  </div>

                  {/* ML Score indicator */}
                  <span className="ml-probability-pill" title="HistGradientBoosting Choice Likelihood">
                    <Sparkles size={12} style={{ display: 'inline', marginRight: '3px' }} />
                    {(j.ml_personalization_score * 100).toFixed(0)}% Match
                  </span>
                </div>

                {/* Multimodal Mode Chain Icons */}
                <div className="multimodal-chain-row">
                  {j.legs?.map((leg, lIdx) => (
                    <React.Fragment key={lIdx}>
                      <span className="chain-node" title={`${leg.mode}: ${leg.service_identifier}`}>
                        {getLegIcon(leg.mode)}
                        <span className="chain-node-text">{leg.mode}</span>
                      </span>
                      {lIdx < j.legs.length - 1 && <span className="chain-arrow">➔</span>}
                    </React.Fragment>
                  ))}
                </div>

                {/* Journey Title */}
                <h3 className="journey-card-title">{j.title}</h3>

                {/* Key Metrics Row: Fare, Duration, Transfers */}
                <div className="journey-metrics-grid">
                  <div className="metric-box">
                    <span className="metric-label">Total Fare</span>
                    <span className="metric-value fare-value">
                      ₹{j.total_fare_inr.toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="metric-box">
                    <span className="metric-label">Duration</span>
                    <span className="metric-value">
                      {j.total_duration_hours}h
                    </span>
                  </div>

                  <div className="metric-box">
                    <span className="metric-label">Transfers</span>
                    <span className="metric-value">
                      {j.transfer_count === 0 ? 'Direct' : `${j.transfer_count} changes`}
                    </span>
                  </div>

                  <div className="metric-box">
                    <span className="metric-label">Carbon</span>
                    <span className="metric-value eco-value">
                      {j.carbon_kg} kg
                    </span>
                  </div>
                </div>

                {/* Reliability & Connection Guardian Bar */}
                <div className="journey-card-reliability">
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '3px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>
                      Reliability:{' '}
                      <strong style={{ color: j.reliability_score >= 0.85 ? 'var(--semantic-success)' : 'var(--semantic-warning)' }}>
                        {(j.reliability_score * 100).toFixed(0)}%
                      </strong>
                    </span>
                    <span className={`guardian-status-badge status-${j.connection_guardian?.status?.toLowerCase() || 'safe'}`}>
                      <ShieldCheck size={12} style={{ display: 'inline', marginRight: '3px' }} />
                      {j.connection_guardian?.status || 'SAFE'} Buffer
                    </span>
                  </div>
                  <div className="reliability-progress-track">
                    <div
                      className="reliability-progress-fill"
                      style={{
                        width: `${Math.min(100, j.reliability_score * 100)}%`,
                        background: j.reliability_score >= 0.85 ? 'var(--semantic-success)' : 'var(--semantic-warning)',
                      }}
                    />
                  </div>
                </div>

                {/* Why Yātrā AI Recommends This (Collapsible) */}
                {j.why_recommended && j.why_recommended.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <button
                      type="button"
                      className="why-recommend-toggle"
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedReasonId(isReasonsOpen ? null : j.journey_id);
                      }}
                    >
                      <Sparkles size={12} className="text-cyan" />
                      <span>Why Yātrā recommends this</span>
                      <ChevronRight
                        size={12}
                        style={{
                          transform: isReasonsOpen ? 'rotate(90deg)' : 'none',
                          transition: 'transform 0.2s',
                        }}
                      />
                    </button>

                    {isReasonsOpen && (
                      <ul className="why-reasons-list">
                        {j.why_recommended.map((reason, rIdx) => (
                          <li key={rIdx}>
                            <CheckCircle2 size={12} style={{ color: '#059669', flexShrink: 0, marginTop: '2px' }} />
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

