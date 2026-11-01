export type Language = 'en'|'hi'|'kn';
export type Verdict = 'SCAM'|'GENUINE'|'UNSURE';
export type Status = 'VERIFIED'|'CONTRADICTED'|'DANGEROUS'|'SUSPICIOUS'|'UNVERIFIED'|'NOT_PROVIDED';
export type Tactic = {phrase:string;tactic:string;explanation:string;start:number;end:number};
export type Evidence = {source_id:string;url:string;publisher:string;document_date:string;title:string;evidence_text:string;relation:'contradicts'|'supports'|'context_only';retrieval_status:'live_fetched'|'verified_snapshot';sha256_hash:string;retrieved_at_utc:string};
export type Trace = {tool_name:string;input_summary:string;output_summary:string;status:'ok'|'warning'|'fallback';duration_ms:number};
export type Channel = {name:string;url_or_number:string;when_to_use:string};
export type Report = {report_id:string;signature:string;provider_status:Record<string,string>;verdict:Verdict;risk_level:'HIGH'|'MEDIUM'|'LOW';summary:string;language:Language;checks:{authority:Status;requested_action:Status;destination:Status};extracted:{raw_text_redacted:string;urls:string[];upi_ids:string[];amounts:string[];input_type:string;user_reported_loss:boolean};tactics:Tactic[];script_family:string|null;evidence:Evidence[];trace:Trace[];recommended_actions:string[];which_door_routing:Channel[];limitations:string[];report_hash:string;generated_at_utc:string;complaint:string};
