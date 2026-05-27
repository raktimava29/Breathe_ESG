import { Link, Route, Routes } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ReviewPage from "./pages/ReviewPage";
import AuditPage from "./pages/AuditPage";
import TenantBar from "./components/TenantBar";

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>Breathe ESG</h1>
        <nav>
          <Link to="/">Ingest</Link>
          <Link to="/review">Review</Link>
          <Link to="/audit">Audit</Link>
        </nav>
        <TenantBar />
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/review/:id" element={<ReviewPage />} />
          <Route path="/audit" element={<AuditPage />} />
        </Routes>
      </main>
    </div>
  );
}
