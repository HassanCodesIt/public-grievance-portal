import { Navigate, createBrowserRouter } from "react-router";
import type { ReactNode } from "react";
import type { Role } from "./api";
import { AppShell, Card } from "./components";
import { LoginPage, RegisterPage } from "./pages/AuthPages";
import { CitizenDashboard, CitizenDetail, SubmitGrievancePage } from "./pages/CitizenPages";
import { CmoDetail, CmoOverview } from "./pages/CmoPages";
import { OfficerDetail, OfficerOverview } from "./pages/OfficerPages";
import {
  AboutPage,
  ContactPage,
  DepartmentsPage,
  FaqPage,
  HomePage,
  HowItWorksPage,
  TrackPage,
} from "./pages/PublicPages";

function Protected({ role, children }: { role: Role; children: ReactNode }) {
  return localStorage.getItem("role") === role ? children : <Navigate to="/login" replace />;
}
function NotFound() {
  return (
    <div className="container page narrow">
      <Card>
        <div className="empty-state">
          <strong className="error-code">404</strong>
          <h1>Page not found</h1>
          <p>The page may have moved or the address may be incorrect.</p>
          <a className="btn primary" href="/">
            Return home
          </a>
        </div>
      </Card>
    </div>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    Component: AppShell,
    children: [
      { index: true, Component: HomePage },
      { path: "about", Component: AboutPage },
      { path: "how-it-works", Component: HowItWorksPage },
      { path: "departments", Component: DepartmentsPage },
      { path: "contact", Component: ContactPage },
      { path: "faq", Component: FaqPage },
      { path: "track", Component: TrackPage },
      { path: "login", Component: LoginPage },
      { path: "register", Component: RegisterPage },
      {
        path: "citizen",
        element: (
          <Protected role="citizen">
            <CitizenDashboard />
          </Protected>
        ),
      },
      {
        path: "citizen/submit",
        element: (
          <Protected role="citizen">
            <SubmitGrievancePage />
          </Protected>
        ),
      },
      {
        path: "citizen/grievances/:id",
        element: (
          <Protected role="citizen">
            <CitizenDetail />
          </Protected>
        ),
      },
      {
        path: "cmo",
        element: (
          <Protected role="cmo_admin">
            <CmoOverview />
          </Protected>
        ),
      },
      {
        path: "cmo/grievances/:id",
        element: (
          <Protected role="cmo_admin">
            <CmoDetail />
          </Protected>
        ),
      },
      {
        path: "officer",
        element: (
          <Protected role="officer">
            <OfficerOverview />
          </Protected>
        ),
      },
      {
        path: "officer/grievances/:id",
        element: (
          <Protected role="officer">
            <OfficerDetail />
          </Protected>
        ),
      },
      { path: "*", Component: NotFound },
    ],
  },
]);
