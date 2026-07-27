// PHASE 6: REACT DASHBOARD (with cross-filtering)
// Location: frontend/Dashboard.jsx
// Assumes FastAPI backend (Phase 5) running at http://localhost:8000
// Requires: npm install recharts
//
// HOW CROSS-FILTERING WORKS:
// Clicking a bar in "Profit by Region" sets a region filter. Every OTHER
// chart (trend, sales method, top products, summary cards) re-fetches with
// that filter applied. The region chart itself stays showing all regions
// (so you can always click a different one, or click the same bar again
// to clear the filter).

import { useEffect, useState } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from "recharts";

// Get API base URL from environment or derive it intelligently
const getAPIBase = () => {
  // If explicitly set in environment (Docker/Railway), use it
  if (import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE;
  }
  
  // For local development
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    return "http://localhost:8000";
  }
  
  // In production, if they are served from same host/port (e.g. behind proxy/same Railway service),
  // we can use a relative URL (empty string) so the browser targets the same host.
  // If they are separate apps, we fall back to relative paths.
  return "";
};

const getCleanedAPIBase = () => {
  const base = getAPIBase();
  return base.endsWith("/") ? base.slice(0, -1) : base;
};

const API_BASE = getCleanedAPIBase();

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [byRegion, setByRegion] = useState([]);
  const [bySalesMethod, setBySalesMethod] = useState([]);
  const [topProducts, setTopProducts] = useState([]);

  // The active cross-filters. null = "no filter on this dimension".
  const [filters, setFilters] = useState({
    region: null,
    salesMethod: null,
    product: null,
  });

  // Toggle a filter: clicking the same value again clears it.
  function toggleFilter(dimension, value) {
    setFilters(prev => ({
      ...prev,
      [dimension]: prev[dimension] === value ? null : value,
    }));
  }

  function clearFilters() {
    setFilters({ region: null, salesMethod: null, product: null });
  }

  // Build a querystring from whichever filters are active, skipping the
  // dimension a chart owns (so that chart never filters itself down to one bar).
  function buildQuery(skipDimension) {
    const params = new URLSearchParams();
    if (filters.region && skipDimension !== "region") params.set("region", filters.region);
    if (filters.salesMethod && skipDimension !== "salesMethod") params.set("sales_method", filters.salesMethod);
    if (filters.product && skipDimension !== "product") params.set("product", filters.product);
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }

  const [dataError, setDataError] = useState(null);

  useEffect(() => {
    setDataError(null);

    const checkJsonAndSet = (res, setter) => {
      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new TypeError("Backend returned HTML/non-JSON content (likely service is offline or starting up)");
      }
      return res.json().then(data => {
        if (data && data.error) {
          setDataError(data.error);
        } else if (data && data.status === "waiting_for_data") {
          setDataError(data.message || "Data not loaded on backend.");
        } else {
          setter(data);
        }
      });
    };

    // Summary and trend respect ALL filters (they don't own any dimension).
    fetch(`${API_BASE}/data/summary${buildQuery(null)}`)
      .then(r => checkJsonAndSet(r, setSummary))
      .catch(err => {
        console.error("Error fetching summary:", err);
        setDataError(err.message || "Failed to fetch summary data or backend data is not loaded.");
      });

    fetch(`${API_BASE}/data/trends${buildQuery(null)}`)
      .then(r => checkJsonAndSet(r, setTrends))
      .catch(err => {
        console.error("Error fetching trends:", err);
        setDataError(err.message || "Failed to fetch trends.");
      });

    // Each of these skips its OWN dimension so it always shows all its bars.
    fetch(`${API_BASE}/data/by-region${buildQuery("region")}`)
      .then(r => checkJsonAndSet(r, setByRegion))
      .catch(err => {
        console.error("Error fetching region data:", err);
        setDataError(err.message || "Failed to fetch region data.");
      });

    fetch(`${API_BASE}/data/by-sales-method${buildQuery("salesMethod")}`)
      .then(r => checkJsonAndSet(r, setBySalesMethod))
      .catch(err => {
        console.error("Error fetching sales method data:", err);
        setDataError(err.message || "Failed to fetch sales method data.");
      });

    fetch(`${API_BASE}/data/top-products${buildQuery("product")}`)
      .then(r => checkJsonAndSet(r, setTopProducts))
      .catch(err => {
        console.error("Error fetching top products:", err);
        setDataError(err.message || "Failed to fetch top products.");
      });
  }, [filters]);

  const hasActiveFilters = filters.region || filters.salesMethod || filters.product;

  return (
    <div style={{ padding: "24px", fontFamily: "sans-serif" }}>
      <h1>Adidas Sales Dashboard</h1>

      {/* Active filter chips */}
      <div style={{ marginBottom: "16px", minHeight: "32px" }}>
        {filters.region && <Chip label={`Region: ${filters.region}`} onClear={() => toggleFilter("region", filters.region)} />}
        {filters.salesMethod && <Chip label={`Method: ${filters.salesMethod}`} onClear={() => toggleFilter("salesMethod", filters.salesMethod)} />}
        {filters.product && <Chip label={`Product: ${filters.product}`} onClear={() => toggleFilter("product", filters.product)} />}
        {hasActiveFilters && (
          <button onClick={clearFilters} style={clearButtonStyle}>Clear all filters</button>
        )}
      </div>

      {dataError && (
        <div style={{ padding: "12px 16px", background: "#fef2f2", color: "#b91c1c", borderRadius: "6px", marginBottom: "20px", border: "1px solid #fee2e2", fontSize: "14px" }}>
          <strong>Error loading dashboard data:</strong> {dataError}
        </div>
      )}

      {summary && (
        <div style={{ display: "flex", gap: "16px", marginBottom: "24px" }}>
          <StatCard label="Total Sales" value={`$${summary.total_sales.toLocaleString()}`} />
          <StatCard label="Total Profit" value={`$${summary.total_profit.toLocaleString()}`} />
          <StatCard label="Avg Margin" value={`${(summary.avg_margin * 100).toFixed(1)}%`} />
          <StatCard label="Units Sold" value={summary.total_units.toLocaleString()} />
        </div>
      )}

      <ChartCard title="Monthly Sales Trend">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="Invoice Date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="Total Sales" stroke="#2563eb" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Profit by Region (click a bar to filter everything else)">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={byRegion}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="Region" />
            <YAxis />
            <Tooltip />
            <Bar
              dataKey="Operating Profit"
              onClick={(data) => toggleFilter("region", data.Region)}
              style={{ cursor: "pointer" }}
            >
              {byRegion.map((entry, index) => (
                <Cell
                  key={index}
                  fill={filters.region === entry.Region ? "#166534" : "#16a34a"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Avg Margin by Sales Method (click to filter)">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={bySalesMethod}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="Sales Method" />
            <YAxis />
            <Tooltip />
            <Bar
              dataKey="Operating Margin"
              onClick={(data) => toggleFilter("salesMethod", data["Sales Method"])}
              style={{ cursor: "pointer" }}
            >
              {bySalesMethod.map((entry, index) => (
                <Cell
                  key={index}
                  fill={filters.salesMethod === entry["Sales Method"] ? "#92400e" : "#d97706"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Top 10 Products (click to filter)">
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={topProducts} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="Product" type="category" width={180} />
            <Tooltip />
            <Bar
              dataKey="Total Sales"
              onClick={(data) => toggleFilter("product", data.Product)}
              style={{ cursor: "pointer" }}
            >
              {topProducts.map((entry, index) => (
                <Cell
                  key={index}
                  fill={filters.product === entry.Product ? "#4c1d95" : "#7c3aed"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: "8px", padding: "16px", flex: 1 }}>
      <div style={{ fontSize: "13px", color: "#6b7280" }}>{label}</div>
      <div style={{ fontSize: "22px", fontWeight: 600 }}>{value}</div>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div style={{ marginBottom: "32px" }}>
      <h3>{title}</h3>
      {children}
    </div>
  );
}

function Chip({ label, onClear }) {
  return (
    <span style={chipStyle}>
      {label}
      <button onClick={onClear} style={chipButtonStyle}>×</button>
    </span>
  );
}

const chipStyle = {
  display: "inline-flex",
  alignItems: "center",
  gap: "6px",
  background: "#eff6ff",
  color: "#1d4ed8",
  padding: "4px 10px",
  borderRadius: "999px",
  fontSize: "13px",
  marginRight: "8px",
};

const chipButtonStyle = {
  border: "none",
  background: "none",
  color: "#1d4ed8",
  cursor: "pointer",
  fontSize: "14px",
  lineHeight: 1,
};

const clearButtonStyle = {
  border: "1px solid #d1d5db",
  background: "white",
  borderRadius: "6px",
  padding: "4px 10px",
  fontSize: "13px",
  cursor: "pointer",
};