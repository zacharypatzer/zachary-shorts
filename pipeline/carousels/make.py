import os, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1350
R='/home/claude/zacharypatzer/zachary-shorts/pipeline'
LORA='/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
INTER='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
INTERM='/usr/share/fonts/opentype/inter/Inter-Medium.otf'
GOLD=(232,184,96); CREAM=(250,242,228); DIM=(205,190,170)
OUT='/home/claude/carousels/out'; os.makedirs(OUT,exist_ok=True)
SCR='/tmp/claude-0/-home-claude/cb0a3232-efbb-506f-975f-a63d141a917e/scratchpad'

def lora(sz,bold=True):
    f=ImageFont.truetype(LORA,sz)
    try: f.set_variation_by_name('Bold' if bold else 'Regular')
    except Exception: pass
    return f

def bg():
    y=np.linspace(0,1,H)[:,None,None]; x=np.linspace(0,1,W)[None,:,None]
    top=np.array([16,24,40]); bot=np.array([46,30,22])
    a=top*(1-y)+bot*y
    glow=np.exp(-(((x-0.5)/0.6)**2+((y-0.38)/0.45)**2))
    a=a+glow*np.array([40,26,10])
    rng=np.random.default_rng(3); a=a+rng.normal(0,2.2,(H,W,1))
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))

def wrap(d,text,f,maxw):
    out=[]
    for para in text.split('\n'):
        line=''
        for w in para.split():
            t=(line+' '+w).strip()
            if d.textlength(t,font=f)<=maxw: line=t
            else: out.append(line); line=w
        out.append(line)
    return out

def balanced(d,text,f,maxw):
    n=len(wrap(d,text,f,maxw)); w=maxw
    while w>300 and len(wrap(d,text,f,w-10))==n: w-=10
    return wrap(d,text,f,w)

def block(d,y,text,f,fill,maxw=900,lh=1.25,center=True):
    for ln in balanced(d,text,f,maxw):
        tw=d.textlength(ln,font=f); x=(W-tw)/2 if center else 90
        d.text((x,y),ln,font=f,fill=fill); y+=f.size*lh
    return y

def measure(d,text,f,maxw=900,lh=1.25): return len(wrap(d,text,f,maxw))*f.size*lh

def footer(d,i,n):
    f=ImageFont.truetype(INTER,30)
    d.text((90,H-95),'@zacharypatzer',font=f,fill=DIM)
    s=f'{i}/{n}'; d.text((W-90-d.textlength(s,font=f),H-95),s,font=f,fill=DIM)

def slide(big,small=None,i=1,n=6,swipe=False,kicker=None):
    im=bg(); d=ImageDraw.Draw(im)
    fb=lora(76 if len(big)<70 else 64); fs=lora(44,False)
    hb=measure(d,big,fb); hs=measure(d,small,fs)+40 if small else 0
    hk=90 if kicker else 0
    y=(H-hb-hs-hk)/2-40
    if kicker:
        fk=ImageFont.truetype(INTER,32)
        sp=' '.join(kicker.upper()); tw=d.textlength(sp,font=fk); d.text(((W-tw)/2,y),sp,font=fk,fill=GOLD); y+=hk
    y=block(d,y,big,fb,CREAM)
    if small:
        y+=10; d.line([(W/2-70,y),(W/2+70,y)],fill=GOLD,width=3); y+=30
        block(d,y,small,fs,DIM)
    if swipe:
        f=ImageFont.truetype(INTERM,34); s='Swipe  →'; d.text(((W-d.textlength(s,font=f))/2,H-210),s,font=f,fill=GOLD)
    footer(d,i,n); return im

def portrait_slide(big,small,i,n):
    im=bg()
    P=cv2.imread(f'{R}/assets/face_src.jpg'); m=cv2.imread(f'{SCR}/matte.png',0).astype(np.float32)/255
    P=cv2.cvtColor(P,cv2.COLOR_BGR2RGB).astype(np.float32)
    s=0.66; P=cv2.resize(P,None,fx=s,fy=s,interpolation=cv2.INTER_AREA); m=cv2.resize(m,(P.shape[1],P.shape[0]))
    ph,pw=P.shape[:2]; x0=(W-pw)//2; y0=150
    yy=np.linspace(0,1,ph)[:,None]; m=m*np.clip((1-yy)/0.18,0,1)  # fade bottom
    base=np.asarray(im).astype(np.float32)
    reg=base[y0:y0+ph,x0:x0+pw]; base[y0:y0+ph,x0:x0+pw]=reg*(1-m[...,None])+P*m[...,None]
    im=Image.fromarray(base.astype(np.uint8)); d=ImageDraw.Draw(im)
    y=y0+ph+10
    y=block(d,y,big,lora(84 if len(big)<25 else 62),CREAM); y+=10
    d.line([(W/2-70,y),(W/2+70,y)],fill=GOLD,width=3); y+=30
    block(d,y,small,lora(42,False),DIM)
    f=ImageFont.truetype(INTERM,34); s='Swipe  →'; d.text(((W-d.textlength(s,font=f))/2,H-180),s,font=f,fill=GOLD)
    footer(d,i,n); return im

C={
'c1_after_the_bell':[
 dict(portrait=True,big='Ringing the bell was the best day of my life.',small='Here’s what nobody sees after.'),
 dict(big='The tired doesn’t leave with the cancer.',small='Some days, a shower is the whole plan.'),
 dict(big='Every checkup brings it all back.',small='Scanxiety is real, no matter how many years clear you are.'),
 dict(big='Your body keeps the receipts.',small='Some of us walk with a little help now. I call mine my buggie.'),
 dict(big='Everyone expects you to go back to normal.',small='There is no going back. There’s only building a new normal.'),
 dict(big='If you’re there too:\nyou’re not behind.\nYou’re rebuilding.',small='Follow along. No one should fight alone.'),
],
'c2_what_helps':[
 dict(portrait=True,big='What actually helps someone after cancer',small='From someone who’s been there.'),
 dict(big='Skip “You look great!”',small='Try: “How are you really doing?”'),
 dict(big='Don’t disappear when treatment ends.',small='That’s when the quiet hits hardest.'),
 dict(big='Offer something specific.',small='“Can I bring dinner Tuesday?” beats “Let me know if you need anything.”'),
 dict(big='Let them be tired without explaining.',small='Canceled plans aren’t personal.'),
 dict(big='Just keep showing up.\nThat’s the whole thing.',small='Send this to someone who needs it.'),
],
'c3_meet_zachary':[
 dict(portrait=True,big='Hi, I’m Zachary.',small='Stage 4 Hodgkin’s lymphoma survivor.'),
 dict(big='I rang the bell three times.',small='And I’m still here.'),
 dict(big='Chemo took a lot from me.',small='My energy. My body. Not my voice.'),
 dict(big='So I write songs and books about real life after cancer.'),
 dict(big='For anyone still fighting.\nAnyone who made it out.\nAnyone who loves them.'),
 dict(big='Follow along.',small='No one should fight alone.'),
],
}
for k,slides in C.items():
    n=len(slides); ims=[]
    for i,s in enumerate(slides,1):
        im=portrait_slide(s['big'],s['small'],i,n) if s.get('portrait') else slide(s['big'],s.get('small'),i,n,s.get('swipe',False),s.get('kicker'))
        p=f'{OUT}/{k}_{i}.jpg'; im.save(p,quality=93); ims.append(im)
    sheet=Image.new('RGB',(3*W//2,2*H//2))
    for j,im in enumerate(ims): sheet.paste(im.resize((W//2,H//2)),((j%3)*W//2,(j//3)*H//2))
    sheet.save(f'{OUT}/{k}_preview.jpg',quality=90)
print('ok')
