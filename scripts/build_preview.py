#!/usr/bin/env python3
"""Produce a portable preview with all four pages and assets inside one HTML file."""
from pathlib import Path
import base64
import json
import mimetypes
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'homepage-preview.html'
OUT.parent.mkdir(exist_ok=True)
css=(ROOT/'assets/style.css').read_text()
js=(ROOT/'assets/site.js').read_text()
pdf=base64.b64encode((ROOT/'Joonghyuk_Hahn_CV.pdf').read_bytes()).decode()
favicon=base64.b64encode((ROOT/'assets/favicon.svg').read_bytes()).decode()

def data_url(path):
 mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
 return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()

css=re.sub(r'url\((fonts/[^)]+)\)',lambda m:'url('+data_url(ROOT/'assets'/m.group(1))+')',css)
pages={}
for name in ['index.html','publications.html','cv.html','contact.html']:
 s=(ROOT/name).read_text()
 s=s.replace('<link rel="stylesheet" href="assets/style.css">','<style>'+css+'</style>')
 s=s.replace('<script src="assets/site.js" defer></script>','')
 s=re.sub(r'src="(assets/[^\"]+)"',lambda m:'src="'+data_url(ROOT/m.group(1))+'"',s)
 s=s.replace('href="assets/favicon.svg"','href="data:image/svg+xml;base64,'+favicon+'"')
 s=s.replace('href="Joonghyuk_Hahn_CV.pdf"','href="data:application/pdf;base64,'+pdf+'"')
 # The parent supplies the route so the same filters work inside srcdoc.
 previewjs=js.replace('window.location.search',"window.frameElement.dataset.query || ''")
 bridge="""
 document.addEventListener('click',function(event){
   const anchor=event.target.closest('a');
   if(!anchor)return;
   const href=anchor.getAttribute('href');
   if(!href || /^(https?:|mailto:|data:|#)/.test(href))return;
   event.preventDefault();
   parent.postMessage({type:'preview-route',href:href},'*');
 });
 """
 pages[name]=s.replace('</body>','<script>'+previewjs+'\n'+bridge+'</script></body>')
serialized=json.dumps(pages,ensure_ascii=False).replace('<','\\u003c')
html='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Joonghyuk Hahn · Website preview</title>
<style>
*{box-sizing:border-box}html,body{margin:0;height:100%;background:#e6e9e2;font:13px -apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:#20382c}body{height:100dvh;display:flex;flex-direction:column}.preview-toolbar{flex:0 0 auto;min-height:56px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 22px;padding:10px 22px;background:#173e30;color:#fff}.preview-brand{font-weight:600;font-size:13px}.preview-controls{display:flex;align-items:center;gap:7px}.preview-controls button,.preview-controls select{font:inherit;color:white;border:1px solid #75917c;background:transparent;padding:7px 10px;border-radius:3px;cursor:pointer}.preview-controls select option{color:#173e30;background:#fff}.preview-controls button[aria-pressed=true]{background:#f6f7f1;color:#173e30}.preview-controls button:focus-visible,.preview-controls select:focus-visible{outline:3px solid #dbc699;outline-offset:3px}.preview-label{font-size:11px;color:#d0ddcc;margin-right:6px}.preview-stage{flex:1;min-height:0;display:flex;justify-content:center;overflow:auto}iframe{width:100%;height:100%;border:0;background:#faf9f6;transition:width .15s}iframe.mobile{width:390px;max-width:100%;box-shadow:0 0 0 1px #b8c2b1}@media(max-width:620px){.preview-label{display:none}.preview-toolbar{padding:10px 12px}.preview-controls button,.preview-controls select{font-size:11px}}@media(prefers-reduced-motion:reduce){iframe{transition:none}}
</style></head><body>
<div class="preview-toolbar"><span class="preview-brand">Joonghyuk Hahn <span class="preview-label">/ Website preview</span></span><div class="preview-controls"><label class="preview-label" for="page-picker">Page</label><select id="page-picker" aria-label="Preview page"><option value="index.html">Home</option><option value="publications.html">Publications</option><option value="cv.html">CV</option><option value="contact.html">Contact</option></select><button id="desktop" type="button" aria-pressed="true">Desktop</button><button id="mobile" type="button" aria-pressed="false">Mobile</button></div></div>
<div class="preview-stage"><iframe id="preview" title="Academic website preview" sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-downloads"></iframe></div>
<script id="preview-pages" type="application/json">'''+serialized+'''</script>
<script>
const pages=JSON.parse(document.querySelector('#preview-pages').textContent);
const frame=document.querySelector('#preview');
const picker=document.querySelector('#page-picker');
let active='index.html';
let pendingHash='';
function navigate(route){
 const parsed=new URL(route,'https://preview.invalid/');
 const file=parsed.pathname.split('/').pop()||'index.html';
 if(!Object.prototype.hasOwnProperty.call(pages,file))return;
 active=file;picker.value=file;frame.dataset.query=parsed.search;pendingHash=parsed.hash;
 frame.srcdoc=pages[file];
}
frame.addEventListener('load',()=>{
 if(pendingHash){const target=frame.contentDocument.getElementById(pendingHash.slice(1));if(target)target.scrollIntoView();pendingHash='';}
});
window.addEventListener('message',event=>{
 if(event.source===frame.contentWindow&&event.data&&event.data.type==='preview-route'&&typeof event.data.href==='string')navigate(event.data.href);
});
picker.addEventListener('change',()=>navigate(picker.value));
for(const mode of ['desktop','mobile'])document.getElementById(mode).addEventListener('click',()=>{
 frame.classList.toggle('mobile',mode==='mobile');
 document.getElementById('desktop').setAttribute('aria-pressed',String(mode==='desktop'));
 document.getElementById('mobile').setAttribute('aria-pressed',String(mode==='mobile'));
});
navigate(active);
</script></body></html>
'''
OUT.write_text(html,encoding='utf-8')
print(OUT)
