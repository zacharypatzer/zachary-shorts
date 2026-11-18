from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import glob,random
P='/home/claude/zachary-shorts/pipeline/'
W,H=1280,720
covers=sorted(set(glob.glob(P+'out/*_Cover.jpg'))-set(glob.glob(P+'out/*Reel_Cover.jpg')))
skip=['Thatd_Be_Easy','Unfinished','What_Im_Livin','Its_Your_Birthday']
covers=[c for c in covers if not any(s in c for s in skip)]
covers+= [P+'qh/covers/'+s+'.jpg' for s in ['a_mile_an_hour','take_a_number','lions_heart','light_one_let_it_go','floor_of_shadows','beautiful_anyway','living_in_the_echo','remember_me_when_im_gone']]
random.seed(7); random.shuffle(covers)
bg=Image.new('RGB',(W,H)); t=184
i=0
for y in range(-40,H,t):
  for x in range(-60,W,t):
    bg.paste(Image.open(covers[i%len(covers)]).convert('RGB').resize((t-6,t-6)),(x+3,y+3)); i+=1
bg=ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(1.2))).enhance(0.38)
# left dark gradient
g=Image.new('L',(W,H)); gd=ImageDraw.Draw(g)
for x in range(W): gd.line([(x,0),(x,H)],fill=int(235*max(0,1-x/820)))
bg=Image.composite(Image.new('RGB',(W,H),(8,8,12)),bg,g)
# portrait
f=Image.open(P+'assets/face_src.jpg').convert('RGB'); m=Image.open(P+'assets/face_matte.png').convert('L')
s=760/f.height; f=f.resize((int(f.width*s),760)); m=m.resize(f.size)
glow=Image.new('L',(W,H)); px=W-f.width+90
glow.paste(m,(px,H-760+20)); glow=glow.filter(ImageFilter.GaussianBlur(28))
bg=Image.composite(Image.new('RGB',(W,H),(255,196,92)),bg,glow.point(lambda v:int(v*0.55)))
bg.paste(f,(px,H-760+20),m)
d=ImageDraw.Draw(bg)
F=P+'fonts/gfonts/ofl/'
small=ImageFont.truetype(F+'anton/Anton-Regular.ttf',40)
big=ImageFont.truetype(F+'bebasneue/BebasNeue-Regular.ttf',190)
sub=ImageFont.truetype(F+'dmserifdisplay/DMSerifDisplay-Italic.ttf',54)
def spaced(xy,txt,font,fill,sp):
  x,y=xy
  for ch in txt:
    d.text((x,y),ch,font=font,fill=fill); x+=d.textlength(ch,font=font)+sp
spaced((70,150),'ZACHARY PATZER',small,(235,235,235),9)
d.text((64,205),'THE',font=big,fill=(255,255,255),stroke_width=2,stroke_fill=(0,0,0))
d.text((64,375),'PLAYLIST',font=big,fill=(255,190,80),stroke_width=2,stroke_fill=(0,0,0))
d.text((72,585),"You're not alone.",font=sub,fill=(240,240,240))
bg.save(P+'out/Zachary_Patzer_Playlist_Cover_YouTube.jpg',quality=93)
print(len(covers))
