import {
  HealthResponse,
  CorridorsResponse,
  Persona,
  RecommendResponse,
  SearchQuery,
  TravelDNA,
  User,
  SavedTrip,
  MultimodalPlanResponse,
  LocationItem,
  PopularCorridor,
} from '../types';

const API_BASE = '/api';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('yatra_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  // System Health
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to retrieve system health');
    return res.json();
  },

  // Location Autocomplete
  async autocompleteLocations(
    query: string,
    category?: string,
    limit: number = 8
  ): Promise<LocationItem[]> {
    const params = new URLSearchParams({ q: query, limit: String(limit) });
    if (category) params.append('category', category);

    const res = await fetch(`${API_BASE}/locations/autocomplete?${params.toString()}`);
    if (!res.ok) return [];
    return res.json();
  },

  // Popular Map Corridors
  async getPopularCorridors(): Promise<PopularCorridor[]> {
    try {
      const res = await fetch(`${API_BASE}/corridors/popular`);
      if (!res.ok) return [];
      const data = await res.json();
      return data.corridors || [];
    } catch {
      return [];
    }
  },

  // Multimodal Journey Planner
  async planMultimodal(payload: {
    origin: string;
    destination: string;
    intermediate_stops?: string[];
    departure_window?: string;
    travel_date?: string;
    return_date?: string;
    party_size?: number;
    lead_days?: number;
    primary_preference?: string;
    secondary_preference?: string | null;
    travel_class?: string;
    travel_dna?: TravelDNA;
  }): Promise<MultimodalPlanResponse> {
    const res = await fetch(`${API_BASE}/multimodal/plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Multimodal journey planning failed');
    }
    return data;
  },

  // Legacy Recommend Endpoint (preserved for backward compatibility)
  async recommend(payload: {
    origin_city: string;
    destination_city: string;
    departure_window: string;
    trip_purpose: string;
    party_size: number;
    lead_days: number;
    travel_dna: TravelDNA;
  }): Promise<RecommendResponse> {
    const res = await fetch(`${API_BASE}/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Recommendation calculation failed');
    }
    return data;
  },

  // Personas Archetypes
  async getPersonas(): Promise<Persona[]> {
    const res = await fetch(`${API_BASE}/personas`);
    if (!res.ok) throw new Error('Failed to retrieve persona archetypes');
    const data = await res.json();
    return data.personas || [];
  },

  // Corridors list
  async getCorridors(): Promise<CorridorsResponse> {
    const res = await fetch(`${API_BASE}/corridors`);
    if (!res.ok) throw new Error('Failed to retrieve supported corridors');
    return res.json();
  },

  // Authentication
  async register(email: string, password: string, fullName?: string, travelDna?: TravelDNA): Promise<{ token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: fullName, travel_dna: travelDna }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed');
    localStorage.setItem('yatra_token', data.access_token);
    return { token: data.access_token, user: data.user };
  },

  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Authentication failed');
    localStorage.setItem('yatra_token', data.access_token);
    return { token: data.access_token, user: data.user };
  },

  async getProfile(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/profile`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load profile');
    return res.json();
  },

  async updateTravelDNA(dna: TravelDNA): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/profile/travel-dna`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(dna),
    });
    if (!res.ok) throw new Error('Failed to update Travel DNA');
    return res.json();
  },

  // Saved Trips (Connected to backend + fallback to local storage)
  async getSavedTrips(): Promise<SavedTrip[]> {
    try {
      const res = await fetch(`${API_BASE}/trips`, {
        headers: { ...getAuthHeader() },
      });
      if (res.ok) {
        const remoteTrips = await res.json();
        // Merge with local storage trips
        const local = JSON.parse(localStorage.getItem('yatra_saved_trips') || '[]');
        const existingIds = new Set(remoteTrips.map((t: SavedTrip) => t.id));
        const combined = [...remoteTrips, ...local.filter((t: SavedTrip) => !existingIds.has(t.id))];
        return combined;
      }
    } catch {
      // Fallback to local storage
    }
    return JSON.parse(localStorage.getItem('yatra_saved_trips') || '[]');
  },

  async saveTrip(trip: Partial<SavedTrip>): Promise<SavedTrip> {
    const tripToSave: SavedTrip = {
      id: Date.now(),
      origin_city: trip.origin_city || 'Origin',
      destination_city: trip.destination_city || 'Destination',
      mode: trip.mode || 'Multimodal',
      carrier: trip.carrier || 'Yatra AI Orchestrated',
      service_identifier: trip.service_identifier || 'YTR-ML',
      service_tier: trip.service_tier || 'Standard',
      cost_inr: trip.cost_inr || 0,
      duration_hours: trip.duration_hours || 0,
      departure_window: trip.departure_window || 'Morning',
      notes: trip.notes || '',
      created_at: new Date().toISOString(),
      journey_id: trip.journey_id,
      title: trip.title,
      multimodal_type: trip.multimodal_type,
      carbon_kg: trip.carbon_kg,
      transfer_count: trip.transfer_count,
      booking_reference: `YTR-${Math.floor(100000 + Math.random() * 900000)}`,
      status: 'Saved',
      travel_date: trip.travel_date || new Date().toISOString().split('T')[0],
      legs_summary: trip.legs_summary,
    };

    // Try backend persistence if authenticated
    try {
      const res = await fetch(`${API_BASE}/trips`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(),
        },
        body: JSON.stringify({
          origin_city: tripToSave.origin_city,
          destination_city: tripToSave.destination_city,
          mode: tripToSave.mode,
          carrier: tripToSave.carrier,
          service_identifier: tripToSave.service_identifier,
          service_tier: tripToSave.service_tier,
          cost_inr: tripToSave.cost_inr,
          duration_hours: tripToSave.duration_hours,
          departure_window: tripToSave.departure_window,
          notes: tripToSave.notes,
        }),
      });
      if (res.ok) {
        const savedBackend = await res.json();
        tripToSave.id = savedBackend.id;
      }
    } catch {
      // Graceful local persistence
    }

    // Always persist to localStorage for seamless instant retrieval
    const local = JSON.parse(localStorage.getItem('yatra_saved_trips') || '[]');
    const updated = [tripToSave, ...local.filter((t: SavedTrip) => t.id !== tripToSave.id)];
    localStorage.setItem('yatra_saved_trips', JSON.stringify(updated));
    return tripToSave;
  },

  async deleteSavedTrip(tripId: number): Promise<void> {
    try {
      await fetch(`${API_BASE}/trips/${tripId}`, {
        method: 'DELETE',
        headers: { ...getAuthHeader() },
      });
    } catch {}

    const local = JSON.parse(localStorage.getItem('yatra_saved_trips') || '[]');
    const updated = local.filter((t: SavedTrip) => t.id !== tripId);
    localStorage.setItem('yatra_saved_trips', JSON.stringify(updated));
  },
};
