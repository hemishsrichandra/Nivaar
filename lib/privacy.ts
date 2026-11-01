export function redact(text:string) {
 const phones:string[]=[];
 text=text.replace(/\+\d[\d -]{6,20}\d(?!\d)/g,raw=>{const digits=raw.replace(/\D/g,'');if(digits.length<8||digits.length>15)return raw;phones.push(raw);return `[PHONE_TOKEN_${phones.length-1}]`;});
 const masked=text.replace(/\b(?:\d[ -]?){13,19}\b/g,'[REDACTED_CARD]').replace(/\b\d{4}[ -]?\d{4}[ -]?\d{4}\b/g,'[REDACTED_ID]').replace(/\b\d{12}\b/g,'[REDACTED_ID]').replace(/\b\d{6}\b/g,'[REDACTED_OTP]');
 return masked.replace(/\[PHONE_TOKEN_(\d+)\]/g,(_,i)=>phones[Number(i)]);
}
