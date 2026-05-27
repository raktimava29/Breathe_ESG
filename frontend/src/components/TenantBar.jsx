import { useEffect, useState } from "react";
import { api, getTenantSlug, setTenantSlug } from "../api";

export default function TenantBar() {
  const [tenants, setTenants] = useState([]);
  const [slug, setSlug] = useState(getTenantSlug());

  useEffect(() => {
    api.listTenants().then(setTenants).catch(console.error);
  }, []);

  const onChange = (e) => {
    const v = e.target.value;
    setSlug(v);
    setTenantSlug(v);
    window.location.reload();
  };

  return (
    <label className="tenant-bar">
      Tenant{" "}
      <select value={slug} onChange={onChange}>
        {tenants.map((t) => (
          <option key={t.id} value={t.slug}>
            {t.name}
          </option>
        ))}
        {!tenants.length && <option value={slug}>{slug}</option>}
      </select>
    </label>
  );
}
