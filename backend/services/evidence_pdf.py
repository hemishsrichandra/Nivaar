from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from backend.config import ROOT
from backend.services.report_integrity import canonical
FONTS=ROOT/'assets/fonts'
def styled_text(text):
    return escape(str(text)).replace('\n','<br/>')
def build_pdf(report):
    if 'NivaarUnicode' not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont('NivaarUnicode',str(FONTS/'NivaarUnicode.ttf'),shapable=True))
    out=BytesIO();doc=SimpleDocTemplate(out,pagesize=(595,842),rightMargin=43,leftMargin=43,topMargin=45,bottomMargin=48,title='Nivaar Evidence Pack',author='Nivaar')
    styles=getSampleStyleSheet();body=ParagraphStyle('NivaarBody',fontName='NivaarUnicode',fontSize=9,leading=15,textColor=colors.HexColor('#30483d'),spaceAfter=8,shaping=1,splitLongWords=True)
    heading=ParagraphStyle('NivaarHeading',parent=body,fontSize=14,leading=19,spaceBefore=16,spaceAfter=10,textColor=colors.HexColor('#245c43'))
    tiny=ParagraphStyle('NivaarTiny',parent=body,fontSize=7,leading=11,textColor=colors.HexColor('#657365'))
    story=[]
    def p(text,style=body):story.append(Paragraph(styled_text(text),style))
    p('NIVAAR | Evidence & reporting pack',heading)
    p(f'{report.verdict} | {report.risk_level} risk',heading)
    p(f'Generated UTC: {report.generated_at_utc}',tiny)
    p(f'Report ID: {report.report_id}',tiny);p(f'Canonical report SHA-256: {report.report_hash}',tiny)
    p('Automated guidance, not a legal certificate. Hashes provide integrity checks, not proof of an offence. Sender identity has not been authenticated.',tiny)
    p(report.summary)
    p('Redacted message',heading);p(report.extracted.raw_text_redacted)
    p('Dimension checks',heading)
    for k,v in report.checks.model_dump().items():p(f'{k.replace("_"," ").title()}: {v}')
    if report.evidence_coverage.components:
        p('Evidence Coverage',heading)
        p(f'{report.evidence_coverage.score if report.evidence_coverage.score is not None else "—"}/100 — {report.evidence_coverage.label}')
        p(report.evidence_coverage.note,tiny)
        for c in report.evidence_coverage.components:p(f'{c.name}: {c.completed if c.applicable else "N/A"}. {c.explanation}',tiny)
    if report.claims:
        p('Claim-by-claim evidence',heading)
        for c in report.claims:
            p(f'{c.claim_id}: {c.status} — {c.text}')
            p(c.explanation);p('Evidence IDs: '+(', '.join(c.evidence_ids) or 'None'),tiny)
    if report.source_conflicts:p('Unresolved official-source conflicts: '+', '.join(report.source_conflicts))
    p('User-confirmed situation: '+report.user_situation)
    p('Tactics',heading)
    if not report.tactics:p('No matching manipulation spans. This does not prove authenticity.')
    for t in report.tactics:p(f'{t.tactic.replace("_"," ")}: “{t.phrase}” — {t.explanation}')
    p('Identifiers preserved in the redacted report',heading)
    for k in ('urls','upi_ids','phone_numbers','amounts','deadlines'):
        v=getattr(report.extracted,k)
        if v:p(k.replace('_',' ').title()+': '+', '.join(v))
    p('Official evidence',heading)
    if not report.evidence:p('No corroborating official document was fetched.')
    for e in report.evidence:
        p((e.evidence_id+' | ' if e.evidence_id else '')+e.publisher+' — '+e.title,heading);p(e.url,tiny);p(f'{e.document_date or "Date unavailable"} | {e.relation} | {e.fetch_status}',tiny);p(e.evidence_text);p('Document text SHA-256: '+e.sha256_hash,tiny);p('Retrieved UTC: '+e.retrieved_at_utc,tiny)
    p('Next actions',heading)
    for i,a in enumerate(report.recommended_actions,1):p(f'{i}. {a}')
    for c in report.which_door_routing:p(c.name+' — '+c.url_or_number+'\n'+c.when_to_use)
    p('Complaint draft — review and complete before filing',heading);p(report.complaint)
    p('Investigation trace',heading)
    for s in report.trace:p(f'{s.step_number}. {s.tool_name} ({s.duration_ms} ms, {s.status})\n{s.output_summary}',tiny)
    p('Limitations',heading)
    for l in report.limitations:p(l,tiny)
    def footer(canvas,document):
        canvas.setFont('Helvetica',7);canvas.setFillColor(colors.HexColor('#87957f'));canvas.drawString(43,28,'Nivaar | preserve original records separately');canvas.drawRightString(552,28,str(document.page))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
