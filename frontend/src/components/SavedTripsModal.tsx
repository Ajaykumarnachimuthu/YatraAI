import React from 'react';
import { X, Trash2, Plane, Train, Calendar, IndianRupee, Clock } from 'lucide-react';
import { SavedTrip } from '../types';

interface SavedTripsModalProps {
  isOpen: boolean;
  onClose: () => void;
  trips: SavedTrip[];
  onDeleteTrip: (id: number) => void;
}

export const SavedTripsModal: React.FC<SavedTripsModalProps> = ({
  isOpen,
  onClose,
  trips,
  onDeleteTrip,
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '650px', maxHeight: '85vh', overflowY: 'auto' }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>My Saved Journeys</h2>
            <p style={{ fontSize: '0.85rem', color: '#9ca3af' }}>{trips.length} saved transit itineraries</p>
          </div>
          <button type="button" onClick={onClose} style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {trips.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: '#9ca3af' }}>
            <p>You have not bookmarked any journey options yet.</p>
            <p style={{ fontSize: '0.8rem', marginTop: '6px' }}>Search a corridor and click "Save Itinerary" to store it here.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {trips.map((trip) => {
              const isFlight = trip.mode === 'Flight';
              return (
                <div
                  key={trip.id}
                  style={{
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '12px',
                    padding: '16px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '16px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '10px',
                        background: isFlight ? 'rgba(6, 182, 212, 0.15)' : 'rgba(99, 102, 241, 0.15)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: isFlight ? '#06b6d4' : '#6366f1',
                      }}
                    >
                      {isFlight ? <Plane size={20} /> : <Train size={20} />}
                    </div>

                    <div>
                      <div style={{ fontWeight: 800, fontSize: '1rem' }}>
                        {trip.origin_city} ➔ {trip.destination_city}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
                        {trip.carrier} ({trip.service_identifier}) • {trip.service_tier}
                      </div>
                      <div style={{ display: 'flex', gap: '12px', marginTop: '4px', fontSize: '0.8rem' }}>
                        <span style={{ color: '#10b981', fontWeight: 700 }}>₹{trip.cost_inr.toLocaleString()}</span>
                        <span>•</span>
                        <span>{trip.duration_hours.toFixed(1)} hrs</span>
                        {trip.departure_window && (
                          <>
                            <span>•</span>
                            <span style={{ color: '#06b6d4' }}>{trip.departure_window}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => onDeleteTrip(trip.id)}
                    className="btn btn-secondary"
                    style={{ padding: '8px', color: '#f43f5e' }}
                    title="Delete Saved Trip"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

