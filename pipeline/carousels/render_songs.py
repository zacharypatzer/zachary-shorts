from lib import *
from songs import SONGS
def lyric_slide(text,title,i,n):
    im=bg(); d=ImageDraw.Draw(im)
    fb=lora(70 if max(len(x) for x in text.split('\n'))<32 else 58)
    lines=[]
    for part in text.split('\n'): lines+=balanced(d,part,fb,920)
    lh=fb.size*1.28; hb=len(lines)*lh; fq=lora(150)
    y=(H-hb)/2-60
    d.text(((W-d.textlength('“',font=fq))/2,y-150),'“',font=fq,fill=GOLD)
    for ln in lines:
        d.text(((W-d.textlength(ln,font=fb))/2,y),ln,font=fb,fill=CREAM); y+=lh
    y+=30; d.line([(W/2-70,y),(W/2+70,y)],fill=GOLD,width=3); y+=30
    ft=lora(40,False); s='— '+title; d.text(((W-d.textlength(s,font=ft))/2,y),s,font=ft,fill=DIM)
    footer(d,i,n); return im
def cta_slide(title,i,n):
    return slide('Hear the full song',f'“{title}” is on YouTube.\n@zacharypatzer',i,n)
for date,slug,title,sub,sl,q in SONGS:
    n=len(sl)+2; ims=[portrait_slide(title,sub,1,n)]
    ims+=[lyric_slide(x,title,k+2,n) for k,x in enumerate(sl)]
    ims.append(cta_slide(title,n,n))
    for k,im in enumerate(ims,1): im.save(f'{OUT}/s_{slug}_{k}.jpg',quality=92)
    sh=Image.new('RGB',(len(ims)*W//3,H//3))
    for k,im in enumerate(ims): sh.paste(im.resize((W//3,H//3)),(k*W//3,0))
    sh.save(f'{OUT}/sheet_{slug}.jpg',quality=85)
print('done')
