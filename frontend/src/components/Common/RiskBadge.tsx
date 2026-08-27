import type { RiskLevel } from '../../types';

interface RiskBadgeProps {
  level: RiskLevel;
  size?: 'sm' | 'md';
}

export default function RiskBadge({ level, size = 'md' }: RiskBadgeProps) {
  const cls = {
    HIGH: 'badge badge-high',
    MEDIUM: 'badge badge-medium',
    LOW: 'badge badge-low',
  }[level];

  return (
    <span className={`${cls}${size === 'sm' ? ' badge-sm' : ''}`}>
      {level === 'HIGH' ? '🔴 HIGH' : level === 'MEDIUM' ? '🟠 MED' : '🟢 LOW'}
    </span>
  );
}
