from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
Language = Literal['en','hi','kn']
InputType = Literal['text','image','link','voice']
TacticType = Literal['authority_impersonation','fear_of_arrest','urgency','secrecy_or_isolation','payment_redirection','too_good_returns','otp_or_credential_harvesting','link_lure','remote_access_app']
Status = Literal['VERIFIED','CONTRADICTED','DANGEROUS','SUSPICIOUS','UNVERIFIED','NOT_PROVIDED']
Verdict = Literal['SCAM','GENUINE','UNSURE']
class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
class AnalyzeInput(StrictModel):
    text: str = Field(min_length=3,max_length=12000)
    language: Language = 'en'
    input_type: InputType = 'text'
    user_reported_loss: bool = False
class TacticSpan(StrictModel):
    phrase: str = Field(min_length=1,max_length=1000)
    tactic: TacticType
    explanation: str = Field(max_length=1500)
    start: int = 0
    end: int = 0
class ExtractedClaim(StrictModel):
    claim_id: str
    text: str
    claim_type: str
class ExtractionResult(StrictModel):
    input_type: InputType
    detected_language: Language
    raw_text_redacted: str
    claimed_authority: str | None = None
    script_family: str | None = None
    claims: list[ExtractedClaim] = Field(default_factory=list)
    tactics: list[TacticSpan] = Field(default_factory=list)
    requested_actions: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    upi_ids: list[str] = Field(default_factory=list)
    phone_numbers: list[str] = Field(default_factory=list)
    amounts: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    user_reported_loss: bool = False
class EvidenceItem(StrictModel):
    source_id: str
    url: str
    publisher: str
    document_date: str | None = None
    title: str
    source_type: str = 'official_document'
    claim_id: str | None = None
    relation: Literal['supports','contradicts','context_only','unclear'] = 'context_only'
    evidence_text: str
    retrieval_status: Literal['live_fetched','verified_registry_fetched'] = 'live_fetched'
    sha256_hash: str
    retrieved_at_utc: str
class DimensionChecks(StrictModel):
    authority: Status
    requested_action: Status
    destination: Status
class ReportingChannel(StrictModel):
    name: str
    url_or_number: str
    when_to_use: str
    draft_complaint: str = ''
class TraceStep(StrictModel):
    step_number: int
    tool_name: str
    input_summary: str
    output_summary: str
    status: Literal['ok','warning','fallback']
    duration_ms: int
class VerificationReport(StrictModel):
    report_id: str
    verdict: Verdict
    detailed_verdict: str
    risk_level: Literal['HIGH','MEDIUM','LOW']
    summary: str
    language: Language
    checks: DimensionChecks
    extracted: ExtractionResult
    tactics: list[TacticSpan]
    script_family: str | None
    evidence: list[EvidenceItem]
    trace: list[TraceStep]
    recommended_actions: list[str]
    which_door_routing: list[ReportingChannel]
    limitations: list[str]
    report_hash: str
    generated_at_utc: str
    complaint: str
    provider_status: dict
class LLMExtraction(StrictModel):
    detected_language: Language
    claimed_authority: str | None
    script_family: str | None
    claims: list[ExtractedClaim]
    tactics: list[TacticSpan]
    requested_actions: list[str]
    search_query: str
class EvidenceAssessment(StrictModel):
    matches: list['ClaimMatch']
    unverified_claim_ids: list[str]
class ClaimMatch(StrictModel):
    claim_id: str
    source_id: str
    relation: Literal['supports','contradicts','context_only','unclear']
    quote: str
class SpeakInput(StrictModel):
    text: str = Field(min_length=1,max_length=2500)
    language: Language = 'en'
class BenchmarkInput(StrictModel):
    token: str = ''
class PdfInput(StrictModel):
    report: VerificationReport
    signature: str
