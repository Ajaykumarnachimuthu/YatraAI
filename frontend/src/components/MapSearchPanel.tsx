import React, { useState, useEffect, useRef } from 'react';
import {
  MapPin,
  ArrowRightLeft,
  Plus,
  Trash2,
  Calendar,
  Users,
  Compass,
  Search,
  Train,
  Plane,
  Bus,
  Building,
  RotateCw,
  ChevronLeft,
} from 'lucide-react';
import { LocationItem } from '../types';
import { api } from '../services/api';

interface MapSearchPanelProps {
  origin: string;
  destination: string;
  intermediateStops: string[];
  departureDate: string;
  returnDate: string;
  partySize: number;
  travelClass: string;
  departureWindow: string;
  isLoading: boolean;
  onOriginChange: (val: string) => void;
  onDestinationChange: (val: string) => void;
  onAddStop: () => void;
  onRemoveStop: (idx: number) => void;
  onStopChange: (idx: number, val: string) => void;
  onDepartureDateChange: (val: string) => void;
  onReturnDateChange: (val: string) => void;
  onPartySizeChange: (val: number) => void;
  onTravelClassChange: (val: string) => void;
  onDepartureWindowChange: (val: string) => void;
  onSearch: () => void;
  onSelectOriginLocation?: (loc: LocationItem) => void;
  onSelectDestLocation?: (loc: LocationItem) => void;
  onToggleCollapse?: () => void;
}

export const MapSearchPanel: React.FC<MapSearchPanelProps> = ({
  origin,
  destination,
  intermediateStops,
  departureDate,
  returnDate,
  partySize,
  travelClass,
  departureWindow,
  isLoading,
  onOriginChange,
  onDestinationChange,
  onAddStop,
  onRemoveStop,
  onStopChange,
  onDepartureDateChange,
  onReturnDateChange,
  onPartySizeChange,
  onTravelClassChange,
  onDepartureWindowChange,
  onSearch,
  onSelectOriginLocation,
  onSelectDestLocation,
  onToggleCollapse,
}) => {
  // Autocomplete state
  const [originSuggestions, setOriginSuggestions] = useState<LocationItem[]>([]);
  const [destSuggestions, setDestSuggestions] = useState<LocationItem[]>([]);
  const [showOriginDropdown, setShowOriginDropdown] = useState(false);
  const [showDestDropdown, setShowDestDropdown] = useState(false);

  // Active stop autocomplete state
  const [activeStopIndex, setActiveStopIndex] = useState<number | null>(null);
  const [stopSuggestions, setStopSuggestions] = useState<LocationItem[]>([]);

  // Search debounce ref
  const debounceRef = useRef<any>(null);

  // Fetch Origin Autocomplete
  useEffect(() => {
    if (!origin || origin.length < 2) {
      setOriginSuggestions([]);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      const results = await api.autocompleteLocations(origin);
      setOriginSuggestions(results);
    }, 200);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [origin]);

  // Fetch Destination Autocomplete
  useEffect(() => {
    if (!destination || destination.length < 2) {
      setDestSuggestions([]);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      const results = await api.autocompleteLocations(destination);
      setDestSuggestions(results);
    }, 200);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [destination]);

  // Handle Swap Locations
  const handleSwap = () => {
    const temp = origin;
    onOriginChange(destination);
    onDestinationChange(temp);
  };

  const getCategoryBadge = (cat: string) => {
    switch (cat) {
      case 'airport':
        return { label: 'Airport', icon: <Plane size={12} />, color: '#06b6d4' };
      case 'rail_station':
        return { label: 'Railway Stn', icon: <Train size={12} />, color: '#6366f1' };
      case 'bus_terminal':
        return { label: 'Bus Terminal', icon: <Bus size={12} />, color: '#f97316' };
      case 'landmark':
        return { label: 'Landmark', icon: <Building size={12} />, color: '#10b981' };
      default:
        return { label: 'City Hub', icon: <Compass size={12} />, color: '#94a3b8' };
    }
  };

  return (
    <div className="search-panel-container glass-card" style={{ padding: '16px' }}>
      {/* Panel Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Compass size={18} className="text-cyan" />
          <h2 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
            Multimodal Journey Planner
          </h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span className="badge-pill">Door-to-Door</span>
          {onToggleCollapse && (
            <button
              type="button"
              className="sidebar-collapse-btn"
              onClick={onToggleCollapse}
              title="Collapse sidebar to maximize map view"
            >
              <ChevronLeft size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Origin & Destination Inputs with Swap */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', position: 'relative' }}>
        {/* Origin Input */}
        <div style={{ position: 'relative' }}>
          <label className="input-field-label">
            <span style={{ color: '#059669', fontWeight: 800 }}>● FROM</span> Starting Point / Station / Airport
          </label>
          <div className="input-with-icon">
            <MapPin size={18} style={{ color: '#059669' }} />
            <input
              type="text"
              className="planner-input"
              placeholder="e.g. Connaught Place, New Delhi (NDLS), DEL..."
              value={origin}
              onChange={(e) => {
                onOriginChange(e.target.value);
                setShowOriginDropdown(true);
              }}
              onFocus={() => setShowOriginDropdown(true)}
            />
          </div>

          {/* Origin Autocomplete Dropdown */}
          {showOriginDropdown && originSuggestions.length > 0 && (
            <div className="autocomplete-dropdown glass-card">
              {originSuggestions.map((loc) => {
                const badge = getCategoryBadge(loc.category);
                return (
                  <div
                    key={loc.id}
                    className="autocomplete-item"
                    onClick={() => {
                      onOriginChange(loc.name);
                      if (onSelectOriginLocation) onSelectOriginLocation(loc);
                      setShowOriginDropdown(false);
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ color: badge.color }}>{badge.icon}</span>
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem' }}>
                          {loc.name}
                        </span>
                      </div>
                      <span
                        className="cat-badge"
                        style={{ color: badge.color, borderColor: badge.color }}
                      >
                        {loc.code || badge.label}
                      </span>
                    </div>
                    {loc.description && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '3px', paddingLeft: '20px' }}>
                        {loc.description}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Swap Button in Center */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', margin: '-4px 16px -4px 0', zIndex: 10 }}>
          <button
            type="button"
            className="swap-btn"
            title="Swap Origin and Destination"
            onClick={handleSwap}
          >
            <ArrowRightLeft size={14} />
          </button>
        </div>

        {/* Intermediate Stops (if any) */}
        {intermediateStops.map((stop, idx) => (
          <div key={idx} style={{ position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label className="input-field-label">
                <span style={{ color: '#d97706', fontWeight: 800 }}>◆ STOP {idx + 1}</span> Intermediate Via Point
              </label>
              <button
                type="button"
                className="remove-stop-btn"
                onClick={() => onRemoveStop(idx)}
                title="Remove Stop"
              >
                <Trash2 size={13} /> Remove
              </button>
            </div>
            <div className="input-with-icon">
              <Compass size={18} style={{ color: '#d97706' }} />
              <input
                type="text"
                className="planner-input"
                placeholder="Intermediate junction or city (e.g. Vadodara, Jaipur)..."
                value={stop}
                onChange={(e) => onStopChange(idx, e.target.value)}
              />
            </div>
          </div>
        ))}

        {/* Destination Input */}
        <div style={{ position: 'relative' }}>
          <label className="input-field-label">
            <span style={{ color: '#dc2626', fontWeight: 800 }}>■ TO</span> Final Destination / Station / Address
          </label>
          <div className="input-with-icon">
            <MapPin size={18} style={{ color: '#dc2626' }} />
            <input
              type="text"
              className="planner-input"
              placeholder="e.g. Bandra Kurla Complex, Mumbai (CSMT), BOM..."
              value={destination}
              onChange={(e) => {
                onDestinationChange(e.target.value);
                setShowDestDropdown(true);
              }}
              onFocus={() => setShowDestDropdown(true)}
            />
          </div>

          {/* Destination Autocomplete Dropdown */}
          {showDestDropdown && destSuggestions.length > 0 && (
            <div className="autocomplete-dropdown glass-card">
              {destSuggestions.map((loc) => {
                const badge = getCategoryBadge(loc.category);
                return (
                  <div
                    key={loc.id}
                    className="autocomplete-item"
                    onClick={() => {
                      onDestinationChange(loc.name);
                      if (onSelectDestLocation) onSelectDestLocation(loc);
                      setShowDestDropdown(false);
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ color: badge.color }}>{badge.icon}</span>
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem' }}>
                          {loc.name}
                        </span>
                      </div>
                      <span
                        className="cat-badge"
                        style={{ color: badge.color, borderColor: badge.color }}
                      >
                        {loc.code || badge.label}
                      </span>
                    </div>
                    {loc.description && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '3px', paddingLeft: '20px' }}>
                        {loc.description}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Add Stop Button */}
      <div style={{ marginTop: '8px', marginBottom: '12px' }}>
        <button
          type="button"
          className="add-stop-link"
          onClick={onAddStop}
        >
          <Plus size={14} /> Add Intermediate Stop
        </button>
      </div>

      {/* Date, Travellers & Preferences Grid */}
      <div className="search-grid-row">
        {/* Departure Date */}
        <div>
          <label className="input-field-label">
            <Calendar size={13} style={{ display: 'inline', marginRight: '4px' }} />
            Departure Date
          </label>
          <input
            type="date"
            className="planner-input"
            value={departureDate}
            onChange={(e) => onDepartureDateChange(e.target.value)}
          />
        </div>

        {/* Departure Window */}
        <div>
          <label className="input-field-label">Preferred Time</label>
          <select
            className="planner-input"
            value={departureWindow}
            onChange={(e) => onDepartureWindowChange(e.target.value)}
          >
            <option value="Early Morning">Early Morning (04:00 - 08:00)</option>
            <option value="Morning">Morning (08:00 - 12:00)</option>
            <option value="Afternoon">Afternoon (12:00 - 16:00)</option>
            <option value="Evening">Evening (16:00 - 20:00)</option>
            <option value="Night">Night (20:00 - 04:00)</option>
          </select>
        </div>

        {/* Travellers Counter */}
        <div>
          <label className="input-field-label">
            <Users size={13} style={{ display: 'inline', marginRight: '4px' }} />
            Travellers
          </label>
          <select
            className="planner-input"
            value={partySize}
            onChange={(e) => onPartySizeChange(Number(e.target.value))}
          >
            {[1, 2, 3, 4, 5, 6, 8, 10].map((num) => (
              <option key={num} value={num}>
                {num} {num === 1 ? 'Passenger' : 'Passengers'}
              </option>
            ))}
          </select>
        </div>

        {/* Travel Class */}
        <div>
          <label className="input-field-label">Travel Class</label>
          <select
            className="planner-input"
            value={travelClass}
            onChange={(e) => onTravelClassChange(e.target.value)}
          >
            <option value="All">All Travel Classes</option>
            <option value="Economy">Economy / Sleeper</option>
            <option value="AC">AC 3-Tier / Standard AC</option>
            <option value="Premium">AC 2-Tier / Business Air</option>
            <option value="Executive">1-Tier AC / First Class</option>
          </select>
        </div>
      </div>

      {/* Search Button */}
      <div style={{ marginTop: '16px' }}>
        <button
          type="button"
          className="btn btn-primary search-submit-btn"
          disabled={isLoading}
          onClick={onSearch}
        >
          {isLoading ? (
            <>
              <RotateCw size={18} className="spinner" />
              <span>Orchestrating Multimodal Routes...</span>
            </>
          ) : (
            <>
              <Search size={18} />
              <span>Search Multimodal Journeys</span>
            </>
          )}
        </button>
      </div>

      {/* Quick Corridor Suggestions Chips */}
      <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--border-default)' }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase' }}>
          Popular Multimodal Corridors:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {[
            { label: 'Delhi ➔ Mumbai', orig: 'Connaught Place, Delhi', dest: 'Bandra Kurla Complex, Mumbai' },
            { label: 'Bangalore ➔ Chennai', orig: 'MG Road, Bangalore', dest: 'T. Nagar, Chennai' },
            { label: 'Delhi ➔ Kolkata', orig: 'New Delhi Railway Station', dest: 'Park Street, Kolkata' },
            { label: 'Mumbai ➔ Bangalore', orig: 'Mumbai Central', dest: 'Whitefield, Bangalore' },
          ].map((corridor, idx) => (
            <button
              key={idx}
              type="button"
              className="corridor-chip"
              onClick={() => {
                onOriginChange(corridor.orig);
                onDestinationChange(corridor.dest);
              }}
            >
              {corridor.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
