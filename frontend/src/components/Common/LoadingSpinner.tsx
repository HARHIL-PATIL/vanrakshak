interface LoadingSpinnerProps {
  label?: string;
  size?: 'sm' | 'md';
}

export default function LoadingSpinner({ label = 'Loading...', size = 'md' }: LoadingSpinnerProps) {
  return (
    <div className="loading-overlay">
      <div
        className="spinner"
        style={size === 'sm' ? { width: 14, height: 14 } : undefined}
      />
      <span>{label}</span>
    </div>
  );
}
