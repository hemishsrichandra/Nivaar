from backend.schemas import ReportingChannel
TEXT={
'en':{
 'SCAM':'Dangerous signals or contradictory official evidence were found. Do not pay, share credentials, or follow the supplied links. Verify the sender independently.',
 'GENUINE':'The factual content matches the official sources listed below. Always verify the sender independently before taking financial action.',
 'UNSURE':'There is not enough corroborating evidence to verify every material claim. Do not pay or follow links until independently confirmed.',
 'normal':['Pause the conversation. Do not send money or share an OTP.','Contact the organisation through an independently found official channel.','Preserve the message and report suspected fraud through the appropriate portal.'],
 'loss':['Call 1930 promptly and contact your bank using its official fraud number.','Block compromised cards or accounts and change exposed passwords.','Preserve messages, transaction references and complaint acknowledgements.'],
 'genuine':['Read the official source directly. Verified content does not authenticate the sender.','Independently verify any separate payment, link or credential request.'],
 'complaint':'Suspected cyber fraud report','message':'Original message (sensitive number patterns redacted)','loss_label':'Money or credentials shared','yes':'Yes, user reported','no':'Not reported','review':'Please investigate. I will add sender details, dates, transaction references, amount and supporting screenshots before filing.'},
'hi':{
 'SCAM':'खतरे के संकेत या विरोधाभासी आधिकारिक प्रमाण मिले हैं। भुगतान न करें, OTP या पासवर्ड न बताएं और भेजे गए लिंक न खोलें। भेजने वाले की स्वतंत्र पुष्टि करें।',
 'GENUINE':'तथ्यात्मक सामग्री नीचे दिए आधिकारिक स्रोतों से मेल खाती है। वित्तीय कार्रवाई से पहले भेजने वाले की स्वतंत्र पुष्टि करें।',
 'UNSURE':'सभी महत्वपूर्ण दावों की पुष्टि के लिए पर्याप्त प्रमाण नहीं हैं। स्वतंत्र पुष्टि होने तक भुगतान न करें और लिंक न खोलें।',
 'normal':['बातचीत रोकें। पैसे या OTP साझा न करें।','स्वतंत्र रूप से मिले आधिकारिक माध्यम से संस्था से संपर्क करें।','संदेश सुरक्षित रखें और उचित पोर्टल पर संदिग्ध धोखाधड़ी रिपोर्ट करें।'],
 'loss':['तुरंत 1930 पर कॉल करें और अपने बैंक के आधिकारिक धोखाधड़ी नंबर पर संपर्क करें।','प्रभावित कार्ड या खाते ब्लॉक कराएँ और उजागर पासवर्ड बदलें।','संदेश, लेनदेन संदर्भ और शिकायत की पावती सुरक्षित रखें।'],
 'genuine':['आधिकारिक स्रोत सीधे पढ़ें। सामग्री की पुष्टि भेजने वाले की पहचान की पुष्टि नहीं है।','भुगतान, लिंक या निजी जानकारी के किसी अलग अनुरोध की स्वतंत्र पुष्टि करें।'],
 'complaint':'संदिग्ध साइबर धोखाधड़ी की रिपोर्ट','message':'मूल संदेश (संवेदनशील संख्या पैटर्न छिपाए गए)','loss_label':'धन या जानकारी साझा की गई','yes':'हाँ, उपयोगकर्ता ने बताया','no':'नहीं बताया गया','review':'कृपया जाँच करें। शिकायत से पहले मैं भेजने वाले का विवरण, तारीख, लेनदेन संदर्भ, राशि और स्क्रीनशॉट जोड़ूँगा।'},
'kn':{
 'SCAM':'ಅಪಾಯದ ಸೂಚನೆಗಳು ಅಥವಾ ವಿರುದ್ಧ ಅಧಿಕೃತ ಪುರಾವೆ ಕಂಡುಬಂದಿದೆ. ಹಣ ಪಾವತಿಸಬೇಡಿ, OTP ಅಥವಾ ಪಾಸ್‌ವರ್ಡ್ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ ಮತ್ತು ಕಳುಹಿಸಿದ ಲಿಂಕ್ ತೆರೆಯಬೇಡಿ. ಕಳುಹಿಸಿದವರನ್ನು ಸ್ವತಂತ್ರವಾಗಿ ಪರಿಶೀಲಿಸಿ.',
 'GENUINE':'ವಾಸ್ತವಿಕ ವಿಷಯವು ಕೆಳಗಿನ ಅಧಿಕೃತ ಮೂಲಗಳಿಗೆ ಹೊಂದಿಕೆಯಾಗುತ್ತದೆ. ಹಣಕಾಸಿನ ಕ್ರಮದ ಮೊದಲು ಕಳುಹಿಸಿದವರನ್ನು ಸ್ವತಂತ್ರವಾಗಿ ಪರಿಶೀಲಿಸಿ.',
 'UNSURE':'ಎಲ್ಲ ಪ್ರಮುಖ ಹೇಳಿಕೆಗಳನ್ನು ದೃಢೀಕರಿಸಲು ಸಾಕಷ್ಟು ಪುರಾವೆಗಳಿಲ್ಲ. ಸ್ವತಂತ್ರವಾಗಿ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳುವವರೆಗೆ ಹಣ ಪಾವತಿಸಬೇಡಿ ಅಥವಾ ಲಿಂಕ್ ತೆರೆಯಬೇಡಿ.',
 'normal':['ಸಂಭಾಷಣೆ ನಿಲ್ಲಿಸಿ. ಹಣ ಅಥವಾ OTP ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.','ಸ್ವತಂತ್ರವಾಗಿ ಕಂಡುಕೊಂಡ ಅಧಿಕೃತ ಮಾರ್ಗದಿಂದ ಸಂಸ್ಥೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.','ಸಂದೇಶ ಉಳಿಸಿ ಮತ್ತು ಸೂಕ್ತ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಶಂಕಿತ ವಂಚನೆಯನ್ನು ವರದಿ ಮಾಡಿ.'],
 'loss':['ತಕ್ಷಣ 1930 ಕರೆ ಮಾಡಿ ಮತ್ತು ಬ್ಯಾಂಕಿನ ಅಧಿಕೃತ ವಂಚನೆ ವಿಭಾಗವನ್ನು ಸಂಪರ್ಕಿಸಿ.','ಅಪಾಯದಲ್ಲಿರುವ ಕಾರ್ಡ್ ಅಥವಾ ಖಾತೆ ತಡೆಹಿಡಿಯಿರಿ ಮತ್ತು ಪಾಸ್‌ವರ್ಡ್ ಬದಲಿಸಿ.','ಸಂದೇಶ, ವ್ಯವಹಾರದ ಉಲ್ಲೇಖ ಮತ್ತು ದೂರಿನ ಸ್ವೀಕೃತಿ ಉಳಿಸಿಕೊಳ್ಳಿ.'],
 'genuine':['ಅಧಿಕೃತ ಮೂಲವನ್ನು ನೇರವಾಗಿ ಓದಿ. ವಿಷಯದ ಪರಿಶೀಲನೆ ಕಳುಹಿಸಿದವರ ಗುರುತನ್ನು ದೃಢೀಕರಿಸುವುದಿಲ್ಲ.','ಪ್ರತ್ಯೇಕ ಹಣ ಪಾವತಿ, ಲಿಂಕ್ ಅಥವಾ ಗೌಪ್ಯ ಮಾಹಿತಿಯ ವಿನಂತಿಯನ್ನು ಸ್ವತಂತ್ರವಾಗಿ ಪರಿಶೀಲಿಸಿ.'],
 'complaint':'ಶಂಕಿತ ಸೈಬರ್ ವಂಚನೆ ವರದಿ','message':'ಮೂಲ ಸಂದೇಶ (ಸಂವೇದನಾಶೀಲ ಸಂಖ್ಯೆ ಮಾದರಿಗಳನ್ನು ಮರೆಮಾಡಲಾಗಿದೆ)','loss_label':'ಹಣ ಅಥವಾ ಮಾಹಿತಿ ಹಂಚಿಕೊಂಡಿರುವುದು','yes':'ಹೌದು, ಬಳಕೆದಾರರು ತಿಳಿಸಿದ್ದಾರೆ','no':'ತಿಳಿಸಿಲ್ಲ','review':'ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ. ದೂರು ಸಲ್ಲಿಸುವ ಮೊದಲು ಕಳುಹಿಸಿದವರ ವಿವರ, ದಿನಾಂಕ, ವ್ಯವಹಾರದ ಉಲ್ಲೇಖ, ಮೊತ್ತ ಮತ್ತು ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಸೇರಿಸುತ್ತೇನೆ.'}}
def guidance(verdict,language,extracted,evidence,generated):
    t=TEXT[language];loss=extracted.user_reported_loss
    summary=t[verdict]
    if verdict=='GENUINE':summary+=' '+'; '.join(dict.fromkeys(e.publisher for e in evidence if e.relation=='supports'))
    actions=t['loss'] if loss else t['genuine'] if verdict=='GENUINE' else t['normal']
    complaint=f"{t['complaint']}\nUTC: {generated}\n{t['message']}:\n{extracted.raw_text_redacted}\n{t['loss_label']}: {t['yes'] if loss else t['no']}\n{t['review']}"
    channels=[]
    if loss:
        channels=[ReportingChannel(name='Call 1930',url_or_number='tel:1930',when_to_use='Report financial cyber fraud promptly.'),ReportingChannel(name='Cybercrime portal',url_or_number='https://cybercrime.gov.in/',when_to_use='File a cybercrime report and preserve the acknowledgement.')]
    elif verdict=='GENUINE':
        channels=[ReportingChannel(name='Read official record',url_or_number=e.url,when_to_use='Read the verified content directly.') for e in evidence[:2]]
    else:channels=[ReportingChannel(name='Report on Chakshu',url_or_number='https://www.sancharsaathi.gov.in/sfc/Home/sfc-complaint.jsp',when_to_use='Suspected fraudulent call, SMS or WhatsApp; no financial loss reported.')]
    if extracted.script_family=='investment_scam':channels.append(ReportingChannel(name='SEBI Check',url_or_number='https://siportal.sebi.gov.in/intermediary/sebi-check',when_to_use='Check an intermediary payment destination independently.'))
    if extracted.urls and verdict!='GENUINE':channels.append(ReportingChannel(name='Report suspicious link',url_or_number='https://sancharsaathi.gov.in/sfc/Home/murl-complaint.jsp',when_to_use='Report a suspected fraudulent web link.'))
    if extracted.claimed_authority and verdict!='GENUINE':channels.append(ReportingChannel(name='PIB Fact Check',url_or_number='https://factcheck.pib.gov.in/',when_to_use='Central government claim or impersonation.'))
    for c in channels:c.draft_complaint=complaint
    return summary,actions,complaint,channels
