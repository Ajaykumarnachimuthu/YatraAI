import React from 'react';
import { TravelDNA } from '../types';

interface RadarChartProps {
  dna: TravelDNA;
  size?: number;
}

const DIMENSIONS: Array<{ key: keyof TravelDNA; label: string }> = [
  { key: 'cost_sensitivity', label: 'Cost' },
  { key: 'time_sensitivity', label: 'Time' },
  { key: 'reliability_sensitivity', label: 'Reliability' },
  { key: 'comfort_preference', label: 'Comfort' },
  { key: 'transfer_tolerance', label: 'Transfers' },
  { key: 'departure_time_flexibility', label: 'Flexibility' },
  { key: 'sustainability_preference', label: 'Eco' },
];

export const RadarChart: React.FC<RadarChartProps> = ({ dna, size = 260 }) => {
  const center = size / 2;
  const radius = (size / 2) - 40;
  const numAxes = DIMENSIONS.length;
  const angleStep = (Math.PI * 2) / numAxes;

  // Concentric polygon grid points
  const rings = [0.25, 0.5, 0.75, 1.0];

  // Calculate polygon points for a given normalized radius factor
  const getRingPoints = (factor: number) => {
    return DIMENSIONS.map((_, i) => {
      const angle = i * angleStep - Math.PI / 2;
      const x = center + radius * factor * Math.cos(angle);
      const y = center + radius * factor * Math.sin(angle);
      return `${x},${y}`;
    }).join(' ');
  };

  // Calculate coordinates for DNA data points
  const dataPoints = DIMENSIONS.map((dim, i) => {
    const val = Math.max(0, Math.min(1, dna[dim.key] ?? 0.5));
    const angle = i * angleStep - Math.PI / 2;
    const x = center + radius * val * Math.cos(angle);
    const y = center + radius * val * Math.sin(angle);
    return { x, y, val };
  });

  const polygonPath = dataPoints.map(p => `${p.x},${p.y}`).join(' ');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Concentric grid rings (Light Theme Slate) */}
        {rings.map((factor, idx) => (
          <polygon
            key={idx}
            points={getRingPoints(factor)}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="1.2"
          />
        ))}

        {/* Axes lines */}
        {DIMENSIONS.map((_, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const x = center + radius * Math.cos(angle);
          const y = center + radius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x}
              y2={y}
              stroke="#e2e8f0"
              strokeWidth="1.2"
            />
          );
        })}

        {/* Data polygon filled shape (Sky blue transparent fill with Sky-600 stroke) */}
        <polygon
          points={polygonPath}
          fill="rgba(2, 132, 199, 0.18)"
          stroke="#0284c7"
          strokeWidth="2.5"
        />

        {/* Data vertices points */}
        {dataPoints.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="4.5"
            fill="#0284c7"
            stroke="#ffffff"
            strokeWidth="2"
          />
        ))}

        {/* Axis Labels (High contrast Slate-700) */}
        {DIMENSIONS.map((dim, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const labelDist = radius + 22;
          const lx = center + labelDist * Math.cos(angle);
          const ly = center + labelDist * Math.sin(angle);
          return (
            <text
              key={i}
              x={lx}
              y={ly}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize="11"
              fontWeight="700"
              fill="#334155"
              fontFamily="system-ui, sans-serif"
            >
              {dim.label}
            </text>
          );
        })}
      </svg>
    </div>
  );
};

