"""Localized explanations; raw claims, identifiers and official quotes are never translated."""
PAIRS={
'How much of this message we could verify':('इस संदेश का कितना हिस्सा हम जाँच सके','ಈ ಸಂದೇಶದ ಎಷ್ಟು ಭಾಗವನ್ನು ಪರಿಶೀಲಿಸಲು ಸಾಧ್ಯವಾಯಿತು'),
'Evidence coverage is not a probability of fraud or safety. Low coverage is not proof of fraud.':('प्रमाण कवरेज धोखाधड़ी या सुरक्षा की संभावना नहीं है। कम कवरेज धोखाधड़ी का प्रमाण नहीं है।','ಪುರಾವೆಯ ವ್ಯಾಪ್ತಿ ವಂಚನೆ ಅಥವಾ ಸುರಕ್ಷತೆಯ ಸಂಭವನೀಯತೆ ಅಲ್ಲ. ಕಡಿಮೆ ವ್ಯಾಪ್ತಿ ವಂಚನೆಯ ಪುರಾವೆ ಅಲ್ಲ.'),
'Public sources cannot establish this private event.':('सार्वजनिक स्रोत इस निजी घटना की पुष्टि नहीं कर सकते।','ಸಾರ್ವಜನಿಕ ಮೂಲಗಳು ಈ ಖಾಸಗಿ ಘಟನೆಯನ್ನು ದೃಢೀಕರಿಸಲಾರವು.'),
'Official passages disagree; both are shown. No precedence rule resolves this conflict.':('आधिकारिक अंशों में विरोध है; दोनों दिखाए गए हैं। यह विरोध सुलझा नहीं है।','ಅಧಿಕೃತ ಅಂಶಗಳು ಪರಸ್ಪರ ವಿರೋಧಿಸುತ್ತವೆ; ಎರಡನ್ನೂ ತೋರಿಸಲಾಗಿದೆ. ಈ ವಿರೋಧ ಬಗೆಹರಿದಿಲ್ಲ.'),
'Relevant fetched passage directly addresses this claim.':('प्राप्त संबंधित अंश इस दावे को सीधे संबोधित करता है।','ಪಡೆದ ಸಂಬಂಧಿತ ಅಂಶ ಈ ಹೇಳಿಕೆಯನ್ನು ನೇರವಾಗಿ ಉದ್ದೇಶಿಸುತ್ತದೆ.'),
'No sufficiently specific matching passage was located. This does not mean the claim is false.':('पर्याप्त विशिष्ट मेल खाता अंश नहीं मिला। इसका अर्थ दावा गलत होना नहीं है।','ಸಾಕಷ್ಟು ನಿರ್ದಿಷ್ಟವಾಗಿ ಹೊಂದುವ ಅಂಶ ಸಿಗಲಿಲ್ಲ. ಇದರಿಂದ ಹೇಳಿಕೆ ತಪ್ಪೆಂದು ಸಾಬೀತಾಗುವುದಿಲ್ಲ.'),
'Sender identity is not authenticated.':('भेजने वाले की पहचान प्रमाणित नहीं है।','ಕಳುಹಿಸಿದವರ ಗುರುತನ್ನು ದೃಢೀಕರಿಸಿಲ್ಲ.'),
'Checks may be incomplete; inspect provider availability.':('जाँच अधूरी हो सकती है; सेवा की उपलब्धता देखें।','ಪರಿಶೀಲನೆ ಅಪೂರ್ಣವಾಗಿರಬಹುದು; ಸೇವೆಯ ಲಭ್ಯತೆ ನೋಡಿ.'),
'Exact public content is corroborated by the cited official material.':('ठीक इसी सार्वजनिक सामग्री का उद्धृत आधिकारिक प्रमाण से समर्थन मिलता है।','ಇದೇ ಸಾರ್ವಜನಿಕ ವಿಷಯಕ್ಕೆ ಉಲ್ಲೇಖಿಸಿದ ಅಧಿಕೃತ ಅಂಶ ಬೆಂಬಲ ನೀಡುತ್ತದೆ.'),
'Specific official evidence contradicts a material claim.':('विशिष्ट आधिकारिक प्रमाण एक महत्वपूर्ण दावे का खंडन करता है।','ನಿರ್ದಿಷ್ಟ ಅಧಿಕೃತ ಪುರಾವೆ ಮುಖ್ಯ ಹೇಳಿಕೆಯನ್ನು ವಿರೋಧಿಸುತ್ತದೆ.'),
'The precise issuer/content relationship has not been established.':('जारी करने वाली संस्था और ठीक इस सामग्री का संबंध स्थापित नहीं हुआ है।','ನಿರ್ದಿಷ್ಟ ವಿಷಯ ಮತ್ತು ನೀಡಿದ ಸಂಸ್ಥೆಯ ಸಂಬಂಧ ಸ್ಥಾಪಿತವಾಗಿಲ್ಲ.'),
'A document match does not authenticate the sender or a private account.':('दस्तावेज़ से मेल भेजने वाले या निजी खाते की पहचान प्रमाणित नहीं करता।','ದಾಖಲೆ ಹೊಂದಾಣಿಕೆ ಕಳುಹಿಸಿದವರ ಅಥವಾ ಖಾಸಗಿ ಖಾತೆಯ ಗುರುತನ್ನು ದೃಢೀಕರಿಸುವುದಿಲ್ಲ.'),
'A credential/remote access request or coercive payment pattern was found.':('गोपनीय जानकारी, रिमोट एक्सेस या दबाव देकर भुगतान का अनुरोध मिला।','ಗೌಪ್ಯ ಮಾಹಿತಿ, ರಿಮೋಟ್ ಪ್ರವೇಶ ಅಥವಾ ಒತ್ತಾಯದ ಪಾವತಿ ವಿನಂತಿ ಕಂಡುಬಂದಿದೆ.'),
'Requested action remains unverified.':('अनुरोधित कार्रवाई की पुष्टि नहीं हुई है।','ಕೋರಿದ ಕ್ರಮ ದೃಢೀಕರಿಸಲ್ಪಟ್ಟಿಲ್ಲ.'),
'No actionable instruction was identified.':('कार्रवाई का निर्देश नहीं मिला।','ಕ್ರಮ ಕೈಗೊಳ್ಳುವ ಸೂಚನೆ ಕಂಡುಬಂದಿಲ್ಲ.'),
'Pattern inference is separate from an issuer-confirmed process.':('पैटर्न पर आधारित अनुमान संस्था द्वारा पुष्ट प्रक्रिया से अलग है।','ಮಾದರಿಯ ಆಧಾರದ ನಿರ್ಣಯ ಸಂಸ್ಥೆ ದೃಢೀಕರಿಸಿದ ಪ್ರಕ್ರಿಯೆಯಿಂದ ಪ್ರತ್ಯೇಕವಾಗಿದೆ.'),
'Phone/payment identifiers were supplied, but no authorised source establishes their ownership or purpose.':('फोन या भुगतान विवरण दिए गए हैं, लेकिन अधिकृत स्रोत इनके मालिक या उद्देश्य की पुष्टि नहीं करता।','ಫೋನ್ ಅಥವಾ ಪಾವತಿ ವಿವರಗಳಿವೆ, ಆದರೆ ಅಧಿಕೃತ ಮೂಲ ಅವುಗಳ ಮಾಲೀಕತ್ವ ಅಥವಾ ಉದ್ದೇಶ ದೃಢೀಕರಿಸುವುದಿಲ್ಲ.'),
'No destination was supplied.':('कोई गंतव्य नहीं दिया गया।','ಯಾವುದೇ ಗಮ್ಯಸ್ಥಾನ ನೀಡಲಾಗಿಲ್ಲ.'),
'No phone subscriber or UPI ownership lookup. Absence from a threat list does not establish safety.':('फोन ग्राहक या UPI मालिक की जाँच नहीं की गई। खतरे की सूची में न होना सुरक्षा का प्रमाण नहीं है।','ಫೋನ್ ಗ್ರಾಹಕ ಅಥವಾ UPI ಮಾಲೀಕತ್ವ ಪರಿಶೀಲನೆ ಇಲ್ಲ. ಅಪಾಯ ಪಟ್ಟಿಯಲ್ಲಿ ಇಲ್ಲದಿರುವುದು ಸುರಕ್ಷತೆಯ ಪುರಾವೆ ಅಲ್ಲ.'),
'Material claims':('महत्वपूर्ण दावे','ಮುಖ್ಯ ಹೇಳಿಕೆಗಳು'),'Authority':('दावा की गई संस्था','ಹೇಳಲಾದ ಸಂಸ್ಥೆ'),'Requested action':('अनुरोधित कार्रवाई','ಕೋರಿದ ಕ್ರಮ'),'Destination':('गंतव्य','ಗಮ್ಯಸ್ಥಾನ'),
'Local risk patterns do not establish the issuer’s actual procedure.':('स्थानीय जोखिम पैटर्न संस्था की वास्तविक प्रक्रिया स्थापित नहीं करते।','ಸ್ಥಳೀಯ ಅಪಾಯ ಮಾದರಿಗಳು ಸಂಸ್ಥೆಯ ನಿಜವಾದ ಪ್ರಕ್ರಿಯೆಯನ್ನು ಸ್ಥಾಪಿಸುವುದಿಲ್ಲ.'),
'Syntax/reputation checks do not verify the recipient or purpose.':('प्रारूप या प्रतिष्ठा की जाँच प्राप्तकर्ता या उद्देश्य की पुष्टि नहीं करती।','ರೂಪ ಅಥವಾ ಖ್ಯಾತಿಯ ಪರಿಶೀಲನೆ ಸ್ವೀಕರಿಸುವವರನ್ನು ಅಥವಾ ಉದ್ದೇಶವನ್ನು ದೃಢೀಕರಿಸುವುದಿಲ್ಲ.')}
PAIRS.update({
'Fraction with relevant validated source relations; capped at partial if AI extraction/comparison was unavailable.':('संबंधित सत्यापित प्रमाण वाले दावों का अंश; AI जाँच उपलब्ध न होने पर आंशिक तक सीमित।','ಸಂಬಂಧಿತ ದೃಢೀಕೃತ ಪುರಾವೆ ಹೊಂದಿರುವ ಹೇಳಿಕೆಗಳ ಭಾಗ; AI ಪರಿಶೀಲನೆ ಇಲ್ಲದಿದ್ದರೆ ಭಾಗಶಃ ಮಾತ್ರ.'),
'Scoped source relation; document identity does not authenticate a caller.':('सीमित दायरे में स्रोत से संबंध; दस्तावेज़ कॉलर की पहचान प्रमाणित नहीं करता।','ನಿರ್ದಿಷ್ಟ ವ್ಯಾಪ್ತಿಯ ಮೂಲ ಸಂಬಂಧ; ದಾಖಲೆ ಕರೆ ಮಾಡಿದವರ ಗುರುತನ್ನು ದೃಢೀಕರಿಸುವುದಿಲ್ಲ.'),
'This phone/message customs-duty demand into an explicitly private account conflicts with the cited CBIC process warning.':('फोन या संदेश में निजी खाते में सीमा शुल्क माँगना उद्धृत CBIC चेतावनी से विरोध रखता है।','ಫೋನ್ ಅಥವಾ ಸಂದೇಶದ ಮೂಲಕ ಖಾಸಗಿ ಖಾತೆಗೆ ಕಸ್ಟಮ್ಸ್ ಶುಲ್ಕ ಕೇಳುವುದು ಉಲ್ಲೇಖಿಸಿದ CBIC ಎಚ್ಚರಿಕೆಗೆ ವಿರುದ್ಧವಾಗಿದೆ.'),
'Cited CBIC guidance contradicts this exact requested process.':('उद्धृत CBIC मार्गदर्शन ठीक इस अनुरोधित प्रक्रिया का खंडन करता है।','ಉಲ್ಲೇಖಿಸಿದ CBIC ಮಾರ್ಗದರ್ಶನ ಇದೇ ಕೋರಿದ ಪ್ರಕ್ರಿಯೆಯನ್ನು ವಿರೋಧಿಸುತ್ತದೆ.')})
def localize(ledger,assessments,coverage,language):
 if language=='en':return
 index=0 if language=='hi' else 1
 tr=lambda s:PAIRS.get(s,(s,s))[index]
 for c in ledger:c.explanation=tr(c.explanation);c.limitations=[tr(l) for l in c.limitations]
 for a in assessments.values():a.reason=tr(a.reason);a.limitation=tr(a.limitation)
 coverage.label=tr(coverage.label);coverage.note=tr(coverage.note)
 for c in coverage.components:c.name=tr(c.name);c.explanation=tr(c.explanation)
