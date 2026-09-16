#!/usr/bin/env python3
"""Build the static website from two editable JSON files; Python 3.9+, no dependencies."""
from pathlib import Path
from html import escape
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
PUBS = json.loads((ROOT / 'data/publications.json').read_text(encoding='utf-8'))
E = lambda value: escape(str(value), quote=True)
ARROW = '<span class="arrow" aria-hidden="true">↗</span>'
TOPICS = {'all': 'All research', 'verification': 'Verification & safety', 'code': 'Code intelligence', 'language': 'Language & learning', 'formal': 'Formal languages'}
TYPES = {'conference': 'Conference', 'journal': 'Journal', 'preprint': 'Preprint'}


def link(url, label, cls=''):
    """Escape data while keeping external navigation explicit and safe."""
    ext = ' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else ''
    return f'<a href="{E(url)}"{ext}' + (f' class="{E(cls)}"' if cls else '') + f'>{label}</a>'


def authors(p):
    return E(p['authors']).replace('Joonghyuk Hahn', '<strong>Joonghyuk Hahn</strong>').replace('*', '<sup>*</sup>')


def venue(p):
    return f"arXiv · {p['year']}" if p['type'] == 'preprint' else p['venue']


def paper_links(p):
    result = [link(p['url'], f'Paper {ARROW}')]
    if 'aclanthology.org/' in p['url']:
        result.append(link(p['url'].rstrip('/') + '.pdf', f'PDF {ARROW}'))
    elif p['url'].startswith('https://arxiv.org/abs/'):
        result.append(link(p['url'].replace('/abs/', '/pdf/'), f'PDF {ARROW}'))
    if p.get('code'):
        result.append(link(p['code'], f'Code {ARROW}'))
    return '<div class="paper-links">' + ''.join(result) + '</div>'


def header(active):
    nav = ''.join(f'<a href="{file}"' + (' aria-current="page"' if file == active else '') + f'>{label}</a>' for file, label in [('index.html','Home'),('publications.html','Publications'),('cv.html','CV'),('contact.html','Contact')])
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap header-inner">
<a href="index.html" class="brand"><span class="monogram" aria-hidden="true">jh</span>{E(S['name'])}</a>
<button class="menu-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="site-navigation" hidden>Menu <span aria-hidden="true">☰</span></button>
<nav class="site-nav" id="site-navigation" aria-label="Main navigation">{nav}</nav></div></header>'''


def footer():
    return f'''<footer class="site-footer"><div class="wrap footer-inner">
<span>© {S['updated'][:4]} {E(S['name'])} <span lang="ko">{E(S['name_ko'])}</span></span>
<div class="footer-links">{link(S['university_url'],E(S['university']))}<a href="mailto:{E(S['email'])}">Email</a><span>Updated {E(S['updated'])}</span></div>
</div></footer><div class="action-status" id="action-status" role="status" aria-live="polite" aria-atomic="true"></div>'''


def page(file, title, description, body):
    full_title = f"{S['name']} | {S['university']}" if file == 'index.html' else f"{title} | {S['name']}"
    canonical = S['site_url'] + ('/' if file == 'index.html' else '/' + file)
    schema = {'@context':'https://schema.org','@type':'Person','name':S['name'],'alternateName':S['name_ko'],'url':S['site_url'],'jobTitle':S['role'],'affiliation':{'@type':'Organization','name':S['university'],'url':S['university_url']},'sameAs':[p['url'] for p in S['profiles']],'knowsAbout':['Trustworthy AI','Formal language theory','Code intelligence','Neuro-symbolic AI']}
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(description)}"><meta name="author" content="{E(S['name'])}">
<meta name="theme-color" content="#173e30"><meta name="color-scheme" content="light">
<link rel="canonical" href="{E(canonical)}"><link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<meta property="og:type" content="website"><meta property="og:locale" content="en_US">
<meta property="og:title" content="{E(full_title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{E(canonical)}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{E(full_title)}"><meta name="twitter:description" content="{E(description)}">
<link rel="stylesheet" href="assets/style.css"><script src="assets/site.js" defer></script>
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')}</script>
</head><body>
{header(file)}
{body}
{footer()}
</body></html>
'''


def news_row(n):
    return f'''<div class="news-row{' featured' if n.get('featured') else ''}"><div class="news-date">{E(n['date'])}</div><p class="news-body">{E(n['text']).replace(E(S['host']), '<span class="nowrap">'+E(S['host'])+'</span>')} {link(n['url'],E(n['link_text'])+' '+ARROW)}</p></div>'''


def now_section():
    if not S.get('now'):
        return ''
    return f'''<section class="now" aria-labelledby="now-title"><p class="eyebrow" id="now-title"><span class="status-dot" aria-hidden="true"></span>{E(S.get('now_title','Now'))}</p><p class="now-text">{E(S['now'])}</p></section>'''


def home():
    profiles = ''.join(link(p['url'], E(p['label'])+' '+ARROW) for p in S['profiles'][:3])
    themes = ''
    for i, t in enumerate(S['themes']):
        topics = t.get('topics', [t['id']])
        count = sum(p['topic'] in topics for p in PUBS)
        label = 'Related papers'
        more = ''
        themes += f'''<article class="theme"><div class="theme-top"><span class="theme-number">0{i+1}</span><span class="theme-label">{E(t['label'])}</span></div><h3>{E(t['title'])}</h3><p>{E(t['text'])}</p><div class="theme-bottom"><a href="publications.html?topic={E(','.join(topics))}" class="theme-link">{label} <span class="paper-count">{count}</span><span aria-hidden="true">→</span></a>{more}</div></article>'''
    selected = ''
    for pid in S['selected_ids']:
        p = next(p for p in PUBS if p['id'] == pid)
        art = f'<figure class="research-art"><img src="{E(p["illustration"])}" alt="{E(p["illustration_alt"])}" width="560" height="220" loading="lazy" decoding="async"></figure>' if p.get('illustration') else ''
        selected += f'''<article class="research-card">{art}<div class="research-card-body"><div class="research-card-meta"><span class="eyebrow">{E(p.get('overline',TOPICS[p['topic']]))}</span><span class="venue {p['type']}">{E(venue(p))}</span></div>
<h3>{link(p['url'],E(p['short'])+' '+ARROW)}</h3><p class="research-card-title">{E(p['title'])}</p><p class="paper-summary">{E(p['summary'])}</p><p class="paper-authors">{authors(p)}</p>{paper_links(p)}</div></article>'''
    headline = E(S['headline']).replace('grounded in ', '<br>grounded in ').replace('language and structure.', '<em>language and structure.</em>')
    return f'''<main id="main">
<div class="wrap hero"><div class="hero-copy">
<p class="eyebrow"><span class="status-dot" aria-hidden="true"></span>{E(S['role'])}<span aria-hidden="true">/</span>{E(S['university'])}</p>
<div class="hero-name"><h1>{E(S['name'])}</h1><span class="korean-name" lang="ko">{E(S['name_ko'])}</span></div>
<p class="hero-headline">{headline}</p>
<p class="hero-bio">I am a postdoctoral researcher in the {link(S['group_url'],E(S['group']))} at {link(S['university_url'],E(S['university']))}. Working with {link(S['host_url'],E(S['host']))}, I contribute to {link(S['centre_url'],'RESIST')}, a research center for resilient and secure AI systems.</p>
<div class="actions"><a class="button" href="#selected-work">Explore my research <span class="arrow" aria-hidden="true">↓</span></a><a class="button button-secondary" href="cv.html">Curriculum vitae <span class="arrow" aria-hidden="true">→</span></a></div>
<div class="profile-links"><a href="mailto:{E(S['email'])}">Email {ARROW}</a>{profiles}</div></div>
<div class="hero-portrait"><figure class="portrait-frame"><img class="portrait" src="assets/profile.jpg" alt="Joonghyuk Hahn at Griffith Observatory" width="599" height="1280" fetchpriority="high"></figure>
<div class="portrait-note"><span class="location-label">Currently based in</span><span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-7 7-13a7 7 0 0 0-14 0c0 6 7 13 7 13Z"/><circle cx="12" cy="8" r="2.3"/></svg>{E(S['location'])}</span></div></div></div>
<section class="affiliation-band" aria-label="Current affiliation"><div class="wrap affiliation-inner">
<div class="affiliation-item"><p class="eyebrow">University</p>{link(S['university_url'],E(S['university']))}<small>{link(S['department_url'],E(S['department']))}</small></div>
<div class="affiliation-item"><p class="eyebrow">Research group</p>{link(S['group_url'],E(S['group']))}<small>{link(S['division_url'],'Division of '+E(S['division']))}</small></div>
<div class="affiliation-item"><p class="eyebrow">Research center</p>{link(S['centre_url'],'RESIST '+ARROW)}<small>{E(S['centre_full'])}</small></div>
</div></section>
<div class="wrap">{now_section()}<section class="section" id="research"><div class="section-heading research-heading"><div><p class="eyebrow">Research directions</p><h2>From structure<br> to <em>trust.</em></h2></div><p class="section-intro">{E(S['research_detail'])}</p></div><div class="theme-grid">{themes}</div></section>
<section class="section selected-section" id="selected-work"><div class="section-heading"><div><p class="eyebrow">Selected work</p><h2>A closer look at the research.</h2></div><a href="publications.html" class="text-link">All publications <span aria-hidden="true">→</span></a></div><div class="research-grid">{selected}</div><p class="fine-print">* Equal contribution. Illustrations describe research concepts; see each paper for methods and results.</p></section>
<div class="home-notes section"><section id="news"><div class="section-heading"><div><p class="eyebrow">Updates</p><h2>Recently.</h2></div></div>{''.join(news_row(n) for n in S['news'][:3])}<details class="news-archive"><summary>Earlier updates <span aria-hidden="true">+</span></summary>{''.join(news_row(n) for n in S['news'][3:])}</details></section>
<section id="about"><div class="section-heading"><div><p class="eyebrow">Background</p><h2>Along the way.</h2></div></div><ol class="timeline">
<li class="current"><span class="timeline-date">{E(S['start'])}–present</span><h3>Postdoctoral Researcher</h3><p>Linköping University · TSG / RESIST</p></li>
<li><span class="timeline-date">2019–Feb 2026</span><h3>Ph.D. in Computer Science</h3><p>Yonsei University<br>Advisor: {link(S['phd_advisor_url'],E(S['phd_advisor']))}</p></li>
<li><span class="timeline-date">2015–2019</span><h3>Computer Science</h3><p>Bachelor’s degree · Yonsei University</p></li></ol><a class="text-link" href="cv.html">Full background &amp; experience <span aria-hidden="true">→</span></a></section></div>
<section class="contact-banner" aria-label="Research contact"><div><p class="eyebrow">An open conversation</p><h2>Good research starts<br>with a <em>question.</em></h2><p>I welcome conversations about trustworthy AI,<br class="desktop-break"> formal methods, and code intelligence.</p></div><div class="contact-banner-action"><a href="mailto:{E(S['email'])}" class="button">Let’s connect {ARROW}</a><a href="mailto:{E(S['email'])}" class="contact-banner-email">{E(S['email'])}</a></div></section></div></main>'''


def publication(p):
    reference = f"{p['authors'].replace('*', '')} ({p['year']}). {p['title'].rstrip('.')}. {p['venue']}. {p['url']}"
    search = ' '.join(str(p.get(k,'')) for k in ['title','authors','venue','year','summary']) + ' ' + TOPICS[p['topic']]
    return f'''<article class="publication" id="{E(p['id'])}" data-paper data-topic="{E(p['topic'])}" data-type="{E(p['type'])}" data-year="{p['year']}" data-search="{E(search)}">
<div class="publication-meta"><span class="venue {p['type']}">{E(venue(p))}</span><span class="publication-type">{TYPES[p['type']]}</span></div><h3>{link(p['url'],E(p['title']))}</h3><p class="paper-authors">{authors(p)}</p>{'<p class="paper-summary">'+E(p['summary'])+'</p>' if p.get('summary') else ''}{paper_links(p)}<details class="citation"><summary>Cite this paper <span aria-hidden="true">+</span></summary><div class="citation-body"><p id="cite-{E(p['id'])}" tabindex="-1">{E(reference)}</p><button type="button" data-copy-target="cite-{E(p['id'])}" hidden>Copy reference</button></div></details></article>'''


def publications():
    years = sorted(set(p['year'] for p in PUBS),reverse=True)
    opts = ''.join(f'<option value="{year}">{year}</option>' for year in years)
    topic_buttons = ''.join(f'<button type="button" data-topic-filter="{key}" aria-pressed="{str(key=="all").lower()}">{value}</button>' for key,value in TOPICS.items())
    groups = ''.join(f'<section class="publication-year-group" data-year-group aria-labelledby="year-{year}"><h2 class="year-heading" id="year-{year}">{year}</h2><div>'+''.join(publication(p) for p in PUBS if p['year']==year)+'</div></section>' for year in years)
    return f'''<main id="main" class="wrap"><div class="page-intro"><p class="eyebrow">Research output</p><h1>Publications.</h1><p class="lede">Work across verification, code intelligence, natural language processing, and formal language theory.</p><p class="fine-print">* Equal contribution. Preprints are identified separately from peer-reviewed publications.</p></div>
<div class="publications-body"><div class="publication-controls" data-publication-controls hidden><div class="search-row"><div class="field"><label for="publication-search">Search publications <span class="search-hint" aria-hidden="true">Press <kbd>/</kbd></span></label><input id="publication-search" type="search" aria-keyshortcuts="/" placeholder="Title, author, venue, or keyword" autocomplete="off"></div><div class="field"><label for="publication-year">Year</label><select id="publication-year"><option value="all">All years</option>{opts}</select></div><div class="field"><label for="publication-type">Publication type</label><select id="publication-type"><option value="all">All types</option><option value="conference">Conferences</option><option value="journal">Journals</option><option value="preprint">Preprints</option></select></div></div><div class="topic-filters" role="group" aria-label="Research topic">{topic_buttons}</div></div>
<div class="results-line"><span id="publication-count" role="status" aria-live="polite">{len(PUBS)} publications</span><button type="button" id="reset-filters" class="reset-button" hidden>Clear filters</button></div>
<div id="no-publications" class="empty-state" hidden><h2>No matching publications.</h2><p>Try a different keyword or clear the filters above.</p></div>{groups}</div></main>'''


def cv_entry(dates, title, text):
    return f'<div class="cv-entry"><div class="cv-date">{E(dates)}</div><div><h3>{title}</h3>{text}</div></div>'


def cv():
    navigation = ''.join(f'<a href="#{key}">{label}</a>' for key,label in [('appointments','Appointments'),('education','Education'),('cv-research','Research'),('projects','Projects'),('teaching','Teaching & service'),('skills','Skills')])
    appointments = cv_entry(f"{S['start']}–present",E(S['role']),f'<p class="current-role">{link(S["university_url"],E(S["university"]))}</p><p>{E(S["group"])}<br>{E(S["division"])}<br>{E(S["department"])}</p><p>Working with {link(S["host_url"],E(S["host"]))} as part of {link(S["centre_url"],"RESIST")}.</p>')
    appointments += cv_entry('2019–2026','Graduate Researcher','<p>Theory of Computation Lab, Yonsei University<br>Formal language theory, grammar-based NLP, and program analysis.</p>')
    appointments += cv_entry('2017–2018','Research Intern','<p>Theory of Computation Lab, Yonsei University<br>Automata, grammar classification, and natural language processing.</p>')
    education = cv_entry('2019–Feb 2026','Ph.D. in Computer Science',f'<p>Yonsei University, Seoul, Republic of Korea<br>Advisor: {link(S["phd_advisor_url"],E(S["phd_advisor"]))}</p><p class="thesis">Dissertation: <em>{E(S["thesis"])}</em></p>')
    education += cv_entry('2015–2019','Bachelor’s Degree in Computer Science','<p>Yonsei University, Seoul, Republic of Korea</p>')
    projects = ''.join(cv_entry(p['dates'],E(p['title']),f'<p>{E(p["organisation"])}</p><p>{E(p["description"])}</p>') for p in S['projects'])
    teaching = ''.join(cv_entry(p['dates'],E(p['title']),f'<p>{E(p["description"])}</p>') for p in S['teaching'])
    teaching += cv_entry('Since 2022','Reviewing & program committees',f'<p>{E(S["service"])}</p>')
    return f'''<main id="main" class="wrap"><div class="page-intro split"><div><p class="eyebrow">Background & experience</p><h1>Curriculum vitae.</h1><p class="lede">{E(S['role'])} · {E(S['university'])}</p></div><a class="button" href="Joonghyuk_Hahn_CV.pdf" target="_blank" rel="noopener" aria-label="View CV as PDF (opens in a new tab)">View CV (PDF) <span aria-hidden="true">↗</span></a></div>
<div class="cv-layout"><nav class="cv-nav" aria-label="CV sections">{navigation}</nav><div>
<section class="cv-section" id="appointments"><h2>Appointments</h2>{appointments}</section>
<section class="cv-section" id="education"><h2>Education</h2>{education}</section>
<section class="cv-section" id="cv-research"><h2>Research</h2><p>{E(S['research_intro'])} {E(S['research_detail'])}</p><a class="text-link" href="publications.html">Complete publication list <span aria-hidden="true">→</span></a></section>
<section class="cv-section" id="projects"><h2>Research projects</h2>{projects}</section>
<section class="cv-section" id="teaching"><h2>Teaching & service</h2>{teaching}</section>
<section class="cv-section" id="skills"><h2>Technical background</h2><dl class="skills-list"><dt>Programming</dt><dd>Python, C/C++, Java</dd><dt>ML / NLP</dt><dd>PyTorch, TensorFlow, Hugging Face Transformers</dd><dt>Foundations</dt><dd>Automata, formal grammars, decidability, formal language hierarchies</dd><dt>Tools</dt><dd>LaTeX, Git, Linux / Unix</dd></dl></section>
</div></div></main>'''


def contact():
    profiles = ''.join(link(p['url'],E(p['label'])+ARROW,'profile-row') for p in S['profiles'])
    return f'''<main id="main" class="wrap"><div class="page-intro"><p class="eyebrow">Contact</p><h1>Let’s connect.</h1><p class="lede">For research conversations and collaborations in trustworthy AI, formal methods, language, and code.</p></div><div class="contact-layout"><div><section class="contact-panel"><h2>Get in touch</h2><div class="contact-label">Email</div><a class="email-link" href="mailto:{E(S['email'])}">{E(S['email'])}</a><div class="contact-label">Alternative email</div><a href="mailto:{E(S['personal_email'])}">{E(S['personal_email'])}</a><div class="contact-label">Research profiles</div>{profiles}</section></div>
<div><section class="contact-affiliation"><p class="eyebrow">Current affiliation</p><h3>{link(S['university_url'],E(S['university']))}</h3><p>{E(S['role'])}<br>{link(S['group_url'],E(S['group']))}<br>{link(S['division_url'],'Division of '+E(S['division']))}<br>{link(S['department_url'],E(S['department']))}</p><p class="contact-label">Research center</p><p>{link(S['centre_url'],'RESIST '+ARROW)}<br>{E(S['centre_full'])}</p><p class="contact-label">Location</p><p>{E(S['location'])}</p></section><p class="fine-print">Working with {link(S['host_url'],E(S['host']))}.</p></div></div></main>'''


def build(check=False):
    """Render deterministically; check mode flags edited HTML without overwriting it."""
    outputs = {
        'index.html': page('index.html','Home',f"{S['name']}, {S['role']} at {S['university']}. Research in trustworthy AI, formal methods, and code intelligence.",home()),
        'publications.html': page('publications.html','Publications',f"Publications by {S['name']} in verification, code intelligence, NLP, and formal language theory.",publications()),
        'cv.html': page('cv.html','CV',f"Curriculum vitae of {S['name']}, {S['role']} at {S['university']}.",cv()),
        'contact.html': page('contact.html','Contact',f"Contact {S['name']}, {S['role']} in TSG at {S['university']} and RESIST.",contact()),
        'sitemap.xml': '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{S["site_url"]}/{file}</loc><lastmod>{S["updated"]}</lastmod></url>\n' for file in ['', 'publications.html','cv.html','contact.html']) + '</urlset>\n',
        'robots.txt': f'User-agent: *\nAllow: /\nSitemap: {S["site_url"]}/sitemap.xml\n',
        'assets/favicon.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="32" fill="#173e30"/><text x="32" y="43" fill="#faf9f6" font-family="Georgia,serif" font-size="38" text-anchor="middle">jh</text></svg>\n'
    }
    mismatches = []
    for file, content in outputs.items():
        path = ROOT / file
        if check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                mismatches.append(file)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding='utf-8')
    if mismatches:
        raise SystemExit('Generated files are out of date: ' + ', '.join(mismatches))
    print(('Verified' if check else 'Built') + f' {len(outputs)} files; {len(PUBS)} publication entries.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    build(parser.parse_args().check)
