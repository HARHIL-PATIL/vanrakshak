import type { VillageMapNode } from '../../types';

const VILLAGES: VillageMapNode[] = [
  { id: 'sasan', name: 'Sasan Gir', name_gu: 'સાસણ ગીર', x: 50, y: 42, risk: 'HIGH', incidents: 2 },
  { id: 'dhari', name: 'Dhari', name_gu: 'ધારી', x: 20, y: 25, risk: 'MEDIUM', incidents: 1 },
  { id: 'talala', name: 'Talala', name_gu: 'તાળાળા', x: 68, y: 60, risk: 'HIGH', incidents: 1 },
  { id: 'mendarda', name: 'Mendarda', name_gu: 'મેંદરડા', x: 34, y: 58, risk: 'LOW', incidents: 1 },
  { id: 'visavadar', name: 'Visavadar', name_gu: 'વિસાવદર', x: 15, y: 68, risk: 'MEDIUM', incidents: 1 },
  { id: 'una', name: 'Una', name_gu: 'ઉના', x: 80, y: 78, risk: 'MEDIUM', incidents: 1 },
  { id: 'kodinar', name: 'Kodinar', name_gu: 'કોડીનાર', x: 72, y: 88, risk: 'LOW', incidents: 0 },
  { id: 'jafrabad', name: 'Jafrabad', name_gu: 'જાફરાબાદ', x: 88, y: 55, risk: 'LOW', incidents: 0 },
];

const RISK_COLORS: Record<string, string> = {
  HIGH: '#ff3b3b',
  MEDIUM: '#ff8c00',
  LOW: '#00c896',
};

export default function RiskMap() {
  return (
    <div
      className="card"
      style={{ padding: 0, overflow: 'hidden' }}
    >
      <div className="card-header" style={{ padding: '12px 14px', borderBottom: '1px solid var(--border)' }}>
        <span className="card-title">Village Risk Map — Gir Region</span>
        <div style={{ display: 'flex', gap: 6 }}>
          <span className="demo-data-label">ILLUSTRATIVE</span>
          <span className="demo-data-label">DEMO DATA</span>
        </div>
      </div>

      {/* Map SVG */}
      <div className="risk-map-container" style={{ height: 280 }}>
        <svg
          viewBox="0 0 100 100"
          className="risk-map-svg"
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Forest background blobs */}
          <defs>
            <radialGradient id="forestGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#0d2a1a" />
              <stop offset="100%" stopColor="#0a0e1a" />
            </radialGradient>
          </defs>
          <rect width="100" height="100" fill="url(#forestGrad)" />

          {/* Forest zone indicators */}
          <ellipse cx="50" cy="50" rx="35" ry="28" fill="#0f2a1a" opacity="0.6" />
          <ellipse cx="45" cy="48" rx="28" ry="22" fill="#122a1c" opacity="0.5" />

          {/* Road-like lines */}
          <line x1="10" y1="50" x2="90" y2="50" stroke="#1e2d4a" strokeWidth="0.4" strokeDasharray="2,1" />
          <line x1="50" y1="10" x2="50" y2="90" stroke="#1e2d4a" strokeWidth="0.4" strokeDasharray="2,1" />
          <line x1="20" y1="20" x2="80" y2="80" stroke="#1e2d4a" strokeWidth="0.3" strokeDasharray="1,2" />

          {/* Hotspot zone for HIGH risk */}
          {VILLAGES.filter((v) => v.risk === 'HIGH').map((v) => (
            <g key={`hotspot-${v.id}`}>
              <circle
                cx={v.x}
                cy={v.y}
                r="14"
                fill="rgba(255,59,59,0.05)"
                stroke="rgba(255,59,59,0.2)"
                strokeWidth="0.5"
                className="pulse-ring"
              />
            </g>
          ))}

          {/* Village nodes */}
          {VILLAGES.map((v) => {
            const color = RISK_COLORS[v.risk];
            return (
              <g key={v.id}>
                {/* Outer glow */}
                <circle
                  cx={v.x}
                  cy={v.y}
                  r="5"
                  fill="transparent"
                  stroke={color}
                  strokeWidth="0.5"
                  opacity="0.4"
                />
                {/* Village circle */}
                <circle
                  cx={v.x}
                  cy={v.y}
                  r="3.5"
                  fill={color}
                  opacity="0.85"
                />
                <circle cx={v.x} cy={v.y} r="1.5" fill="#fff" opacity="0.9" />

                {/* Name label */}
                <text
                  x={v.x}
                  y={v.y - 5.5}
                  textAnchor="middle"
                  fill="#e8eaf0"
                  fontSize="3"
                  fontFamily="Inter, sans-serif"
                  fontWeight="600"
                >
                  {v.name}
                </text>

                {/* Incident count */}
                {v.incidents > 0 && (
                  <text
                    x={v.x}
                    y={v.y + 8}
                    textAnchor="middle"
                    fill={color}
                    fontSize="2.5"
                    fontFamily="monospace"
                  >
                    {v.incidents} INC
                  </text>
                )}
              </g>
            );
          })}

          {/* GIR label */}
          <text
            x="50"
            y="44"
            textAnchor="middle"
            fill="#1a4028"
            fontSize="6"
            fontFamily="Inter, sans-serif"
            fontWeight="800"
            letterSpacing="2"
            opacity="0.7"
          >
            GIR
          </text>
          <text
            x="50"
            y="49"
            textAnchor="middle"
            fill="#1a4028"
            fontSize="2.5"
            fontFamily="Inter, sans-serif"
            opacity="0.6"
          >
            NATIONAL PARK
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div
        style={{
          display: 'flex',
          gap: 14,
          padding: '8px 14px',
          borderTop: '1px solid var(--border)',
          fontSize: 11,
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        {(['HIGH', 'MEDIUM', 'LOW'] as const).map((r) => (
          <div key={r} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: RISK_COLORS[r],
              }}
            />
            <span style={{ color: RISK_COLORS[r], fontWeight: 600 }}>{r}</span>
          </div>
        ))}
        <span style={{ color: 'var(--text-muted)', marginLeft: 'auto', fontSize: 10, fontStyle: 'italic' }}>
          ILLUSTRATIVE MAP — Demo coordinates only, not real GPS
        </span>
      </div>
    </div>
  );
}
