import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";
import { Check, Eye, EyeOff, LockKeyhole, ShieldCheck, UserRound } from "lucide-react";
import * as api from "../api";
import { Button, Card, Field, PageHeader } from "../components";

export function LoginPage() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const fill = (role: api.Role) =>
    setForm({
      email:
        role === "cmo_admin"
          ? "admin@janasevanam.example.test"
          : role === "officer"
            ? "officer@janasevanam.example.test"
            : "citizen@janasevanam.example.test",
      password: "Demo@123",
    });
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.email || !form.password) {
      setError("Enter both email and password.");
      return;
    }
    const response = await api.login(form.email, form.password);
    localStorage.setItem("role", response.user.role);
    localStorage.setItem("name", response.user.name);
    navigate(
      response.user.role === "cmo_admin"
        ? "/cmo"
        : response.user.role === "officer"
          ? "/officer"
          : "/citizen",
    );
  };
  return (
    <div className="auth-page">
      <div className="auth-copy">
        <span className="large-icon inverse">
          <ShieldCheck />
        </span>
        <h1>Welcome back</h1>
        <p>
          Sign in to view assigned work, manage your grievances, or review the fictional CMO
          workflow.
        </p>
        <ul>
          <li>
            <Check /> Role-aware workspaces
          </li>
          <li>
            <Check /> Clear public and internal visibility
          </li>
          <li>
            <Check /> Human-controlled decisions
          </li>
        </ul>
      </div>
      <Card className="auth-card">
        <PageHeader
          eyebrow="Secure demo access"
          title="Log in"
          description="Use any demo account below. No real credentials are required."
        />
        <form onSubmit={submit} className="form-stack">
          <Field label="Email address">
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="name@example.test"
            />
          </Field>
          <Field label="Password">
            <div className="password-field">
              <input
                type={show ? "text" : "password"}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
              <button
                type="button"
                onClick={() => setShow(!show)}
                aria-label={show ? "Hide password" : "Show password"}
              >
                {show ? <EyeOff /> : <Eye />}
              </button>
            </div>
          </Field>
          {error && <p className="form-error">{error}</p>}
          <Button type="submit">Log in</Button>
        </form>
        <div className="demo-panel">
          <strong>Demo accounts</strong>
          <p>Fill the form with a fictional account:</p>
          <div>
            <button onClick={() => fill("citizen")}>
              <UserRound />
              Citizen
            </button>
            <button onClick={() => fill("cmo_admin")}>
              <ShieldCheck />
              CMO Admin
            </button>
            <button onClick={() => fill("officer")}>
              <LockKeyhole />
              Officer
            </button>
          </div>
        </div>
        <p className="auth-switch">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </Card>
    </div>
  );
}

export function RegisterPage() {
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    mobile: "",
    password: "",
    confirm: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const navigate = useNavigate();
  const strength = Math.min(
    4,
    [
      form.password.length >= 8,
      /[A-Z]/.test(form.password),
      /\d/.test(form.password),
      /[^A-Za-z0-9]/.test(form.password),
    ].filter(Boolean).length,
  );
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const next: Record<string, string> = {};
    if (form.fullName.trim().length < 3) next.fullName = "Enter your full name.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) next.email = "Enter a valid email address.";
    if (!/^[6-9]\d{9}$/.test(form.mobile))
      next.mobile = "Enter a valid 10-digit Indian mobile number.";
    if (strength < 3) next.password = "Use 8+ characters with uppercase, number and symbol.";
    if (form.password !== form.confirm) next.confirm = "Passwords do not match.";
    setErrors(next);
    if (Object.keys(next).length) return;
    await api.register({ fullName: form.fullName, email: form.email });
    navigate("/login");
  };
  return (
    <div className="container page narrow">
      <Card className="auth-card register-card">
        <PageHeader
          eyebrow="Citizen registration"
          title="Create your account"
          description="Use fictional details ending in example.test for this recruitment prototype."
        />
        <form onSubmit={submit} className="form-stack">
          <Field label="Full name" error={errors.fullName}>
            <input
              value={form.fullName}
              onChange={(e) => setForm({ ...form, fullName: e.target.value })}
            />
          </Field>
          <Field label="Email address" error={errors.email}>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="name@example.test"
            />
          </Field>
          <Field label="Mobile number" error={errors.mobile}>
            <div className="prefix-input">
              <span>+91</span>
              <input
                inputMode="numeric"
                maxLength={10}
                value={form.mobile}
                onChange={(e) => setForm({ ...form, mobile: e.target.value.replace(/\D/g, "") })}
              />
            </div>
          </Field>
          <Field label="Password" error={errors.password}>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
            <div className="strength" aria-label={`Password strength ${strength} of 4`}>
              {[1, 2, 3, 4].map((i) => (
                <span key={i} className={i <= strength ? "filled" : ""} />
              ))}
            </div>
            <small className="hint">
              {["Very weak", "Weak", "Fair", "Strong", "Very strong"][strength]}
            </small>
          </Field>
          <Field label="Confirm password" error={errors.confirm}>
            <input
              type="password"
              value={form.confirm}
              onChange={(e) => setForm({ ...form, confirm: e.target.value })}
            />
          </Field>
          <Button type="submit">Create account</Button>
        </form>
        <p className="auth-switch">
          Already registered? <Link to="/login">Log in</Link>
        </p>
      </Card>
    </div>
  );
}
