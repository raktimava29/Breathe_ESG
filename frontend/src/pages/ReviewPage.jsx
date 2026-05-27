import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";

const STATUS_OPTIONS = ["", "PENDING", "FLAGGED", "APPROVED", "LOCKED"];

export default function ReviewPage() {
  const { id } = useParams();
  const [records, setRecords] = useState([]);
  const [detail, setDetail] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [analyst, setAnalyst] = useState("j.rivera");
  const [msg, setMsg] = useState("");

  const loadList = () => {
    const q = statusFilter ? `?status=${statusFilter}` : "";
    return api.listRecords(q).then(setRecords);
  };

  useEffect(() => {
    loadList();
  }, [statusFilter]);

  useEffect(() => {
    if (id) {
      api.getRecord(id).then(setDetail).catch(console.error);
    } else {
      setDetail(null);
    }
  }, [id]);

  const act = async (action) => {
    if (!detail) return;
    try {
      const updated = await api.reviewRecord(detail.id, {
        action,
        analyst,
        comment: "",
      });
      setDetail(updated);
      setMsg(`Record ${updated.id} → ${updated.status}`);
      loadList();
    } catch (e) {
      setMsg(e.message);
    }
  };

  return (
    <div className="review-layout">
      <section>
        <h2>Review dashboard</h2>
        <label>
          Status filter{" "}
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s || "All"}
              </option>
            ))}
          </select>
        </label>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Category</th>
              <th>Scope</th>
              <th>Date</th>
              <th>Qty</th>
              <th>Status</th>
              <th>Flags</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id} className={id === String(r.id) ? "selected" : ""}>
                <td>
                  <Link to={`/review/${r.id}`}>{r.id}</Link>
                </td>
                <td>{r.activity_category}</td>
                <td>{r.scope}</td>
                <td>{r.activity_date || "—"}</td>
                <td>
                  {r.canonical_quantity ?? r.distance_km ?? "—"}{" "}
                  {r.canonical_unit || (r.distance_km ? "km" : "")}
                </td>
                <td>
                  <span className={`badge badge-${r.status.toLowerCase()}`}>{r.status}</span>
                </td>
                <td>{r.flag_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <aside className="detail-panel">
        <h3>Record detail</h3>
        {!detail && <p className="muted">Select a record from the table.</p>}
        {detail && (
          <>
            <p>
              <strong>{detail.description}</strong>
            </p>
            <dl className="detail-dl">
              <dt>Status</dt>
              <dd>{detail.status}</dd>
              <dt>Scope / category</dt>
              <dd>
                {detail.scope} / {detail.activity_category}
              </dd>
              <dt>Canonical</dt>
              <dd>
                {detail.canonical_quantity} {detail.canonical_unit}
                {detail.distance_km != null && ` / ${detail.distance_km} km`}
              </dd>
              <dt>Normalization notes</dt>
              <dd>
                <ul>
                  {(detail.normalization_notes || []).map((n) => (
                    <li key={n}>{n}</li>
                  ))}
                  {!detail.normalization_notes?.length && <li>—</li>}
                </ul>
              </dd>
            </dl>

            <h4>Flags</h4>
            <ul className="flags">
              {(detail.flags || []).map((f) => (
                <li key={f.id}>
                  <strong>{f.rule_code}</strong> ({f.severity}): {f.message}
                </li>
              ))}
              {!detail.flags?.length && <li className="muted">No flags</li>}
            </ul>

            <h4>Raw payload</h4>
            <pre className="raw-json">{JSON.stringify(detail.raw_record?.payload, null, 2)}</pre>

            <h4>Actions</h4>
            <label>
              Analyst <input value={analyst} onChange={(e) => setAnalyst(e.target.value)} />
            </label>
            <div className="actions">
              <button type="button" onClick={() => act("approve")} disabled={detail.status === "LOCKED"}>
                Approve
              </button>
              <button type="button" onClick={() => act("reject")} disabled={detail.status === "LOCKED"}>
                Send to pending
              </button>
              <button
                type="button"
                onClick={() => act("lock")}
                disabled={detail.status !== "APPROVED"}
              >
                Lock (audit)
              </button>
            </div>
            {msg && <p className="message">{msg}</p>}

            <h4>Review history</h4>
            <ul>
              {(detail.decisions || []).map((d) => (
                <li key={d.id}>
                  {d.created_at}: {d.previous_status} → {d.new_status} by {d.analyst}
                </li>
              ))}
            </ul>
          </>
        )}
      </aside>
    </div>
  );
}
