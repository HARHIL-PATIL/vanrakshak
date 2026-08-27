import { useState, useEffect } from 'react';
import {
  startCompensation,
  getCompensationChecklist,
  FALLBACK_INCIDENTS,
} from '../../api/client';
import type {
  LossType,
  StartCompensationRequest,
  CompensationClaim,
  CompensationChecklist,
} from '../../types';
import LoadingSpinner from '../Common/LoadingSpinner';

const LOSS_TYPES: { value: LossType; label: string }[] = [
  { value: 'LIVESTOCK_PREDATION', label: 'Livestock Predation' },
  { value: 'CROP_DAMAGE', label: 'Crop Damage' },
  { value: 'PROPERTY_DAMAGE', label: 'Property Damage' },
  { value: 'INJURY', label: 'Human Injury' },
];

const BLANK: StartCompensationRequest = {
  incident_id: '',
  villager_name: '',
  village: '',
  contact: '',
  loss_type: 'LIVESTOCK_PREDATION',
  loss_details: '',
  animals_lost: undefined,
  estimated_value: undefined,
};

export default function CompensationPage() {
  const [form, setForm] = useState<StartCompensationRequest>(BLANK);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState<CompensationClaim | null>(null);
  const [checklist, setChecklist] = useState<CompensationChecklist | null>(null);
  const [checklistLoading, setChecklistLoading] = useState(false);
  const [claims, setClaims] = useState<CompensationClaim[]>([]);
  const [checkedDocs, setCheckedDocs] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadChecklist(form.loss_type);
  }, [form.loss_type]);

  async function loadChecklist(lossType: LossType) {
    setChecklistLoading(true);
    const data = await getCompensationChecklist(lossType);
    setChecklist(data);
    setCheckedDocs({});
    setChecklistLoading(false);
  }

  function updateForm(key: keyof StartCompensationRequest, value: string | number) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.incident_id || !form.villager_name || !form.village) return;
    setSubmitting(true);
    try {
      const result = await startCompensation(form);
      if (result) {
        setClaims((prev) => [result, ...prev]);
        setSubmitted(result);
        setForm(BLANK);
      } else {
        // Offline fallback: create a mock claim
        const mockClaim: CompensationClaim = {
          claim_id: `CLM-${Date.now().toString(36).toUpperCase()}`,
          incident_id: form.incident_id,
          villager_name: form.villager_name,
          village: form.village,
          contact: form.contact,
          loss_type: form.loss_type,
          loss_details: form.loss_details,
          animals_lost: form.animals_lost,
          estimated_value: form.estimated_value,
          status: 'DRAFT',
          officer_review_status: 'PENDING',
          created_at: new Date().toISOString(),
          documents_checklist: checklist?.required_documents ?? [],
        };
        setClaims((prev) => [mockClaim, ...prev]);
        setSubmitted(mockClaim);
        setForm(BLANK);
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="page-title">💰 Compensation Assistant</div>
            <div className="page-subtitle">
              Guided compensation claim filing for wildlife conflict losses
            </div>
          </div>
          <span className="demo-data-label">DEMO</span>
        </div>
      </div>

      {/* AI disclaimer */}
      <div className="notice-box info mb-16">
        <span>🤖</span>
        <span>
          <strong>AI ASSISTANCE ONLY</strong> — AI never approves or rejects claims. The
          compensation agent assists with document checklists and form guidance only.{' '}
          <strong>Final decision rests with authorized Forest Department officer.</strong>
        </span>
      </div>

      {/* Success confirmation */}
      {submitted && (
        <div
          className="notice-box mb-16"
          style={{
            background: 'var(--accent-green-dim)',
            border: '1px solid var(--accent-green)',
            color: 'var(--accent-green)',
          }}
        >
          <span>✅</span>
          <div>
            <strong>Claim submitted!</strong> Claim ID:{' '}
            <span style={{ fontFamily: 'monospace', fontWeight: 700 }}>
              {submitted.claim_id}
            </span>
            {' '}— Status: <strong>DRAFT — Pending Officer Review</strong>
            <button
              style={{
                marginLeft: 12,
                fontSize: 11,
                padding: '2px 8px',
                background: 'transparent',
                border: '1px solid var(--accent-green)',
                color: 'var(--accent-green)',
                borderRadius: 3,
                cursor: 'pointer',
              }}
              onClick={() => setSubmitted(null)}
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Two-panel layout */}
      <div className="grid-2 mb-20">
        {/* Left: New Claim Form */}
        <div className="card">
          <div className="card-header">
            <span className="card-title-main">Start New Compensation Claim</span>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Incident Reference *</label>
              <select
                className="form-select"
                value={form.incident_id}
                onChange={(e) => updateForm('incident_id', e.target.value)}
                required
              >
                <option value="">— Select incident —</option>
                {FALLBACK_INCIDENTS.map((inc) => (
                  <option key={inc.id} value={inc.id}>
                    {inc.display_id} · {inc.species} · {inc.village}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Villager Name *</label>
                <input
                  className="form-input"
                  placeholder="Full name"
                  value={form.villager_name}
                  onChange={(e) => updateForm('villager_name', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Village *</label>
                <input
                  className="form-input"
                  placeholder="Village name"
                  value={form.village}
                  onChange={(e) => updateForm('village', e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Contact Number</label>
              <input
                className="form-input"
                placeholder="+91 XXXXX XXXXX"
                value={form.contact}
                onChange={(e) => updateForm('contact', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Loss Type *</label>
              <select
                className="form-select"
                value={form.loss_type}
                onChange={(e) => updateForm('loss_type', e.target.value as LossType)}
                required
              >
                {LOSS_TYPES.map((lt) => (
                  <option key={lt.value} value={lt.value}>
                    {lt.label}
                  </option>
                ))}
              </select>
            </div>

            {form.loss_type === 'LIVESTOCK_PREDATION' && (
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Animals Lost</label>
                  <input
                    className="form-input"
                    type="number"
                    min={1}
                    placeholder="Count"
                    value={form.animals_lost ?? ''}
                    onChange={(e) => updateForm('animals_lost', parseInt(e.target.value))}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Est. Value (₹)</label>
                  <input
                    className="form-input"
                    type="number"
                    min={0}
                    placeholder="Amount"
                    value={form.estimated_value ?? ''}
                    onChange={(e) => updateForm('estimated_value', parseInt(e.target.value))}
                  />
                </div>
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Loss Details</label>
              <textarea
                className="form-textarea"
                placeholder="Describe the loss in detail (species, date/time, extent of damage...)"
                value={form.loss_details}
                onChange={(e) => updateForm('loss_details', e.target.value)}
              />
            </div>

            <button className="btn btn-primary" type="submit" disabled={submitting} style={{ width: '100%' }}>
              {submitting ? '⌛ Submitting...' : '📤 Submit Claim for Officer Review'}
            </button>
          </form>
        </div>

        {/* Right: Document Checklist */}
        <div className="card">
          <div className="card-header">
            <span className="card-title-main">📋 Required Documents</span>
            {checklist && (
              <span className="badge badge-ai" style={{ fontSize: 9 }}>
                AI GENERATED
              </span>
            )}
          </div>

          <div
            style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}
          >
            Documents required for{' '}
            <strong style={{ color: 'var(--text-secondary)' }}>
              {LOSS_TYPES.find((lt) => lt.value === form.loss_type)?.label}
            </strong>{' '}
            claim:
          </div>

          {checklistLoading ? (
            <LoadingSpinner size="sm" label="Loading checklist..." />
          ) : checklist ? (
            <>
              <div style={{ marginBottom: 16 }}>
                <div
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: 'var(--accent-orange)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.8px',
                    marginBottom: 8,
                  }}
                >
                  Required Documents ({checklist.required_documents.length})
                </div>
                {checklist.required_documents.map((doc, i) => (
                  <div key={i} className="checklist-item">
                    <input
                      type="checkbox"
                      className="checklist-checkbox"
                      checked={!!checkedDocs[`req-${i}`]}
                      onChange={(e) =>
                        setCheckedDocs((prev) => ({
                          ...prev,
                          [`req-${i}`]: e.target.checked,
                        }))
                      }
                    />
                    <span>{doc}</span>
                  </div>
                ))}
              </div>

              {checklist.optional_documents.length > 0 && (
                <div style={{ marginBottom: 14 }}>
                  <div
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      color: 'var(--text-muted)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.8px',
                      marginBottom: 8,
                    }}
                  >
                    Optional / Supporting ({checklist.optional_documents.length})
                  </div>
                  {checklist.optional_documents.map((doc, i) => (
                    <div key={i} className="checklist-item">
                      <input
                        type="checkbox"
                        className="checklist-checkbox"
                        checked={!!checkedDocs[`opt-${i}`]}
                        onChange={(e) =>
                          setCheckedDocs((prev) => ({
                            ...prev,
                            [`opt-${i}`]: e.target.checked,
                          }))
                        }
                      />
                      <span style={{ color: 'var(--text-muted)' }}>{doc}</span>
                    </div>
                  ))}
                </div>
              )}

              {checklist.notes && (
                <div
                  style={{
                    padding: '8px 10px',
                    background: 'var(--accent-blue-dim)',
                    border: '1px solid rgba(59,130,246,0.2)',
                    borderRadius: 4,
                    fontSize: 11,
                    color: 'var(--accent-blue)',
                  }}
                >
                  ℹ️ {checklist.notes}
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <div>Select a loss type to see required documents</div>
            </div>
          )}
        </div>
      </div>

      {/* Active Claims */}
      {claims.length > 0 && (
        <div className="card">
          <div className="card-header">
            <span className="card-title">Active Claims (This Session)</span>
            <span className="demo-data-label">SESSION DATA</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {claims.map((claim) => (
              <div
                key={claim.claim_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 12px',
                  background: 'var(--bg-elevated)',
                  borderRadius: 4,
                  flexWrap: 'wrap',
                  gap: 8,
                }}
              >
                <div>
                  <span
                    style={{
                      fontFamily: 'monospace',
                      fontSize: 12,
                      fontWeight: 700,
                      color: 'var(--accent-blue)',
                    }}
                  >
                    {claim.claim_id}
                  </span>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 10 }}>
                    {claim.villager_name} · {claim.village}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <span
                    className="badge badge-assigned"
                    style={{ fontSize: 9 }}
                  >
                    DRAFT — Pending Officer Review
                  </span>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    {new Date(claim.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="notice-box warning mt-12">
            <span>⚠️</span>
            <span>
              <strong>IMPORTANT:</strong> AI never approves or rejects claims. Final decision
              by authorized forest official only. Claims marked DRAFT require officer review.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
