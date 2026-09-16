#!/usr/bin/env python3
"""Build the downloadable CV from the same verified content as the website.
Requires ReportLab. The website itself has no Python or package dependency.
"""
from pathlib import Path
from html import escape
import json
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
FONTROOT=Path(reportlab.__file__).resolve().parent/"fonts"
pdfmetrics.registerFont(TTFont("CVSans",str(FONTROOT/"Vera.ttf")))
pdfmetrics.registerFont(TTFont("CVSansBold",str(FONTROOT/"VeraBd.ttf")))
pdfmetrics.registerFontFamily("CVSans",normal="CVSans",bold="CVSansBold",italic="CVSans",boldItalic="CVSansBold")
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
S=json.loads((ROOT/'data/site.json').read_text())
PUBS=json.loads((ROOT/'data/publications.json').read_text())
GREEN=colors.HexColor('#265b46')
INK=colors.HexColor('#202c29')
MUTED=colors.HexColor('#58645d')
styles={
 'name':ParagraphStyle('name',fontName='CVSans',fontSize=31,leading=36,textColor=INK,spaceAfter=9),
 'h1':ParagraphStyle('h1',fontName='CVSans',fontSize=22,leading=27,textColor=GREEN,spaceAfter=16),
 'h2':ParagraphStyle('h2',fontName='CVSansBold',fontSize=10.5,leading=14,textColor=GREEN,spaceBefore=18,spaceAfter=8,keepWithNext=True),
 'body':ParagraphStyle('body',fontName='CVSans',fontSize=9.2,leading=13.5,textColor=INK,spaceAfter=6),
 'small':ParagraphStyle('small',fontName='CVSans',fontSize=8.2,leading=12,textColor=MUTED,spaceAfter=5),
 'pubtitle':ParagraphStyle('pubtitle',fontName='CVSansBold',fontSize=9.1,leading=12.6,textColor=INK,spaceAfter=3),
 'pubmeta':ParagraphStyle('pubmeta',fontName='CVSans',fontSize=8,leading=11.3,textColor=MUTED,spaceAfter=3),
}

def clean(s):
 return escape(str(s)).replace('–','-').replace('—','-').replace('‑','-').replace('’',"'").replace('³','<super>3</super>')

def P(s,style='body'):
 return Paragraph(s,styles[style])

def L(url,label):
 return f'<link href="{escape(url,quote=True)}" color="#265b46">{clean(label)}</link>'

def entry(title,meta,body=''):
 return KeepTogether([P(clean(title),'pubtitle'),P(clean(meta),'small')]+([P(clean(body))] if body else [])+[Spacer(1,8)])

def pub(p):
 title=clean(p['title'])
 auth=clean(p['authors']).replace('Joonghyuk Hahn','<b>Joonghyuk Hahn</b>').replace('*','<super>*</super>')
 venue=f"arXiv, {p['year']}" if p['type']=='preprint' else p['venue']
 return KeepTogether([P(title,'pubtitle'),P(auth,'pubmeta'),P(clean(venue)+'  |  '+L(p['url'],'Paper'),'pubmeta'),Spacer(1,10)])

story=[P(clean(S['name']),'name'),P(clean(S['role'])+' | '+clean(S['university']),'body'),P(clean(S['group'])+'<br/>'+clean(S['division'])+' | '+clean(S['department'])+'<br/>RESIST: '+clean(S['centre_full']),'small'),P(L('mailto:'+S['email'],S['email'])+' | '+L('mailto:'+S['personal_email'],S['personal_email'])+'<br/>'+L(S['site_url'],'peer0.github.io')+' | '+L(S['profiles'][0]['url'],'Google Scholar')+' | '+L(S['profiles'][2]['url'],'DBLP')+' | '+L(S['profiles'][3]['url'],'ORCID')+' | '+L(S['profiles'][4]['url'],'LinkedIn'),'small')]
story += [P('Research','h2'),P(clean(S['research_intro'])+' '+clean(S['research_detail']))]
story += [P('Appointments','h2'),entry('Postdoctoral Researcher, Linköping University',S['start']+'-present | Linköping, Sweden','Trustworthy Systems Group, Cybersecurity division, IDA. Working with Simin Nadjm-Tehrani as part of RESIST.'),entry('Graduate Researcher, Theory of Computation Lab','2019-2026 | Yonsei University','Formal language theory, grammar-based NLP, and program analysis.'),entry('Research Intern, Theory of Computation Lab','2017-2018 | Yonsei University','Automata, grammar classification, and natural language processing.')]
story += [P('Education','h2'),entry('Ph.D. in Computer Science, Yonsei University','March 2019-February 2026 | Seoul, Republic of Korea','Advisor: Yo-Sub Han. Dissertation: '+S['thesis']+'.'),entry("Bachelor's Degree in Computer Science, Yonsei University",'March 2015-February 2019 | Seoul, Republic of Korea')]
peer=[p for p in PUBS if p['type']!='preprint']
peer.sort(key=lambda p:-p['year'])
story += [PageBreak(),P('Publications','h1'),P('Peer-reviewed conference and journal papers. * Equal contribution.','small')]
for p in peer[:9]:
 story.append(pub(p))
story += [PageBreak(),P('Publications, continued','h1')]
for p in peer[9:]:
 story.append(pub(p))
story += [PageBreak(),P('Preprints & other manuscripts','h1')]
for p in PUBS:
 if p['type']=='preprint':story.append(pub(p))
story += [P('Other manuscripts','h2')]
for p in S['additional_manuscripts']:
 story.append(entry(p['title'],p['authors']))
story += [P('Teaching & academic service','h2')]
for p in S['teaching']:
 story.append(entry(p['title'],p['dates'],p['description']))
story += [P(clean(S['service'])),P('Technical background','h2'),P('<b>Programming:</b> Python, C/C++, Java<br/><b>ML / NLP:</b> PyTorch, TensorFlow, Hugging Face Transformers<br/><b>Foundations:</b> Automata, formal grammars, decidability, formal language hierarchies<br/><b>Tools:</b> LaTeX, Git, Linux / Unix')]
story += [PageBreak(),P('Research projects','h1')]
for p in S['projects']:
 story.append(entry(p['title'],p['dates']+' | '+p['organisation'],p['description']))

def footer(canvas,doc):
 canvas.saveState()
 canvas.setStrokeColor(colors.HexColor('#d8ddd4'))
 canvas.line(48,40,A4[0]-48,40)
 canvas.setFont('CVSans',7.5)
 canvas.setFillColor(MUTED)
 canvas.drawString(48,27,S['name']+' | Updated '+S['updated'])
 canvas.drawRightString(A4[0]-48,27,str(doc.page))
 canvas.restoreState()

path=ROOT/'Joonghyuk_Hahn_CV.pdf'
doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=44,bottomMargin=55,title=S['name']+' - Curriculum Vitae',author=S['name'],subject='Postdoctoral Researcher, Linköping University; TSG, CYBER, IDA, RESIST')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(path)
