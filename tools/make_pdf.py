# Builds villa-71-brochure.pdf: sixteen A4-landscape sheets from the site's markup, tokens and images (no 360° tour).
# Usage: python3 tools/make_pdf.py   (Python 3 with Pillow and Playwright + Chromium)
import os, re, io, asyncio, html
from PIL import Image
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A=os.path.join(B,"assets"); P=os.path.join(B,"tools","print"); IMG=os.path.join(P,"img"); os.makedirs(IMG,exist_ok=True)
site=open(os.path.join(B,"index.html"),encoding="utf-8").read()
BASALT=(21,19,15); WHITE=(246,243,236); BONE=(239,233,220)

def prep(src,name,long=1600,q=80):
    im=Image.open(src).convert("RGB"); w,h=im.size; L=max(w,h)
    if L>long: s=long/L; im=im.resize((round(w*s),round(h*s)),Image.LANCZOS)
    im.save(os.path.join(IMG,name),"JPEG",quality=q,optimize=True,progressive=True); return name
def flat(src,name,ink,bg,long=2200):
    im=Image.open(src).convert("RGBA"); w,h=im.size; L=max(w,h)
    if L>long: s=long/L; im=im.resize((round(w*s),round(h*s)),Image.LANCZOS)
    a=im.split()[3]; out=Image.new("RGB",im.size,bg); out.paste(Image.new("RGB",im.size,ink),(0,0),a); out.save(os.path.join(IMG,name),"JPEG",quality=84,optimize=True); return name

# ---- images ----
for n,long in [("hero",1800),("gate",1800),("rec-a",1700),("rec-b",1700),("rec-c",1700),("front-cloud",1800),("chalet",1700)]: prep(os.path.join(A,n+".jpg"),n+".jpg",long)
for n in ("pool-house","terrace-1","terrace-2","master-bath","kitchen-2","master-closet-1","stairhall"): prep(os.path.join(A,"i",n+".jpg"),"i-"+n+".jpg",1400)
flat(os.path.join(A,"site-plan.png"),"site-plan.jpg",BONE,BASALT,2600)
for n in ("basement","ground","first","second","guest"): flat(os.path.join(A,"plan-%s.png"%n),"plan-%s.jpg"%n,(27,25,21),WHITE,2200)
tiles=re.findall(r'<figure class="tile rv" data-g="(\w+)" data-lb="interiors" data-src="assets/i/([\w-]+)\.jpg" data-cap="([^"]+)"',site)
for g,slug,cap in tiles: prep(os.path.join(A,"t",slug+".jpg"),"t-"+slug+".jpg",900,76)
GROUP={"arrive":"Arrival","live":"Living and kitchen","suite":"Suites","leisure":"Leisure","chalet":"Guest chalet"}

def block(start,end): s=site.index(start); e=site.index(end,s); return site[s:e]
story=block('<div class="story">','    <div class="fr wide rv wipe"')
def panel(key):
    b=block('<div class="pp" data-p="%s"'%key,'        </div>\n'); return b[b.index('>')+1:]
spec=block('<div class="spec">','    <div class="specimg">')+'</div>'
strat=block('<ul class="strat">','<p class="principle')
principle=re.search(r'<p class="principle rv" style="--i:7">(.*?)</p>',site).group(1)
facts=block('<div class="clim-facts">','    <div class="pfoot"><span><b>Villa 71</b> · Climate and ground</span>')
cols=block('<div class="cols">','    <p class="disc rv">')
disc=re.search(r'<p class="disc rv">(.*?)</p>',site,re.S).group(1)
mql=block('<div class="mql rv"','    <div class="pfoot"><span><b>Villa 71</b> · Guzape · Abuja · 2026</span>')
mats=block('<div class="mats rv" style="--i:2">','        <div class="fr rv wipe" style="--i:3" data-lb="scheme" data-src="assets/chalet.jpg"')
def clean(s): return re.sub(r' (rv|wipe)\b','',re.sub(r' style="--i:\d+"','',s)).replace(' loading="lazy"','').replace(' decoding="async"','')

N=16
def foot(n,label): return '<div class="pfoot"><span><b>Villa 71</b> · %s</span><span class="pn">%02d / %02d</span></div>'%(label,n,N)
def head(n,eyebrow,title,lede=''):
    return '<div class="head"><div><p class="eyebrow"><span class="idx">%02d</span>%s</p><h2 class="title">%s</h2></div>%s</div>'%(n,eyebrow,title,('<p class="lede">%s</p>'%lede) if lede else '')

sheets=[]
# 01 cover
sheets.append('''<section class="sheet dark cover"><div class="cl"><div class="mark"><span class="v">Villa</span><span class="n">71</span></div><div class="side"><b>A private residence <em>in Guzape,</em> Abuja</b>Seven suites · guest chalet · pool<br>A365 Designs</div></div><div class="cr"><img src="img/hero.jpg" alt=""></div></section>''')
# 02 at a glance
sheets.append('''<section class="sheet light">'''+head(2,'At a glance','Three floors, seven suites, <em>one garden wall.</em>')+'''
<div class="g2"><div>
<div class="stats"><div class="stat"><div class="n">7</div><div class="l">En-suite suites</div></div><div class="stat"><div class="n">4<small>+1</small></div><div class="l">Levels + guest chalet</div></div><div class="stat"><div class="n">1,735<small>m²</small></div><div class="l">Main house · four levels</div></div><div class="stat"><div class="n">2,000<small>m²</small></div><div class="l">Plot · 30 × 67 m</div></div><div class="stat"><div class="n">15<small>+</small></div><div class="l">Cars inside the wall</div></div><div class="stat"><div class="n">24,000<small>L</small></div><div class="l">Water reservoir</div></div></div>
'''+clean(story)+'''</div>
<div class="fr tall"><img src="img/gate.jpg" alt="" style="object-position:50% 45%"><span class="k"><i>01</i>From the road</span></div></div>'''+foot(2,'At a glance')+'</section>')
# 03 the scheme
sheets.append('''<section class="sheet dark">'''+head(3,'The scheme','Travertine, white render, <em>timber.</em>','Warm travertine against white render, timber slats over the terraces: the latest visualisations of the house.')+'''
<div class="trip"><div class="fr"><img src="img/rec-a.jpg" alt=""><span class="k"><i>02</i>The approach</span></div><div class="fr"><img src="img/rec-b.jpg" alt=""><span class="k"><i>03</i>The corner</span></div><div class="fr"><img src="img/rec-c.jpg" alt=""><span class="k"><i>04</i>The forecourt</span></div></div>
'''+clean(mats)+foot(3,'The scheme')+'</section>')
# 04 the scheme II
sheets.append('''<section class="sheet dark">'''+head(4,'The scheme','Under a Guzape sky, <em>and the guest chalet.</em>')+'''
<div class="duo"><div class="fr"><img src="img/front-cloud.jpg" alt=""><span class="k"><i>05</i>The front</span></div><div class="fr"><img src="img/chalet.jpg" alt=""><span class="k"><i>06</i>Guest chalet</span></div></div>'''+foot(4,'The scheme')+'</section>')
# 05 grounds
sheets.append('''<section class="sheet dark grounds">'''+head(5,'Grounds','Pool, terraces, <em>courtyards.</em>','The pool, gazebo and outdoor kitchen sit at the rear of the plot; the drive, forecourt and guest chalet at the road.')+'''
<div class="gv"><div class="fr"><img src="img/i-pool-house.jpg" alt=""><span class="k">Pool and house</span></div><div class="fr"><img src="img/i-terrace-1.jpg" alt=""><span class="k">Expanse terrace</span></div><div class="fr"><img src="img/i-terrace-2.jpg" alt=""><span class="k">Terrace dining</span></div></div>
<div class="dims"><span><b>67.44 m</b>north</span><span><b>30.23 m</b>road frontage</span><span><b>66.24 m</b>south</span><span><b>30.11 m</b>rear</span><span><b>≈2,000 m²</b>plot</span><span class="r">Site plan · A_71_23 · N.T.S</span></div>
<div class="siteplan"><img src="img/site-plan.jpg" alt=""></div>'''+foot(5,'Grounds')+'</section>')
# 06-08 interiors
chunks=[tiles[0:18],tiles[18:36],tiles[36:51]]; rom=['I','II','III']
for k,ch in enumerate(chunks):
    groups=[]; [groups.append(GROUP[g]) for g,_,_ in ch if GROUP[g] not in groups]
    grid=''.join('<figure><img src="img/t-%s.jpg" alt=""><figcaption>%s</figcaption></figure>'%(slug,html.escape(cap)) for g,slug,cap in ch)
    sheets.append('<section class="sheet light">'+head(6+k,'Interiors · %s of III'%rom[k],'Fifty-one views, <em>one palette.</em>' if k==0 else '<em>%s.</em>'%(' · '.join(groups)),' · '.join(groups) if k==0 else '')+'<div class="masonry">'+grid+'</div>'+foot(6+k,'Interiors')+'</section>')
# 09-12 plans
for n,key,title,label in [(9,'ground','Ground <em>floor.</em>','Ground floor · N.T.S'),(10,'first','First <em>floor.</em>','First floor · N.T.S'),(11,'second','Second <em>floor.</em>','Second floor · N.T.S')]:
    sheets.append('<section class="sheet light">'+head(n,'Plans','%s'%title)+'<div class="pv"><div class="planbox"><img src="img/plan-%s.jpg" alt=""><span class="k">%s</span></div><div class="pp">'%(key,label)+clean(panel(key))+'</div></div>'+foot(n,'Plans')+'</section>')
sheets.append('<section class="sheet light">'+head(12,'Plans','Basement and <em>guest chalet.</em>','A lift and stair core serves four levels, from the basement garage and cinema to the second floor. Areas are as scheduled by the architects; drawing set A_71_23, June 2026.')+'<div class="pv2"><div class="planbox"><img src="img/plan-basement.jpg" alt=""><span class="k">Basement · N.T.S</span></div><div class="pp">'+clean(panel('basement'))+'</div><div class="planbox"><img src="img/plan-guest.jpg" alt=""><span class="k">Guest chalet and staff · N.T.S</span></div><div class="pp">'+clean(panel('guest'))+'</div></div>'+foot(12,'Plans')+'</section>')
# 13 climate
sheets.append('''<section class="sheet light">'''+head(13,'Climate and ground','Sun, shade <em>and the hillside.</em>','Guzape sits at nine degrees north on the granite hills south of Abuja\'s centre: a high sun all year, harmattan haze from December, rains from April to October. The approach balcony, the largest of the villa\'s balconies, at three times of a December day.')+'''
<div class="suns"><figure><svg data-h="9" viewBox="0 0 300 186"></svg><figcaption><b>09:00</b><span id="r9"></span></figcaption></figure><figure><svg data-h="12" viewBox="0 0 300 186"></svg><figcaption><b>12:00</b><span id="r12"></span></figcaption></figure><figure><svg data-h="15" viewBox="0 0 300 186"></svg><figcaption><b>15:00</b><span id="r15"></span></figcaption></figure></div>
'''+clean(strat)+'</ul><p class="principle">'+principle+'</p>'+clean(facts)+foot(13,'Climate and ground')+'</section>')
# 14 specification
sheets.append('<section class="sheet light">'+head(14,'Specification','Built <em>to last.</em>')+clean(spec)+'<div class="specimg"><div class="fr"><img src="img/i-master-bath.jpg" alt=""></div><div class="fr"><img src="img/i-kitchen-2.jpg" alt=""></div><div class="fr"><img src="img/i-master-closet-1.jpg" alt=""></div><div class="fr"><img src="img/i-stairhall.jpg" alt=""></div></div>'+foot(14,'Specification')+'</section>')
# 15 contact
c=clean(cols).replace('<li><a href="#p9"><span class="num">09</span><span>Contact</span></a></li>','')
c=re.sub(r'<ol class="toc">.*?</ol>','<ol class="toc"><li><span class="num">02</span><span>At a glance</span></li><li><span class="num">03</span><span>The scheme</span></li><li><span class="num">05</span><span>Grounds and site plan</span></li><li><span class="num">06</span><span>Interiors</span></li><li><span class="num">09</span><span>Plans</span></li><li><span class="num">13</span><span>Climate and ground</span></li><li><span class="num">14</span><span>Specification</span></li></ol>',c,flags=re.S)
sheets.append('<section class="sheet dark contact">'+head(15,'Contact','See the house <em>in Guzape.</em>','Drawings, the full specification and a site visit can be arranged through A365 Designs.')+'<div class="cg"><div>'+c+'</div><div class="fr"><img src="img/rec-b.jpg" alt=""><span class="k">The corner</span></div></div><p class="disc">'+disc+'</p>'+clean(mql)+foot(15,'Contact')+'</section>')
# 16 back
sheets.append('<section class="sheet dark back"><div class="mark"><span class="v">Villa</span><span class="n">71</span></div><p>Guzape · Abuja · A365 Designs · brochure by Mizan Qist Limited · 2026</p></section>')

CSS='''
@page{size:297mm 210mm;margin:0}
:root{--white:#f6f3ec;--white-2:#ece6da;--white-3:#dfd6c6;--basalt:#15130f;--basalt-2:#1d1a15;--basalt-3:#2a251d;--trav:#d6c5a6;--bronze:#8f6234;--bronze-2:#c48f52;--bronze-3:#e2b57c;--ink:#1b1915;--bone:#efe9dc;--font-d:"Cormorant",Garamond,serif;--font-b:"Manrope","Helvetica Neue",Arial,sans-serif}
*{box-sizing:border-box}html,body{margin:0;padding:0}
body{font-family:var(--font-b);font-weight:300;font-size:9.5pt;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{width:297mm;height:210mm;overflow:hidden;position:relative;padding:14mm 14mm 11mm;page-break-after:always;break-after:page;background:var(--bg);color:var(--fg)}
.sheet.dark{--bg:var(--basalt);--bg-2:var(--basalt-2);--bg-3:var(--basalt-3);--fg:var(--bone);--muted:#9d937f;--line:rgba(239,233,220,.16);--acc:var(--bronze-2);--acc-2:var(--bronze-3)}
.sheet.light{--bg:var(--white);--bg-2:var(--white-2);--bg-3:var(--white-3);--fg:var(--ink);--muted:#77705f;--line:rgba(27,25,21,.14);--acc:var(--bronze);--acc-2:#a08c67}
img{display:block;max-width:100%}
.eyebrow{font-size:7pt;letter-spacing:.3em;text-transform:uppercase;font-weight:600;color:var(--acc);margin:0 0 3mm;display:flex;align-items:center;gap:3mm}
.eyebrow .idx{font-family:var(--font-d);font-weight:400;font-size:11pt;letter-spacing:.04em;color:var(--muted);text-transform:none}
.eyebrow::before{content:"";width:7mm;height:.3mm;background:var(--acc)}
.title{font-family:var(--font-d);font-weight:300;font-size:26pt;line-height:1;letter-spacing:-.01em;margin:0}
.title em{font-style:italic;font-weight:300;color:var(--acc)}
.lede{font-family:var(--font-d);font-weight:400;font-size:12.5pt;line-height:1.35;margin:0;max-width:60ch}
.body{margin:0 0 3mm;font-size:9pt}
.head{display:grid;grid-template-columns:1.15fr .85fr;gap:8mm;align-items:end;margin:0 0 6mm}
.pfoot{position:absolute;left:14mm;right:14mm;bottom:7mm;display:flex;justify-content:space-between;align-items:baseline;padding-top:2mm;border-top:.25mm solid var(--line);font-size:6.5pt;letter-spacing:.22em;text-transform:uppercase;color:var(--muted)}
.pfoot b{font-weight:500;color:var(--fg)}.pfoot .pn{font-family:var(--font-d);font-size:10pt;letter-spacing:.06em;text-transform:none;color:var(--fg)}
.fr{position:relative;overflow:hidden;border-radius:0 9mm 0 0;background:var(--bg-2)}
.fr img{width:100%;height:100%;object-fit:cover}
.fr .k{position:absolute;left:0;bottom:0;padding:2.2mm 3.5mm;font-size:6pt;letter-spacing:.24em;text-transform:uppercase;font-weight:600;color:#fff;background:linear-gradient(90deg,rgba(21,19,15,.62),rgba(21,19,15,0))}
.fr .k i{font-style:normal;font-family:var(--font-d);font-size:9pt;letter-spacing:.06em;text-transform:none;margin-right:2.5mm;color:var(--trav)}
/* cover */
.cover{padding:0;display:grid;grid-template-columns:118mm 1fr}
.cover .cl{padding:16mm 12mm 14mm 16mm;display:flex;flex-direction:column;justify-content:flex-end;gap:10mm}
.cover .mark,.back .mark{font-family:var(--font-d);font-weight:300;line-height:.8;display:flex;align-items:flex-end;gap:5mm}
.cover .mark .v,.back .mark .v{font-size:16pt;letter-spacing:.34em;text-transform:uppercase;font-weight:400;writing-mode:vertical-rl;transform:rotate(180deg);color:var(--trav);margin-bottom:3mm}
.cover .mark .n,.back .mark .n{font-size:150pt;letter-spacing:-.04em;margin-left:-.03em;color:#fff}
.cover .side{font-size:7.5pt;letter-spacing:.26em;text-transform:uppercase;font-weight:500;line-height:2;color:rgba(255,255,255,.88)}
.cover .side b{display:block;font-family:var(--font-d);font-weight:300;font-size:19pt;letter-spacing:.02em;text-transform:none;line-height:1.1;margin-bottom:3mm;color:#fff}
.cover .side b em{font-style:italic;color:var(--trav)}
.cover .cr{height:210mm;overflow:hidden}.cover .cr img{width:100%;height:100%;object-fit:cover;object-position:56% 40%}
.back{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8mm}
.back .mark .n{font-size:90pt}.back p{margin:0;font-size:7pt;letter-spacing:.26em;text-transform:uppercase;color:var(--muted)}
/* at a glance */
.g2{display:grid;grid-template-columns:1fr 92mm;gap:8mm;align-items:stretch;height:150mm}
.stats{display:grid;grid-template-columns:repeat(3,1fr);border-top:.25mm solid var(--line);border-bottom:.25mm solid var(--line);margin:0 0 5mm}
.stat{padding:3mm 3mm 3mm 0;border-right:.25mm solid var(--line)}.stat:nth-child(3n){border-right:0}.stat:nth-child(-n+3){border-bottom:.25mm solid var(--line)}
.stat .n{font-family:var(--font-d);font-weight:300;font-size:22pt;line-height:1}.stat .n small{font-size:.5em;margin-left:.5mm;color:var(--acc)}
.stat .l{font-size:6pt;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);margin-top:1.5mm;font-weight:600}
.story{display:grid;grid-template-columns:1fr 46mm;gap:6mm;align-items:start}
.story .lede{font-size:11.5pt;margin-bottom:2.5mm}.story .body{color:var(--muted);font-size:8.6pt}
.feat{list-style:none;margin:0;padding:0;border-top:.25mm solid var(--line)}
.feat li{padding:2.2mm 0;border-bottom:.25mm solid var(--line)}
.feat li b{display:block;font-family:var(--font-d);font-weight:500;font-size:12pt;line-height:1.15}
.feat li span{font-size:6.2pt;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.fr.tall{height:150mm}
/* scheme */
.trip{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;height:112mm;margin-bottom:5mm}
.mats{display:grid;grid-template-columns:repeat(3,1fr);border:.25mm solid var(--line);border-radius:0 6mm 0 0;overflow:hidden}
.mat{padding:3.5mm 4mm;border-right:.25mm solid var(--line);display:grid;grid-template-columns:22mm 1fr;gap:3mm;align-items:center}.mat:last-child{border-right:0}
.mat .sw{height:12mm;border-radius:0 3mm 0 0}
.mat .sw.trav{background:linear-gradient(135deg,#e3d4b6,#cdb894 55%,#dccdb0)}.mat .sw.render{background:linear-gradient(135deg,#f7f4ee,#e9e3d6)}.mat .sw.timber{background:repeating-linear-gradient(90deg,#8d5a2b 0 2.2mm,#a26c37 2.2mm 3mm,#7a4c22 3mm 3.5mm)}
.mat b{display:block;font-weight:500;font-size:9pt}.mat span{font-size:6.2pt;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.duo{display:grid;grid-template-columns:1fr 1fr;gap:6mm;height:158mm}
/* grounds */
.grounds .head{margin-bottom:4mm}
.gv{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;height:58mm;margin-bottom:3mm}
.dims{display:flex;gap:8mm;font-size:6.5pt;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:2mm}
.dims b{font-family:var(--font-d);font-weight:400;font-size:11pt;letter-spacing:0;text-transform:none;color:var(--fg);margin-right:1.5mm}.dims .r{margin-left:auto}
.siteplan{height:84mm;border:.25mm solid var(--line);border-radius:0 6mm 0 0;overflow:hidden;background:var(--basalt)}.siteplan img{width:100%;height:100%;object-fit:contain}
/* interiors */
.masonry{display:grid;grid-template-columns:repeat(6,1fr);gap:3.2mm 3mm}
.masonry figure{margin:0}.masonry img{width:100%;height:47mm;object-fit:cover;border-radius:0 4mm 0 0}
.masonry figcaption{font-size:6pt;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-top:1.5mm;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600}
/* plans */
.pv{display:grid;grid-template-columns:1fr 72mm;gap:8mm;height:158mm}
.pv2{display:grid;grid-template-columns:1fr 62mm 1fr 62mm;gap:5mm;height:150mm}
.planbox{position:relative;border:.25mm solid var(--line);border-radius:0 8mm 0 0;background:#fff;padding:5mm;height:100%}
.planbox img{width:100%;height:100%;object-fit:contain}
.planbox .k{position:absolute;left:0;bottom:0;padding:2mm 3.5mm;font-size:6pt;letter-spacing:.24em;text-transform:uppercase;font-weight:600;color:var(--muted)}
.floornote{font-family:var(--font-d);font-size:12.5pt;font-weight:300;line-height:1.25;margin:0 0 3mm}.floornote em{font-style:italic;color:var(--acc)}
.rooms{list-style:none;margin:0;padding:0;border-top:.25mm solid var(--line)}
.rooms li{display:flex;justify-content:space-between;gap:3mm;padding:1.6mm 0;border-bottom:.25mm solid var(--line);font-size:8pt}.rooms li span:last-child{color:var(--muted)}.rooms li.tot{font-weight:500}.rooms li.tot span:last-child{color:var(--fg)}
.pv2 .rooms li{font-size:7.4pt;padding:1.3mm 0}.pv2 .floornote{font-size:10.5pt}
/* climate */
.suns{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;margin-bottom:3.5mm}
.suns figure{margin:0;border:.25mm solid var(--line);border-radius:0 5mm 0 0;padding:2.5mm 2.5mm 2mm;background:var(--white)}
.suns svg{max-height:44mm}
.suns svg{width:100%;height:auto;display:block;font-family:var(--font-b)}
.suns figcaption{display:flex;justify-content:space-between;font-size:6.5pt;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-top:2mm}.suns figcaption b{color:var(--fg)}
.sk-sky{fill:var(--white-2)}.sk-ground{fill:var(--white-3)}.sk-wall{fill:var(--white);stroke:var(--ink);stroke-width:.6}.sk-slab{fill:var(--white-3);stroke:var(--ink);stroke-width:.6}.sk-slat{fill:var(--bronze)}.sk-glass{fill:#9fb4bd;opacity:.35}.sk-shade{fill:var(--basalt);opacity:.2}.sk-sun{fill:var(--bronze-2)}.sk-ray{stroke:var(--bronze);stroke-width:.4;opacity:.55;stroke-dasharray:1.2 1.6}.sk-arc{fill:none;stroke:rgba(27,25,21,.34);stroke-width:.4;stroke-dasharray:1 1.6}
.sk-txt{font-size:2.7px;letter-spacing:.16em;text-transform:uppercase;fill:#77705f;font-weight:600}.sk-txt.b{font-family:var(--font-d);font-size:5.2px;letter-spacing:0;text-transform:none;fill:var(--ink);font-weight:500}.sk-dim{stroke:rgba(27,25,21,.34);stroke-width:.3}.sk-people{fill:none;stroke:var(--ink);stroke-width:.5;stroke-linecap:round}.sk-car{fill:none;stroke:var(--ink);stroke-width:.45}
.strat{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:0 6mm;border-top:.25mm solid var(--line)}
.strat li{display:grid;grid-template-columns:20mm 1fr;gap:2mm;padding:1.6mm 0;border-bottom:.25mm solid var(--line);font-size:7pt;line-height:1.35}
.strat li .h{font-size:6pt;letter-spacing:.2em;text-transform:uppercase;color:var(--acc);padding-top:.8mm;font-weight:600}.strat li p{margin:0;color:var(--muted)}.strat li p b{color:var(--fg);font-weight:500}
.principle{font-family:var(--font-d);font-weight:300;font-size:11pt;margin:2mm 0 0}
.clim-facts{display:grid;grid-template-columns:repeat(4,1fr);gap:6mm;margin-top:2.5mm;padding-top:2.5mm;border-top:.25mm solid var(--line)}
.clim-facts .n{font-family:var(--font-d);font-weight:300;font-size:15pt;line-height:1}.clim-facts .n small{font-size:6.5pt;color:var(--acc);margin-left:1mm;letter-spacing:.1em;font-family:var(--font-b)}
.clim-facts .l{font-size:6pt;letter-spacing:.2em;text-transform:uppercase;color:var(--acc);margin:1.5mm 0;font-weight:600}.clim-facts p{margin:0;font-size:6.8pt;line-height:1.35;color:var(--muted)}
/* specification */
.spec{display:grid;grid-template-columns:repeat(3,1fr);gap:8mm;margin-bottom:6mm}
.spec h4{font-size:6.5pt;letter-spacing:.28em;text-transform:uppercase;color:var(--acc);margin:0 0 2.5mm;padding-bottom:2mm;border-bottom:.25mm solid var(--line);font-weight:600}
.spec ul{list-style:none;margin:0;padding:0}.spec li{padding:1.8mm 0 1.8mm 4mm;position:relative;font-size:8.2pt;line-height:1.4;border-bottom:.25mm solid var(--line)}.spec li::before{content:"";position:absolute;left:0;top:3.6mm;width:2mm;height:.25mm;background:var(--acc)}
.specimg{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm;height:66mm}
/* contact */
.cg{display:grid;grid-template-columns:1fr 78mm;gap:8mm;align-items:start;margin-bottom:5mm}
.cg .fr{height:105mm}
.cols{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6mm}.cols h4{font-size:6.5pt;letter-spacing:.28em;text-transform:uppercase;color:var(--acc);margin:0 0 2.5mm;font-weight:600}
.toc{list-style:none;margin:0;padding:0}.toc li{display:flex;gap:3mm;padding:1.4mm 0;border-bottom:.25mm solid var(--line);font-size:8pt}.toc li .num{font-family:var(--font-d);color:var(--muted);width:6mm}
.who{margin:0 0 2.5mm;font-size:8pt;line-height:1.5}.who b{display:block;font-weight:500;color:var(--fg)}
.contact{display:flex;flex-direction:column}.contact a{display:flex;justify-content:space-between;align-items:center;gap:3mm;text-decoration:none;color:inherit;padding:1.6mm 0;border-bottom:.25mm solid var(--line);font-size:8pt}
.contact a .chip{display:inline-flex;align-items:center;gap:1.5mm;font-size:6pt;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:var(--acc)}.contact a .chip svg{width:3.4mm;height:3.4mm;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.disc{font-size:7pt;color:var(--muted);line-height:1.45;max-width:190mm;margin:0}
.mql{display:flex;flex-wrap:wrap;align-items:center;gap:1.5mm 6mm;margin:2.5mm 0 0;font-size:7pt;color:var(--muted)}
.mql a{display:inline-flex;align-items:center;gap:1.5mm;color:var(--acc);text-decoration:none;font-weight:500}.mql a svg{width:3.2mm;height:3.2mm;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
'''
JS=r'''
(function(){
  var NS='http://www.w3.org/2000/svg', LAT=9.06*Math.PI/180, dec=-23.44*Math.PI/180;
  function draw(svg,hh){
    function el(n,a){ var e=document.createElementNS(NS,n); for(var k in a) e.setAttribute(k,a[k]); svg.appendChild(e); return e; }
    function txt(x,y,s,c,a){ var t=el('text',{x:x,y:y,'class':c}); if(a) for(var k in a) t.setAttribute(k,a[k]); t.textContent=s; return t; }
    var S=13, GF=158, FF=GF-3.6*S, SF=GF-7.2*S, RF=GF-10.8*S, PAR=RF-1.05*S, SL=0.3*S, W1=100, W2=W1-2.3*S, E1=W1+3.7*S, E2=W1+2.7*S, ER=W1+6.4*S, CX=E1+36, R=90, BAL=1.1*S;
    el('rect',{'class':'sk-sky',x:0,y:0,width:300,height:GF}); el('path',{'class':'sk-arc',d:'M'+(CX+R)+','+GF+' A'+R+' '+R+' 0 0 0 '+CX+','+(GF-R)});
    txt(CX+R,GF-3,'06:00 · 18:00','sk-txt',{'text-anchor':'end'}); txt(CX+3,GF-R-2,'12:00','sk-txt'); txt(CX+R*0.72+3,GF-R*0.72,'09:00 · 15:00','sk-txt');
    el('rect',{'class':'sk-ground',x:0,y:GF,width:300,height:28}); el('line',{'class':'sk-dim',x1:0,y1:GF,x2:300,y2:GF});
    var shG=el('polygon',{'class':'sk-shade'}), sh1=el('polygon',{'class':'sk-shade'}), sh2=el('polygon',{'class':'sk-shade'});
    el('rect',{'class':'sk-wall',x:0,y:FF+SL,width:W1,height:GF-FF-SL}); el('rect',{'class':'sk-wall',x:0,y:SF+SL,width:W1,height:FF-SF-SL}); el('rect',{'class':'sk-wall',x:0,y:RF+SL,width:W2,height:SF-RF-SL});
    el('rect',{'class':'sk-slab',x:0,y:FF,width:E1,height:SL}); el('rect',{'class':'sk-slab',x:0,y:SF,width:E2,height:SL}); el('rect',{'class':'sk-slab',x:0,y:RF,width:E2,height:SL});
    for(var k=0;k<9;k++) el('rect',{'class':'sk-slat',x:E2+3+k*(ER-E2-3)/9,y:RF+0.6,width:2.2,height:SL-1.2});
    el('rect',{'class':'sk-slab',x:E2-2.2,y:PAR,width:2.2,height:RF-PAR});
    el('rect',{'class':'sk-glass',x:W1-1.5,y:FF+SL,width:3,height:GF-FF-SL}); el('rect',{'class':'sk-glass',x:W1-1.5,y:SF+SL,width:3,height:FF-SF-SL}); el('rect',{'class':'sk-glass',x:W2-1.5,y:RF+SL,width:3,height:SF-RF-SL});
    el('rect',{'class':'sk-glass',x:E1-1.2,y:FF-BAL,width:1.4,height:BAL}); el('rect',{'class':'sk-glass',x:E2-1.2,y:SF-BAL,width:1.4,height:BAL});
    var px=W1+1.7*S, ph=1.75*S, py=FF-ph; el('circle',{'class':'sk-people',cx:px,cy:py+2.2,r:2.2});
    el('path',{'class':'sk-people',d:'M'+px+','+(py+4.4)+' V'+(py+15)+' M'+(px-4.5)+','+(py+9)+' H'+(px+4.5)+' M'+px+','+(py+15)+' L'+(px-3.2)+','+FF+' M'+px+','+(py+15)+' L'+(px+3.2)+','+FF});
    var cx=W1+1.9*S, cw=4.4*S, chh=1.45*S;
    el('path',{'class':'sk-car',d:'M'+(cx-cw/2)+','+(GF-4)+' V'+(GF-chh*0.55)+' L'+(cx-cw/2+7)+','+(GF-chh*0.55)+' L'+(cx-cw/2+15)+','+(GF-chh)+' H'+(cx+cw/2-14)+' L'+(cx+cw/2-5)+','+(GF-chh*0.55)+' H'+(cx+cw/2)+' V'+(GF-4)+' Z'});
    el('circle',{'class':'sk-car',cx:cx-cw/2+11,cy:GF-4,r:3.6}); el('circle',{'class':'sk-car',cx:cx+cw/2-11,cy:GF-4,r:3.6});
    txt(W1/2,GF-16,'Grand lobby','sk-txt b',{'text-anchor':'middle'}); txt(W1/2,FF-18,'Suite 1','sk-txt b',{'text-anchor':'middle'}); txt(W2/2,SF-18,'Suite 6','sk-txt b',{'text-anchor':'middle'});
    txt(W1+2,GF-20.5,'ENTRANCE PORCH','sk-txt'); txt(W1+2,FF-22.5,'APPROACH BALCONY · 53 M²','sk-txt'); txt(W2+2,SF-20,'SUITE 6 BALCONY','sk-txt'); txt(E2+3,RF-3,'TIMBER SLATS','sk-txt');
    el('path',{'class':'sk-dim',d:'M'+W1+','+(FF-11)+' V'+(FF-7)+' M'+E1+','+(FF-11)+' V'+(FF-7)+' M'+W1+','+(FF-9)+' H'+E1}); txt((W1+E1)/2,FF-12.5,'3.7 M','sk-txt',{'text-anchor':'middle'});
    txt(2,GF-2,'0','sk-txt'); txt(2,FF-2,'+3.60','sk-txt'); txt(2,SF-2,'+7.20','sk-txt'); txt(2,RF-2,'+10.80','sk-txt');
    var ray1=el('line',{'class':'sk-ray'}), ray2=el('line',{'class':'sk-ray'}), sun=el('circle',{'class':'sk-sun',r:5});
    var H=(hh-12)*15*Math.PI/180, sa=Math.sin(LAT)*Math.sin(dec)+Math.cos(LAT)*Math.cos(dec)*Math.cos(H), a=Math.asin(sa), t=Math.tan(a);
    function shade(edgeX,soffit,floor,wall){ var hit=soffit+(edgeX-wall)*t; if(hit<floor) return {pts:edgeX+','+soffit+' '+wall+','+soffit+' '+wall+','+hit.toFixed(2),end:[wall,hit],onFloor:wall}; var xf=edgeX-(floor-soffit)/t; return {pts:edgeX+','+soffit+' '+wall+','+soffit+' '+wall+','+floor+' '+xf.toFixed(2)+','+floor,end:[xf,floor],onFloor:xf}; }
    var sx=CX+R*Math.cos(a), sy=GF-R*Math.sin(a); sun.setAttribute('cx',sx); sun.setAttribute('cy',sy);
    var g=shade(E1,FF+SL,GF,W1), b1=shade(E2,SF+SL,FF,W1), b2=shade(E2,RF+SL,SF,W2);
    shG.setAttribute('points',g.pts); sh1.setAttribute('points',b1.pts); sh2.setAttribute('points',b2.pts);
    ray1.setAttribute('x1',sx); ray1.setAttribute('y1',sy); ray1.setAttribute('x2',b1.end[0]); ray1.setAttribute('y2',b1.end[1]); ray2.setAttribute('x1',sx); ray2.setAttribute('y1',sy); ray2.setAttribute('x2',b2.end[0]); ray2.setAttribute('y2',b2.end[1]);
    var shadedM=Math.max(0,Math.min(2.7,(b1.onFloor-W1)/S));
    return 'Sun '+Math.round(a*180/Math.PI)+'° · balcony '+Math.round(shadedM/3.7*100)+'% in shade · sun '+(2.7-shadedM).toFixed(1)+' m under the slab';
  }
  document.querySelectorAll('.suns svg').forEach(function(svg){ var h=parseFloat(svg.getAttribute('data-h')); var r=draw(svg,h); document.getElementById('r'+h).textContent=r; });
  window.__done=true;
})();
'''
doc='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Villa 71</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Manrope:wght@300;400;500;600&display=swap"><style>'+CSS+'</style></head><body>'+''.join(sheets)+'<script>'+JS+'</script></body></html>'
open(os.path.join(P,"print.html"),"w",encoding="utf-8").write(doc); print("print.html", len(doc)//1024, "KB, sheets:", len(sheets))

async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        await pg.goto("file://"+os.path.join(P,"print.html")); await pg.wait_for_function("window.__done===true"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(1500)
        await pg.emulate_media(media="print")
        out=os.path.join(B,"villa-71-brochure.pdf")
        await pg.pdf(path=out,width="297mm",height="210mm",print_background=True,prefer_css_page_size=True,margin={"top":"0","bottom":"0","left":"0","right":"0"})
        await b.close(); print("PDF", out, os.path.getsize(out)//1024, "KB")
asyncio.run(render())
