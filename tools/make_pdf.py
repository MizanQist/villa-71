# Builds villa-71-brochure.pdf: A4-landscape sheets, one subject to a page, from the site's markup, tokens and images (no 360° tour).
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
EXT=[("hero",1800),("gate",1800),("rec-a",1800),("rec-b",1800),("rec-c",1800),("front-cloud",1800),("chalet",1800)]
for n,long in EXT: prep(os.path.join(A,n+".jpg"),n+".jpg",long,82)
tiles=re.findall(r'<figure class="tile rv" data-g="(\w+)" data-lb="interiors" data-src="assets/i/([\w-]+)\.jpg" data-cap="([^"]+)"',site)
CAP={slug:cap for g,slug,cap in tiles}
AR={}
for g,slug,cap in tiles:
    prep(os.path.join(A,"i",slug+".jpg"),"i-"+slug+".jpg",1500,78); AR["i-"+slug]=Image.open(os.path.join(IMG,"i-"+slug+".jpg")).size
for n,_ in EXT: AR[n]=Image.open(os.path.join(IMG,n+".jpg")).size
flat(os.path.join(A,"site-plan.png"),"site-plan.jpg",BONE,BASALT,2600)
for n in ("basement","ground","first","second","guest"): flat(os.path.join(A,"plan-%s.png"%n),"plan-%s.jpg"%n,(27,25,21),WHITE,2200)

def block(start,end): s=site.index(start); e=site.index(end,s); return site[s:e]
def panel(key):
    b=block('<div class="pp" data-p="%s"'%key,'        </div>\n'); return b[b.index('>')+1:]
story=block('<div class="story">','    <div class="fr wide rv wipe"')
spec=block('<div class="spec">','    <div class="specimg">')+'</div>'
strat=block('<ul class="strat">','<p class="principle')
principle=re.search(r'<p class="principle rv" style="--i:7">(.*?)</p>',site).group(1)
facts=block('<div class="clim-facts">','    <div class="pfoot"><span><b>Villa 71</b> · Climate and ground</span>')
cols=block('<div class="cols">','    <p class="disc rv">')
disc=re.search(r'<p class="disc rv">(.*?)</p>',site,re.S).group(1)
mql=block('<div class="mql rv"','    <div class="pfoot"><span><b>Villa 71</b> · Guzape · Abuja · 2026</span>')
mats=block('<div class="mats rv" style="--i:2">','        <div class="fr rv wipe" style="--i:3" data-lb="scheme" data-src="assets/chalet.jpg"')
def clean(s): return re.sub(r' (rv|wipe)\b','',re.sub(r' style="--i:\d+"','',s)).replace(' loading="lazy"','').replace(' decoding="async"','')

sheets=[]
def foot(label): return '<div class="pfoot"><span><b>Villa 71</b> · %s</span><span class="pn">{PN} / {N}</span></div>'%label
def head(eyebrow,title,lede=''):
    return '<div class="head"><div><p class="eyebrow"><span class="idx">{SN}</span>%s</p><h2 class="title">%s</h2></div>%s</div>'%(eyebrow,title,('<p class="lede">%s</p>'%lede) if lede else '')
def imgbox(name,h=174,maxw=200):
    ar=AR[name]; w=min(maxw,h*ar[0]/ar[1]); hh=w*ar[1]/ar[0]
    return '<div class="fr plate-img" style="width:%.1fmm;height:%.1fmm"><img src="img/%s.jpg" alt=""></div>'%(w,hh,name)
def plate(tone,eyebrow,title,note,name,label):
    return '<section class="sheet %s plate">'%tone+'<div class="plate-txt"><p class="eyebrow"><span class="idx">{SN}</span>%s</p><h2 class="title">%s</h2><p class="lede">%s</p></div>'%(eyebrow,title,note)+imgbox(name)+foot(label)+'</section>'
def tilepage(tone,eyebrow,title,slugs,label,note=''):
    n=len(slugs); tl=''.join('<figure><div class="fr"><img src="img/i-%s.jpg" alt=""></div><figcaption>%s</figcaption></figure>'%(s,html.escape(CAP[s])) for s in slugs)
    if n==1: return plate(tone,eyebrow,title,note or CAP[slugs[0]],'i-'+slugs[0],label)
    if n==4: return '<section class="sheet %s">'%tone+'<div class="quad"><div class="plate-txt"><p class="eyebrow"><span class="idx">{SN}</span>%s</p><h2 class="title">%s</h2>%s</div><div class="grid2">%s</div></div>'%(eyebrow,title,('<p class="lede">%s</p>'%note) if note else '',tl)+foot(label)+'</section>'
    return '<section class="sheet %s">'%tone+head(eyebrow,title,note)+'<div class="band band%d">%s</div>'%(n,tl)+foot(label)+'</section>'

# 01 cover
sheets.append('<section class="sheet dark cover"><div class="cl"><div class="mark"><span class="v">Villa</span><span class="n">71</span></div><div class="side"><b>A private residence <em>in Guzape,</em> Abuja</b>Seven suites · guest chalet · pool<br>A365 Designs</div></div><div class="cr"><img src="img/hero.jpg" alt=""></div></section>')
# 02 at a glance
sheets.append('<section class="sheet light">'+head('At a glance','Three floors, seven suites, <em>one garden wall.</em>')+'<div class="g2"><div><div class="stats"><div class="stat"><div class="n">7</div><div class="l">En-suite suites</div></div><div class="stat"><div class="n">4<small>+1</small></div><div class="l">Levels + guest chalet</div></div><div class="stat"><div class="n">1,735<small>m²</small></div><div class="l">Main house · four levels</div></div><div class="stat"><div class="n">2,000<small>m²</small></div><div class="l">Plot · 30 × 67 m</div></div><div class="stat"><div class="n">15<small>+</small></div><div class="l">Cars inside the wall</div></div><div class="stat"><div class="n">24,000<small>L</small></div><div class="l">Water reservoir</div></div></div>'+clean(story)+'</div><div class="fr tall"><img src="img/gate.jpg" alt="" style="object-position:50% 45%"><span class="k"><i>01</i>From the road</span></div></div>'+foot('At a glance')+'</section>')
# the scheme: overview, then one exterior view per page, the chalet last
sheets.append('<section class="sheet dark">'+head('The scheme','Travertine, white render, <em>timber.</em>','Warm travertine against white render, timber slats over the terraces: the latest visualisations of the house, one view to a page.')+'<div class="trip"><div class="fr"><img src="img/rec-a.jpg" alt=""><span class="k"><i>02</i>The approach</span></div><div class="fr"><img src="img/rec-b.jpg" alt=""><span class="k"><i>03</i>The corner</span></div><div class="fr"><img src="img/rec-c.jpg" alt=""><span class="k"><i>04</i>The forecourt</span></div></div>'+clean(mats)+foot('The scheme')+'</section>')
for name,title,note in [("hero","The garden <em>side.</em>","The rounded parapet, the travertine tower and the timber slats over the terrace, seen from the cactus garden."),("rec-a","The <em>approach.</em>","Cars under the porte-cochère, the travertine tower and the slatted roof terrace above."),("rec-b","The <em>corner.</em>","The rounded corner of the house from the drive."),("rec-c","The <em>forecourt.</em>","The forecourt with the palm and the travertine tower."),("front-cloud","Under a <em>Guzape sky.</em>","The front of the villa, timber slats shading the roof terrace."),("gate","From the <em>road.</em>","The gatehouse and the garage door in the boundary wall, the villa rising behind."),("chalet","The guest <em>chalet.</em>","A single-storey guest chalet in travertine and white render beside the drive.")]:
    sheets.append(plate('dark','The scheme',title,note,name,'The scheme'))
# grounds: page by page
sheets.append(plate('dark','Grounds','Pool and <em>house.</em>',"The pool with the villa's garden elevation behind it, a parasol and loungers on the deck.",'i-pool-house','Grounds'))
sheets.append(plate('dark','Grounds','Expanse <em>terrace.</em>','The second-floor terrace with a fire pit, parasol and lounge seating under the timber pergola.','i-terrace-1','Grounds'))
sheets.append(plate('dark','Grounds','Terrace <em>dining.</em>','Dining on the terrace, palms and the rounded parapet edge.','i-terrace-2','Grounds'))
sheets.append(tilepage('dark','Grounds','The <em>courtyard.</em>',['garden-1','garden-2'],'Grounds','The indoor garden: a planted court at the heart of the ground floor, glazed on every side.'))
sheets.append('<section class="sheet dark grounds">'+head('Grounds','The <em>site.</em>','The pool, gazebo and outdoor kitchen sit at the rear of the plot; the drive, forecourt and guest chalet at the road.')+'<div class="dims"><span><b>67.44 m</b>north</span><span><b>30.23 m</b>road frontage</span><span><b>66.24 m</b>south</span><span><b>30.11 m</b>rear</span><span><b>≈2,000 m²</b>plot</span></div><div class="siteplan big"><img src="img/site-plan.jpg" alt=""></div>'+foot('Grounds')+'</section>')
# interiors: website order, at most four to a page, main rooms on their own pages, chalet last
INT=[('Arrival','The grand <em>lobby.</em>',['lobby','lobby-entrance','stairhall','lounge'],'The entrance sequence: lobby, stair hall and lounge.'),
     ('Living and kitchen','The main <em>living room.</em>',['living-1','living-2','living-3','living-dining'],'The 98 m² living and entertainment room, opening to the garden and the dining.'),
     ('Living and kitchen','<em>Dining.</em>',['dining'],'The dining room off the main living room.'),
     ('Living and kitchen','The <em>kitchen.</em>',['kitchen-1','kitchen-2'],'Marble island, integrated appliances, a window over the counter.'),
     ('Living and kitchen','Private lounge and <em>home office.</em>',['private-lounge-1','private-lounge-2','office'],''),
     ('Living and kitchen','The family <em>lounge.</em>',['family-1','family-2','boxroom'],'The first-floor family living room, with the box room beside it.'),
     ('Suites','Suite <em>1.</em>',['suite1-1','suite1-2'],'The largest of the first-floor suites, 70 m² with dressing room and bathroom.'),
     ('Suites','Suite <em>2.</em>',['suite2-1','suite2-2','suite2-bath'],''),
     ('Suites','Suite <em>3.</em>',['suite3-1','suite3-2','suite3-bath-1','suite3-bath-2'],''),
     ('Suites','Suite <em>4.</em>',['suite4-1','suite4-2','suite4-bath-1','suite4-bath-2'],''),
     ('Suites','The master <em>suite.</em>',['master-lounge-1','master-lounge-2','master-bed-1','master-bed-2'],'Lounge and bedroom on the second floor.'),
     ('Suites','Master suite · <em>dressing and bath.</em>',['master-closet-1','master-closet-2','master-closet-3','master-bath'],''),
     ('Leisure','The <em>gym.</em>',['gym-1','gym-2'],''),
     ('Leisure','The <em>cinema.</em>',['cinema-1','cinema-2','cinema-3'],'In the basement, beside the garage.'),
     ('Guest chalet','The guest <em>chalet.</em>',['chalet-living','chalet-kitchen-1','chalet-kitchen-2'],'Living room and kitchen of the one-bedroom chalet by the drive.')]
used=set(sum([x[2] for x in INT],[])+['garden-1','garden-2','pool-house','terrace-1','terrace-2'])
missing=[s for _,s,_ in tiles if s not in used]; assert not missing, missing
for ey,ti,sl,note in INT: sheets.append(tilepage('light','Interiors · '+ey,ti,sl,'Interiors',note))
# plans: -1, ground, first, second, then the chalet on its own
for key,title,label,lede in [('basement','Basement <em>(−1).</em>','Basement · N.T.S','Cut into the hillside below the entrance side: garage, cinema and a staff room, 2.85 m below the ground floor.'),('ground','Ground <em>floor.</em>','Ground floor · N.T.S','A lift and stair core serves four levels, from the basement garage and cinema to the second floor. Areas are as scheduled by the architects on the June 2026 drawings.'),('first','First <em>floor.</em>','First floor · N.T.S',''),('second','Second <em>floor.</em>','Second floor · N.T.S',''),('guest','The guest <em>chalet.</em>','Guest chalet and staff · N.T.S','A one-bedroom guest chalet with its own living room and kitchen, plus two staff rooms and a laundry, beside the drive.')]:
    sheets.append('<section class="sheet light">'+head('Plans',title,lede)+'<div class="pv"><div class="planbox"><img src="img/plan-%s.jpg" alt=""><span class="k">%s</span></div><div class="pp">'%(key,label)+clean(panel(key))+'</div></div>'+foot('Plans')+'</section>')
# climate
sheets.append('<section class="sheet light">'+head('Climate and ground','Sun, shade <em>and the hillside.</em>',"Guzape sits at nine degrees north on the granite hills south of Abuja's centre: a high sun all year, harmattan haze from December, rains from April to October. The approach balcony, the largest of the villa's balconies, at three times of a December day.")+'<div class="suns"><figure><svg data-h="9" viewBox="0 0 300 186"></svg><figcaption><b>09:00</b><span id="r9"></span></figcaption></figure><figure><svg data-h="12" viewBox="0 0 300 186"></svg><figcaption><b>12:00</b><span id="r12"></span></figcaption></figure><figure><svg data-h="15" viewBox="0 0 300 186"></svg><figcaption><b>15:00</b><span id="r15"></span></figcaption></figure></div>'+clean(strat)+'</ul><p class="principle">'+principle+'</p>'+clean(facts)+foot('Climate and ground')+'</section>')
# specification
sheets.append('<section class="sheet light">'+head('Specification','Built <em>to last.</em>')+clean(spec)+'<div class="specimg"><div class="fr"><img src="img/i-master-bath.jpg" alt=""></div><div class="fr"><img src="img/i-kitchen-2.jpg" alt=""></div><div class="fr"><img src="img/i-master-closet-1.jpg" alt=""></div><div class="fr"><img src="img/i-stairhall.jpg" alt=""></div></div>'+foot('Specification')+'</section>')
# contact
c=clean(cols); c=re.sub(r'<h4>In this brochure</h4>\s*<ol class="toc">.*?</ol>','<h4>In this brochure</h4><ol class="toc">{TOC}</ol>',c,flags=re.S)
sheets.append('<section class="sheet dark contact">'+head('Contact','See the house <em>in Guzape.</em>','Drawings, the full specification and a site visit can be arranged through A365 Designs.')+'<div class="cg"><div>'+c+'</div><div class="fr"><img src="img/rec-b.jpg" alt=""><span class="k">The corner</span></div></div><p class="disc">'+disc+'</p>'+clean(mql)+foot('Contact')+'</section>')
sheets.append('<section class="sheet dark back"><div class="mark"><span class="v">Villa</span><span class="n">71</span></div><p>Guzape · Abuja · A365 Designs · brochure by Mizan Qist Limited · 2026</p></section>')

# numbering and contents
N=len(sheets); out=[]; first={}
for i,sh in enumerate(sheets,1):
    lab=re.search(r'<b>Villa 71</b> · ([^<]+)</span>',sh); key=lab.group(1) if lab else None
    if key and key not in first: first[key]=i
    out.append(sh.replace('{PN}','%02d'%i).replace('{N}','%02d'%N).replace('{SN}','%02d'%i))
toc=''.join('<li><span class="num">%02d</span><span>%s</span></li>'%(first[k],k) for k in ['At a glance','The scheme','Grounds','Interiors','Plans','Climate and ground','Specification'] if k in first)
sheets=[x.replace('{TOC}',toc) for x in out]

CSS=open(os.path.join(P,"print.css"),encoding="utf-8").read()

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
