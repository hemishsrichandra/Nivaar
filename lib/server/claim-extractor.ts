import type {Tactic,Language} from '../types';
const rules:[string,RegExp,string][]=[
 ['authority_impersonation',/\b(?:CBI|Mumbai Police|police officer|Cabinet Secretariat|Reserve Bank|RBI|India Post)\b|सीबीआई|पुलिस|ಪೊಲೀಸ್|ಸಿಬಿಐ/gi,'An authority name can be used to borrow trust. The name alone does not authenticate the sender.'],
 ['fear_of_arrest',/digital arrest|arrest warrant|under arrest|arrest you|डिजिटल अरेस्ट|गिरफ्तार|ಬಂಧನ|ಡಿಜಿಟಲ್ ಅರೆಸ್ಟ್/gi,'Threats of arrest pressure you to comply before verifying.'],
 ['urgency',/immediately|within \d+ (?:minutes|hours)|urgent|last chance|आज ही|तुरंत|ತಕ್ಷಣ|ಕೂಡಲೇ/gi,'A short deadline reduces the time you have to check the claim.'],
 ['secrecy_or_isolation',/do not (?:tell|inform|share with) (?:anyone|your family)|keep (?:this )?(?:secret|confidential)|किसी को मत बताना|गुप्त|ಯಾರಿಗೂ ಹೇಳಬೇಡಿ|ಗೌಪ್ಯ/gi,'Keeping you isolated prevents others from questioning the request.'],
 ['payment_redirection',/transfer (?:the )?(?:money|funds|₹?[\d,]+)|security deposit|verification fee|safe account|verification account|RTGS|पैसे भेज|पैसे ट्रांसफर|ಹಣ ಕಳುಹಿಸಿ|ಹಣ ವರ್ಗಾಯಿಸಿ/gi,'A request to move money needs independent verification.'],
 ['too_good_returns',/guaranteed returns|double your money|risk.free profit|गारंटीड रिटर्न|खाता दोगुना|ಖಚಿತ ಲಾಭ/gi,'Guaranteed or unusually large returns are a warning sign.'],
 ['otp_or_credential_harvesting',/(?:share|send|tell|provide|enter|reveal) (?:your |the )?(?:OTP|PIN|password)|OTP (?:बताएं|भेजें|ಬಿಡಿ|ಕಳುಹಿಸಿ)|ओटीपी (?:बताएं|भेजें)|ಪಿನ್ ಕಳುಹಿಸಿ/gi,'Sharing a one-time password, PIN or password can give someone access to your money.'],
 ['remote_access_app',/install (?:the )?(?:APK|AnyDesk|TeamViewer)|screen.shar(?:e|ing)|स्क्रीन शेयर|ಸ್ಕ್ರೀನ್ ಶೇರ್/gi,'Remote access or screen sharing can expose your banking details.'],
 ['link_lure',/https?:\/\/[^\s<>]+|(?:[a-z0-9-]+\.)+(?:top|xyz|click|gov\.in|org\.in)\/[^\s<>]*/gi,'The destination must be checked independently; a familiar name in a link proves nothing.']
];
export function extract(text:string){
 const tactics:Tactic[]=[];
 for(const [tactic,re,explanation] of rules){for(const m of text.matchAll(re)){tactics.push({phrase:m[0],tactic,explanation,start:m.index!,end:m.index!+m[0].length});}}
 const family=/digital arrest|arrest warrant|डिजिटल अरेस्ट|गिरफ्तार|ಬಂಧನ|ಡಿಜಿಟಲ್ ಅರೆಸ್ಟ್/i.test(text)?'digital_arrest':/1736|1,736|Field Assistant/i.test(text)?'fake_recruitment':/India Post|parcel|डाक|ಅಂಚೆ/i.test(text)?'fake_delivery_sms':/KYC|RBI|bank verification/i.test(text)?'fake_kyc':/investment|trading|returns|ನಿವೇಶ|निवेश/i.test(text)?'investment_scam':null;
 const urls=[...new Set([...text.matchAll(/https?:\/\/[^\s<>"']+|\b(?:[a-z0-9-]+\.)+(?:top|xyz|click|com|in|org|net)(?:\/[^\s<>"']*)?/gi)].map(m=>(/^https?:/i.test(m[0])?'':'https://')+m[0].replace(/[.,;!?)]+$/,'')))];
 const language:Language=/[\u0c80-\u0cff]/.test(text)?'kn':/[\u0900-\u097f]/.test(text)?'hi':'en';
 return {tactics,family,urls,language,amounts:[...text.matchAll(/(?:₹|Rs\.?|INR)\s?[\d,]+/gi)].map(m=>m[0]),upi_ids:[...text.matchAll(/\b[a-z\d._-]+@(?:upi|ybl|paytm|ok[a-z]+|ibl|axl)\b/gi)].map(m=>m[0])};
}
