import React from 'react';

interface TransitMapProps {
  origin: string;
  destination: string;
  mode?: string;
}

interface MetroNode {
  city: string;
  code: string;
  x: number;
  y: number;
}

const METRO_NODES: Record<string, MetroNode> = {
  Delhi: { city: 'Delhi', code: 'DEL / NDLS', x: 180, y: 65 },
  Mumbai: { city: 'Mumbai', code: 'BOM / MMCT', x: 110, y: 205 },
  Bangalore: { city: 'Bangalore', code: 'BLR / SBC', x: 180, y: 310 },
  Chennai: { city: 'Chennai', code: 'MAA / MAS', x: 240, y: 305 },
  Hyderabad: { city: 'Hyderabad', code: 'HYD / SC', x: 195, y: 220 },
  Kolkata: { city: 'Kolkata', code: 'CCU / HWH', x: 320, y: 155 },
};

export const TransitMap: React.FC<TransitMapProps> = ({ origin, destination, mode }) => {
  const origNode = METRO_NODES[origin];
  const destNode = METRO_NODES[destination];

  // Calculate curved path between origin and destination
  let activePath = '';
  if (origNode && destNode) {
    const midX = (origNode.x + destNode.x) / 2;
    const midY = (origNode.y + destNode.y) / 2;
    // Slight arc curvature
    const curveOffset = (origNode.x > destNode.x ? 25 : -25);
    activePath = `M ${origNode.x} ${origNode.y} Q ${midX + curveOffset} ${midY - 20} ${destNode.x} ${destNode.y}`;
  }

  // Pre-drawn background network corridor connections
  const corridors = [
    ['Delhi', 'Mumbai'],
    ['Delhi', 'Kolkata'],
    ['Delhi', 'Bangalore'],
    ['Mumbai', 'Bangalore'],
    ['Mumbai', 'Hyderabad'],
    ['Bangalore', 'Chennai'],
    ['Hyderabad', 'Chennai'],
    ['Hyderabad', 'Kolkata'],
    ['Chennai', 'Kolkata'],
    ['Mumbai', 'Kolkata'],
  ];

  return (
    <div className="glass-card" style={{ padding: '18px', textAlign: 'center' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Intercity Transit Corridor Network
        </span>
        <span className="pill pill-cyan">
          {origin} ➔ {destination} ({mode || 'Multimodal'})
        </span>
      </div>

      <svg width="100%" height="280" viewBox="0 0 420 370" style={{ overflow: 'visible' }}>
        <defs>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Network corridor background grid lines */}
        {corridors.map(([c1, c2], idx) => {
          const n1 = METRO_NODES[c1];
          const n2 = METRO_NODES[c2];
          if (!n1 || !n2) return null;
          return (
            <line
              key={idx}
              x1={n1.x}
              y1={n1.y}
              x2={n2.x}
              y2={n2.y}
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
          );
        })}

        {/* Active Route Arc */}
        {activePath && (
          <>
            <path
              d={activePath}
              fill="none"
              stroke="#6366f1"
              strokeWidth="5"
              filter="url(#glow)"
              opacity="0.6"
            />
            <path
              d={activePath}
              fill="none"
              stroke="#06b6d4"
              strokeWidth="2.5"
              strokeDasharray={mode === 'Flight' ? '6 4' : 'none'}
            />
          </>
        )}

        {/* Metro City Nodes */}
        {Object.values(METRO_NODES).map((node) => {
          const isSelected = node.city === origin || node.city === destination;
          const isOrigin = node.city === origin;

          return (
            <g key={node.city}>
              {isSelected && (
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="14"
                  fill={isOrigin ? 'rgba(16, 185, 129, 0.25)' : 'rgba(99, 102, 241, 0.25)'}
                  stroke={isOrigin ? '#10b981' : '#6366f1'}
                  strokeWidth="1.5"
                />
              )}
              <circle
                cx={node.x}
                cy={node.y}
                r={isSelected ? '7' : '5'}
                fill={isSelected ? (isOrigin ? '#10b981' : '#6366f1') : '#4b5563'}
                stroke="#ffffff"
                strokeWidth="1.5"
              />
              <text
                x={node.x}
                y={node.y - 12}
                textAnchor="middle"
                fontSize="11"
                fontWeight={isSelected ? '700' : '500'}
                fill={isSelected ? '#ffffff' : '#9ca3af'}
                fontFamily="system-ui, sans-serif"
              >
                {node.city}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

