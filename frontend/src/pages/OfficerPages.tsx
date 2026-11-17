import { useState } from "react";
import { Link, useParams } from "react-router";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ClipboardList,
  Clock3,
  File,
  Paperclip,
  Send,
  UploadCloud,
} from "lucide-react";
import * as api from "../api";
import {
  AssignmentChip,
  Button,
  Card,
  CountCard,
  EmptyState,
  ErrorBanner,
  Field,
  PageHeader,
  Skeleton,
  StatusBadge,
  Toast,
} from "../components";
import { useLoad } from "../hooks";

export function OfficerOverview() {
  const { data, loading, error, retry } = useLoad(api.getOfficerGrievances, []);
  return (
    <div className="container portal-page">
      <PageHeader
        eyebrow="Water Resources Department"
        title="Assigned grievances"
        description="Welcome, Ravi. Review CMO instructions and keep action progress up to date."
      />
      <div className="count-grid four">
        <CountCard label="Assigned" value={data?.length ?? "—"} icon={ClipboardList} />
        <CountCard
          label="In progress"
          value={data?.filter((g) => g.status === "In Progress").length ?? "—"}
          icon={Clock3}
          tone="blue"
        />
        <CountCard
          label="Reports submitted"
          value={data?.filter((g) => g.assignmentState === "Report Submitted").length ?? "—"}
          icon={CheckCircle2}
          tone="green"
        />
        <CountCard
          label="Overdue"
          value={data?.filter(api.isOverdue).length ?? "—"}
          icon={AlertTriangle}
          tone="danger"
        />
      </div>
      <Card>
        <div className="card-heading">
          <div>
            <h2>Department queue</h2>
            <p>Only grievances forwarded to this fictional department or officer are shown.</p>
          </div>
        </div>
        {loading ? (
          <Skeleton rows={5} />
        ) : error ? (
          <ErrorBanner onRetry={retry} />
        ) : !data?.length ? (
          <EmptyState title="No assigned grievances" />
        ) : (
          <div className="responsive-table">
            <table>
              <thead>
                <tr>
                  <th>Reference</th>
                  <th>Subject</th>
                  <th>District</th>
                  <th>Status</th>
                  <th>Assignment</th>
                  <th>Due date</th>
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
                    <td data-label="Assignment">
                      <AssignmentChip value={g.assignmentState} />
                    </td>
                    <td data-label="Due date">
                      <span className={api.isOverdue(g) ? "overdue" : ""}>
                        {new Date(g.dueAt).toLocaleDateString("en-IN")}
                      </span>
                    </td>
                    <td>
                      <Link to={`/officer/grievances/${g.id}`}>
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

export function OfficerDetail() {
  const { id = "3" } = useParams();
  const {
    data: g,
    loading,
    error,
    retry,
    setData,
  } = useLoad(() => api.getOfficerGrievance(id), [id]);
  const [progress, setProgress] = useState("");
  const [report, setReport] = useState("");
  const [file, setFile] = useState<File | null>(null);
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
  return (
    <div className="container portal-page">
      <PageHeader
        eyebrow="Officer action"
        title={g.referenceNo}
        description={g.subject}
        action={<AssignmentChip value={g.assignmentState} />}
      />
      {g.assignmentState === "Returned" && (
        <div className="rework-banner">
          <AlertTriangle />
          <div>
            <strong>CMO returned this report for rework</strong>
            <p>Please review the remarks, revise the action-taken report and submit it again.</p>
          </div>
        </div>
      )}
      <div className="detail-layout">
        <div>
          <Card>
            <h2>Complaint details</h2>
            <div className="detail-grid three">
              <div>
                <span>District</span>
                <strong>{g.district}</strong>
              </div>
              <div>
                <span>Category</span>
                <strong>{g.category}</strong>
              </div>
              <div>
                <span>Priority</span>
                <strong>{g.priority}</strong>
              </div>
            </div>
            <h3>Description</h3>
            <p>{g.description}</p>
            {g.attachments?.map((attachment) => (
              <div className="file-chip static" key={attachment}>
                <Paperclip />
                {attachment}
              </div>
            ))}
          </Card>
          <Card>
            <h2>CMO instructions and remarks</h2>
            <div className="instruction">
              <strong>CMO reviewer</strong>
              <p>
                Please inspect the reported location, document the action taken and provide a
                concise public-safe report.
              </p>
            </div>
            {g.publicRemarks?.map((remark) => (
              <div className="instruction" key={remark}>
                <strong>Public remark</strong>
                <p>{remark}</p>
              </div>
            ))}
          </Card>
        </div>
        <div>
          <Card>
            <h2>Add progress update</h2>
            <p>Progress remarks are recorded for CMO review.</p>
            <Field label="Progress remark">
              <textarea rows={4} value={progress} onChange={(e) => setProgress(e.target.value)} />
            </Field>
            <Button
              variant="secondary"
              disabled={!progress.trim()}
              onClick={async () => {
                await api.addProgress(g.id, progress);
                setProgress("");
                setToast("Progress update saved.");
              }}
            >
              Save update
            </Button>
          </Card>
          <Card>
            <h2>Action-taken report</h2>
            <p>
              Describe the inspection, action and outcome. The CMO makes the final resolution
              decision.
            </p>
            <Field label="Report text">
              <textarea
                rows={7}
                value={report}
                onChange={(e) => setReport(e.target.value)}
                placeholder="Summarise action taken and evidence…"
              />
            </Field>
            <Field label="Supporting file (optional)">
              {file ? (
                <div className="file-chip">
                  <File />
                  {file.name}
                  <button onClick={() => setFile(null)}>Remove</button>
                </div>
              ) : (
                <label className="upload-zone compact-upload">
                  <UploadCloud />
                  <span>Attach JPG, PNG or PDF</span>
                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png,.pdf"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                </label>
              )}
            </Field>
            <Button
              disabled={report.trim().length < 20}
              onClick={async () => {
                const updated = await api.submitActionReport(g.id, report);
                setData(updated ?? null);
                setToast("Action-taken report submitted to the CMO.");
              }}
            >
              Submit to CMO <Send size={17} />
            </Button>
          </Card>
        </div>
      </div>
      {toast && <Toast message={toast} onClose={() => setToast("")} />}
    </div>
  );
}
