import { useEffect, useState } from "react";
import { api } from "../api";

export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [entityType, setEntityType] = useState("");
  const [entityId, setEntityId] = useState("");

  const load = () => {
    const params = new URLSearchParams();
    if (entityType) params.set("entity_type", entityType);
    if (entityId) params.set("entity_id", entityId);
    const q = params.toString() ? `?${params}` : "";
    api.listAudit(q).then(setLogs);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <h2>Audit history</h2>
      <p className="muted">Append-only event log for ingestion and review actions.</p>
      <div className="filters">
        <input
          placeholder="Entity type (e.g. NormalizedEmissionRecord)"
          value={entityType}
          onChange={(e) => setEntityType(e.target.value)}
        />
        <input
          placeholder="Entity ID"
          value={entityId}
          onChange={(e) => setEntityId(e.target.value)}
        />
        <button type="button" onClick={load}>
          Filter
        </button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Entity</th>
            <th>Action</th>
            <th>Actor</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((l) => (
            <tr key={l.id}>
              <td>{new Date(l.created_at).toLocaleString()}</td>
              <td>
                {l.entity_type} #{l.entity_id}
              </td>
              <td>{l.action}</td>
              <td>{l.actor || "—"}</td>
              <td>
                <code>{JSON.stringify(l.after_state || l.metadata)}</code>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
