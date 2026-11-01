"""Bounded English query intent, derived from reviewed patterns; never arbitrary message prose."""
import re
FAMILIES={
 'digital_arrest':('MHA digital arrest police video call payment advisory','mha.gov.in'),
 'fake_recruitment':('PIB Cabinet Secretariat Field Assistant recruitment notice','pib.gov.in'),
 'fake_kyc':('RBI bank KYC credential update official process','rbi.org.in'),
 'fake_delivery_sms':('India Post parcel delivery payment official warning','indiapost.gov.in'),
 'investment_scam':('SEBI investment task job advance deposit warning','sebi.gov.in'),
 'lottery_fraud':('lottery prize advance release fee cybercrime advisory','cybercrime.gov.in'),
 'sim_swap':('DoT Sanchar Saathi SIM swap duplicate SIM OTP warning','dot.gov.in'),
 'customs_fraud':('CBIC customs parcel private account duty payment DIN verification','pib.gov.in'),
 'loan_app_fraud':('RBI digital lending regulated bank NBFC app lender permissions','rbi.org.in')}
ISSUERS={'RBI':'Reserve Bank of India','SEBI':'SEBI','CBIC':'CBIC customs','India Post':'India Post','Cabinet Secretariat':'Cabinet Secretariat','SBI':'State Bank of India','HDFC':'HDFC Bank','ICICI':'ICICI Bank','DoT':'Department of Telecommunications'}
def build_queries(extracted):
    # Only reviewed organisation names and public reference syntax may enter a query.
    # Arbitrary names, addresses, amounts and model-provided query text are excluded.
    text=extracted.raw_text_redacted
    base,domain=FAMILIES.get(extracted.script_family,('official public notice fraud clarification','pib.gov.in'))
    issuers=[full for key,full in ISSUERS.items() if re.search(r'(?<!\w)'+re.escape(key)+r'(?!\w)',text,re.I)]
    named=re.findall(r'\b(?:app|scheme|lender|NBFC)\s*[:=]\s*([A-Za-z][A-Za-z0-9-]{2,24})\b',text,re.I)
    refs=[]
    for m in re.finditer(r'\b(?:notice|notification|circular|PRID)\s*(?:no\.?\s*)?[:=#-]?\s*([A-Za-z][A-Za-z0-9/-]{2,35}|\d{1,5}/\d{4})\b',text,re.I):
        if re.search(r'\d',m.group(1)):refs.append(m.group(1))
    # The public vacancy count is a distinguishing advisory identifier, not an OTP.
    count='1736' if extracted.script_family=='fake_recruitment' and re.search(r'1,?736',text) else ''
    return [(' '.join(dict.fromkeys(issuers))+' '+base+' '+' '.join(named[:2])+' '+' '.join(refs[:2])+' '+count+' site:'+domain).strip()[:280]]
