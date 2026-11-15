// Aqua-Sense: Water Quality Analysis System API Client

const API_BASE = process.env.REACT_APP_API_URL || "";

export const api = {
  // Analyze manual water sample inputs
  async analyzeSample(sampleData) {
    const res = await fetch(`${API_BASE}/api/tests/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sampleData)
    });
    return res.json();
  },

  // Get test records history
  async getTestRecords(status = "", search = "", limit = 100) {
    const params = new URLSearchParams();
    if (status && status !== "All") params.append("status", status);
    if (search) params.append("search", search);
    if (limit) params.append("limit", limit);

    const res = await fetch(`${API_BASE}/api/tests?${params.toString()}`);
    return res.json();
  },

  // Get specific test record details
  async getTestRecord(id) {
    const res = await fetch(`${API_BASE}/api/tests/${id}`);
    return res.json();
  },

  // Delete test record
  async deleteTestRecord(id) {
    const res = await fetch(`${API_BASE}/api/tests/${id}`, {
      method: "DELETE"
    });
    return res.json();
  },

  // Get PDF report download URL
  getPdfReportUrl(id) {
    return `${API_BASE}/api/tests/${id}/report/pdf`;
  },

  // Get CSV export URL
  getExportCsvUrl() {
    return `${API_BASE}/api/tests/export/csv`;
  },

  // Get dashboard analytics and trends
  async getDashboardAnalytics() {
    const res = await fetch(`${API_BASE}/api/analytics/dashboard`);
    return res.json();
  },

  // Get WHO / EPA reference limits
  async getReferenceLimits() {
    const res = await fetch(`${API_BASE}/api/reference-limits`);
    return res.json();
  },

  // Update custom reference limits
  async updateReferenceLimit(parameterKey, minSafe, maxSafe, idealValue) {
    const res = await fetch(`${API_BASE}/api/reference-limits/${parameterKey}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        min_safe: minSafe,
        max_safe: maxSafe,
        ideal_value: idealValue
      })
    });
    return res.json();
  },

  // Health check
  async getHealth() {
    const res = await fetch(`${API_BASE}/api/health`);
    return res.json();
  }
};
