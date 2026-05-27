const API_BASE = import.meta.env.VITE_API_BASE || "/api";

let tenantSlug = localStorage.getItem("tenantSlug") || "acme-corp";

export function setTenantSlug(slug) {
  tenantSlug = slug;
  localStorage.setItem("tenantSlug", slug);
}

export function getTenantSlug() {
  return tenantSlug;
}

async function request(path, options = {}) {
  const headers = {
    "X-Tenant-Slug": tenantSlug,
    ...(options.headers || {}),
  };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || JSON.stringify(err));
  }
  if (res.status === 204) return null;
  return res.json();
}

/** DRF PageNumberPagination returns { count, next, previous, results }. */
function asList(data) {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
}

export const api = {
  listTenants: () => request("/tenants/").then(asList),
  listSources: () => request("/sources/").then(asList),
  listBatches: () => request("/batches/").then(asList),
  listRecords: (params = "") => request(`/records/${params}`).then(asList),
  getRecord: (id) => request(`/records/${id}/`),
  reviewRecord: (id, body) =>
    request(`/records/${id}/review/`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listAudit: (params = "") => request(`/audit/${params}`).then(asList),
  upload: (category, file, uploadedBy) => {
    const form = new FormData();
    form.append("file", file);
    form.append("uploaded_by", uploadedBy);
    return request(`/ingest/${category}/`, { method: "POST", body: form, headers: {} });
  },
  syncTravel: (uploadedBy) =>
    request("/ingest/travel/sync/", {
      method: "POST",
      body: JSON.stringify({ uploaded_by: uploadedBy, limit: 10 }),
    }),
};
