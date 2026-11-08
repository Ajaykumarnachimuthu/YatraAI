import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { InteractiveMap } from './components/InteractiveMap';
import { MapSearchPanel } from './components/MapSearchPanel';
import { PreferenceSelector } from './components/PreferenceSelector';
import { JourneyResultsList } from './components/JourneyResultsList';
import { JourneyTimeline } from './components/JourneyTimeline';
import { MyTripsView } from './components/MyTripsView';
import { ExploreView } from './components/ExploreView';
import { TravelProfileView } from './components/TravelProfileView';
import { AuthModal } from './components/AuthModal';
import { AdvancedDNAModal } from './components/AdvancedDNAModal';
import { api } from './services/api';
import {
  HealthResponse,
  TravelDNA,
  User,
  SavedTrip,
  MultimodalJourney,
  LocationItem,
  MultimodalPlanResponse,
} from './types';

const DEFAULT_DNA: TravelDNA = {
  cost_sensitivity: 0.50,
  time_sensitivity: 0.50,
  reliability_sensitivity: 0.50,
  comfort_preference: 0.50,
  transfer_tolerance: 0.50,
  departure_time_flexibility: 0.50,
  sustainability_preference: 0.50,
};

export const App: React.FC = () => {
  // Navigation View State
  const [activeView, setActiveView] = useState<'planner' | 'trips' | 'explore' | 'profile'>('planner');

  // Search & Journey Parameters
  const [origin, setOrigin] = useState<string>('Connaught Place, Delhi');
  const [destination, setDestination] = useState<string>('Bandra Kurla Complex, Mumbai');
  const [originLocation, setOriginLocation] = useState<LocationItem | null>(null);
  const [destLocation, setDestLocation] = useState<LocationItem | null>(null);
  const [intermediateStops, setIntermediateStops] = useState<string[]>([]);
  const [intermediateStopLocations, setIntermediateStopLocations] = useState<LocationItem[]>([]);

  const [departureDate, setDepartureDate] = useState<string>(() => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    return d.toISOString().split('T')[0];
  });
  const [returnDate, setReturnDate] = useState<string>('');
  const [partySize, setPartySize] = useState<number>(1);
  const [travelClass, setTravelClass] = useState<string>('All');
  const [departureWindow, setDepartureWindow] = useState<string>('Morning');

  // Preferences & DNA
  const [primaryPreference, setPrimaryPreference] = useState<string>('fastest');
  const [secondaryPreference, setSecondaryPreference] = useState<string | null>('eco_friendly');
  const [travelDna, setTravelDna] = useState<TravelDNA>(DEFAULT_DNA);

  // Recommendations & Active Selected Journey
  const [journeys, setJourneys] = useState<MultimodalJourney[]>([]);
  const [selectedJourneyId, setSelectedJourneyId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // User & Saved Trips
  const [user, setUser] = useState<User | null>(null);
  const [savedTrips, setSavedTrips] = useState<SavedTrip[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  // Modals & Panels
  const [isAuthModalOpen, setIsAuthModalOpen] = useState<boolean>(false);
  const [isAdvancedDNAOpen, setIsAdvancedDNAOpen] = useState<boolean>(false);
  const [isTimelineOpen, setIsTimelineOpen] = useState<boolean>(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);

  // Initial Boot & System Health
  useEffect(() => {
    const bootApp = async () => {
      try {
        const [healthData, tripsData] = await Promise.all([
          api.getHealth().catch(() => null),
          api.getSavedTrips().catch(() => []),
        ]);
        if (healthData) setHealth(healthData);
        setSavedTrips(tripsData);

        // Check stored token
        const token = localStorage.getItem('yatra_token');
        if (token) {
          try {
            const profile = await api.getProfile();
            setUser(profile);
            if (profile.travel_dna) setTravelDna(profile.travel_dna);
          } catch {
            localStorage.removeItem('yatra_token');
          }
        }
      } catch {}

      // Execute initial search so map and routes are immediately alive
      executeJourneySearch(
        'Connaught Place, Delhi',
        'Bandra Kurla Complex, Mumbai',
        [],
        'fastest',
        'eco_friendly'
      );
    };

    bootApp();
  }, []);

  // Execute Multimodal Search
  const executeJourneySearch = async (
    origStr: string = origin,
    destStr: string = destination,
    stopsStr: string[] = intermediateStops,
    primPref: string = primaryPreference,
    secPref: string | null = secondaryPreference
  ) => {
    if (!origStr.trim() || !destStr.trim()) {
      setError('Please provide both origin and destination.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res: MultimodalPlanResponse = await api.planMultimodal({
        origin: origStr,
        destination: destStr,
        intermediate_stops: stopsStr.filter((s) => s.trim().length > 0),
        departure_window: departureWindow,
        travel_date: departureDate,
        return_date: returnDate || undefined,
        party_size: partySize,
        lead_days: 14,
        primary_preference: primPref,
        secondary_preference: secPref,
        travel_class: travelClass,
        travel_dna: travelDna,
      });

      setOriginLocation(res.origin);
      setDestLocation(res.destination);
      setIntermediateStopLocations(res.intermediate_stops || []);
      setJourneys(res.journeys || []);

      if (res.journeys && res.journeys.length > 0) {
        setSelectedJourneyId(res.journeys[0].journey_id);
      } else {
        setSelectedJourneyId(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to calculate multimodal routes.');
    } finally {
      setIsLoading(false);
    }
  };

  // Preference change handler: re-ranks immediately
  const handleSelectPrimaryPreference = (pref: string) => {
    setPrimaryPreference(pref);
    executeJourneySearch(origin, destination, intermediateStops, pref, secondaryPreference);
  };

  const handleSelectSecondaryPreference = (pref: string | null) => {
    setSecondaryPreference(pref);
    executeJourneySearch(origin, destination, intermediateStops, primaryPreference, pref);
  };

  // Intermediate Stops Handlers
  const handleAddStop = () => {
    if (intermediateStops.length >= 3) return;
    setIntermediateStops([...intermediateStops, '']);
  };

  const handleRemoveStop = (idx: number) => {
    const updated = intermediateStops.filter((_, i) => i !== idx);
    setIntermediateStops(updated);
  };

  const handleStopChange = (idx: number, val: string) => {
    const updated = [...intermediateStops];
    updated[idx] = val;
    setIntermediateStops(updated);
  };

  // Save Trip to Bookmarks
  const handleSaveTrip = async (journey: MultimodalJourney) => {
    const tripToSave: Partial<SavedTrip> = {
      origin_city: originLocation?.city || origin,
      destination_city: destLocation?.city || destination,
      mode: journey.multimodal_type,
      carrier: journey.title,
      service_identifier: journey.legs?.[1]?.service_identifier || journey.title,
      service_tier: journey.legs?.[1]?.service_tier || 'Standard',
      cost_inr: journey.total_fare_inr,
      duration_hours: journey.total_duration_hours,
      departure_window: departureWindow,
      journey_id: journey.journey_id,
      title: journey.title,
      multimodal_type: journey.multimodal_type,
      carbon_kg: journey.carbon_kg,
      transfer_count: journey.transfer_count,
      travel_date: departureDate,
      notes: `${journey.multimodal_type} • Connection Guardian: ${journey.connection_guardian?.status || 'SAFE'} Buffer`,
    };

    const saved = await api.saveTrip(tripToSave);
    setSavedTrips((prev) => [saved, ...prev.filter((t) => t.id !== saved.id)]);
  };

  // Corridor 1-Click Load into Planner
  const handleLoadCorridorToPlanner = (orig: string, dest: string) => {
    setOrigin(orig);
    setDestination(dest);
    setIntermediateStops([]);
    setActiveView('planner');
    executeJourneySearch(orig, dest, [], primaryPreference, secondaryPreference);
  };

  // Selected Journey Object
  const activeSelectedJourney =
    journeys.find((j) => j.journey_id === selectedJourneyId) || journeys[0] || null;

  return (
    <div className="app-shell">
      {/* Top Application Navigation */}
      <Header
        activeView={activeView}
        onNavigate={setActiveView}
        health={health}
        user={user}
        savedTripsCount={savedTrips.length}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onLogout={() => {
          localStorage.removeItem('yatra_token');
          setUser(null);
        }}
      />

      {/* Main Content Area */}
      <main className="app-main-content">
        {activeView === 'trips' && (
          <div className="content-container">
            <MyTripsView onLoadTripToPlanner={handleLoadCorridorToPlanner} />
          </div>
        )}

        {activeView === 'explore' && (
          <div className="content-container">
            <ExploreView onSelectCorridor={handleLoadCorridorToPlanner} />
          </div>
        )}

        {activeView === 'profile' && (
          <div className="content-container">
            <TravelProfileView
              currentDNA={travelDna}
              onUpdateDNA={setTravelDna}
              user={user}
            />
          </div>
        )}

        {/* MAP-FIRST PLANNER VIEW */}
        {activeView === 'planner' && (
          <div className={`map-first-layout ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            {/* LEFT SIDEBAR: Search, Preferences & Journey Alternatives */}
            <aside className="planner-left-sidebar">
              {/* Search Panel */}
              <MapSearchPanel
                origin={origin}
                destination={destination}
                intermediateStops={intermediateStops}
                departureDate={departureDate}
                returnDate={returnDate}
                partySize={partySize}
                travelClass={travelClass}
                departureWindow={departureWindow}
                isLoading={isLoading}
                onOriginChange={setOrigin}
                onDestinationChange={setDestination}
                onAddStop={handleAddStop}
                onRemoveStop={handleRemoveStop}
                onStopChange={handleStopChange}
                onDepartureDateChange={setDepartureDate}
                onReturnDateChange={setReturnDate}
                onPartySizeChange={setPartySize}
                onTravelClassChange={setTravelClass}
                onDepartureWindowChange={setDepartureWindow}
                onSearch={() => executeJourneySearch()}
                onSelectOriginLocation={setOriginLocation}
                onSelectDestLocation={setDestLocation}
                onToggleCollapse={() => setIsSidebarCollapsed(true)}
              />

              {/* Journey Preferences Selector */}
              <PreferenceSelector
                primaryPreference={primaryPreference}
                secondaryPreference={secondaryPreference}
                onSelectPrimary={handleSelectPrimaryPreference}
                onSelectSecondary={handleSelectSecondaryPreference}
                onOpenAdvancedDNA={() => setIsAdvancedDNAOpen(true)}
              />

              {/* Error Message if any */}
              {error && (
                <div className="error-alert-box glass-card">
                  ⚠️ {error}
                </div>
              )}

              {/* Journey Alternative Cards List */}
              <JourneyResultsList
                journeys={journeys}
                selectedJourneyId={selectedJourneyId}
                onSelectJourney={(id) => {
                  setSelectedJourneyId(id);
                  setIsTimelineOpen(true);
                }}
                primaryPreference={primaryPreference}
                onOpenTimeline={() => setIsTimelineOpen(true)}
              />
            </aside>

            {/* MAIN PANEL: Interactive Leaflet Map & Slide-Over Inspector */}
            <section className="planner-main-panel">
              {/* Interactive Map (Full Height Hero Canvas) */}
              <div className="map-canvas-container">
                <InteractiveMap
                  origin={originLocation}
                  destination={destLocation}
                  intermediateStops={intermediateStopLocations}
                  journeys={journeys}
                  selectedJourneyId={selectedJourneyId}
                  onSelectJourney={(id) => {
                    setSelectedJourneyId(id);
                    setIsTimelineOpen(true);
                  }}
                  onOpenTimeline={() => setIsTimelineOpen(!isTimelineOpen)}
                  isTimelineOpen={isTimelineOpen}
                  isSidebarCollapsed={isSidebarCollapsed}
                  onExpandSidebar={() => setIsSidebarCollapsed(false)}
                  onMapClickLocation={(lat, lng) => {
                    // Quick location hint
                  }}
                />
              </div>

              {/* Slide-Over Journey Timeline & Connection Guardian Inspector */}
              {isTimelineOpen && activeSelectedJourney && (
                <JourneyTimeline
                  journey={activeSelectedJourney}
                  onSaveTrip={handleSaveTrip}
                  isSaved={savedTrips.some(
                    (t) => t.journey_id === activeSelectedJourney?.journey_id
                  )}
                  onClose={() => setIsTimelineOpen(false)}
                />
              )}
            </section>
          </div>
        )}
      </main>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={(u) => setUser(u)}
        currentDna={travelDna}
      />

      {/* Advanced Travel DNA Modal */}
      <AdvancedDNAModal
        isOpen={isAdvancedDNAOpen}
        onClose={() => setIsAdvancedDNAOpen(false)}
        travelDna={travelDna}
        onChangeDNA={setTravelDna}
      />
    </div>
  );
};
