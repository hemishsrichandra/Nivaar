from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
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
    user_situation: Literal['ONLY_RECEIVED','MONEY_SENT','OTP_OR_PASSWORD_SHARED','APP_INSTALLED_OR_REMOTE_ACCESS_GRANTED','SIM_SUSPECTED_COMPROMISED','OTHER_OR_UNSURE'] | None = None
class TacticSpan(StrictModel):
    phrase: str = Field(min_length=1,max_length=1000)
    tactic: TacticType
    explanation: str = Field(max_length=1500)
    origin: Literal['rule','model'] = 'rule'
    start: int = 0
    end: int = 0
class ExtractedClaim(StrictModel):
    claim_id: str = Field(pattern=r'^[a-zA-Z0-9_-]{1,80}$')
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
    evidence_id: str = ''
    cached: bool = False
    fetch_status: Literal['fetched','cached'] = 'fetched'
    @model_validator(mode='after')
    def dates(self):
        if self.document_date:
            from backend.services.source_ranking import valid_date
            if valid_date(self.document_date)!=self.document_date:raise ValueError('Invalid source publication date')
        return self
class DimensionChecks(StrictModel):
    authority: Status
    requested_action: Status
    destination: Status
class ReportingChannel(StrictModel):
    name: str
    url_or_number: str
    when_to_use: str
    draft_complaint: str = ''
    source_urls: list[str] = Field(default_factory=list)
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
    provider_errors: dict[str,Literal['MISSING_KEY','RATE_LIMITED','TIMEOUT','UPSTREAM_ERROR','INVALID_RESPONSE','NOT_CONFIGURED']] = Field(default_factory=dict)
    claims: list['ClaimFinding'] = Field(default_factory=list)
    assessments: dict[Literal['authority','requested_action','destination'],'DimensionAssessment'] = Field(default_factory=dict)
    identifiers: 'IdentifierFindings' = Field(default_factory=lambda: IdentifierFindings())
    evidence_coverage: 'EvidenceCoverage' = Field(default_factory=lambda: EvidenceCoverage())
    user_situation: Literal['ONLY_RECEIVED','MONEY_SENT','OTP_OR_PASSWORD_SHARED','APP_INSTALLED_OR_REMOTE_ACCESS_GRANTED','SIM_SUSPECTED_COMPROMISED','OTHER_OR_UNSURE'] = 'ONLY_RECEIVED'
    source_conflicts: list[str] = Field(default_factory=list)
    @model_validator(mode='after')
    def references(self):
        ids={e.evidence_id for e in self.evidence if e.evidence_id}
        if len({c.claim_id for c in self.claims})!=len(self.claims):raise ValueError('Duplicate claim IDs')
        for c in [*self.claims,*self.assessments.values(),*self.identifiers.upi_ids,*self.identifiers.phone_numbers]:
            if not set(c.evidence_ids)<=ids:raise ValueError('Unknown evidence reference')
        return self
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

Situation = Literal['ONLY_RECEIVED','MONEY_SENT','OTP_OR_PASSWORD_SHARED','APP_INSTALLED_OR_REMOTE_ACCESS_GRANTED','SIM_SUSPECTED_COMPROMISED','OTHER_OR_UNSURE']
class ClaimFinding(StrictModel):
    claim_id: str = Field(pattern=r'^[a-zA-Z0-9_-]{1,80}$')
    text: str
    category: str
    status: Literal['SUPPORTED','CONTRADICTED','NOT_FOUND','UNVERIFIABLE']
    explanation: str
    evidence_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
class DimensionAssessment(StrictModel):
    status: Status
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)
    limitation: str
class CoverageComponent(StrictModel):
    name: str
    weight: int
    applicable: bool
    completed: float = Field(ge=0,le=1)
    explanation: str
class EvidenceCoverage(StrictModel):
    score: int | None = Field(default=None,ge=0,le=100)
    label: str = 'How much of this message we could verify'
    components: list[CoverageComponent] = Field(default_factory=list)
    note: str = 'Evidence coverage is not a probability of fraud or safety. Low coverage is not proof of fraud.'
class PhoneFinding(StrictModel):
    original: str
    normalized: str | None
    status: Literal['PARSED','UNPARSED','PUBLISHED_HELPLINE']
    international: bool = False
    official_comparison: Literal['NOT_CHECKED','MATCH_FORMAT','MISMATCH'] = 'NOT_CHECKED'
    evidence_ids: list[str] = Field(default_factory=list)
    warning: str
class UpiFinding(StrictModel):
    original: str
    local_part: str | None
    handle: str | None
    status: Literal['PAYEE_NOT_VERIFIED','UNPARSED','MISMATCH']
    payment_context: bool = False
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)
class MessagingLink(StrictModel):
    original: str
    normalized: str
    platform: Literal['WhatsApp','Telegram']
    invite: bool
    warning: str
class IdentifierFindings(StrictModel):
    phone_numbers: list[PhoneFinding] = Field(default_factory=list)
    upi_ids: list[UpiFinding] = Field(default_factory=list)
    messaging_links: list[MessagingLink] = Field(default_factory=list)

VerificationReport.model_rebuild()
PdfInput.model_rebuild()
