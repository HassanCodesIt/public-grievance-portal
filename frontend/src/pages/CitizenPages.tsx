import { useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router";
import {
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  ClipboardList,
  Clock3,
  Copy,
  File,
  MessageSquareText,
  Paperclip,
  RotateCcw,
  Sparkles,
  UploadCloud,
  X,
} from "lucide-react";
import * as api from "../api";
import {
  Button,
  Card,
  CountCard,
  EmptyState,
  ErrorBanner,
  Field,
  HistoryTimeline,
  Modal,
  PageHeader,
  PriorityChip,
  SelectField,
  Skeleton,
  StarRating,
  StatusBadge,
  Toast,
} from "../components";
import { useLoad } from "../hooks";

export function SubmitGrievancePage() {
  const [form, setForm] = useState({
    district: "",
    category: "",
    subject: "",
    description: "",
    priority: "Medium" as api.Priority,
    department: "",
  });
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<Awaited<ReturnType<typeof api.analyzeGrievance>> | null>(
    null,
  );
  const [analyzing, setAnalyzing] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState<api.Grievance | null>(null);
  const [toast, setToast] = useState(false);

  const analyze = async () => {
    if (form.description.trim().length < 20) {
      setErrors({
        ...errors,
        description: "Enter at least 20 characters before requesting a suggestion.",
      });
      return;
    }
    setAnalyzing(true);
    setAnalysis(await api.analyzeGrievance(form.description, form.district));
    setAnalyzing(false);
  };
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const next: Record<string, string> = {};
    if (!form.district) next.district = "Select a district.";
    if (!form.category) next.category = "Select a category.";
    if (form.subject.trim().length < 8)
      next.subject = "Enter a clear subject of at least 8 characters.";
    if (form.description.trim().length < 20)
      next.description = "Describe the issue in at least 20 characters.";
    setErrors(next);
    if (Object.keys(next).length) return;
    setSubmitted(await api.submitGrievance({ ...form, attachments: file ? [file.name] : [] }));
  };
  if (submitted)
    return (
      <div className="container portal-page narrow">
        <Card className="submission-success">
          <span className="success-check">
            <Check />
          </span>
          <span className="eyebrow">Successfully submitted</span>
          <h1>Your grievance has been received</h1>
          <p>Keep this fictional reference number to track public updates.</p>
          <div className="reference-box">
            <strong>{submitted.referenceNo}</strong>
            <button
              onClick={() => {
                navigator.clipboard.writeText(submitted.referenceNo);
                setToast(true);
              }}
              aria-label="Copy reference number"
            >
              <Copy /> Copy
            </button>
          </div>
          <div className="hero-actions centered-actions">
            <Link className="btn secondary" to={`/track?reference=${submitted.referenceNo}`}>
              Track grievance
            </Link>
            <Link className="btn primary" to="/citizen">
              Go to dashboard
            </Link>
          </div>
          {toast && <Toast message="Reference number copied." onClose={() => setToast(false)} />}
        </Card>
      </div>
    );
  return (
    <div className="container portal-page">
      <PageHeader
        eyebrow="New grievance"
        title="Tell us what happened"
        description="Use clear, factual language. Do not enter real personal, medical or financial information in this prototype."
      />
      <form onSubmit={submit}>
        <div className="submit-layout">
          <Card className="form-card">
            <div className="form-grid">
              <div>
                <SelectField
                  label="District"
                  value={form.district}
                  onChange={(district) => setForm({ ...form, district })}
                  options={api.districts}
                />
                {errors.district && <small className="field-error">{errors.district}</small>}
              </div>
              <div>
                <SelectField
                  label="Category"
                  value={form.category}
                  onChange={(category) => setForm({ ...form, category })}
                  options={api.categories}
                />
                {errors.category && <small className="field-error">{errors.category}</small>}
              </div>
            </div>
            <Field label="Subject" error={errors.subject}>
              <input
                value={form.subject}
                maxLength={120}
                onChange={(e) => setForm({ ...form, subject: e.target.value })}
                placeholder="A short title for the issue"
              />
            </Field>
            <Field
              label="Detailed description"
              error={errors.description}
              hint={`${form.description.length} / 2000 characters`}
            >
              <textarea
                rows={9}
                maxLength={2000}
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="What happened, where, and how has it affected the community?"
              />
            </Field>
            <Field label="Supporting file (optional)" hint="JPG, PNG or PDF · Maximum 2 MB">
              {file ? (
                <div className="file-chip">
                  <File size={17} />
                  <span>{file.name}</span>
                  <button type="button" onClick={() => setFile(null)} aria-label="Remove file">
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <label className="upload-zone">
                  <UploadCloud />
                  <strong>Choose a file</strong>
                  <span>or drag and drop here</span>
                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png,.pdf"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                </label>
              )}
            </Field>
          </Card>
          <aside>
            <Card className="ai-panel">
              <div className="ai-title">
                <span>
                  <Sparkles />
                </span>
                <div>
                  <h2>AI Grievance Assistant</h2>
                  <p>Optional, editable guidance</p>
                </div>
              </div>
              {!analysis && !analyzing && (
                <>
                  <p>Get a suggested category, department and summary from your description.</p>
                  <Button type="button" variant="secondary" onClick={analyze}>
                    Get AI suggestion
                  </Button>
                </>
              )}
              {analyzing && (
                <div className="ai-loading">
                  <span className="spinner" />
                  <strong>Preparing a suggestion…</strong>
                  <p>A human will still make every decision.</p>
                </div>
              )}
              {analysis && (
                <div className="analysis-result">
                  <span className="source-label">
                    {analysis.source === "groq" ? "AI suggestion" : "Keyword fallback, not AI"}
                  </span>
                  <dl>
                    <div>
                      <dt>Category</dt>
                      <dd>{analysis.category}</dd>
                    </div>
                    <div>
                      <dt>Department</dt>
                      <dd>{analysis.department}</dd>
                    </div>
                    <div>
                      <dt>Priority</dt>
                      <dd>
                        <PriorityChip priority={analysis.priority} />
                      </dd>
                    </div>
                  </dl>
                  <div>
                    <span className="small-label">CMO summary</span>
                    <p>{analysis.summary}</p>
                  </div>
                  <div className="confidence">
                    <span>
                      Confidence <strong>{analysis.confidence}%</strong>
                    </span>
                    <div>
                      <i style={{ width: `${analysis.confidence}%` }} />
                    </div>
                  </div>
                  <p className="decision-note">
                    You can change these before submitting. The CMO makes the final decision.
                  </p>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() =>
                      setForm({
                        ...form,
                        category: analysis.category,
                        department: analysis.department,
                        priority: analysis.priority,
                      })
                    }
                  >
                    Use suggestion
                  </Button>
                  {analysis.duplicateCandidates.length > 0 && (
                    <div className="duplicate-notice">
                      <AlertTriangle />
                      Possible similar complaints found, a human will review.
                    </div>
                  )}
                </div>
              )}
            </Card>
          </aside>
        </div>
        <div className="form-actions">
          <Button type="submit">
            Submit grievance <ArrowRight size={18} />
          </Button>
        </div>
      </form>
    </div>
  );
}

export function CitizenDashboard() {
  const { data, loading, error, retry } = useLoad(api.getMyGrievances, []);
  const pending = data?.filter((g) => g.status !== "Resolved").length ?? 0;
  return (
    <div className="container portal-page">
      <PageHeader
        eyebrow="Citizen dashboard"
        title="Good morning, Meera"
        description="Track progress, review updates and respond when action is complete."
        action={
          <Link to="/citizen/submit" className="btn primary">
            Submit grievance
          </Link>
        }
      />
      <div className="count-grid three">
        <CountCard label="Total submitted" value={data?.length ?? "—"} icon={ClipboardList} />
        <CountCard label="Pending" value={pending || "—"} icon={Clock3} tone="amber" />
        <CountCard
          label="Resolved"
          value={data?.filter((g) => g.status === "Resolved").length ?? "—"}
          icon={CheckCircle2}
          tone="green"
        />
      </div>
      <Card>
        <div className="card-heading">
          <div>
            <h2>My grievances</h2>
            <p>Your latest submissions and updates.</p>
          </div>
        </div>
        {loading ? (
          <Skeleton rows={5} />
        ) : error ? (
          <ErrorBanner onRetry={retry} />
        ) : !data?.length ? (
          <EmptyState
            title="No grievances yet"
            text="Submit your first grievance to see it here."
          />
        ) : (
          <div className="responsive-table">
            <table>
              <thead>
                <tr>
                  <th>Reference</th>
                  <th>Subject</th>
                  <th>District</th>
                  <th>Status</th>
                  <th>Submitted</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {data.map((g) => (
                  <tr key={g.id}>
                    <td data-label="Reference">
                      <strong>{g.referenceNo}</strong>
                    </td>
                    <td data-label="Subject">{g.subject}</td>
                    <td data-label="District">{g.district}</td>
                    <td data-label="Status">
                      <StatusBadge status={g.status} />
                    </td>
                    <td data-label="Submitted">
                      {new Date(g.createdAt).toLocaleDateString("en-IN")}
                    </td>
                    <td>
                      <Link to={`/citizen/grievances/${g.id}`} aria-label={`View ${g.referenceNo}`}>
                        <ArrowRight />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}

export function CitizenDetail() {
  const { id = "1" } = useParams();
  const { data: g, loading, error, retry, setData } = useLoad(() => api.getGrievance(id), [id]);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [reopen, setReopen] = useState(false);
  const [reason, setReason] = useState("");
  const [toast, setToast] = useState("");
  if (loading)
    return (
      <div className="container portal-page">
        <Skeleton rows={8} />
      </div>
    );
  if (error)
    return (
      <div className="container portal-page">
        <ErrorBanner onRetry={retry} />
      </div>
    );
  if (!g)
    return (
      <div className="container portal-page">
        <EmptyState title="Grievance not found" />
      </div>
    );
  const doReopen = async () => {
    const updated = await api.reopenGrievance(g.id, reason);
    setData(updated ?? null);
    setReopen(false);
    setToast("Grievance reopened for CMO review.");
  };
  return (
    <div className="container portal-page">
      <PageHeader
        eyebrow="Grievance detail"
        title={g.referenceNo}
        description={g.subject}
        action={<StatusBadge status={g.status} />}
      />
      <div className="detail-layout">
        <div>
          <Card>
            <h2>Complaint details</h2>
            <div className="detail-grid">
              <div>
                <span>District</span>
                <strong>{g.district}</strong>
              </div>
              <div>
                <span>Category</span>
                <strong>{g.category}</strong>
              </div>
              <div>
                <span>Department</span>
                <strong>{g.department}</strong>
              </div>
              <div>
                <span>Submitted</span>
                <strong>
                  {new Date(g.createdAt).toLocaleDateString("en-IN", { dateStyle: "medium" })}
                </strong>
              </div>
            </div>
            <h3>Description</h3>
            <p>{g.description}</p>
            {g.attachments?.map((file) => (
              <div className="file-chip static" key={file}>
                <Paperclip />
                {file}
              </div>
            ))}
          </Card>
          <Card>
            <h2>Public remarks</h2>
            {g.publicRemarks?.length ? (
              g.publicRemarks.map((remark) => (
                <div className="remark" key={remark}>
                  <MessageSquareText />
                  {remark}
                </div>
              ))
            ) : (
              <p className="muted">No public remarks yet.</p>
            )}
          </Card>
        </div>
        <Card>
          <h2>Status history</h2>
          <HistoryTimeline history={g.history} publicOnly />
        </Card>
      </div>
      {g.status === "Resolved" && (
        <div className="two-column-section">
          <Card>
            <h2>How was the resolution?</h2>
            <p>Your feedback helps demonstrate a complete citizen journey.</p>
            <StarRating value={rating} onChange={setRating} />
            <Field label="Comment (optional)">
              <textarea rows={3} value={comment} onChange={(e) => setComment(e.target.value)} />
            </Field>
            <Button
              onClick={async () => {
                await api.submitFeedback(g.id, rating, comment);
                setToast("Feedback submitted. Thank you.");
              }}
            >
              Submit feedback
            </Button>
          </Card>
          <Card className="reopen-card">
            <span className="large-icon amber">
              <RotateCcw />
            </span>
            <h2>Issue not resolved?</h2>
            <p>Reopen this grievance with a reason. It will return to the CMO for human review.</p>
            <Button variant="secondary" onClick={() => setReopen(true)}>
              Reopen grievance
            </Button>
          </Card>
        </div>
      )}
      {reopen && (
        <Modal title="Reopen grievance" onClose={() => setReopen(false)}>
          <p>Explain why the issue needs another review.</p>
          <Field label="Reason for reopening" error={!reason ? "A reason is required." : undefined}>
            <textarea rows={4} value={reason} onChange={(e) => setReason(e.target.value)} />
          </Field>
          <div className="modal-actions">
            <Button variant="ghost" onClick={() => setReopen(false)}>
              Cancel
            </Button>
            <Button variant="primary" disabled={!reason.trim()} onClick={doReopen}>
              Reopen grievance
            </Button>
          </div>
        </Modal>
      )}
      {toast && <Toast message={toast} onClose={() => setToast("")} />}
    </div>
  );
}
