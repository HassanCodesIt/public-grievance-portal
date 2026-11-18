import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";
import {
  ArrowRight,
  BarChart3,
  BookOpenCheck,
  Building2,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Droplets,
  GraduationCap,
  HeartPulse,
  Lightbulb,
  MapPin,
  MessageSquareText,
  Phone,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  Target,
  Users,
  Wrench,
} from "lucide-react";
import * as api from "../api";
import {
  Accordion,
  Button,
  Card,
  CountCard,
  ErrorBanner,
  Field,
  HistoryTimeline,
  PageHeader,
  PriorityChip,
  Skeleton,
  StatusBadge,
  Toast,
  WakeBanner,
} from "../components";
import { useLoad } from "../hooks";

const steps = [
  ["01", "Submit", "Share the issue and receive a reference number."],
  ["02", "CMO Review", "A human reviewer checks and categorises it."],
  ["03", "Assignment", "It is sent to the responsible department."],
  ["04", "Action", "An officer investigates and submits a report."],
  ["05", "Resolution", "The CMO reviews the report; you can give feedback or reopen."],
];

export function HomePage() {
  const [reference, setReference] = useState("");
  const navigate = useNavigate();
  const { data: stats, loading } = useLoad(api.getPublicStats, []);
  return (
    <>
      <section className="hero">
        <div className="hero-bg-grid" />
        <div className="container hero-inner">
          <div className="hero-copy">
            <span className="eyebrow light">A fictional civic service prototype</span>
            <h1>Janasevanam gives every concern a clear path to action.</h1>
            <p>
              With Janasevanam, submit, follow and understand the progress of a public service
              grievance through one accessible portal.
            </p>
            <div className="hero-actions">
              <Link className="btn amber" to="/citizen/submit">
                Submit Grievance <ArrowRight size={18} />
              </Link>
              <Link className="btn outline-light" to="/track">
                Track Grievance
              </Link>
            </div>
            <div className="hero-trust">
              <ShieldCheck size={18} /> Human-reviewed workflow · Clear status updates · Accessible
              by design
            </div>
          </div>
          <Card className="track-widget">
            <div className="track-widget-icon">
              <Search />
            </div>
            <span className="eyebrow">Quick tracking</span>
            <h2>Check grievance status</h2>
            <p>Enter your reference number to see public updates.</p>
            <Field label="Reference number">
              <input
                value={reference}
                onChange={(e) => setReference(e.target.value.toUpperCase())}
                placeholder="CMK-2026-000123"
              />
            </Field>
            <Button onClick={() => navigate(`/track?reference=${reference}`)}>
              Track now <ArrowRight size={18} />
            </Button>
            <small>Try the sample: CMK-2026-000123</small>
          </Card>
        </div>
      </section>
      <section className="section stats-section">
        <div className="container">
          <div className="section-heading split">
            <div>
              <span className="eyebrow">Sample data</span>
              <h2>Designed around measurable outcomes</h2>
            </div>
            <p>Illustrative figures for this recruitment prototype.</p>
          </div>
          <div className="count-grid">
            {loading ? (
              <Skeleton rows={4} />
            ) : (
              stats && (
                <>
                  <CountCard
                    label="Total received"
                    value={stats.total.toLocaleString("en-IN")}
                    icon={MessageSquareText}
                  />
                  <CountCard
                    label="Resolved"
                    value={stats.resolved.toLocaleString("en-IN")}
                    icon={CheckCircle2}
                    tone="green"
                  />
                  <CountCard
                    label="In progress"
                    value={stats.inProgress}
                    icon={Clock3}
                    tone="blue"
                  />
                  <CountCard
                    label="Average resolution"
                    value={`${stats.averageDays} days`}
                    icon={BarChart3}
                    tone="amber"
                  />
                </>
              )
            )}
          </div>
        </div>
      </section>
      <section className="section white">
        <div className="container">
          <div className="section-heading centered">
            <span className="eyebrow">A transparent process</span>
            <h2>How it works</h2>
            <p>Five clear steps from submission to resolution.</p>
          </div>
          <div className="steps-strip">
            {steps.map(([number, title, text]) => (
              <div className="step" key={number}>
                <span>{number}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </div>
            ))}
          </div>
          <div className="center-action">
            <Link to="/how-it-works" className="text-link arrow">
              Explore the full process <ArrowRight size={17} />
            </Link>
          </div>
        </div>
      </section>
      <DepartmentFeature />
      <section className="cta-band">
        <div className="container">
          <div>
            <span className="eyebrow light">Ready to begin?</span>
            <h2>Raise a concern in a few clear steps.</h2>
            <p>Please do not enter real personal data in this fictional prototype.</p>
          </div>
          <Link className="btn amber" to="/citizen/submit">
            Submit Grievance <ArrowRight size={18} />
          </Link>
        </div>
      </section>
    </>
  );
}

function DepartmentFeature() {
  const icons = [Wrench, HeartPulse, GraduationCap, Droplets, Lightbulb, Building2];
  const { data: depts, loading } = useLoad(api.getDepartments, []);
  const items = depts ?? api.departments;
  return (
    <section className="section">
      <div className="container">
        <div className="section-heading split">
          <div>
            <span className="eyebrow">Coordinated response</span>
            <h2>Featured departments</h2>
          </div>
          <Link to="/departments" className="text-link arrow">
            View all departments <ArrowRight size={17} />
          </Link>
        </div>
        <div className="department-grid">
          {loading
            ? Array.from({ length: 6 }).map((_, i) => (
                <Card className="department-card" key={i}>
                  <Skeleton rows={2} />
                </Card>
              ))
            : items.slice(0, 6).map((item, i) => {
                const Icon = icons[i];
                return (
                  <Card className="department-card" key={item.name}>
                    <span className="department-icon">
                      <Icon />
                    </span>
                    <h3>{item.name}</h3>
                    <p>{item.description}</p>
                  </Card>
                );
              })}
        </div>
      </div>
    </section>
  );
}

export function AboutPage() {
  const values = [
    [
      Target,
      "Purpose",
      "Create a clear, respectful route for civic concerns to reach the right team.",
    ],
    [
      Sparkles,
      "Vision",
      "A public service experience where progress is understandable and accountability is visible.",
    ],
    [
      ShieldCheck,
      "Mission",
      "Support timely, human-reviewed grievance handling with accessible digital tools.",
    ],
  ] as const;
  return (
    <div className="container page">
      <PageHeader
        eyebrow="About the prototype"
        title="About Janasevanam"
        description="Janasevanam demonstrates how a modern grievance redressal experience could make complex administrative workflows easier to understand."
      />
      <div className="feature-trio">
        {values.map(([Icon, title, text]) => (
          <Card key={title}>
            <span className="large-icon">
              <Icon />
            </span>
            <h2>{title}</h2>
            <p>{text}</p>
          </Card>
        ))}
      </div>
      <Card className="objectives">
        <div>
          <span className="eyebrow">Our objectives</span>
          <h2>What this experience is designed to do</h2>
          <p>Every interaction should help people understand what happens next.</p>
        </div>
        <ul>
          {[
            "Make grievance submission simple and inclusive.",
            "Route concerns to the appropriate department.",
            "Keep public updates clear without exposing private information.",
            "Support human decision-making with changeable AI suggestions.",
            "Create a visible, auditable history of status changes.",
          ].map((item) => (
            <li key={item}>
              <CheckCircle2 />
              {item}
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

export function HowItWorksPage() {
  const statusText: Record<api.Status, string> = {
    Submitted: "Your grievance has been received and given a reference number.",
    "Under Review": "A CMO reviewer is checking the details and routing.",
    "In Progress": "A department officer is investigating or taking action.",
    Resolved: "The CMO has accepted the department's action-taken report.",
    Reopened: "The citizen has asked for a resolved issue to be reviewed again.",
  };
  return (
    <div className="container page">
      <PageHeader
        eyebrow="From concern to closure"
        title="A process you can follow"
        description="Each transition is recorded with a timestamp and responsible user. Public views show public updates only."
      />
      <div className="vertical-stepper">
        {steps.map(([number, title, text]) => (
          <div key={number}>
            <span>{number}</span>
            <div>
              <h2>
                {title === "Assignment"
                  ? "Department Assignment"
                  : title === "Action"
                    ? "Action and Report"
                    : title === "Resolution"
                      ? "Resolution or Reopen"
                      : title}
              </h2>
              <p>{text}</p>
            </div>
          </div>
        ))}
      </div>
      <section className="subsection">
        <div className="section-heading">
          <span className="eyebrow">Status guide</span>
          <h2>What each status means</h2>
        </div>
        <div className="status-guide">
          {api.statuses.map((status) => (
            <Card key={status}>
              <StatusBadge status={status} />
              <p>{statusText[status]}</p>
            </Card>
          ))}
        </div>
      </section>
      <Card className="ai-explainer">
        <span className="large-icon amber">
          <Sparkles />
        </span>
        <div>
          <h2>AI offers suggestions, never decisions</h2>
          <p>
            The assistant may suggest a category, department, priority and concise summary. Every
            output is labelled as an AI suggestion or keyword fallback, and a human can change it.
            The CMO makes the final decision.
          </p>
        </div>
      </Card>
    </div>
  );
}

export function DepartmentsPage() {
  const icons = [
    Wrench,
    HeartPulse,
    GraduationCap,
    Droplets,
    Lightbulb,
    Building2,
    ClipboardCheck,
    MapPin,
    Send,
    Users,
  ];
  const { data: depts, loading, error, retry } = useLoad(api.getDepartments, []);
  const items = depts ?? api.departments;
  return (
    <div className="container page">
      <PageHeader
        eyebrow="Service directory"
        title="Departments"
        description="Government departments that handle citizen grievances in this portal."
      />
      {error && <ErrorBanner onRetry={retry} />}
      <div className="department-grid large">
        {loading
          ? Array.from({ length: 10 }).map((_, i) => (
              <Card className="department-card" key={i}>
                <Skeleton rows={2} />
              </Card>
            ))
          : items.map((item, i) => {
              const Icon = icons[i % icons.length];
              return (
                <Card className="department-card" key={item.name}>
                  <span className="department-icon">
                    <Icon />
                  </span>
                  <h2>{item.name}</h2>
                  <p>{item.description}</p>
                </Card>
              );
            })}
      </div>
    </div>
  );
}

export function ContactPage() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [sent, setSent] = useState(false);
  const [toast, setToast] = useState(false);
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const next: Record<string, string> = {};
    if (!form.name.trim()) next.name = "Please enter your name.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) next.email = "Enter a valid email address.";
    if (!form.subject.trim()) next.subject = "Please enter a subject.";
    if (form.message.trim().length < 20) next.message = "Please enter at least 20 characters.";
    setErrors(next);
    if (Object.keys(next).length) return;
    await api.submitContact(form);
    setSent(true);
    setToast(true);
  };
  return (
    <div className="container page">
      <PageHeader
        eyebrow="Contact"
        title="How can we help?"
        description="This form demonstrates a backend-ready contact flow. Please use fictional information only."
      />
      <div className="contact-layout">
        <Card>
          {sent ? (
            <div className="success-state">
              <CheckCircle2 />
              <h2>Message received</h2>
              <p>Thank you. Your fictional enquiry has been saved for review.</p>
              <Button
                variant="secondary"
                onClick={() => {
                  setSent(false);
                  setForm({ name: "", email: "", subject: "", message: "" });
                }}
              >
                Send another message
              </Button>
            </div>
          ) : (
            <form onSubmit={submit} className="form-stack">
              <div className="form-grid">
                <Field label="Full name" error={errors.name}>
                  <input
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                </Field>
                <Field label="Email address" error={errors.email}>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                  />
                </Field>
              </div>
              <Field label="Subject" error={errors.subject}>
                <input
                  value={form.subject}
                  onChange={(e) => setForm({ ...form, subject: e.target.value })}
                />
              </Field>
              <Field label="Message" error={errors.message}>
                <textarea
                  rows={6}
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                />
              </Field>
              <Button type="submit">
                Send message <Send size={17} />
              </Button>
            </form>
          )}
        </Card>
        <aside className="contact-panel">
          <span className="large-icon">
            <Phone />
          </span>
          <h2>Fictional support desk</h2>
          <p>For prototype assistance and accessibility questions.</p>
          <dl>
            <div>
              <dt>Phone</dt>
              <dd>1800 123 4567</dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>support@janasevanam.example.test</dd>
            </div>
            <div>
              <dt>Hours</dt>
              <dd>Monday–Friday, 9:00–17:00</dd>
            </div>
            <div>
              <dt>Address</dt>
              <dd>12 Civic Square, Thiruvananthapuram 695001</dd>
            </div>
          </dl>
        </aside>
      </div>
      {toast && (
        <Toast message="Your message was saved successfully." onClose={() => setToast(false)} />
      )}
    </div>
  );
}

export function FaqPage() {
  const items = [
    [
      "How do I submit a grievance?",
      "Register or use the citizen demo account, then choose Submit Grievance. Complete the required fields and review any optional suggestion before submitting.",
    ],
    [
      "What files are allowed?",
      "You may attach one JPG, PNG or PDF file up to 2 MB in this prototype.",
    ],
    [
      "How do I get a reference number?",
      "A reference number in the format CMK-2026-000123 is generated after a successful submission.",
    ],
    [
      "How do I track a grievance?",
      "Use Track Grievance from the public navigation and enter the full reference number. No login is required.",
    ],
    [
      "What do the statuses mean?",
      "Submitted means received; Under Review means CMO review; In Progress means department action; Resolved means the report was accepted; Reopened means the citizen requested another review.",
    ],
    [
      "How long does resolution take?",
      "Time varies by issue. Illustrative due dates are 3 days for High, 7 for Medium and 14 for Low priority.",
    ],
    [
      "What are AI suggestions?",
      "They are editable routing suggestions only. They do not make an official decision, and a human reviewer determines the final category and priority.",
    ],
    [
      "How do I reopen a grievance?",
      "When a grievance is Resolved, open it from the citizen dashboard and choose Reopen grievance. A reason is required.",
    ],
  ].map(([question, answer]) => ({ question, answer }));
  return (
    <div className="container page narrow">
      <PageHeader
        eyebrow="Help centre"
        title="Frequently asked questions"
        description="Answers about submission, tracking, privacy and the human-reviewed workflow."
      />
      <Accordion items={items} />
    </div>
  );
}

export function TrackPage() {
  const params = new URLSearchParams(location.search);
  const [reference, setReference] = useState(params.get("reference") || "CMK-2026-000123");
  const [result, setResult] = useState<api.Grievance | null | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const search = async (e?: FormEvent) => {
    e?.preventDefault();
    setLoading(true);
    setSearched(true);
    setResult(await api.trackGrievance(reference));
    setLoading(false);
  };
  return (
    <div className="container page narrow">
      <PageHeader
        eyebrow="Public tracking"
        title="Track your grievance"
        description="See status and public updates only. Personal details and internal remarks are never shown."
      />
      <Card className="search-card">
        <form onSubmit={search} className="search-row">
          <Field label="Reference number">
            <input
              value={reference}
              onChange={(e) => setReference(e.target.value.toUpperCase())}
              placeholder="CMK-2026-000123"
              pattern="CMK-2026-[0-9]{6}"
            />
          </Field>
          <Button type="submit">
            <Search size={17} /> Track grievance
          </Button>
        </form>
        <small>Reference format: CMK-2026-000123</small>
      </Card>
      {loading && (
        <>
          <WakeBanner />
          <Card>
            <Skeleton rows={5} />
          </Card>
        </>
      )}
      {!loading && searched && result === null && (
        <Card>
          <div className="empty-state">
            <Search size={32} />
            <h2>No grievance found</h2>
            <p>Check the reference number and try again. Try CMK-2026-000123.</p>
          </div>
        </Card>
      )}
      {!loading && result && (
        <Card className="tracking-result">
          <div className="result-head">
            <div>
              <span className="eyebrow">Reference</span>
              <h2>{result.referenceNo}</h2>
              <p>{result.subject}</p>
            </div>
            <StatusBadge status={result.status} />
          </div>
          <div className="detail-grid three">
            <div>
              <span>Assigned department</span>
              <strong>{result.department}</strong>
            </div>
            <div>
              <span>Submitted</span>
              <strong>
                {new Date(result.createdAt).toLocaleDateString("en-IN", { dateStyle: "medium" })}
              </strong>
            </div>
            <div>
              <span>Priority</span>
              <PriorityChip priority={result.priority} />
            </div>
          </div>
          <hr />
          <h3>Public status history</h3>
          <HistoryTimeline history={result.history} publicOnly />
        </Card>
      )}
    </div>
  );
}
