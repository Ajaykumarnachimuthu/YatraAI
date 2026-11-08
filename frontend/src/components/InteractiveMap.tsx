import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import {
  Layers,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Navigation,
  MapPin,
  Plane,
  Train,
  Bus,
  Car,
  ShieldCheck,
  Info,
  Clock,
  ArrowRightLeft,
  Leaf,
  ChevronRight,
  PanelLeftOpen,
} from 'lucide-react';
import { MultimodalJourney, LocationItem } from '../types';

interface InteractiveMapProps {
  origin: LocationItem | null;
  destination: LocationItem | null;
  intermediateStops: LocationItem[];
  journeys: MultimodalJourney[];
  selectedJourneyId: string | null;
  onSelectJourney: (journeyId: string) => void;
  onMapClickLocation?: (lat: number, lng: number) => void;
  onOpenTimeline?: () => void;
  isTimelineOpen?: boolean;
  isSidebarCollapsed?: boolean;
  onExpandSidebar?: () => void;
}

// 100% Free, Open Tile Layers (Zero API Key, Zero Setup, Zero Watermark)
const TILE_LAYERS = {
  osm_standard: {
    name: 'OpenStreetMap (Light Clean)',
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors',
    subdomains: 'abc',
    maxZoom: 19,
    className: '',
  },
  esri_street: {
    name: 'World Street Map (Esri)',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri &copy; OpenStreetMap',
    subdomains: '',
    maxZoom: 18,
    className: '',
  },
  osm_hot: {
    name: 'Humanitarian OSM (Clean)',
    url: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors',
    subdomains: 'abc',
    maxZoom: 19,
    className: '',
  },
};

// Mode-specific route colors (High contrast on light map)
const MODE_COLORS: Record<string, string> = {
  Flight: '#0284c7', // Sky 600
  Rail: '#4f46e5',   // Indigo 600
  Metro: '#059669',  // Emerald 600
  Cab: '#d97706',    // Amber 600
  Bus: '#ea580c',    // Orange 600
  Walk: '#64748b',   // Slate 500
};

export const InteractiveMap: React.FC<InteractiveMapProps> = ({
  origin,
  destination,
  intermediateStops,
  journeys,
  selectedJourneyId,
  onSelectJourney,
  onMapClickLocation,
  onOpenTimeline,
  isTimelineOpen,
  isSidebarCollapsed,
  onExpandSidebar,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const routesLayerRef = useRef<L.LayerGroup | null>(null);

  const [activeLayer, setActiveLayer] = useState<keyof typeof TILE_LAYERS>('osm_standard');
  const [showLayerMenu, setShowLayerMenu] = useState(false);
  const [mapTooltip, setMapTooltip] = useState<string | null>(null);

  // Auto-resize Leaflet map whenever container dimensions change (sidebar collapse, timeline toggle, window resize)
  useEffect(() => {
    if (!mapContainerRef.current) return;
    const observer = new ResizeObserver(() => {
      mapInstanceRef.current?.invalidateSize();
    });
    observer.observe(mapContainerRef.current);
    return () => observer.disconnect();
  }, []);

  // Initialize Map Instance once
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Default center on India
    const map = L.map(mapContainerRef.current, {
      center: [21.5, 78.9],
      zoom: 5,
      zoomControl: false,
      attributionControl: false,
    });

    const initialTileConfig = TILE_LAYERS[activeLayer];
    const tileLayer = L.tileLayer(initialTileConfig.url, {
      attribution: initialTileConfig.attribution,
      subdomains: initialTileConfig.subdomains,
      maxZoom: initialTileConfig.maxZoom,
      className: initialTileConfig.className,
    }).addTo(map);

    tileLayerRef.current = tileLayer;

    // Layer groups for markers & routes
    const routesLayer = L.layerGroup().addTo(map);
    const markersLayer = L.layerGroup().addTo(map);

    routesLayerRef.current = routesLayer;
    markersLayerRef.current = markersLayer;
    mapInstanceRef.current = map;

    // Handle map click
    map.on('click', (e: L.LeafletMouseEvent) => {
      if (onMapClickLocation) {
        onMapClickLocation(e.latlng.lat, e.latlng.lng);
      }
    });

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Switch Tile Layer
  useEffect(() => {
    if (!mapInstanceRef.current || !tileLayerRef.current) return;

    mapInstanceRef.current.removeLayer(tileLayerRef.current);
    const cfg = TILE_LAYERS[activeLayer];
    const newLayer = L.tileLayer(cfg.url, {
      attribution: cfg.attribution,
      subdomains: cfg.subdomains,
      maxZoom: cfg.maxZoom,
      className: cfg.className,
    }).addTo(mapInstanceRef.current);

    tileLayerRef.current = newLayer;
  }, [activeLayer]);

  // Update Markers and Routes whenever Origin, Destination, or Journeys change
  useEffect(() => {
    const map = mapInstanceRef.current;
    const markersLayer = markersLayerRef.current;
    const routesLayer = routesLayerRef.current;

    if (!map || !markersLayer || !routesLayer) return;

    markersLayer.clearLayers();
    routesLayer.clearLayers();

    const bounds = L.latLngBounds([]);

    // 1. Add Origin Marker
    if (origin) {
      const originIcon = L.divIcon({
        className: 'custom-map-marker',
        html: `
          <div class="marker-origin-pin">
            <div class="marker-pulse-ring marker-pulse-green"></div>
            <div class="marker-badge marker-badge-green">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>
            </div>
            <div class="marker-label">${origin.name}</div>
          </div>
        `,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      });

      const m = L.marker([origin.lat, origin.lng], { icon: originIcon });
      m.bindPopup(`
        <div style="font-family: system-ui; padding: 4px;">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: #10b981; font-weight: 800; letter-spacing: 0.05em;">Departure Origin</div>
          <div style="font-size: 0.95rem; font-weight: 700; color: #111827; margin: 2px 0;">${origin.name}</div>
          <div style="font-size: 0.8rem; color: #6b7280;">Cluster: ${origin.city} (${origin.category})</div>
        </div>
      `);
      markersLayer.addLayer(m);
      bounds.extend([origin.lat, origin.lng]);
    }

    // 2. Add Destination Marker
    if (destination) {
      const destIcon = L.divIcon({
        className: 'custom-map-marker',
        html: `
          <div class="marker-dest-pin">
            <div class="marker-pulse-ring marker-pulse-rose"></div>
            <div class="marker-badge marker-badge-rose">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
            </div>
            <div class="marker-label">${destination.name}</div>
          </div>
        `,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      });

      const m = L.marker([destination.lat, destination.lng], { icon: destIcon });
      m.bindPopup(`
        <div style="font-family: system-ui; padding: 4px;">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: #f43f5e; font-weight: 800; letter-spacing: 0.05em;">Final Destination</div>
          <div style="font-size: 0.95rem; font-weight: 700; color: #111827; margin: 2px 0;">${destination.name}</div>
          <div style="font-size: 0.8rem; color: #6b7280;">Cluster: ${destination.city} (${destination.category})</div>
        </div>
      `);
      markersLayer.addLayer(m);
      bounds.extend([destination.lat, destination.lng]);
    }

    // 3. Add Intermediate Stops Markers
    intermediateStops.forEach((stop, idx) => {
      const stopIcon = L.divIcon({
        className: 'custom-map-marker',
        html: `
          <div class="marker-stop-pin">
            <div class="marker-badge marker-badge-amber">
              <span style="font-size: 0.8rem; font-weight: 800;">${idx + 1}</span>
            </div>
            <div class="marker-label">Stop ${idx + 1}: ${stop.name}</div>
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

      const m = L.marker([stop.lat, stop.lng], { icon: stopIcon });
      m.bindPopup(`
        <div style="font-family: system-ui; padding: 4px;">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: #f59e0b; font-weight: 800;">Intermediate Stop ${idx + 1}</div>
          <div style="font-size: 0.95rem; font-weight: 700; color: #111827;">${stop.name}</div>
        </div>
      `);
      markersLayer.addLayer(m);
      bounds.extend([stop.lat, stop.lng]);
    });

    // 4. Render Journey Route Paths
    const activeJourney = journeys.find((j) => j.journey_id === selectedJourneyId) || journeys[0];

    // First draw unselected journeys as subtle background routes
    journeys.forEach((j) => {
      const isSelected = activeJourney && j.journey_id === activeJourney.journey_id;
      if (isSelected) return; // Draw active on top later

      if (j.legs) {
        j.legs.forEach((leg) => {
          const latlngs: L.LatLngExpression[] = [
            [leg.departure_coords[0], leg.departure_coords[1]],
            [leg.arrival_coords[0], leg.arrival_coords[1]],
          ];

          const line = L.polyline(latlngs, {
            color: '#475569',
            weight: 3,
            opacity: 0.35,
            dashArray: leg.mode === 'Flight' ? '6 6' : undefined,
          });

          line.on('click', () => onSelectJourney(j.journey_id));
          routesLayer.addLayer(line);
        });
      }
    });

    // Draw Active Selected Journey on top with vivid vibrant styling & waypoints
    if (activeJourney && activeJourney.legs) {
      activeJourney.legs.forEach((leg, lIdx) => {
        const color = MODE_COLORS[leg.mode] || '#6366f1';
        let latlngs: L.LatLngExpression[] = [
          [leg.departure_coords[0], leg.departure_coords[1]],
          [leg.arrival_coords[0], leg.arrival_coords[1]],
        ];

        // Great-circle curve for flights
        if (leg.mode === 'Flight') {
          latlngs = generateArcPoints(leg.departure_coords, leg.arrival_coords);
        }

        // Outer glow polyline
        const glowLine = L.polyline(latlngs, {
          color: color,
          weight: leg.mode === 'Flight' ? 8 : 7,
          opacity: 0.3,
          lineCap: 'round',
        });
        routesLayer.addLayer(glowLine);

        // Core polyline
        const coreLine = L.polyline(latlngs, {
          color: color,
          weight: leg.mode === 'Flight' ? 4 : 4.5,
          opacity: 0.95,
          dashArray: leg.mode === 'Flight' ? '8 6' : leg.mode === 'Walk' ? '4 4' : undefined,
          lineCap: 'round',
        });

        coreLine.bindPopup(`
          <div style="font-family: system-ui; min-width: 180px; padding: 2px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
              <span style="font-size: 0.75rem; font-weight: 800; color: ${color}; text-transform: uppercase;">
                Leg ${lIdx + 1}: ${leg.mode}
              </span>
              <span style="font-size: 0.75rem; background: rgba(0,0,0,0.06); padding: 2px 6px; border-radius: 4px; font-weight: 600;">
                ${leg.duration_hours}h • ₹${leg.fare_inr}
              </span>
            </div>
            <div style="font-size: 0.9rem; font-weight: 700; color: #0f172a;">
              ${leg.carrier || leg.provider || leg.service_identifier}
            </div>
            <div style="font-size: 0.8rem; color: #475569; margin-top: 2px;">
              ${leg.departure_location} ➔ ${leg.arrival_location}
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">
              Departure: <strong>${leg.departure_time}</strong> • Arrival: <strong>${leg.arrival_time}</strong>
            </div>
          </div>
        `);

        coreLine.on('click', () => onSelectJourney(activeJourney.journey_id));
        routesLayer.addLayer(coreLine);

        // Add leg coordinates to bounds
        bounds.extend([leg.departure_coords[0], leg.departure_coords[1]]);
        bounds.extend([leg.arrival_coords[0], leg.arrival_coords[1]]);

        // Add Transit Hub Waypoint Markers for Mainline Departure & Arrival
        if (leg.leg_type === 'mainline' || leg.leg_type === 'transfer_transit') {
          addTransitHubMarker(
            leg.departure_coords,
            leg.departure_location,
            leg.mode,
            'Departure Hub',
            markersLayer
          );
          addTransitHubMarker(
            leg.arrival_coords,
            leg.arrival_location,
            leg.mode,
            'Arrival Hub',
            markersLayer
          );
        }
      });
    }

    // Auto-fit map bounds with asymmetric padding accounting for timeline panel if open
    if (bounds.isValid()) {
      map.fitBounds(bounds, {
        paddingTopLeft: [70, 70],
        paddingBottomRight: isTimelineOpen ? [395, 70] : [70, 70],
        maxZoom: 12,
        animate: true,
      });
    }
  }, [origin, destination, intermediateStops, journeys, selectedJourneyId, isTimelineOpen]);

  // Generate smooth curved arc coordinates for flight paths
  const generateArcPoints = (
    p1: [number, number],
    p2: [number, number],
    steps: number = 20
  ): L.LatLngExpression[] => {
    const lat1 = p1[0];
    const lon1 = p1[1];
    const lat2 = p2[0];
    const lon2 = p2[1];

    const midLat = (lat1 + lat2) / 2.0;
    const midLon = (lon1 + lon2) / 2.0;
    const arcOffset = lon1 > lon2 ? 1.5 : -1.5;

    const points: L.LatLngExpression[] = [];
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const lat = (1 - t) ** 2 * lat1 + 2 * (1 - t) * t * (midLat + arcOffset) + t ** 2 * lat2;
      const lon = (1 - t) ** 2 * lon1 + 2 * (1 - t) * t * midLon + t ** 2 * lon2;
      points.push([lat, lon]);
    }
    return points;
  };

  // Helper to add transit hub marker
  const addTransitHubMarker = (
    coords: [number, number],
    name: string,
    mode: string,
    hubType: string,
    layerGroup: L.LayerGroup
  ) => {
    const isAirport = mode === 'Flight';
    const isStation = mode === 'Rail';
    const isBus = mode === 'Bus';

    const iconHtml = isAirport
      ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/></svg>`
      : isStation
        ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect width="16" height="16" x="4" y="3" rx="2"/><path d="M4 11h16"/><path d="M12 3v8"/><path d="m8 19-2 3"/><path d="m18 22-2-3"/><circle cx="8" cy="15" r="1"/><circle cx="16" cy="15" r="1"/></svg>`
        : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M8 6v6"/><path d="M15 6v6"/><path d="M2 12h19.6"/><path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.2 6 18.2 6H5.8C4.8 6 3.9 6.8 3.6 7.8L2.2 12.8c-.1.4-.2.8-.2 1.2 0 .4.1.8.2 1.2.3 1.1.8 2.8.8 2.8h3"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg>`;

    const badgeColor = isAirport ? '#06b6d4' : isStation ? '#6366f1' : '#f97316';

    const hubIcon = L.divIcon({
      className: 'custom-hub-marker',
      html: `
        <div class="hub-marker-pin" style="border-color: ${badgeColor}; color: ${badgeColor};">
          ${iconHtml}
        </div>
      `,
      iconSize: [26, 26],
      iconAnchor: [13, 13],
    });

    const marker = L.marker(coords, { icon: hubIcon });
    marker.bindPopup(`
      <div style="font-family: system-ui; padding: 2px;">
        <div style="font-size: 0.7rem; text-transform: uppercase; color: ${badgeColor}; font-weight: 800;">${hubType}</div>
        <div style="font-size: 0.85rem; font-weight: 700; color: #111827;">${name}</div>
        <div style="font-size: 0.75rem; color: #64748b;">Mode: ${mode}</div>
      </div>
    `);
    layerGroup.addLayer(marker);
  };

  // Zoom controls
  const handleZoomIn = () => mapInstanceRef.current?.zoomIn();
  const handleZoomOut = () => mapInstanceRef.current?.zoomOut();

  const handleFitBounds = () => {
    const map = mapInstanceRef.current;
    if (!map) return;
    const points: [number, number][] = [];
    if (origin) points.push([origin.lat, origin.lng]);
    if (destination) points.push([destination.lat, destination.lng]);
    intermediateStops.forEach((s) => points.push([s.lat, s.lng]));

    if (points.length > 0) {
      map.fitBounds(L.latLngBounds(points), {
        paddingTopLeft: [70, 70],
        paddingBottomRight: isTimelineOpen ? [395, 70] : [70, 70],
      });
    } else {
      map.setView([21.5, 78.9], 5);
    }
  };

  const activeJourney = journeys.find((j) => j.journey_id === selectedJourneyId) || journeys[0];

  return (
    <div className="map-wrapper" style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Real Leaflet Map Container */}
      <div
        ref={mapContainerRef}
        style={{
          width: '100%',
          height: '100%',
          minHeight: '480px',
          background: '#f8fafc',
          outline: 'none',
        }}
      />

      {/* Floating Top Header Overlay on Map */}
      <div className="map-floating-header">
        {isSidebarCollapsed && onExpandSidebar && (
          <button
            type="button"
            className="map-floating-expand-pill"
            onClick={onExpandSidebar}
            title="Expand Search & Filters"
          >
            <PanelLeftOpen size={16} />
            <span>Search & Filters</span>
          </button>
        )}

        <div className="map-floating-corridor">
          <Navigation size={16} className="text-cyan" />
          <span className="corridor-title">
            {origin?.name || 'Select Origin'} ➔ {destination?.name || 'Select Destination'}
          </span>
          {activeJourney && (
            <span className="corridor-badge">
              {activeJourney.multimodal_type}
            </span>
          )}
        </div>

        {/* Mode Legend */}
        <div className="map-legend-bar">
          <span className="legend-item"><span className="legend-dot" style={{ background: '#0284c7' }}></span> Air</span>
          <span className="legend-item"><span className="legend-dot" style={{ background: '#4f46e5' }}></span> Rail</span>
          <span className="legend-item"><span className="legend-dot" style={{ background: '#059669' }}></span> Metro</span>
          <span className="legend-item"><span className="legend-dot" style={{ background: '#d97706' }}></span> Cab</span>
          <span className="legend-item"><span className="legend-dot" style={{ background: '#ea580c' }}></span> Bus</span>
        </div>
      </div>

      {/* Map Control Tools (Floating Bottom-Right) */}
      <div className="map-floating-controls">
        {/* Layer Selector */}
        <div style={{ position: 'relative' }}>
          <button
            className="map-ctrl-btn"
            title="Map Style"
            onClick={() => setShowLayerMenu(!showLayerMenu)}
          >
            <Layers size={18} />
          </button>

          {showLayerMenu && (
            <div className="map-layer-dropdown glass-card">
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase' }}>
                Map Basemap
              </div>
              {Object.entries(TILE_LAYERS).map(([key, cfg]) => (
                <button
                  key={key}
                  className={`map-layer-option ${activeLayer === key ? 'active' : ''}`}
                  onClick={() => {
                    setActiveLayer(key as any);
                    setShowLayerMenu(false);
                  }}
                >
                  {cfg.name}
                </button>
              ))}
            </div>
          )}
        </div>

        <button className="map-ctrl-btn" title="Zoom In" onClick={handleZoomIn}>
          <ZoomIn size={18} />
        </button>
        <button className="map-ctrl-btn" title="Zoom Out" onClick={handleZoomOut}>
          <ZoomOut size={18} />
        </button>
        <button className="map-ctrl-btn" title="Fit Journey Bounds" onClick={handleFitBounds}>
          <Maximize2 size={18} />
        </button>
      </div>

      {/* Floating Active Journey Metrics Badge */}
      {activeJourney && (
        <div className="map-journey-pill glass-card">
          <div className="journey-pill-row">
            <span className="pill-rank-badge">#{activeJourney.rank}</span>
            <span className="pill-title">{activeJourney.title}</span>
            <span className="pill-fare">₹{activeJourney.total_fare_inr.toLocaleString('en-IN')}</span>
            {onOpenTimeline && (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                style={{ marginLeft: 'auto', padding: '4px 10px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                onClick={onOpenTimeline}
              >
                <span>{isTimelineOpen ? 'Hide Legs' : 'Inspect Legs'}</span>
                <ChevronRight size={13} style={{ transform: isTimelineOpen ? 'rotate(90deg)' : 'none' }} />
              </button>
            )}
          </div>
          <div className="journey-pill-meta">
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={12} /> {activeJourney.total_duration_hours} hrs door-to-door
            </span>
            <span>•</span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <ArrowRightLeft size={12} /> {activeJourney.transfer_count} transfers
            </span>
            <span>•</span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Leaf size={12} /> {activeJourney.carbon_kg} kg CO₂
            </span>
            <span>•</span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: activeJourney.reliability_score >= 0.85 ? 'var(--semantic-success)' : 'var(--semantic-warning)' }}>
              <ShieldCheck size={12} /> {(activeJourney.reliability_score * 100).toFixed(0)}% reliable
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

