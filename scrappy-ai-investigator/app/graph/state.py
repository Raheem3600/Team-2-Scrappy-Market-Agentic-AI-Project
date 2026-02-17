from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class InvestigationStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class IntentModel(BaseModel):
    metric: Optional[str] = None
    time_range: Optional[str] = None
    comparison: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class HypothesisModel(BaseModel):
    name: str
    priority: int
    tested: bool = False
    score: Optional[float] = None


class EvidenceModel(BaseModel):
    hypothesis: str
    summary: str
    raw_data: Optional[Dict[str, Any]] = None


class InvestigationState(BaseModel):
    # ---- Metadata ----
    schema_version: str = Field(default="1.0.0")
    investigation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # ---- Core ----
    question: str
    status: InvestigationStatus = InvestigationStatus.STARTED

    # ---- Structured Fields ----
    intent: Optional[IntentModel] = None
    hypotheses: List[HypothesisModel] = []
    evidence: List[EvidenceModel] = []
    confidence: Optional[float] = None

    # ---- Control Flags ----
    current_hypothesis_index: int = 0

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    def add_hypothesis(self, hypothesis: HypothesisModel):
        self.hypotheses.append(hypothesis)
        self.update_timestamp()

    def add_evidence(self, evidence: EvidenceModel):
        self.evidence.append(evidence)
        self.update_timestamp()
