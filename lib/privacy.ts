export function redact(text:string) {
 return text.replace(/\b(?:\d[ -]?){13,19}\b/g,'[REDACTED_CARD]').replace(/\b\d{4}[ -]?\d{4}[ -]?\d{4}\b/g,'[REDACTED_ID]').replace(/\b\d{12}\b/g,'[REDACTED_ID]').replace(/\b\d{6}\b/g,'[REDACTED_OTP]');
}
