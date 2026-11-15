import json
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from database import Base

class WaterTestRecord(Base):
    __tablename__ = "water_test_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_name = Column(String(120), nullable=False)
    water_source = Column(String(100), nullable=False, default="Municipal Tap")
    location = Column(String(200), nullable=False, default="General Sampling Site")
    tested_by = Column(String(100), nullable=False, default="Analyst")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # 6 Monitored Parameters
    ph = Column(Float, nullable=False)
    tds = Column(Float, nullable=False)                 # ppm
    turbidity = Column(Float, nullable=False)           # NTU
    hardness = Column(Float, nullable=False)            # mg/L CaCO3
    chlorine = Column(Float, nullable=False)            # ppm
    temperature = Column(Float, nullable=False)         # °C

    # Analysis Results
    overall_status = Column(String(50), nullable=False) # 'Safe', 'Unsafe', 'Needs Further Testing'
    wqi_score = Column(Float, nullable=False)
    status_summary = Column(Text, nullable=True)
    evaluations_json = Column(Text, nullable=True)
    recommendations_json = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    def to_dict(self):
        try:
            evaluations = json.loads(self.evaluations_json) if self.evaluations_json else {}
        except Exception:
            evaluations = {}

        try:
            recommendations = json.loads(self.recommendations_json) if self.recommendations_json else []
        except Exception:
            recommendations = []

        return {
            "id": self.id,
            "sample_name": self.sample_name,
            "water_source": self.water_source,
            "location": self.location,
            "tested_by": self.tested_by,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "iso_timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ph": round(self.ph, 2),
            "tds": round(self.tds, 1),
            "turbidity": round(self.turbidity, 2),
            "hardness": round(self.hardness, 1),
            "chlorine": round(self.chlorine, 2),
            "temperature": round(self.temperature, 1),
            "overall_status": self.overall_status,
            "wqi_score": round(self.wqi_score, 1),
            "status_summary": self.status_summary,
            "evaluations": evaluations,
            "recommendations": recommendations,
            "notes": self.notes
        }


class ReferenceLimit(Base):
    __tablename__ = "reference_limits"

    parameter_key = Column(String(50), primary_key=True)
    display_name = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=False)
    min_safe = Column(Float, nullable=True)
    max_safe = Column(Float, nullable=True)
    ideal_value = Column(Float, nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "parameter_key": self.parameter_key,
            "display_name": self.display_name,
            "unit": self.unit,
            "min_safe": self.min_safe,
            "max_safe": self.max_safe,
            "ideal_value": self.ideal_value,
            "description": self.description,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
