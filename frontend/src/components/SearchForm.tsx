import React from 'react';
import { ArrowLeftRight, Search } from 'lucide-react';

interface SearchFormProps {
  cities: string[];
  origin: string;
  destination: string;
  departureWindow: string;
  tripPurpose: string;
  leadDays: number;
  loading: boolean;
  error: string | null;
  onOriginChange: (val: string) => void;
  onDestinationChange: (val: string) => void;
  onDepartureWindowChange: (val: string) => void;
  onTripPurposeChange: (val: string) => void;
  onLeadDaysChange: (val: number) => void;
  onSwapCities: () => void;
  onSubmit: (e: React.FormEvent) => void;
}

export const SearchForm: React.FC<SearchFormProps> = ({
  cities,
  origin,
  destination,
  departureWindow,
  tripPurpose,
  leadDays,
  loading,
  error,
  onOriginChange,
  onDestinationChange,
  onDepartureWindowChange,
  onTripPurposeChange,
  onLeadDaysChange,
  onSwapCities,
  onSubmit,
}) => {
  return (
    <form onSubmit={onSubmit} className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', alignItems: 'end' }}>
        {/* Origin */}
        <div>
          <label className="input-label">Origin Metro Hub</label>
          <select
            value={origin}
            onChange={(e) => onOriginChange(e.target.value)}
            className="form-select"
            required
          >
            {cities.map((c) => (
              <option key={`orig-${c}`} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Swap Button */}
        <div style={{ display: 'flex', justifyContent: 'center', paddingBottom: '4px' }}>
          <button
            type="button"
            onClick={onSwapCities}
            className="btn btn-secondary"
            style={{ padding: '8px', borderRadius: '50%' }}
            title="Swap Origin and Destination"
          >
            <ArrowLeftRight size={18} />
          </button>
        </div>

        {/* Destination */}
        <div>
          <label className="input-label">Destination Metro Hub</label>
          <select
            value={destination}
            onChange={(e) => onDestinationChange(e.target.value)}
            className="form-select"
            required
          >
            {cities.map((c) => (
              <option key={`dest-${c}`} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Departure Window */}
        <div>
          <label className="input-label">Departure Window</label>
          <select
            value={departureWindow}
            onChange={(e) => onDepartureWindowChange(e.target.value)}
            className="form-select"
          >
            <option value="Early Morning">Early Morning (04:00 - 08:00)</option>
            <option value="Morning">Morning (08:00 - 12:00)</option>
            <option value="Afternoon">Afternoon (12:00 - 16:00)</option>
            <option value="Evening">Evening (16:00 - 20:00)</option>
            <option value="Night">Night (20:00 - 04:00)</option>
          </select>
        </div>

        {/* Trip Purpose */}
        <div>
          <label className="input-label">Trip Purpose</label>
          <select
            value={tripPurpose}
            onChange={(e) => onTripPurposeChange(e.target.value)}
            className="form-select"
          >
            <option value="Business">Business / Executive</option>
            <option value="Leisure">Leisure / Vacation</option>
            <option value="Commute">Intercity Commute</option>
            <option value="Family">Family Travel</option>
          </select>
        </div>

        {/* Lead Days */}
        <div>
          <label className="input-label">Advance Booking</label>
          <select
            value={leadDays}
            onChange={(e) => onLeadDaysChange(parseInt(e.target.value, 10))}
            className="form-select"
          >
            <option value={2}>2 Days (Immediate)</option>
            <option value={7}>7 Days (1 Week)</option>
            <option value={14}>14 Days (Standard)</option>
            <option value={30}>30 Days (Advance)</option>
          </select>
        </div>
      </div>

      {error && (
        <div style={{ marginTop: '14px', color: '#f43f5e', fontSize: '0.9rem', fontWeight: 600 }}>
          ⚠️ {error}
        </div>
      )}

      <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
        <button type="submit" className="btn btn-primary" disabled={loading} style={{ minWidth: '220px' }}>
          <Search size={18} />
          {loading ? 'Evaluating Model Inferences...' : 'Find & Rank Personalized Journeys'}
        </button>
      </div>
    </form>
  );
};

