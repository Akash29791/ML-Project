import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

from config import Config
from database import engine, Base, SessionLocal, ACTIVE_DB_TYPE
from models import WaterTestRecord, ReferenceLimit
from analyzer import DEFAULT_REFERENCE_LIMITS, analyze_water_sample

# Import API blueprints
from routes.analysis import analysis_bp
from routes.analytics import analytics_bp

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("App")

def create_app():
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    app = Flask(__name__, static_folder=static_folder, static_url_path="")
    app.config.from_object(Config)

    # Enable Cross-Origin Resource Sharing
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(analysis_bp)
    app.register_blueprint(analytics_bp)

    # Disable caching for SPA index and API responses during development
    @app.after_request
    def add_cache_control_headers(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # Graceful fallback for any old cached browser tabs polling legacy simulation endpoints
    @app.route("/api/telemetry/<path:subpath>", methods=["GET", "POST"])
    @app.route("/api/simulation/<path:subpath>", methods=["GET", "POST"])
    @app.route("/api/alerts", methods=["GET", "POST"])
    @app.route("/api/stations", methods=["GET"])
    def legacy_compatibility(subpath=""):
        return jsonify({
            "status": "deprecated",
            "message": "Live telemetry simulation has been replaced by the Manual Water Quality Analysis Lab. Please refresh your browser (Ctrl+F5)."
        }), 200

    # Initialize Database Schema & Seed baseline records
    init_db_and_seeds()

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "Water Quality Analysis System API",
            "database": ACTIVE_DB_TYPE,
            "architecture": "Pure Software Analysis (No Hardware / No Auto-Simulation)",
            "timestamp": datetime.utcnow().isoformat()
        })

    # Serve Frontend SPA
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        index_path = os.path.join(app.static_folder, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, "index.html")
        return jsonify({
            "status": "online",
            "service": "Water Quality Analysis System API",
            "database": ACTIVE_DB_TYPE
        })

    return app


def init_db_and_seeds():
    """Initializes tables and seeds standard WHO/EPA reference limits and sample test records."""
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Reference Limits
        existing_keys = {r.parameter_key for r in db.query(ReferenceLimit.parameter_key).all()}
        for key, conf in DEFAULT_REFERENCE_LIMITS.items():
            if key not in existing_keys:
                ref = ReferenceLimit(
                    parameter_key=key,
                    display_name=conf["display_name"],
                    unit=conf["unit"],
                    min_safe=conf.get("min_safe"),
                    max_safe=conf.get("max_safe"),
                    ideal_value=conf.get("ideal"),
                    description=conf.get("description")
                )
                db.add(ref)
        db.commit()

        # 2. Seed realistic historical water test records if database is empty
        test_count = db.query(WaterTestRecord).count()
        if test_count == 0:
            logger.info("Seeding initial benchmark water test records for dashboard analytics...")
            now = datetime.utcnow()

            benchmark_samples = [
                {
                    "sample_name": "Municipal Central Tap Water",
                    "water_source": "Municipal Tap",
                    "location": "Kitchen Faucet, Flat 4B",
                    "tested_by": "Dr. Sarah Chen (Analyst)",
                    "hours_ago": 72,
                    "ph": 7.3, "tds": 210.0, "turbidity": 0.8, "hardness": 110.0, "chlorine": 0.6, "temperature": 20.5,
                    "notes": "Standard municipal treated utility supply. Clean odor and clarity."
                },
                {
                    "sample_name": "Deep Borewell Aquifer #3",
                    "water_source": "Groundwater / Borewell",
                    "location": "North Agricultural Zone",
                    "tested_by": "M. Jenkins (Field Officer)",
                    "hours_ago": 54,
                    "ph": 7.8, "tds": 640.0, "turbidity": 1.4, "hardness": 260.0, "chlorine": 0.0, "temperature": 22.0,
                    "notes": "Untreated ground source. High dissolved minerals; hardness requires softening."
                },
                {
                    "sample_name": "Commercial RO Purified Water",
                    "water_source": "Bottled / RO",
                    "location": "Office Cafeteria Dispenser",
                    "tested_by": "Quality Control Lab",
                    "hours_ago": 36,
                    "ph": 6.9, "tds": 95.0, "turbidity": 0.2, "hardness": 45.0, "chlorine": 0.0, "temperature": 18.5,
                    "notes": "Multi-stage reverse osmosis and UV polished sample."
                },
                {
                    "sample_name": "River Runoff Downstream",
                    "water_source": "Surface / River",
                    "location": "Eastern River Intake Canal",
                    "tested_by": "Environmental Safety Team",
                    "hours_ago": 24,
                    "ph": 6.1, "tds": 820.0, "turbidity": 14.5, "hardness": 320.0, "chlorine": 0.05, "temperature": 25.5,
                    "notes": "Unfiltered runoff with high sediment load and particulate matter."
                },
                {
                    "sample_name": "Community Rooftop Rainwater Harvest",
                    "water_source": "Rainwater Harvest",
                    "location": "Sector 9 Storage Cistern",
                    "tested_by": "A. Rahman (Water Auditor)",
                    "hours_ago": 12,
                    "ph": 6.6, "tds": 120.0, "turbidity": 2.2, "hardness": 70.0, "chlorine": 0.0, "temperature": 21.0,
                    "notes": "Collected after heavy storm; slight atmospheric particulates, soft water."
                },
                {
                    "sample_name": "Industrial Canal Effluent Outfall",
                    "water_source": "Industrial Inflow",
                    "location": "Perimeter Drainage Channel",
                    "tested_by": "Pollution Control Squad",
                    "hours_ago": 4,
                    "ph": 4.9, "tds": 1150.0, "turbidity": 9.2, "hardness": 380.0, "chlorine": 4.6, "temperature": 28.5,
                    "notes": "Suspected unauthorized chemical discharge. High acidity and mineral toxicity."
                }
            ]

            for s in benchmark_samples:
                res = analyze_water_sample(s, DEFAULT_REFERENCE_LIMITS)
                record = WaterTestRecord(
                    sample_name=s["sample_name"],
                    water_source=s["water_source"],
                    location=s["location"],
                    tested_by=s["tested_by"],
                    timestamp=now - timedelta(hours=s["hours_ago"]),
                    ph=s["ph"],
                    tds=s["tds"],
                    turbidity=s["turbidity"],
                    hardness=s["hardness"],
                    chlorine=s["chlorine"],
                    temperature=s["temperature"],
                    overall_status=res["overall_status"],
                    wqi_score=res["wqi_score"],
                    status_summary=res["status_summary"],
                    evaluations_json=json.dumps(res["evaluations"]),
                    recommendations_json=json.dumps(res["recommendations"]),
                    notes=s.get("notes", "")
                )
                db.add(record)
            db.commit()
            logger.info("Initial benchmark test records seeded successfully.")

    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(f"Starting Water Quality Analysis System on http://{host}:{port}")
    logger.info(f"Active database backend: {ACTIVE_DB_TYPE}")
    app.run(host=host, port=port, debug=False, use_reloader=False)
