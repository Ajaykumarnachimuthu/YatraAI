export interface TravelDNA {
  cost_sensitivity: number;
  time_sensitivity: number;
  reliability_sensitivity: number;
  comfort_preference: number;
  transfer_tolerance: number;
  departure_time_flexibility: number;
  sustainability_preference: number;
}

export interface Persona {
  persona_name: string;
  travel_dna: TravelDNA;
  purpose_distribution?: Record<string, number>;
}

export interface LocationItem {
  id: string;
  name: string;
  category: 'city' | 'rail_station' | 'airport' | 'bus_terminal' | 'landmark' | 'address';
  city: string;
  state?: string | null;
  code?: string | null;
  lat: number;
  lng: number;
  description?: string | null;
  nearest_airport?: {
    id: string;
    name: string;
    code?: string | null;
    lat: number;
    lng: number;
    distance_km: number;
  } | null;
  nearest_rail_station?: {
    id: string;
    name: string;
    code?: string | null;
    lat: number;
    lng: number;
    distance_km: number;
  } | null;
  nearest_bus_terminal?: {
    id: string;
    name: string;
    code?: string | null;
    lat: number;
    lng: number;
    distance_km: number;
  } | null;
}

export interface ConnectionGuardian {
  status: 'SAFE' | 'TIGHT' | 'RISKY';
  buffer_minutes: number;
  risk_score: number;
  incoming_punctuality: string;
  explanation: string;
  backup_alternative: string;
  is_real_time_gps: boolean;
  data_authenticity_notice: string;
}

export interface MultimodalLeg {
  leg_index: number;
  leg_type: 'first_mile' | 'mainline' | 'transfer_transit' | 'last_mile';
  mode: 'Metro' | 'Rail' | 'Flight' | 'Bus' | 'Cab' | 'Walk';
  provider?: string;
  carrier?: string;
  service_identifier: string;
  service_tier: string;
  departure_location: string;
  arrival_location: string;
  departure_coords: [number, number]; // [lat, lng]
  arrival_coords: [number, number];   // [lat, lng]
  departure_time: string;
  arrival_time: string;
  duration_hours: number;
  distance_km: number;
  fare_inr: number;
  carbon_kg: number;
  historical_punctuality?: number;
  transfer_wait_minutes?: number;
  terminal_guidance?: string;
}

export interface MultimodalJourney {
  journey_id: string;
  rank: number;
  title: string;
  recommendation_badge: string;
  multimodal_type: string;
  is_recommended: boolean;
  total_fare_inr: number;
  total_duration_hours: number;
  total_distance_km: number;
  transfer_count: number;
  waiting_time_minutes: number;
  reliability_score: number;
  carbon_kg: number;
  ml_personalization_score: number;
  why_recommended: string[];
  legs: MultimodalLeg[];
  connection_guardian: ConnectionGuardian;
  map_geojson?: any;
  relative_scores?: {
    cost: number;
    speed: number;
    reliability: number;
    comfort: number;
    eco: number;
  };
}

export interface MultimodalPlanResponse {
  status: string;
  origin: LocationItem;
  destination: LocationItem;
  intermediate_stops: LocationItem[];
  primary_preference: string;
  secondary_preference?: string | null;
  total_journeys: number;
  recommended_journey?: MultimodalJourney | null;
  journeys: MultimodalJourney[];
  scoring_metadata: {
    engine: string;
    ml_model?: string;
    active_preference: string;
    secondary_preference?: string | null;
  };
}

export interface PopularCorridor {
  id: string;
  origin: string;
  destination: string;
  title: string;
  origin_coords: [number, number];
  dest_coords: [number, number];
  distance_km: number;
  modes: string[];
  fastest_time: string;
  lowest_fare: number;
  popular_landmarks: string[];
}

export interface User {
  id: number;
  email: string;
  full_name?: string | null;
  travel_dna?: TravelDNA | null;
}

export interface SavedTrip {
  id: number;
  origin_city: string;
  destination_city: string;
  mode: string;
  carrier: string;
  service_identifier: string;
  service_tier: string;
  cost_inr: number;
  duration_hours: number;
  departure_window?: string;
  notes?: string;
  created_at: string;
  // Extended fields for multimodal trips
  journey_id?: string;
  title?: string;
  multimodal_type?: string;
  carbon_kg?: number;
  transfer_count?: number;
  booking_reference?: string;
  status?: 'Confirmed' | 'Saved' | 'Completed';
  travel_date?: string;
  legs_summary?: string;
}

export interface QualityScores {
  cost: number;
  time: number;
  reliability: number;
  comfort: number;
  carbon: number;
  departure_fit: number;
}

export interface ItineraryItem {
  rank: number;
  is_recommended: boolean;
  preference_threshold_met: boolean;
  ml_personalization_score: number;
  mode: 'Rail' | 'Flight';
  carrier: string;
  service_identifier: string;
  service_tier: string;
  departure_window: string;
  cost_inr: number;
  duration_hours: number;
  distance_km: number;
  transfer_count: number;
  carbon_estimate_kg: number;
  historical_punctuality_rate: number;
  relative_quality_scores: QualityScores;
  feature_reasons: string[];
}

export interface SearchQuery {
  origin_city: string;
  destination_city: string;
  departure_window: string;
  trip_purpose: string;
  party_size: number;
  lead_days: number;
  travel_date?: string | null;
}

export interface RecommendResponse {
  status: string;
  session_id: number;
  search_query: SearchQuery;
  traveller_dna: TravelDNA;
  total_candidates: number;
  recommended_journey: ItineraryItem;
  itineraries: ItineraryItem[];
  scoring_metadata: {
    model_family: string;
    feature_configuration: string;
    decision_threshold: number;
    ranking_method: string;
  };
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  database_status: string;
  cache_backend: string;
  supported_metro_hubs: number;
  decision_threshold?: number;
  model_family?: string;
}

export interface CorridorsResponse {
  metro_cities: string[];
  corridors_count: number;
  corridors: Array<{ origin: string; destination: string }>;
}
