import { useState } from "react";
import { Link, useParams } from "react-router";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Clock3,
  FileDown,
  Filter,
  Gauge,
  LineChart,
  MessageSquareText,
  Paperclip,
  PieChart,
  Search,
  ShieldAlert,
  Sparkles,
  Users,
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
  Pagination,
  PriorityChip,
  SelectField,
  Skeleton,
  StatusBadge,
  Toast,
} from "../components";
import { useLoad } from "../hooks";

function MiniBars({
  values,
  labels,
  color = "teal",
}: {
  values: number[];
  labels: string[];
  color?: string;
}) {
  const max = Math.max(...values);
  return (
    <div className={`mini-bars ${color}`}>
      {values.map((value, i) => (
        <div key={labels[i]}>
          <div>
            <i style={{ height: `${(value / max) * 100}%` }} />
          </div>
          <span>{labels[i]}</span>
          <small>{value}</small>
        </div>
      ))}
    </div>
  );
}
function Donut() {
  return (
    <div className="donut-wrap">
      <div className="donut">
        <span>
          <strong>12</strong>Total
        </span>
      </div>
      <ul>
        <li>
          <i className="submitted" />
          Submitted <strong>2</strong>
        </li>
        <li>
          <i className="progress" />
          In Progress <strong>3</strong>
        </li>
        <li>
          <i className="resolved" />
          Resolved <strong>4</strong>
        </li>
        <li>
          <i className="review" />
          Other <strong>3</strong>
        </li>
      </ul>
    </div>
  );
}
function Trend() {
  return (
    <div className="trend-chart" aria-label="Illustrative grievance trend">
      <svg viewBox="0 0 500 150" role="img">
        <title>Trend over six months</title>
        <path
          className="area"
          d="M0,125 C70,100 80,110 140,75 S230,95 290,50 S390,70 500,20 L500,150 L0,150Z"
        />
        <path d="M0,125 C70,100 80,110 140,75 S230,95 290,50 S390,70 500,20" />
      </svg>
      <div>
        <span>Jan</span>
        <span>Feb</span>
        <span>Mar</span>
        <span>Apr</span>
        <span>May</span>
        <span>Jun</span>
      </div>
    </div>
  );
}

export function CmoOverview() {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    district: "",
    category: "",
    priority: "",
    status: "",
    overdue: false,
    search: "",
  });
  const { data: stats } = useLoad(api.getCmoStats, []);
  const { data, loading, error, retry } = useLoad(
    () => api.getCmoGrievances(filters, page),
    [page, filters.status, filters.search],
  );
  return (
    <div className="container portal-page">
      <PageHeader
        eyebrow="CMO command centre"
        title="Grievance overview"
        description="Monitor workload, review routing and act on overdue grievances."
      />
      <div className="count-grid four">
        <CountCard label="Total grievances" value={stats?.total ?? "—"} icon={Gauge} />
        <CountCard label="Pending" value={stats?.pending ?? "—"} icon={Clock3} tone="amber" />
        <CountCard
          label="Resolved"
          value={stats?.resolved ?? "—"}
          icon={CheckCircle2}
          tone="green"
        />
        <CountCard
          label="Overdue"
          value={stats?.overdue ?? "—"}
          icon={ShieldAlert}
          tone="danger"
          detail="Needs attention"
        />
      </div>
      <div className="chart-grid">
        <Card className="chart-card">
          <div className="chart-head">
            <div>
              <span className="eyebrow">Distribution</span>
              <h2>By district</h2>
            </div>
            <BarChart3 />
          </div>
          <MiniBars
            values={[22, 18, 28, 13, 20, 25]}
            labels={["TVM", "EKM", "TSR", "KTM", "KZD", "KNR"]}
          />
        </Card>
        <Card className="chart-card">
          <div className="chart-head">
            <div>
              <span className="eyebrow">Workload</span>
              <h2>By department</h2>
            </div>
            <Users />
          </div>
          <MiniBars
            values={[30, 18, 25, 15, 22]}
            labels={["PWD", "Health", "Water", "LSG", "Revenue"]}
            color="blue"
          />
        </Card>
        <Card className="chart-card">
          <div className="chart-head">
            <div>
              <span className="eyebrow">Current state</span>
              <h2>By status</h2>
            </div>
            <PieChart />
          </div>
          <Donut />
        </Card>
        <Card className="chart-card">
          <div className="chart-head">
            <div>
              <span className="eyebrow">Six months</span>
              <h2>Trend over time</h2>
            </div>
            <LineChart />
          </div>
          <Trend />
        </Card>
      </div>
      <Card className="data-section">
        <div className="card-heading">
          <div>
            <h2>All grievances</h2>
            <p>Showing fictional records across departments.</p>
          </div>
          <Button variant="secondary">
            <FileDown size={17} /> Export sample
          </Button>
        </div>
        <div className="filters">
          <div className="search-input">
            <Search />
            <input
              aria-label="Search by reference number"
              placeholder="Search reference number"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <select
            aria-label="District"
            value={filters.district}
            onChange={(e) => setFilters({ ...filters, district: e.target.value })}
          >
            <option value="">All districts</option>
            {api.districts.map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
          <select
            aria-label="Category"
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
          >
            <option value="">All categories</option>
            {api.categories.map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
          <select
            aria-label="Priority"
            value={filters.priority}
            onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
          >
            <option value="">All priorities</option>
            {["Low", "Medium", "High"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
          <select
            aria-label="Status"
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <option value="">All statuses</option>
            {api.statuses.map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
          <label className="toggle">
            <input
              type="checkbox"
              checked={filters.overdue}
              onChange={(e) => setFilters({ ...filters, overdue: e.target.checked })}
            />
            <span /> Overdue only
          </label>
        </div>
        {loading ? (
          <Skeleton rows={7} />
        ) : error ? (
          <ErrorBanner onRetry={retry} />
        ) : !data?.items.length ? (
          <EmptyState
            title="No matching grievances"
            text="Change or clear filters to see more results."
          />
        ) : (
          <div className="responsive-table dense">
            <table>
              <thead>
                <tr>
                  <th>Reference</th>
                  <th>Subject</th>
                  <th>District</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Department</th>
                  <th>Due date</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {data.items.map((g) => (
                  <tr key={g.id}>
                    <td data-label="Reference">
                      <strong>{g.referenceNo}</strong>
                      {g.escalated && <span className="flag">Escalated</span>}
                    </td>
                    <td data-label="Subject">{g.subject}</td>
                    <td data-label="District">{g.district}</td>
                    <td data-label="Category">{g.category}</td>
                    <td data-label="Priority">
                      <PriorityChip priority={g.priority} />
                    </td>
                    <td data-label="Status">
                      <StatusBadge status={g.status} />
                    </td>
                    <td data-label="Department">{g.department}</td>
                    <td data-label="Due date">
                      <span className={api.isOverdue(g) ? "overdue" : ""}>
                        {new Date(g.dueAt).toLocaleDateString("en-IN")}
                        {api.isOverdue(g) && " · Overdue"}
                      </span>
                    </td>
                    <td>
                      <Link to={`/cmo/grievances/${g.id}`}>
                        <ArrowRight />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <Pagination page={page} totalPages={2} onChange={setPage} />
      </Card>
    </div>
  );
}

export function CmoDetail() {
  const { id = "1" } = useParams();
  const { data: g, loading, error, retry, setData } = useLoad(() => api.getCmoGrievance(id), [id]);
  const [category, setCategory] = useState("");
  const [priority, setPriority] = useState("");
  const [department, setDepartment] = useState("");
  const [officer, setOfficer] = useState("");
  const [remark, setRemark] = useState("");
  const [visibility, setVisibility] = useState<"Public" | "Internal">("Public");
  const [confirm, setConfirm] = useState("");
  const [toast, setToast] = useState("");
  const act = async (message: string, action: () => Promise<api.Grievance | null | undefined>) => {
    const result = await action();
    if (result) setData(result);
    setToast(message);
  };
  if (loading)
    return (
      <div className="container portal-page">
        <Skeleton rows={10} />
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
        eyebrow="CMO review"
        title={g.referenceNo}
        description={g.subject}
        action={
          <div className="header-badges">
            <PriorityChip priority={g.priority} />
            <StatusBadge status={g.status} />
          </div>
        }
      />
      <div className="cmo-detail-grid">
        <div className="main-column">
          <Card>
            <div className="card-heading">
              <h2>Complaint</h2>
              {api.isOverdue(g) && (
                <span className="overdue-callout">
                  <AlertTriangle /> Overdue
                </span>
              )}
            </div>
            <div className="detail-grid three">
              <div>
                <span>Citizen</span>
                <strong>{g.citizenName}</strong>
              </div>
              <div>
                <span>District</span>
                <strong>{g.district}</strong>
              </div>
              <div>
                <span>Category</span>
                <strong>{g.category}</strong>
              </div>
            </div>
            <h3>Description</h3>
            <p>{g.description}</p>
            {g.attachments?.map((file) => (
              <div className="attachment-row" key={file}>
                <span>
                  <Paperclip />
                  {file}
                </span>
                <button>
                  <FileDown /> Download
                </button>
              </div>
            ))}
          </Card>
          <Card className="ai-review">
            <div className="card-heading">
              <div className="ai-title">
                <span>
                  <Sparkles />
                </span>
                <div>
                  <h2>AI Analysis</h2>
                  <p>AI suggestion, not an official decision</p>
                </div>
              </div>
              <span className="source-label">AI suggestion</span>
            </div>
            <p className="summary">{g.aiSummary}</p>
            <div className="detail-grid three">
              <div>
                <span>Suggested category</span>
                <strong>{g.category}</strong>
              </div>
              <div>
                <span>Department</span>
                <strong>{g.department}</strong>
              </div>
              <div>
                <span>Priority</span>
                <PriorityChip priority={g.priority} />
              </div>
            </div>
            <div className="confidence">
              <span>
                Confidence <strong>84%</strong>
              </span>
              <div>
                <i style={{ width: "84%" }} />
              </div>
            </div>
            <div className="decision-row">
              <Button
                variant="secondary"
                onClick={() => setToast("Suggestion accepted as a human decision.")}
              >
                Accept suggestion
              </Button>
              <Button
                variant="ghost"
                onClick={() => {
                  setCategory(g.category);
                  setPriority(g.priority);
                  document.getElementById("cmo-actions")?.scrollIntoView({ behavior: "smooth" });
                }}
              >
                Override
              </Button>
            </div>
          </Card>
          <Card>
            <h2 id="cmo-actions">CMO actions</h2>
            <div className="form-grid">
              <SelectField
                label="Final category"
                value={category || g.category}
                onChange={setCategory}
                options={api.categories}
              />
              <SelectField
                label="Final priority"
                value={priority || g.priority}
                onChange={setPriority}
                options={["Low", "Medium", "High"]}
              />
            </div>
            <div className="button-row">
              <Button
                variant="secondary"
                onClick={() =>
                  act("Moved to Under Review.", () =>
                    api.reviewGrievance(g.id, {
                      category: category || g.category,
                      priority: (priority || g.priority) as api.Priority,
                    }),
                  )
                }
              >
                Move to Under Review
              </Button>
            </div>
            <hr />
            <h3>Forward grievance</h3>
            <div className="form-grid">
              <SelectField
                label="Department"
                value={department}
                onChange={setDepartment}
                options={api.departments.map((x) => x.name)}
              />
              <SelectField
                label="Officer"
                value={officer}
                onChange={setOfficer}
                options={["Ravi Kumar", "Lakshmi Nair", "Saira Joseph"]}
              />
            </div>
            <Button
              disabled={!department || !officer}
              onClick={() =>
                act("Grievance forwarded to the selected officer.", () =>
                  api.assignGrievance(g.id, department, officer),
                )
              }
            >
              Forward
            </Button>
            <hr />
            <Field label="Add remark">
              <textarea rows={3} value={remark} onChange={(e) => setRemark(e.target.value)} />
            </Field>
            <div className="remark-actions">
              <div className="segmented">
                <button
                  className={visibility === "Public" ? "active" : ""}
                  onClick={() => setVisibility("Public")}
                >
                  Public
                </button>
                <button
                  className={visibility === "Internal" ? "active" : ""}
                  onClick={() => setVisibility("Internal")}
                >
                  Internal
                </button>
              </div>
              <Button
                variant="secondary"
                disabled={!remark}
                onClick={async () => {
                  await api.addRemark(g.id, remark, visibility);
                  setRemark("");
                  setToast(`${visibility} remark added.`);
                }}
              >
                Add remark
              </Button>
            </div>
            <div className="danger-zone">
              <div>
                <strong>Delayed grievance</strong>
                <p>Escalation flags this item for priority review.</p>
              </div>
              <Button variant="danger" onClick={() => setConfirm("escalate")}>
                Escalate
              </Button>
            </div>
          </Card>
          {g.report && (
            <Card>
              <h2>Department response</h2>
              <p>{g.report}</p>
              {g.reportAttachments?.map((file) => (
                <div className="attachment-row" key={file}>
                  <span>
                    <Paperclip />
                    {file}
                  </span>
                  <button>
                    <FileDown /> Download
                  </button>
                </div>
              ))}
              <div className="decision-row">
                <Button
                  onClick={() =>
                    act("Report accepted and grievance resolved.", () =>
                      api.decideReport(g.id, "accept"),
                    )
                  }
                >
                  Accept and mark Resolved
                </Button>
                <Button variant="secondary" onClick={() => setConfirm("return")}>
                  Return for rework
                </Button>
              </div>
            </Card>
          )}
        </div>
        <aside>
          <Card className="sticky-card">
            <h2>History timeline</h2>
            <HistoryTimeline history={g.history} />
          </Card>
        </aside>
      </div>
      {confirm === "escalate" && (
        <Modal title="Escalate delayed grievance?" onClose={() => setConfirm("")}>
          <p>This will flag the grievance for priority review. The action will be recorded.</p>
          <div className="modal-actions">
            <Button variant="ghost" onClick={() => setConfirm("")}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => {
                act("Grievance escalated.", () => api.escalateGrievance(g.id));
                setConfirm("");
              }}
            >
              Confirm escalation
            </Button>
          </div>
        </Modal>
      )}
      {confirm === "return" && (
        <Modal title="Return report for rework" onClose={() => setConfirm("")}>
          <Field
            label="Required remark"
            error={!remark ? "Explain what needs to be revised." : undefined}
          >
            <textarea rows={4} value={remark} onChange={(e) => setRemark(e.target.value)} />
          </Field>
          <div className="modal-actions">
            <Button variant="ghost" onClick={() => setConfirm("")}>
              Cancel
            </Button>
            <Button
              disabled={!remark}
              onClick={() => {
                act("Report returned for rework.", () => api.decideReport(g.id, "return", remark));
                setConfirm("");
              }}
            >
              Return report
            </Button>
          </div>
        </Modal>
      )}
      {toast && <Toast message={toast} onClose={() => setToast("")} />}
    </div>
  );
}
