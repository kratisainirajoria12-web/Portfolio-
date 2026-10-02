"""Seed -> sprout -> soil bridge. Replaces bloom frames 23..62 with K new frames.
Inputs: SRC is the ORIGINAL 160-frame bloom folder (it reads f022 and f063), plus spr_a2.npy (= tools/sprout63_mask.npy, the sprout cut-out mask from sprite.py).
Run: python3 bridge.py <outdir> 160, then write the frames to bloom/f023..f182.webp.
A: a slim sprout pushes out of the cracked seed (camera drifts up with it)
B: the camera tilts up, the shoot climbs into the soil
C: the real sprout breaks out through the mound and hands off to frame 63"""
import cv2,numpy as np,sys,os
SRC='zip/krati-project/bloom'; OUT=sys.argv[1] if len(sys.argv)>1 else 'out'
K=int(sys.argv[2]) if len(sys.argv)>2 else 80
os.makedirs(OUT,exist_ok=True)
W,H=1280,720
ss=lambda x:(lambda c:c*c*(3-2*c))(np.clip(x,0,1))
rng=lambda t,a,b:np.clip((t-a)/(b-a),0,1)
lerp=lambda a,b,t:a+(b-a)*t
F22=cv2.imread(f'{SRC}/f022.webp').astype(np.float32)
F63=cv2.imread(f'{SRC}/f063.webp').astype(np.float32)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
SPK=(1120,560,1200,640)                          # the corner sparkle every frame carries at the same screen spot
def glyph(F):
    x0,y0,x1,y1=SPK;g=F[y0:y1,x0:x1].mean(2);sat=F[y0:y1,x0:x1].max(2)-F[y0:y1,x0:x1].min(2)
    bg=cv2.medianBlur(np.clip(g,0,255).astype(np.uint8),41).astype(np.float32)
    m=(((g-bg)>22)&(sat<35)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    n,l,st,c=cv2.connectedComponentsWithStats(m);k=1+np.argmax(st[1:,4]);m=(l==k).astype(np.uint8)
    ff=m.copy();cv2.floodFill(ff,None,(0,0),1);m=m|(1-ff)
    full=np.zeros(F.shape[:2],np.uint8);full[y0:y1,x0:x1]=m;return full
def unspark(F):
    m=cv2.dilate(GLYPH,np.ones((7,7),np.uint8))
    return cv2.inpaint(np.clip(F,0,255).astype(np.uint8),m*255,5,cv2.INPAINT_TELEA).astype(np.float32)
GLYPH=glyph(F22);_g=GLYPH;SPA=cv2.GaussianBlur(_g.astype(np.float32),(0,0),.7)
SP22=float(np.median(F22[_g>0].reshape(-1,3).mean(1)));SP63=float(np.median(F63[_g>0].reshape(-1,3).mean(1)))
F22c=unspark(F22);F63c=unspark(F63)

# ---------- world above the frame: bokeh band tiled upward ----------
band=F22c[0:110]
def above(n):            # rows of world y in [-n,0), built from mirrored copies of the band
    out=[];k=0
    while sum(b.shape[0] for b in out)<n:
        out.insert(0,band[::-1] if k%2==0 else band);k+=1
    A=np.concatenate(out,0);return A[-n:]
TOP=1000
WORLD=np.concatenate([above(TOP),F22],0)        # world y = row - TOP
WORLD=cv2.GaussianBlur(WORLD,(0,0),.6)
WORLD[TOP:]=F22c                                  # keep the real frame sharp

# ---------- soil plate: frame 63 with its sprout removed ----------
X0,Y0,X1,Y1=570,95,700,470
a63=np.zeros((H,W),np.float32);a63[Y0:Y1,X0:X1]=np.load('spr_a2.npy')
hole=(cv2.dilate((a63>.05).astype(np.uint8),np.ones((15,15),np.uint8)))
hole[456:]=0
src=np.roll(F63,-110,axis=1)                     # soil texture from the right of the sprout
hm=cv2.GaussianBlur(hole.astype(np.float32),(0,0),4)[...,None]
src=np.roll(F63c,-110,axis=1);PLATE=F63c*(1-hm)+src*hm
# soil the shoot breaks through: silhouette of the mound clumps in frame 63, the stem stands in the gap between them
SIL=[(0,352),(520,352),(560,340),(590,332),(606,334),(613,350),(616,470),(622,461),(629,467),(636,457),(643,465),(649,462),(652,402),(670,388),(700,378),(725,366),(745,368),(780,385),(W,385)]
GROUND=np.zeros((H,W),np.uint8);cv2.fillPoly(GROUND,[np.array(SIL+[(W,H),(0,H)],np.int32)],1)
GROUND=cv2.GaussianBlur(GROUND.astype(np.float32),(0,0),1.6)

# ---------- the slim sprout, drawn like a lit tube ----------
SS=3
def draw_sprout(tip_y,base_y,cx,sway,bud_len=58,bud_r=11.5,stem_r=4.6):
    """returns colour, alpha (world-screen px). tip_y<base_y; centreline bends gently."""
    h=int(base_y-tip_y)+4
    if h<3:return None
    y0=int(tip_y)-2
    ys=(np.arange(h*SS)/SS+y0)+.5/SS
    L=base_y-tip_y
    s=np.clip((ys-tip_y)/max(L,1),0,1)            # 0 tip .. 1 base
    d=ys-tip_y                                     # px from tip
    cxs=cx+sway*np.sin(s*2.4)*(1-s)*1.0+1.2*np.sin(d/37.)
    bl=min(bud_len,max(L*.55,6))
    u=np.clip(d/bl,0,1)
    rb=bud_r*np.where(u<.62,np.sqrt(np.clip(u/.62,0,1))*(1-.1*(1-u/.62)),1-(1-stem_r/bud_r)*ss((u-.62)/.38))
    r=np.where(d<bl,rb,stem_r)*np.clip(d/2.5,0,1)
    r=np.maximum(r,0)
    wx=int(bud_r*2+abs(sway)+10);xs=np.arange(-wx*SS,wx*SS)/SS+.5/SS
    X=xs[None,:]+int(cx);dx=(X-cxs[:,None])
    R=r[:,None]+1e-4;q=dx/R;inside=(np.abs(q)<1)&(r[:,None]>.3)
    nz=np.sqrt(np.clip(1-q*q,0,1));nx=q
    Lx,Lz=-.55,.83
    dif=np.clip(nx*Lx+nz*Lz,0,1)
    isbud=(d<bl)[:,None]
    base_stem=np.array([95,200,175],np.float32)  # BGR, light yellow-green
    base_bud=np.array([70,170,120],np.float32)
    col=np.where(isbud[...,None],base_bud,base_stem)
    shade=(.38+.75*dif)[...,None]
    # bud: soft vertical seam and lighter tip
    seam=np.exp(-((q+.15)**2)/.02)*isbud*(u[:,None]>.08)*(u[:,None]<.75)
    tipl=(np.clip(1-u/.35,0,1)[:,None]*isbud)
    c=col*shade*(1-.35*seam[...,None])+np.array([120,230,210])*(.35*tipl)[...,None]
    rim=(1-nz)**3
    c=c+np.array([60,170,255],np.float32)*(.55*rim)[...,None]       # warm rim from the glow
    spec=np.exp(-((q+.45)**2)/.01)*.35
    c=c+255*spec[...,None]
    a=inside.astype(np.float32)
    C=cv2.resize(c*a[...,None],(2*wx,h),interpolation=cv2.INTER_AREA)
    A=cv2.resize(a,(2*wx,h),interpolation=cv2.INTER_AREA)
    C=C/np.maximum(A[...,None],1e-3)
    return C,A,int(cx)-wx,y0

def blit(img,C,A,x0,y0,alpha=1.0,mask=None):
    h,w=A.shape;ya,yb=max(0,y0),min(H,y0+h);xa,xb=max(0,x0),min(W,x0+w)
    if ya>=yb or xa>=xb:return
    a=A[ya-y0:yb-y0,xa-x0:xb-x0]*alpha
    if mask is not None:a=a*mask[ya:yb,xa:xb]
    img[ya:yb,xa:xb]=img[ya:yb,xa:xb]*(1-a[...,None])+C[ya-y0:yb-y0,xa-x0:xb-x0]*a[...,None]

SEEDTOP,SEEDBOT,EMB=134,292,262      # frame-22 px: seed notch, seed bottom, base of the embryo
CX=638
seedmask=np.zeros((H,W),np.float32)   # inside the shell the shoot is seen through it
cv2.ellipse(seedmask,(CX,214),(62,80),0,0,360,1,-1);seedmask=cv2.GaussianBlur(seedmask,(0,0),3)
seedmask[:SEEDTOP-6]=0
D_END=870;PW=-150                      # plate bottom edge in world px; plate fills the screen when D=D_END
spr=np.zeros((H,W),np.float32);spr[Y0:Y1,X0:X1]=np.load('spr_a2.npy')
noise=cv2.GaussianBlur(np.random.default_rng(3).standard_normal((H,W)).astype(np.float32),(0,0),9)*40
edge_wob=np.zeros(W,np.float32);r=np.random.default_rng(7)
for f,a in((3,14),(8,8),(21,5),(53,3)):edge_wob+=a*np.sin(np.arange(W)/W*f*6.283+r.uniform(0,6.28))

for j in range(K):
    t=(j+1)/(K+1)
    # camera: drift with the shoot (A), then tilt up to the surface (B)
    camD=lambda t:lerp(0,140,ss(rng(t,0,.36)))+(D_END-140)*ss(rng(t,.34,.78))
    D=camD(t);blurL=min(abs(camD(t+1/(K+1))-D)*.45,5)         # vertical motion blur ~ the pan between two frames
    Di=int(round(D))
    top=TOP-Di
    img=WORLD[top:top+H].copy() if top>=0 else None
    # the slim shoot, in world px
    g=rng(t,0,.40)
    tipw=lerp(EMB-55,SEEDTOP-150,1-(1-g)**1.6)            # out of the notch and up
    tipw=tipw-260*ss(rng(t,.40,.70))                         # keeps climbing into the soil
    sway=3*np.sin(t*9)
    out=draw_sprout(tipw+D,EMB+D,CX,sway)
    if out:
        C,A,x0,y0=out
        inside=np.roll(seedmask,Di,axis=0) if Di<H else np.zeros_like(seedmask)
        if Di>0 and Di<H: inside[:Di]=0
        vis=1-(1-.55*ss(rng(t,0,.14)))*inside                                     # through the shell it reads softer
        blit(img,C,A,x0,y0,1.0,vis)
    # soil plate sliding in from above, fading into the dark at its crumbly bottom edge
    o=PW-H+D                                                  # plate top on screen
    if o>-H:
        P=np.zeros_like(img);oi=int(round(o))
        PX=np.concatenate([PLATE,PLATE[::-1]],0)           # soil continues past the plate edge (mirrored), the ramp hides the seam
        if oi>=0:P[oi:]=PX[:H-oi]
        else:P[:]=PX[-oi:-oi+H]
        bot=o+H
        pa=ss((bot-yy+edge_wob[None,:]+noise*.6)/150.)
        pa=np.maximum(pa,ss(rng(t,.60,.76)))*(yy>=o)
        img=img*(1-pa[...,None])+P*pa[...,None]
        # the real sprout breaking out of the mound
        hand0=ss(rng(t,.88,1.0))
        e=ss(rng(t,.66,.98))
        sh=(1-e)**1.3*260
        if e>0:
            M=np.float32([[1,0,0],[0,1,o+sh]])
            Cs=cv2.warpAffine(F63,M,(W,H));As=cv2.warpAffine(spr,M,(W,H))
            oi2=int(round(o));clip=1-np.roll(GROUND,oi2,axis=0) if oi2>=0 else 1-np.pad(GROUND[-oi2:],((0,-oi2),(0,0)))            # only what is above the soil line shows
            gd=np.roll(GROUND,oi2,axis=0) if oi2>=0 else np.pad(GROUND[-oi2:],((0,-oi2),(0,0)))
            ao=cv2.GaussianBlur(gd,(0,0),9)          # contact shade where the shoot meets the soil
            Cs=Cs*(1-.55*np.clip(ao*1.6,0,1)*(1-hand0))[...,None]
            a=As*clip*pa
            img=img*(1-a[...,None])+Cs*a[...,None]
    if blurL>1.5:img=cv2.blur(img,(1,int(round(blurL))|1))
    img=img*(1-SPA[...,None])+lerp(SP22,SP63,ss(rng(t,.4,.75)))*SPA[...,None]
    hand=ss(rng(t,.93,1.0))
    if hand>0:img=img*(1-hand)+F63*hand
    cv2.imwrite(f'{OUT}/b{j:03d}.png',np.clip(img,0,255).astype(np.uint8))
print('done',K)
