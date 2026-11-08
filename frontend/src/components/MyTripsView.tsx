import React, { useState, useEffect } from 'react';
import {
  Bookmark,
  Calendar,
  Clock,
  MapPin,
  Trash2,
  Printer,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Train,
  Plane,
  Bus,
  Car,
  Compass,
  FileText,
} from 'lucide-react';
import { SavedTrip } from '../types';
import { api } from '../services/api';

interface MyTripsViewProps {
  onLoadTripToPlanner: (origin: string, destination: string) => void;
}

export const MyTripsView: React.FC<MyTripsViewProps> = ({ onLoadTripToPlanner }) => {
  const [activeTab, setActiveTab] = useState<'saved' | 'upcoming' | 'completed'>('saved');
  const [trips, setTrips] = useState<SavedTrip[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTrips = async () => {
    setIsLoading(true);
    try {
      const data = await api.getSavedTrips();
      setTrips(data);
    } catch {
      setTrips([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTrips();
  }, []);

  const handleDelete = async (id: number) => {
    await api.deleteSavedTrip(id);
    fetchTrips();
  };

  const handlePrint = (trip: SavedTrip) => {
    window.print();
  };

  const filteredTrips = trips.filter((t) => {
    if (activeTab === 'saved') return t.status === 'Saved' || !t.status;
    if (activeTab === 'upcoming') return t.status === 'Confirmed';
    if (activeTab === 'completed') return t.status === 'Completed';
    return true;
  });

  return (
    <div className="my-trips-view-container">
      {/* Top Header */}
      <div className="page-header-banner glass-card">
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            My Multimodal Trips & Itineraries
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Saved multimodal itineraries, PNR booking references, and tracking status.
          </p>
        </div>

        {/* Status Filter Tabs */}
        <div className="trips-tab-bar">
          <button
            className={`trips-tab-btn ${activeTab === 'saved' ? 'active' : ''}`}
            onClick={() => setActiveTab('saved')}
          >
            Saved Journeys ({trips.filter((t) => t.status === 'Saved' || !t.status).length})
          </button>
          <button
            className={`trips-tab-btn ${activeTab === 'upcoming' ? 'active' : ''}`}
            onClick={() => setActiveTab('upcoming')}
          >
            Upcoming Trips ({trips.filter((t) => t.status === 'Confirmed').length})
          </button>
          <button
            className={`trips-tab-btn ${activeTab === 'completed' ? 'active' : ''}`}
            onClick={() => setActiveTab('completed')}
          >
            Past Trips ({trips.filter((t) => t.status === 'Completed').length})
          </button>
        </div>
      </div>

      {/* Trips Content List */}
      <div style={{ marginTop: '20px' }}>
        {isLoading ? (
          <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading your saved itineraries...
          </div>
        ) : filteredTrips.length === 0 ? (
          <div className="glass-card empty-trips-card">
            <Bookmark size={40} className="text-secondary" />
            <h3 style={{ color: 'var(--text-primary)', marginTop: '12px', fontSize: '1.2rem', fontWeight: 700 }}>
              No {activeTab} trips found
            </h3>
            <p style={{ color: 'var(--text-muted)', maxWidth: '420px', margin: '8px auto', fontSize: '0.9rem' }}>
              Plan a multimodal journey on the interactive map and click "Save to My Trips" to bookmark your itinerary.
            </p>
          </div>
        ) : (
          <div className="trips-grid">
            {filteredTrips.map((trip) => (
              <div key={trip.id} className="trip-card glass-card">
                {/* Header */}
                <div className="trip-card-header">
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="trip-pnr-badge">
                        REF: {trip.booking_reference || `YTR-${trip.id.toString().slice(-6)}`}
                      </span>
                      <span className="trip-status-badge status-saved">
                        {trip.status || 'Saved'}
                      </span>
                    </div>
                    <h3 className="trip-title" style={{ marginTop: '6px' }}>
                      {trip.origin_city} ➔ {trip.destination_city}
                    </h3>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div className="trip-fare">₹{trip.cost_inr.toLocaleString('en-IN')}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{trip.duration_hours}h duration</div>
                  </div>
                </div>

                {/* Body Details */}
                <div className="trip-card-body">
                  <div className="trip-meta-item">
                    <Calendar size={14} className="text-cyan" />
                    <span>Travel Date: <strong>{trip.travel_date || new Date(trip.created_at).toLocaleDateString()}</strong></span>
                  </div>

                  <div className="trip-meta-item">
                    <Compass size={14} className="text-cyan" />
                    <span>Multimodal Mode: <strong>{trip.multimodal_type || trip.mode}</strong></span>
                  </div>

                  <div className="trip-meta-item">
                    <Clock size={14} className="text-cyan" />
                    <span>Service: <strong>{trip.carrier} ({trip.service_identifier})</strong></span>
                  </div>

                  {trip.notes && (
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', fontSize: '0.8rem', color: 'var(--text-secondary)', background: 'var(--surface-subtle)', border: '1px solid var(--border-default)', padding: '8px', borderRadius: '6px', marginTop: '8px' }}>
                      <FileText size={14} style={{ color: 'var(--action-primary)', marginTop: '2px', flexShrink: 0 }} />
                      <span>{trip.notes}</span>
                    </div>
                  )}
                </div>

                {/* Actions Footer */}
                <div className="trip-card-footer">
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => onLoadTripToPlanner(trip.origin_city, trip.destination_city)}
                  >
                    <ExternalLink size={14} />
                    <span>View on Map</span>
                  </button>

                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => handlePrint(trip)}
                  >
                    <Printer size={14} />
                    <span>Print Itinerary</span>
                  </button>

                  <button
                    type="button"
                    className="btn-icon-danger"
                    title="Remove Trip"
                    onClick={() => handleDelete(trip.id)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

