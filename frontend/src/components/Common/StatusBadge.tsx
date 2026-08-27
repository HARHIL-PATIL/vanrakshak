import type { IncidentStatus } from '../../types';

interface StatusBadgeProps {
  status: IncidentStatus;
}

const STATUS_CONFIG: Record<IncidentStatus, { cls: string; label: string }> = {
  NEW: { cls: 'badge badge-new', label: 'NEW' },
  ASSIGNED: { cls: 'badge badge-assigned', label: 'ASSIGNED' },
  IN_PROGRESS: { cls: 'badge badge-in-progress', label: 'IN PROGRESS' },
  RESOLVED: { cls: 'badge badge-resolved', label: 'RESOLVED' },
  ESCALATED: { cls: 'badge badge-escalated', label: '⚡ ESCALATED' },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.NEW;
  return <span className={config.cls}>{config.label}</span>;
}
