import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920
GF='/home/claude/fonts/gfonts'
FONT=f'{GF}/ofl/pacifico/Pacifico-Regular.ttf'
INTER_SB='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
sq=cv2.imread('clean_clean.png').astype(np.float32)
sq=cv2.resize(sq,(W,W),interpolation=cv2.INTER_AREA)
y0=H-W  # 840
img=np.zeros((H,W,3),np.float32)
# top: scene sky from source, stretched + softly blurred, blended into square
sc=cv2.imread('scene_src.png').astype(np.float32)
top=sc[0:700,:]                          # sky band
top=cv2.resize(top,(W,y0+200),interpolation=cv2.INTER_CUBIC)
top=cv2.GaussianBlur(top,(0,0),6)
img[0:y0+200]=top
t=np.clip((np.arange(H)-y0)/200,0,1)[:,None,None]
canvas=np.zeros_like(img); canvas[y0:]=sq
img=img*(1-t)+canvas*t
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
img*= (1-0.30*np.clip((700-yy)/700,0,1)**1.2)[...,None]
def hexc(h):
    h=h.lstrip('#');return np.array([int(h[4:6],16),int(h[2:4],16),int(h[0:2],16)],np.float32)
def mask(fn):
    m=Image.new('L',(W,H),0);fn(ImageDraw.Draw(m));return np.asarray(m,np.float32)/255
def styled(img,A,ft,fb,ol,ow,top,bot,shadow=0.65):
    Ao=cv2.dilate(A,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*ow+1,2*ow+1)));Ao=cv2.GaussianBlur(Ao,(0,0),0.8)
    sh=cv2.GaussianBlur(np.roll(np.roll(Ao,9,0),5,1),(0,0),8)*shadow
    img=img*(1-sh[...,None]);img=img*(1-Ao[...,None])+hexc(ol)*Ao[...,None]
    tt=np.clip((yy-top)/max(1,bot-top),0,1)[...,None];col=hexc(ft)*(1-tt)+hexc(fb)*tt
    hb=cv2.GaussianBlur(A,(0,0),3);gy,gx=np.gradient(hb);bev=np.clip(-(gx*0.6+gy*0.8)*9,-1,1)
    col=col+bev[...,None]*70
    return img*(1-A[...,None])+np.clip(col,0,255)*A[...,None]
d0=ImageDraw.Draw(Image.new('L',(8,8)))
lines=['Glad You’re','Here']
f=ImageFont.truetype(FONT,176)
bases=[560,760]
for ln,b in zip(lines,bases):
    l,tp,r,bt=d0.textbbox((0,0),ln,font=f,anchor='ls')
    x=(W-(r-l))/2-l
    A=mask(lambda d:d.text((x,b),ln,font=f,fill=255,anchor='ls'))
    img=styled(img,A,'#fff4bf','#ff7f1a','#5a1a04',7,b+tp,b+10,0.75)
fa=ImageFont.truetype(INTER_SB,50);art,sp='ZACHARY PATZER',18
wid=sum(d0.textlength(c,font=fa) for c in art)+sp*(len(art)-1)
def da(d):
    x=(W-wid)/2
    for c in art:
        d.text((x,250),c,font=fa,fill=255,anchor='ls');x+=d.textlength(c,font=fa)+sp
img=styled(img,mask(da),'#fffaf1','#ffe6c4','#3d0f08',4,210,250,0.55)
cv2.imwrite('/home/claude/out/Glad_Youre_Here_Facebook_Vertical.jpg',np.clip(img,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,93])
