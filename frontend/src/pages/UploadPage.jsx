import { useEffect, useState } from "react";
import { api } from "../api";

export default function UploadPage() {
  const [batches, setBatches] = useState([]);
  const [message, setMessage] = useState("");
  const [analyst, setAnalyst] = useState("j.rivera");
  const [loading, setLoading] = useState(false);

  const refresh = () => api.listBatches().then(setBatches).catch(console.error);

  useEffect(() => {
    refresh();
  }, []);

  const upload = async (category, file) => {
    setLoading(true);
    setMessage("");
    try {
      const batch = await api.upload(category, file, analyst);
      setMessage(`Batch ${batch.id} completed: ${batch.record_count} records (${batch.status})`);
      refresh();
    } catch (e) {
      setMessage(e.message);
    } finally {
      setLoading(false);
    }
  };

  const syncTravel = async () => {
    setLoading(true);
    setMessage("");
    try {
      const batch = await api.syncTravel(analyst);
      setMessage(`Travel sync batch ${batch.id}: ${batch.record_count} records`);
      refresh();
    } catch (e) {
      setMessage(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Data ingestion</h2>
      <p className="muted">
        Upload SAP or utility CSV exports, or pull mock corporate travel API data.
        Raw payloads are preserved; normalization runs in the pipeline.
      </p>

      <label>
        Analyst ID{" "}
        <input value={analyst} onChange={(e) => setAnalyst(e.target.value)} />
      </label>

      <div className="upload-grid">
        <UploadCard
          title="SAP fuel / procurement"
          category="SAP"
          accept=".csv"
          disabled={loading}
          onFile={(f) => upload("SAP", f)}
        />
        <UploadCard
          title="Utility electricity"
          category="UTILITY"
          accept=".csv"
          disabled={loading}
          onFile={(f) => upload("UTILITY", f)}
        />
        <div className="card">
          <h3>Corporate travel (mock API)</h3>
          <p className="muted">Simulates Concur-style booking export pull.</p>
          <button type="button" disabled={loading} onClick={syncTravel}>
            Sync travel bookings
          </button>
        </div>
      </div>

      {message && <p className="message">{message}</p>}

      <h3>Recent batches</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Source</th>
            <th>Status</th>
            <th>Records</th>
            <th>File</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {batches.map((b) => (
            <tr key={b.id}>
              <td>{b.id}</td>
              <td>{b.data_source?.category}</td>
              <td>{b.status}</td>
              <td>{b.record_count}</td>
              <td>{b.filename || "—"}</td>
              <td>{new Date(b.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function UploadCard({ title, category, accept, onFile, disabled }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p className="muted">Category: {category}</p>
      <input
        type="file"
        accept={accept}
        disabled={disabled}
        onChange={(e) => e.target.files[0] && onFile(e.target.files[0])}
      />
    </div>
  );
}
