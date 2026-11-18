export type Role = "citizen" | "cmo_admin" | "officer";
export type Status = "Submitted" | "Under Review" | "In Progress" | "Resolved" | "Reopened";
export type Priority = "Low" | "Medium" | "High";

export interface HistoryEntry {
  timestamp: string;
  actorName: string;
  actorRole: string;
  fromStatus?: Status;
  toStatus: Status;
  remark: string;
  visibility: "Public" | "Internal";
}

export interface Grievance {
  id: string;
  referenceNo: string;
  citizenName: string;
  district: string;
  category: string;
  subject: string;
  description: string;
  priority: Priority;
  status: Status;
  dueAt: string;
  escalated: boolean;
  department: string;
  officer?: string;
  aiSummary: string;
  createdAt: string;
  updatedAt: string;
  assignmentState: "Assigned" | "Report Submitted" | "Returned" | "Closed";
  attachments?: string[];
  report?: string;
  reportAttachments?: string[];
  publicRemarks?: string[];
  history: HistoryEntry[];
}

export const districts = [
  "Thiruvananthapuram",
  "Kollam",
  "Pathanamthitta",
  "Alappuzha",
  "Kottayam",
  "Idukki",
  "Ernakulam",
  "Thrissur",
  "Palakkad",
  "Malappuram",
  "Kozhikode",
  "Wayanad",
  "Kannur",
  "Kasaragod",
];

export const categories = [
  "Roads and Infrastructure",
  "Healthcare",
  "Education",
  "Water Supply",
  "Electricity",
  "Waste and Sanitation",
  "Public Distribution",
  "Land and Revenue",
  "Transport",
  "Other",
];

export const statuses: Status[] = [
  "Submitted",
  "Under Review",
  "In Progress",
  "Resolved",
  "Reopened",
];

export const departments = [
  { name: "Public Works", description: "Roads, bridges and public infrastructure." },
  { name: "Health and Family Welfare", description: "Public health facilities and services." },
  { name: "General Education", description: "Schools and educational administration." },
  { name: "Water Resources", description: "Water supply, irrigation and conservation." },
  { name: "Electricity", description: "Power supply and electrical infrastructure." },
  { name: "Local Self Government", description: "Municipal and panchayat public services." },
  { name: "Civil Supplies", description: "Ration cards and public distribution." },
  { name: "Revenue", description: "Land records, certificates and revenue matters." },
  { name: "Transport", description: "Public transport and road safety." },
  { name: "Social Justice", description: "Inclusive welfare and social support." },
];

export const API_BASE = (
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" && window.location.hostname !== "localhost"
    ? "/api"
    : "http://localhost:8000/api")
).replace(/\/$/, "");

export async function checkServerHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("token");
  const headers = new Headers(options.headers || {});
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = `Request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return res.json() as Promise<T>;
}

// ------------------- MOCK FALLBACK DATA & ENGINE -------------------
const now = new Date();
const days = (n: number) => new Date(now.getTime() + n * 86400000).toISOString();
const ago = (n: number) => new Date(now.getTime() - n * 86400000).toISOString();

const subjects = [
  ["Damaged road near the market junction", "Roads and Infrastructure", "Public Works", "Ernakulam"],
  ["Primary health centre without a doctor in the evening", "Healthcare", "Health and Family Welfare", "Wayanad"],
  ["Irregular drinking water supply for two weeks", "Water Supply", "Water Resources", "Kozhikode"],
  ["Streetlights not working on the school road", "Electricity", "Electricity", "Thrissur"],
  ["Delay in ration card correction", "Public Distribution", "Civil Supplies", "Kollam"],
  ["Unsafe pedestrian crossing near college", "Transport", "Transport", "Kottayam"],
  ["Waste collection missed for several days", "Waste and Sanitation", "Local Self Government", "Alappuzha"],
  ["School classroom roof needs repair", "Education", "General Education", "Palakkad"],
  ["Delay in updating land tax records", "Land and Revenue", "Revenue", "Idukki"],
  ["Accessible ramp needed at community hall", "Other", "Social Justice", "Kannur"],
  ["Low water pressure in hillside ward", "Water Supply", "Water Resources", "Malappuram"],
  ["Potholes on the bus route", "Roads and Infrastructure", "Public Works", "Kasaragod"],
] as const;

const grievanceStatuses: Status[] = [
  "Submitted", "Under Review", "In Progress", "Resolved", "Reopened",
  "Resolved", "In Progress", "Under Review", "Resolved", "Submitted", "In Progress", "Resolved"
];
const priorities: Priority[] = [
  "High", "Medium", "High", "Medium", "Low", "High", "Medium", "High", "Low", "Medium", "Low", "Medium"
];

let mockGrievances: Grievance[] = subjects.map((item, index) => {
  const status = grievanceStatuses[index];
  const createdAt = ago(18 - index);
  const dueAt = index === 1 || index === 6 ? ago(index + 1) : days((index % 6) + 1);
  const history: HistoryEntry[] = [
    {
      timestamp: createdAt,
      actorName: "Portal system",
      actorRole: "System",
      toStatus: "Submitted",
      remark: "Grievance submitted and reference number generated.",
      visibility: "Public",
    },
  ];
  if (status !== "Submitted")
    history.push({
      timestamp: ago(13 - index),
      actorName: "Ananya Menon",
      actorRole: "CMO reviewer",
      fromStatus: "Submitted",
      toStatus: "Under Review",
      remark: "Grievance reviewed and routed for appropriate action.",
      visibility: "Public",
    });
  if (["In Progress", "Resolved", "Reopened"].includes(status))
    history.push({
      timestamp: ago(9 - Math.min(index, 8)),
      actorName: "Ananya Menon",
      actorRole: "CMO reviewer",
      fromStatus: "Under Review",
      toStatus: "In Progress",
      remark: `Forwarded to ${item[2]} for action.`,
      visibility: "Public",
    });
  if (status === "Resolved" || status === "Reopened")
    history.push({
      timestamp: ago(2),
      actorName: "Vivek Nair",
      actorRole: "CMO reviewer",
      fromStatus: "In Progress",
      toStatus: "Resolved",
      remark: "Department report reviewed and resolution confirmed.",
      visibility: "Public",
    });
  if (status === "Reopened")
    history.push({
      timestamp: ago(1),
      actorName: "Meera Krishnan",
      actorRole: "Citizen",
      fromStatus: "Resolved",
      toStatus: "Reopened",
      remark: "The issue recurred after the reported action.",
      visibility: "Public",
    });
  return {
    id: String(index + 1),
    referenceNo: `CMK-2026-${String(123 + index).padStart(6, "0")}`,
    citizenName: index < 5 ? "Meera Krishnan" : ["Arun Das", "Nila Thomas", "Devika Raj", "Fahad Ali"][index % 4],
    district: item[3],
    category: item[1],
    subject: item[0],
    description: `${item[0]} has affected residents in the area. We request an inspection and a clear update on the action planned.`,
    priority: priorities[index],
    status,
    dueAt,
    escalated: index === 1,
    department: item[2],
    officer: index % 2 ? "Ravi Kumar" : "Lakshmi Nair",
    aiSummary: `Residents report ${item[0].toLowerCase()}. A department inspection and timely public update may be appropriate.`,
    createdAt,
    updatedAt: ago(index % 5),
    assignmentState: status === "Resolved" ? "Closed" : index === 2 ? "Report Submitted" : index === 4 ? "Returned" : "Assigned",
    attachments: index === 0 ? ["market-road-photo.jpg"] : [],
    report: index === 2 ? "Inspection completed. Supply valve timing was corrected and service has been monitored for three days." : undefined,
    reportAttachments: index === 2 ? ["action-taken-report.pdf"] : [],
    publicRemarks: index > 1 ? ["Your grievance has been shared with the responsible department."] : [],
    history,
  };
});

// ------------------- API FUNCTIONS WITH DUAL-MODE RESILIENCE -------------------

export async function register(data: { fullName: string; email: string; mobile?: string; password?: string }) {
  try {
    const res = await apiFetch<{ token: string; user: { id: number; name: string; email: string; role: Role } }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        name: data.fullName,
        email: data.email,
        mobile: data.mobile || "9847000000",
        password: data.password || "Demo@123",
        role: "citizen",
      }),
    });
    if (res.token) localStorage.setItem("token", res.token);
    return res;
  } catch (err) {
    console.warn("Backend offline or error, using local fallback registration:", err);
    return { id: "citizen-new", role: "citizen" as Role, token: "demo-citizen-token", user: { name: data.fullName, email: data.email, role: "citizen" as Role } };
  }
}

export async function login(email: string, password = "Demo@123") {
  try {
    const res = await apiFetch<{ token: string; user: { id: number; name: string; email: string; role: Role } }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (res.token) localStorage.setItem("token", res.token);
    return res;
  } catch (err) {
    console.warn("Backend offline or error, using local fallback login:", err);
    const role: Role = email.includes("admin") ? "cmo_admin" : email.includes("officer") ? "officer" : "citizen";
    const name = role === "citizen" ? "Meera Krishnan" : role === "cmo_admin" ? "Ananya Menon" : "Ravi Kumar";
    const token = `demo-${role}`;
    localStorage.setItem("token", token);
    return {
      token,
      user: { name, email, role },
    };
  }
}

export async function me(role: Role = "citizen") {
  try {
    const res = await apiFetch<{ id: number; name: string; email: string; role: Role }>("/auth/me");
    return { name: res.name, role: res.role };
  } catch {
    return {
      name: role === "citizen" ? "Meera Krishnan" : role === "cmo_admin" ? "Ananya Menon" : "Ravi Kumar",
      role,
    };
  }
}

export async function getDepartments() {
  try {
    return await apiFetch<typeof departments>("/departments");
  } catch {
    return departments;
  }
}

export async function getPublicStats() {
  try {
    return await apiFetch<{ total: number; resolved: number; inProgress: number; averageDays: number }>("/stats/public");
  } catch {
    return { total: 1248, resolved: 914, inProgress: 246, averageDays: 6.4 };
  }
}

export async function getMeta() {
  try {
    return await apiFetch<{ districts: string[]; categories: string[]; statuses: Status[] }>("/meta");
  } catch {
    return { districts, categories, statuses };
  }
}

export async function submitContact(data: Record<string, string>) {
  try {
    return await apiFetch<{ id: number; name: string; email: string; subject: string; message: string }>("/contact", {
      method: "POST",
      body: JSON.stringify({
        name: data.name || "Citizen",
        email: data.email || "citizen@example.test",
        subject: data.subject || "Contact inquiry",
        message: data.message || "Message details",
      }),
    });
  } catch {
    return { id: "contact-1042", ...data };
  }
}

export async function trackGrievance(referenceNo: string) {
  try {
    return await apiFetch<Grievance>(`/track/${encodeURIComponent(referenceNo)}`);
  } catch {
    return mockGrievances.find((item) => item.referenceNo.toLowerCase() === referenceNo.toLowerCase()) ?? null;
  }
}

export async function analyzeGrievance(description: string, district: string) {
  try {
    const res = await apiFetch<{
      category: string;
      department: string;
      priority: Priority;
      summary: string;
      confidence: number;
      reasoning: string;
      source: string;
      model: string;
      duplicate_candidates?: unknown[];
    }>("/ai/analyze", {
      method: "POST",
      body: JSON.stringify({ description, district }),
    });

    return {
      category: res.category,
      department: res.department,
      priority: res.priority,
      summary: res.summary,
      confidence: Math.round(res.confidence > 1 ? res.confidence : res.confidence * 100),
      reasoning: res.reasoning,
      source: res.source,
      duplicateCandidates: (res.duplicate_candidates && res.duplicate_candidates.length > 0) ? [mockGrievances[2]] : [],
    };
  } catch (err) {
    console.warn("AI endpoint offline, falling back to local heuristic:", err);
    const water = /water|supply|pipe/i.test(description);
    const road = /road|pothole|bridge/i.test(description);
    return {
      category: water ? "Water Supply" : road ? "Roads and Infrastructure" : "Other",
      department: water ? "Water Resources" : road ? "Public Works" : "Local Self Government",
      priority: /unsafe|danger|urgent/i.test(description) ? ("High" as Priority) : ("Medium" as Priority),
      summary: `A resident of ${district || "the selected district"} reports a local service issue requiring departmental review. The description suggests an inspection and a public update may be helpful.`,
      confidence: 84,
      reasoning: "Suggested from keyword patterns and district context (Fallback Engine).",
      duplicateCandidates: description.length > 40 ? [mockGrievances[2]] : [],
      source: "fallback",
    };
  }
}

export async function submitGrievance(data: Partial<Grievance>, file?: File | null) {
  try {
    const formData = new FormData();
    formData.append("district", data.district || "Ernakulam");
    formData.append("category", data.category || "Roads and Infrastructure");
    formData.append("subject", data.subject || "Grievance Report");
    formData.append("description", data.description || "Details of the issue");
    formData.append("priority", data.priority || "Medium");
    if (file) {
      formData.append("file", file);
    }

    const res = await apiFetch<Grievance>("/grievances", {
      method: "POST",
      body: formData,
    });
    return res;
  } catch (err) {
    console.warn("Submit grievance backend offline, using local mock store:", err);
    const item: Grievance = {
      ...mockGrievances[0],
      ...data,
      id: String(mockGrievances.length + 1),
      referenceNo: `CMK-2026-${String(123 + mockGrievances.length).padStart(6, "0")}`,
      citizenName: "Meera Krishnan",
      status: "Submitted",
      priority: data.priority ?? "Medium",
      dueAt: days(data.priority === "High" ? 3 : data.priority === "Low" ? 14 : 7),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      escalated: false,
      assignmentState: "Assigned",
      department: data.department ?? "Pending CMO review",
      history: [
        {
          timestamp: new Date().toISOString(),
          actorName: "Portal system",
          actorRole: "System",
          toStatus: "Submitted",
          remark: "Grievance submitted and reference number generated.",
          visibility: "Public",
        },
      ],
    };
    mockGrievances = [item, ...mockGrievances];
    return item;
  }
}

export async function getMyGrievances() {
  try {
    return await apiFetch<Grievance[]>("/grievances/mine");
  } catch {
    return mockGrievances.filter((g) => g.citizenName === "Meera Krishnan");
  }
}

export async function getGrievance(id: string) {
  try {
    return await apiFetch<Grievance>(`/grievances/${id}`);
  } catch {
    return mockGrievances.find((g) => g.id === id) ?? null;
  }
}

export async function submitFeedback(id: string, rating: number, comment: string) {
  try {
    return await apiFetch<{ id: string; rating: number; comment: string; saved: boolean }>(`/grievances/${id}/feedback`, {
      method: "POST",
      body: JSON.stringify({ rating, comment }),
    });
  } catch {
    return { id, rating, comment, saved: true };
  }
}

export async function reopenGrievance(id: string, reason: string) {
  try {
    return await apiFetch<Grievance>(`/grievances/${id}/reopen`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
  } catch {
    const g = mockGrievances.find((item) => item.id === id);
    if (g) {
      g.status = "Reopened";
      g.history.push({
        timestamp: new Date().toISOString(),
        actorName: "Meera Krishnan",
        actorRole: "Citizen",
        fromStatus: "Resolved",
        toStatus: "Reopened",
        remark: reason,
        visibility: "Public",
      });
    }
    return g;
  }
}

export async function getCmoGrievances(filters: Record<string, unknown> = {}, page = 1) {
  try {
    const params = new URLSearchParams();
    if (filters.status) params.set("status", String(filters.status));
    if (filters.search) params.set("search", String(filters.search));
    params.set("page", String(page));
    params.set("limit", "8");

    return await apiFetch<{ items: Grievance[]; total: number; page: number }>(`/cmo/grievances?${params.toString()}`);
  } catch {
    let result = [...mockGrievances];
    if (filters.status) result = result.filter((g) => g.status === filters.status);
    if (filters.search)
      result = result.filter((g) =>
        g.referenceNo.toLowerCase().includes(String(filters.search).toLowerCase()),
      );
    return { items: result.slice((page - 1) * 8, page * 8), total: result.length, page };
  }
}

export async function getCmoGrievance(id: string) {
  try {
    return await apiFetch<Grievance>(`/cmo/grievances/${id}`);
  } catch {
    return getGrievance(id);
  }
}

export async function reviewGrievance(id: string, data: Partial<Grievance>) {
  try {
    return await apiFetch<Grievance>(`/cmo/grievances/${id}/review`, {
      method: "PATCH",
      body: JSON.stringify({
        category: data.category || "Roads and Infrastructure",
        priority: data.priority || "Medium",
        remark: "CMO confirmed priority and category.",
      }),
    });
  } catch {
    return updateMock(id, { ...data, status: "Under Review" });
  }
}

export async function assignGrievance(id: string, department: string, officer: string) {
  try {
    return await apiFetch<Grievance>(`/cmo/grievances/${id}/assign`, {
      method: "POST",
      body: JSON.stringify({
        department_name: department,
        officer_name: officer,
        remark: `Forwarded to ${department} for departmental action.`,
      }),
    });
  } catch {
    return updateMock(id, { department, officer, status: "In Progress" });
  }
}

export async function addRemark(id: string, remark: string, visibility: "Public" | "Internal") {
  try {
    return await apiFetch<{ id: string; remark: string; visibility: string; saved: boolean }>(`/cmo/grievances/${id}/remarks`, {
      method: "POST",
      body: JSON.stringify({ remark, visibility }),
    });
  } catch {
    return { id, remark, visibility, saved: true };
  }
}

export async function escalateGrievance(id: string) {
  try {
    return await apiFetch<Grievance>(`/cmo/grievances/${id}/escalate`, {
      method: "POST",
    });
  } catch {
    return updateMock(id, { escalated: true });
  }
}

export async function decideReport(id: string, decision: "accept" | "return", remark = "") {
  try {
    // Look up assignment id for this grievance or use id directly
    return await apiFetch<Grievance>(`/cmo/reports/${id}/decision`, {
      method: "POST",
      body: JSON.stringify({ decision, remark }),
    });
  } catch {
    return updateMock(id, {
      status: decision === "accept" ? "Resolved" : "In Progress",
      assignmentState: decision === "accept" ? "Closed" : "Returned",
      publicRemarks: remark ? [remark] : [],
    });
  }
}

export interface CmoStats {
  total: number;
  pending: number;
  resolved: number;
  overdue: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_district: { name: string; count: number }[];
  by_department: { name: string; count: number }[];
}

export async function getCmoStats(): Promise<CmoStats> {
  try {
    return await apiFetch<CmoStats>("/cmo/stats");
  } catch {
    const by_status: Record<string, number> = {};
    for (const s of ["Submitted", "Under Review", "In Progress", "Resolved", "Reopened"]) {
      by_status[s] = mockGrievances.filter((g) => g.status === s).length;
    }
    return {
      total: mockGrievances.length,
      pending: mockGrievances.filter((g) => g.status !== "Resolved").length,
      resolved: mockGrievances.filter((g) => g.status === "Resolved").length,
      overdue: mockGrievances.filter(isOverdue).length,
      by_status,
      by_priority: { High: 4, Medium: 5, Low: 3 },
      by_district: departments.slice(0, 6).map((d, i) => ({ name: d.name.substring(0, 6), count: 2 + i })),
      by_department: departments.map((d, i) => ({ name: d.name, count: 1 + i })),
    };
  }
}

export async function getOfficerGrievances() {
  try {
    return await apiFetch<Grievance[]>("/officer/grievances");
  } catch {
    return mockGrievances.filter((g) => g.department === "Water Resources" || g.department === "Public Works" || g.officer === "Ravi Kumar");
  }
}

export async function getOfficerGrievance(id: string) {
  try {
    return await apiFetch<Grievance>(`/officer/grievances/${id}`);
  } catch {
    return getGrievance(id);
  }
}

export async function addProgress(id: string, remark: string) {
  try {
    return await apiFetch<{ id: string; remark: string; saved: boolean }>(`/officer/grievances/${id}/progress`, {
      method: "POST",
      body: JSON.stringify({ remark, visibility: "Public" }),
    });
  } catch {
    return { id, remark, saved: true };
  }
}

export async function submitActionReport(id: string, report: string) {
  try {
    const formData = new FormData();
    formData.append("report", report);
    return await apiFetch<Grievance>(`/officer/grievances/${id}/action-report`, {
      method: "POST",
      body: formData,
    });
  } catch {
    return updateMock(id, { report, assignmentState: "Report Submitted" });
  }
}

function updateMock(id: string, changes: Partial<Grievance>) {
  const item = mockGrievances.find((g) => g.id === id);
  if (item) Object.assign(item, changes, { updatedAt: new Date().toISOString() });
  return item;
}

export function isOverdue(g: Grievance) {
  return g.status !== "Resolved" && new Date(g.dueAt) < new Date();
}
