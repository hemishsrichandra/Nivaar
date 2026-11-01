"""Auditable action patterns, including spoken English/Hindi/Kannada variants.

These assess the requested behaviour, not sender identity or factual truth.
Model-only tactic labels never promote a verdict.
"""
import re

CREDENTIAL=r'(?:o[ .-]*t[ .-]*p|one[ -]time (?:password|passcode)|(?:bank |banking |account |net banking )?(?:password|passcode|pin|cvv)|ओ\s*टी\s*पी|ओटीपी|पासवर्ड|पिन|ಒಟಿಪಿ|ಓಟಿಪಿ|ಪಾಸ್.?ವರ್ಡ್|ಪಿನ್)'
PAYMENT=r'\b(?:pay|send|transfer|deposit|recharge|remit)\b|भुगतान|पैसे\s*(?:भेज|जमा|ट्रांसफर)|ಹಣ\s*(?:ಕಳುಹಿ|ವರ್ಗಾಯಿ|ಪಾವತಿ)|ಪಾವತಿಸಿ|ಭರಿಸಿ|जमा करें|भेजिए'
EXTRA_RULES=[
 ('otp_or_credential_harvesting',rf'\b(?:tell|give|read|send|share|provide|reveal|confirm|dictate)\b\s+(?:(?:me|us|your|the|my|that|bank|banking|account|net banking|code|number)\s+){{0,5}}{CREDENTIAL}', 'A request to disclose a banking credential or one-time code can enable account access.'),
 ('otp_or_credential_harvesting',rf'{CREDENTIAL}\s*(?:को\s*)?(?:बताइए|बताओ|बताएं|भेजिए|भेजो|साझा करें|ಹೇಳಿ|ಹಂಚಿಕೊಳ್ಳಿ|ಕಳುಹಿಸಿ)', 'The message asks you to disclose a private credential.'),
 ('remote_access_app',r'\b(?:download|install|open|run)\s+(?:the\s+)?(?:any\s*desk|team\s*viewer|quick\s*support|rust\s*desk)|(?:share|give|allow|enable).{0,35}(?:remote access|screen access|screen control)|(?:anydesk|teamviewer|एनीडेस्क|ಎನಿಡೆಸ್ಕ್).{0,25}(?:इंस्टॉल|डाउनलोड|स्थापित|ಡೌನ್ಲೋಡ್|ಇನ್ಸ್ಟಾಲ್)', 'A remote-control request can expose the device and financial accounts.'),
 ('fear_of_arrest',r'\b(?:arrest|arrested|jail|prison|legal action|police case)\b|गिरफ्तार|जेल|ಬಂಧನ|ಜೈಲು', 'Threats of arrest combined with payment demands indicate coercion.'),
 ('payment_redirection',r'\b(?:safe|verification|security|reserve bank)\s+(?:bank\s+)?account\b|सुरक्षित खाता|ವೆರಿಫಿಕೇಶನ್ ಖಾತೆ', 'Moving money to a so-called safe or verification account is a dangerous request.'),
 ('too_good_returns',r'\b(?:guaranteed|assured|risk[ -]free)\s+(?:daily\s+)?(?:profit|returns?|income)|\bdouble\s+(?:your\s+)?money\b', 'Promised guaranteed profits need independent scrutiny.'),
]

def negated_or_advisory(text,start,end):
    # Scope to the current clause so a genuine warning cannot hide a later demand.
    prefix=re.split(r'[.!?।;\n]|\bbut\b|\bhowever\b|\binstead\b',text[:start],flags=re.I)[-1][-130:]
    if re.search(r"\b(?:never|do not|don[’']t|must not|should not|cannot|won[’']t)\b|no such thing|मत\s|नहीं|ಬೇಡ|ಬಾರದು",prefix,re.I):return True
    if re.search(r'\b(?:beware|warning|avoid|scammers?|fraudsters?)\b|सावधान|ಎಚ್ಚರಿಕೆ',prefix,re.I):return True
    return bool(re.match(r'\s*(?:न\s*(?:करें|करना)|मत\s*करें|नहीं|ಬೇಡಿ|ಬಾರದು)',text[end:end+30],re.I))

def active_matches(pattern,text):
    return [m for m in re.finditer(pattern,text,re.I) if not negated_or_advisory(text,m.start(),m.end())]

def behavioural_risk(extracted):
    text=extracted.raw_text_redacted
    types={t.tactic for t in extracted.tactics if t.origin=='rule'}
    payment=bool(active_matches(PAYMENT,text))
    # Strong compound signals must describe an instruction, not just a topic.
    arrest=bool(active_matches(r'(?:you (?:are|have been)|put you|placing you).{0,25}digital arrest|आप.{0,25}डिजिटल अरेस्ट|ನೀವು.{0,25}ಡಿಜಿಟಲ್ ಅರೆಸ್ಟ್',text))
    customs_context=bool(re.search(r'customs|CBIC|कस्टम्स|सीमा शुल्क|ಕಸ್ಟಮ್ಸ್',text,re.I))
    clauses=re.split(r'[.!?।;\n]+',text)
    customs_private=customs_context and any(active_matches(PAYMENT,clause) and active_matches(r'(?:private|personal|निजी|व्यक्तिगत|ವೈಯಕ್ತಿಕ).{0,50}(?:account|खात|ಖಾತ)',clause) for clause in clauses)
    safe_account=payment and bool(active_matches(r'(?:safe|verification|security|reserve bank)\s+(?:bank\s+)?account',text))
    task=payment and bool(active_matches(r'(?:task|rating|review|part.time|commission).{0,150}(?:deposit|recharge|pay|transfer)|(?:deposit|recharge).{0,150}(?:unlock|withdraw|commission)',text))
    advance=payment and bool(active_matches(r'(?:won|win|claim|release|receive|unlock|collect).{0,100}(?:lottery|prize|winnings)|(?:lottery|prize|winnings).{0,100}(?:release|processing|verification|fee|tax)',text))
    loan=payment and bool(active_matches(r'(?:advance|activation|release) fee.{0,100}(?:release|approve|disburse).{0,35}loan|(?:release|approve|disburse).{0,35}loan.{0,100}(?:advance|activation) fee',text))
    guaranteed=payment and 'too_good_returns' in types and bool(active_matches(r'\binvest\b|trading|double.{0,20}money',text))
    reasons=[]
    for present,reason in [
        ('otp_or_credential_harvesting' in types,'The message asks you to disclose an OTP, PIN or password.'),
        ('remote_access_app' in types,'The message asks for remote access or screen control.'),
        (arrest,'The message claims you are under digital arrest.'),
        (customs_private,'The message asks for a customs payment into an explicitly personal or private account.'),
        (safe_account,'The message asks you to move money into a so-called safe or verification account.'),
        (payment and bool(types & {'fear_of_arrest','secrecy_or_isolation'}),'A payment demand is combined with threats or secrecy.'),
        (task,'A task or commission payout requires a deposit or recharge first.'),
        (advance,'A claimed lottery or prize payout requires an advance payment.'),
        (loan,'An advance fee is demanded to release or approve a loan.'),
        (guaranteed,'A payment or investment request promises guaranteed profits.'),
    ]:
        if present:reasons.append(reason)
    high=bool(reasons or types & {'fear_of_arrest','secrecy_or_isolation','too_good_returns'})
    return ('DANGEROUS' if reasons else 'SUSPICIOUS' if payment or high else 'NOT_PROVIDED'),high,reasons
