import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { api } from './api';

import ManualInputForm from './components/ManualInputForm';
import AnalysisResultCard from './components/AnalysisResultCard';
import AnalyticsCharts from './components/AnalyticsCharts';
import TestHistoryTable from './components/TestHistoryTable';
import ReferenceLimitsModal from './components/ReferenceLimitsModal';
import SampleDetailModal from './components/SampleDetailModal';

function App() {
  const [activeTab, setActiveTab] = useState('lab'); // 'lab', 'charts', 'history'
  const [analysisResult, setAnalysisResult] = useState(null);
  const [testRecords, setTestRecords] = useState([]);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [referenceLimits, setReferenceLimits] = useState([]);
  const [healthInfo, setHealthInfo] = useState(null);

  // Modals
  const [isLimitsModalOpen, setIsLimitsModalOpen] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tableFilter, setTableFilter] = useState('All');

  // Load Initial Data
  const refreshAllData = useCallback(async () => {
    try {
      const [analyticsRes, recordsRes, limitsRes, healthRes] = await Promise.all([
        api.getDashboardAnalytics(),
        api.getTestRecords(),
        api.getReferenceLimits(),
        api.getHealth()
      ]);

      if (analyticsRes.status === "success") setAnalyticsData(analyticsRes);
      if (recordsRes.status === "success") setTestRecords(recordsRes.data || []);
      if (limitsRes.status === "success") setReferenceLimits(limitsRes.data || []);
      if (healthRes.status === "healthy") setHealthInfo(healthRes);
    } catch (err) {
      console.error("Error refreshing data:", err);
    }
  }, []);

  useEffect(() => {
    refreshAllData();
  }, [refreshAllData]);

  // Handle Manual Sample Analysis
  const handleAnalyze = async (formData) => {
    setIsSubmitting(true);
    try {
      const res = await api.analyzeSample(formData);
      if (res.status === "success") {
        setAnalysisResult(res);
        // Refresh history & analytics to reflect new stored test
        await refreshAllData();
        // Scroll to top of lab result
        window.scrollTo({ top: 120, behavior: 'smooth' });
      } else {
        alert("Error analyzing sample: " + (res.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Analysis submission error:", err);
      alert("Failed to connect to backend server.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Delete Record
  const handleDeleteRecord = async (id) => {
    try {
      const res = await api.deleteTestRecord(id);
      if (res.status === "success") {
        if (selectedRecord && selectedRecord.id === id) {
          setSelectedRecord(null);
        }
        await refreshAllData();
      }
    } catch (err) {
      console.error("Delete record error:", err);
    }
  };

  // Handle Save Reference Limit
  const handleSaveLimit = async (key, minVal, maxVal, idealVal) => {
    try {
      await api.updateReferenceLimit(key, minVal, maxVal, idealVal);
      const updated = await api.getReferenceLimits();
      if (updated.data) setReferenceLimits(updated.data);
      alert(`Reference limits for ${key} successfully updated!`);
    } catch (err) {
      console.error("Update limit error:", err);
    }
  };

  const summary = analyticsData?.summary || {
    total_tests: testRecords.length,
    safe_count: 0,
    unsafe_count: 0,
    needs_testing_count: 0,
    compliance_rate: 0
  };

  return (
    <div className="app-wrapper">
      {/* Header */}
      <header className="app-header">
        <div className="header-container">
          <div className="brand-section">
            <div className="brand-icon-wrapper">
              💧
            </div>
            <div>
              <h1 className="brand-title">AQUA-SENSE</h1>
              <p className="brand-subtitle">Software Water Quality Analysis System</p>
            </div>
          </div>

          <div className="header-controls">
            <span className="software-badge">
              🖥️ ZERO HARDWARE • 100% SOFTWARE
            </span>

            <span className="db-pill" title="Active Backend Database Engine">
              🗄️ {healthInfo?.database || 'PostgreSQL'}
            </span>

            <button
              onClick={() => setIsLimitsModalOpen(true)}
              className="btn-header btn-glass"
              title="Configure WHO & EPA reference potability limits"
            >
              ⚙️ Reference Limits
            </button>

            <a
              href={api.getExportCsvUrl()}
              download
              className="btn-header btn-primary"
              style={{ textDecoration: 'none' }}
              title="Download test records as CSV"
            >
              📥 Export CSV
            </a>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Executive Summary Stats Bar */}
        <div className="summary-stats-bar">
          <div className="stat-card">
            <div>
              <div className="stat-value">{summary.total_tests}</div>
              <div className="stat-label">Total Samples Evaluated</div>
            </div>
            <div style={{ fontSize: '2rem' }}>🧪</div>
          </div>

          <div className="stat-card" style={{ borderLeft: '4px solid #16a34a' }}>
            <div>
              <div className="stat-value" style={{ color: '#15803d' }}>{summary.safe_count}</div>
              <div className="stat-label">Safe for Consumption</div>
            </div>
            <div style={{ fontSize: '2rem' }}>🟢</div>
          </div>

          <div className="stat-card" style={{ borderLeft: '4px solid #d97706' }}>
            <div>
              <div className="stat-value" style={{ color: '#b45309' }}>{summary.needs_testing_count}</div>
              <div className="stat-label">Needs Further Testing</div>
            </div>
            <div style={{ fontSize: '2rem' }}>🟡</div>
          </div>

          <div className="stat-card" style={{ borderLeft: '4px solid #dc2626' }}>
            <div>
              <div className="stat-value" style={{ color: '#b91c1c' }}>{summary.unsafe_count}</div>
              <div className="stat-label">Unsafe / Contaminated</div>
            </div>
            <div style={{ fontSize: '2rem' }}>🔴</div>
          </div>

          <div className="stat-card" style={{ borderLeft: '4px solid #2563eb' }}>
            <div>
              <div className="stat-value" style={{ color: '#1d4ed8' }}>{summary.compliance_rate}%</div>
              <div className="stat-label">Potability Compliance</div>
            </div>
            <div style={{ fontSize: '2rem' }}>📊</div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="tabs-navigation">
          <button
            onClick={() => setActiveTab('lab')}
            className={`tab-btn ${activeTab === 'lab' ? 'active' : ''}`}
          >
            <span>🔬</span> Water Quality Analysis Lab
          </button>

          <button
            onClick={() => setActiveTab('charts')}
            className={`tab-btn ${activeTab === 'charts' ? 'active' : ''}`}
          >
            <span>📈</span> Analytics & Trends Dashboard
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          >
            <span>📋</span> Test Records Archive ({testRecords.length})
          </button>
        </div>

        {/* Tab 1: Water Quality Analysis Lab */}
        {activeTab === 'lab' && (
          <div>
            {/* Display Assessment Verdict if sample was analyzed */}
            {analysisResult && (
              <AnalysisResultCard
                result={analysisResult}
                onDismiss={() => setAnalysisResult(null)}
              />
            )}

            {/* Manual Parameter Input Form */}
            <ManualInputForm
              onAnalyze={handleAnalyze}
              isSubmitting={isSubmitting}
            />
          </div>
        )}

        {/* Tab 2: Analytics & Trends Dashboard */}
        {activeTab === 'charts' && (
          <div>
            <AnalyticsCharts
              analyticsData={analyticsData}
              latestSample={analysisResult?.record || (testRecords.length > 0 ? testRecords[0] : null)}
            />
          </div>
        )}

        {/* Tab 3: Test Records Archive & Reports */}
        {activeTab === 'history' && (
          <div>
            <TestHistoryTable
              records={testRecords}
              activeFilter={tableFilter}
              onFilterChange={setTableFilter}
              onSelectRecord={(rec) => setSelectedRecord(rec)}
              onDeleteRecord={handleDeleteRecord}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div>
          <strong>Aqua-Sense Water Quality Analysis System</strong> • 100% Software Laboratory Architecture
        </div>
        <div style={{ marginTop: '0.25rem', fontSize: '0.78rem' }}>
          Backend: Python Flask & PostgreSQL • Frontend: React & Chart.js • WHO / US-EPA Potability Standards
        </div>
      </footer>

      {/* Reference Limits Modal */}
      <ReferenceLimitsModal
        isOpen={isLimitsModalOpen}
        onClose={() => setIsLimitsModalOpen(false)}
        limits={referenceLimits}
        onSave={handleSaveLimit}
      />

      {/* Sample Detail & PDF Report Viewer Modal */}
      <SampleDetailModal
        record={selectedRecord}
        onClose={() => setSelectedRecord(null)}
      />
    </div>
  );
}

export default App;
