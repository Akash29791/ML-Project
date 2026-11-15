# 💧 Aqua-Sense: Software-Based Water Quality Analysis System

A comprehensive, full-stack, **100% software-based** water potability and contamination analysis platform built with **React**, **Chart.js**, **Python Flask**, and **PostgreSQL** *(with zero-config SQLite fallback)*.

> **Zero Hardware / No Sensors / No Arduino / No ESP32 / No Automatic Simulation**: 
> This is a professional laboratory software application. Users manually enter measured water quality parameters (or choose benchmark presets), and the system evaluates them against configurable WHO/EPA drinking water standards, computes the Water Quality Index (WQI), classifies potability as **Safe**, **Unsafe**, or **Needs Further Testing**, stores records in the database, and generates downloadable **Official PDF Certification Reports**.

---

## 🛠️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | **React 18** | Modern blue-and-white responsive interface with live validation |
| **Data Visualizations** | **Chart.js 4** | Time-series WQI trends, source breakdown doughnut, and compliance radar |
| **Backend API** | **Python Flask** | RESTful endpoints, analysis engine, and database ORM layer |
| **PDF Generation** | **ReportLab 5** | High-resolution, official PDF Water Quality Assessment Certificates |
| **Database** | **PostgreSQL** | Primary relational store for test history and reference limits *(auto-switches to SQLite if PostgreSQL is unconfigured)* |
| **ORM** | **SQLAlchemy** | Schema definition, migrations, and relationship management |

---

## 🧪 Evaluated Physicochemical Parameters

The system evaluates all 6 parameters specified by WHO & US-EPA potability guidelines:

| Parameter | Unit | Permissible Limit | Ideal Benchmark | Potential Health / System Risk |
| :--- | :---: | :---: | :---: | :--- |
| **1. pH Level** | pH | **6.5 – 8.5** | **7.0** | < 6.5: Corrosive, heavy metal leaching. > 8.5: Scaling, alkaline taste. |
| **2. Total Dissolved Solids (TDS)** | ppm | **≤ 500 ppm** | **150 ppm** | > 1000 ppm: Mineral toxicity, gastrointestinal issues, severe scaling. |
| **3. Turbidity** | NTU | **≤ 5.0 NTU** | **< 1.0 NTU** | > 5.0 NTU: High suspended sediment; shields microbial pathogens. |
| **4. Total Hardness** | mg/L $\text{CaCO}_3$ | **≤ 200 mg/L** | **100 mg/L** | > 300 mg/L: Severe calcification, plumbing damage, appliance clogs. |
| **5. Free Residual Chlorine** | ppm (mg/L) | **0.2 – 2.0 ppm** | **0.5 ppm** | < 0.2: Bacterial regrowth risk. > 4.0 ppm: Chemical irritation, trihalomethanes. |
| **6. Temperature** | °C | **12°C – 25°C** | **20°C** | > 28°C: Accelerates bacterial growth, reduces dissolved oxygen retention. |

---

## 🏷️ Multi-Factor Classification Logic

The system evaluates all measured parameters using a deterministic rules engine:

1. 🟢 **SAFE FOR HUMAN CONSUMPTION**:
   - All 6 parameters strictly meet WHO/EPA safe boundaries.
   - WQI Score $\ge$ 80.
   - Zero parameter violations.
2. 🟡 **NEEDS FURTHER TESTING**:
   - 1 or 2 borderline deviations (e.g., Hardness 200–280 mg/L, TDS 500–800 ppm, or zero chlorine in raw well water).
   - Requires secondary laboratory culturing (coliforms/heavy metals) before clearing.
3. 🔴 **UNSAFE FOR HUMAN CONSUMPTION**:
   - Critical breach in any primary parameter (Turbidity > 5 NTU, extreme pH < 6 or > 9, TDS > 1000 ppm, Chlorine > 4.0 ppm, or Hardness > 300 mg/L).
   - Generates immediate corrective engineering remediation actions (e.g. RO filtration, ion-exchange softening, calcite neutralization).

---

## 📂 Project Architecture

```
smart water quality system/
│
├── backend/
│   ├── app.py                      # Flask API server & static SPA server
│   ├── analyzer.py                 # Multi-parameter analysis & verdict logic
│   ├── pdf_generator.py            # ReportLab official PDF certificate engine
│   ├── config.py                   # Configuration settings & environment variables
│   ├── database.py                 # SQLAlchemy engine, session provider & auto-fallback
│   ├── models.py                   # Database models (WaterTestRecord, ReferenceLimit)
│   ├── init_db.sql                 # Pure SQL schema & seed script
│   ├── requirements.txt            # Python dependencies (Flask, ReportLab, SQLAlchemy, etc.)
│   ├── .env                        # Active environment configuration
│   ├── routes/
│   │   ├── analysis.py             # Sample evaluation, CRUD, PDF & CSV export
│   │   └── analytics.py            # Statistical summaries & reference limits API
│   └── static/
│       └── index.html              # Standalone, ready-to-run React 18 + Chart.js application
│
├── frontend/
│   ├── package.json                # React 18 dependencies
│   ├── public/
│   │   └── index.html              # HTML shell
│   └── src/
│       ├── index.js                # React DOM entrypoint
│       ├── App.js                  # Main controller with 3 tabs (Lab, Charts, History)
│       ├── App.css                 # Modern Blue & White responsive styles
│       ├── api.js                  # Asynchronous REST API service
│       └── components/
│           ├── ManualInputForm.js       # 6-parameter input form with presets & sliders
│           ├── AnalysisResultCard.js    # Verdict banner, findings & PDF report button
│           ├── AnalyticsCharts.js       # Trend line, source doughnut, and radar chart
│           ├── TestHistoryTable.js      # Stored records table with PDF download & filters
│           ├── ReferenceLimitsModal.js  # Configurable WHO/EPA threshold settings
│           └── SampleDetailModal.js     # Full test detail modal view
│
├── scripts/
│   ├── run_backend.bat             # 1-click Windows launcher for backend
│   ├── run_backend.ps1             # PowerShell launcher for backend
│   ├── run_frontend.bat            # Windows launcher for React development server
│   ├── run_frontend.ps1            # PowerShell launcher for React development server
│   └── setup_postgres.sql          # Dedicated PostgreSQL setup commands
│
└── README.md                       # Complete documentation
```

---

## 🚀 How to Run on Your Windows Laptop

### 1. Launch the Backend Server
Open PowerShell in the project directory:
```powershell
python backend\app.py
```
*(Or double-click [`scripts/run_backend.bat`](file:///c:/Users/anbuk/OneDrive/Desktop/smart%20water%20quality%20system/scripts/run_backend.bat))*

### 2. Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```
The full React single-page application is served immediately!

### 3. Connect PostgreSQL (Optional)
To use your local PostgreSQL server instead of SQLite:
1. In `psql` or **pgAdmin**, create the database:
   ```sql
   CREATE DATABASE water_quality_db;
   ```
2. Configure your credentials in [`backend/.env`](file:///c:/Users/anbuk/OneDrive/Desktop/smart%20water%20quality%20system/backend/.env):
   ```env
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=water_quality_db
   DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/water_quality_db
   ```
3. Restart `python backend\app.py`. SQLAlchemy will automatically connect to PostgreSQL and create all tables.

---

## 📄 Generating Official PDF Certificates
Every analyzed sample can generate a signed, printable **Water Quality Assessment Certificate**:
- Click **"📄 PDF"** in the Test Records table or **"Download Official PDF Report"** in the assessment card.
- A high-resolution PDF certificate is generated on the fly via ReportLab, containing the official laboratory header, certificate ID, verdict, 6-parameter breakdown table, and remedial engineering actions.
