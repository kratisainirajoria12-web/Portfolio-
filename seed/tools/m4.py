import cv2, numpy as np
W,H=1280,720; N=40
E=lambda i:cv2.imread('vE/f%03d.png'%i).astype(np.float32)
ss=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
TRAVEL=.60; SOIL=.56; SEEDTOP=.215
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
rng=np.random.default_rng(5)
# crumbly soil line: low-frequency wobble across x
wob=np.zeros(W,np.float32)
for f,a in ((3,.012),(7,.007),(19,.004),(41,.002)): wob+=a*np.sin(np.arange(W)/W*f*6.283+rng.uniform(0,6.28))
def stem_layer(y0,y1,x0,x1):
    """tapered, softly lit stem from (x0,y0) bottom to (x1,y1) top, in screen px. returns color,alpha"""
    S=3; c=np.zeros((H*S//2,W*S//2,3),np.float32); a=np.zeros((H*S//2,W*S//2),np.float32)
    k=S/2; n=60
    pts=[]
    for i in range(n+1):
        t=i/n; x=x0+(x1-x0)*t+6*np.sin(t*3.1); y=y0+(y1-y0)*t; pts.append((x,y,lerp(15,13,t)))
    for i in range(n):
        (xa,ya,ra),(xb,yb,rb)=pts[i],pts[i+1]
        for j,(sh,col) in enumerate(((1.0,(28,72,66)),(.62,(62,140,128)),(.25,(120,205,190)))):
            cv2.line(c,(int(xa*k),int(ya*k)),(int(xb*k),int(yb*k)),col,max(1,int(ra*2*sh*k)),cv2.LINE_AA)
        cv2.line(a,(int(xa*k),int(ya*k)),(int(xb*k),int(yb*k)),1.0,max(1,int(ra*2*k)),cv2.LINE_AA)
    c=cv2.resize(c,(W,H),interpolation=cv2.INTER_AREA); a=cv2.resize(a,(W,H),interpolation=cv2.INTER_AREA)
    c=cv2.GaussianBlur(c,(0,0),1.2); a=cv2.GaussianBlur(a,(0,0),1.2)
    return c,a
def lerp(a,b,t): return a+(b-a)*t

SEEDY=(SEEDTOP+TRAVEL)*H+6          # top of the seed, S-world px
def sprout(S):
    hsv=cv2.cvtColor(S.clip(0,255).astype(np.uint8),cv2.COLOR_BGR2HSV)
    g=((hsv[...,0]>26)&(hsv[...,0]<52)&(hsv[...,1]>70)&(hsv[...,2]>45)).astype(np.uint8)
    g[:,:560]=0;g[:,720:]=0;g[:80]=0
    n,l,st,c=cv2.connectedComponentsWithStats(g);k=1+np.argmax(st[1:,4]);m=(l==k).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8));m=cv2.dilate(m,np.ones((3,3),np.uint8))
    ys=np.nonzero(m)[0];top,bot=ys.min(),ys.max()
    a=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.2)
    # stem texture strip from just above where it enters the soil
    r0=bot-34;strip=S[r0:bot-6].copy();sa=a[r0:bot-6].copy()
    return a,top,bot,strip,sa
def inpaint(S,a):
    m=(cv2.dilate((a>.05).astype(np.uint8),np.ones((9,9),np.uint8))*255)
    return cv2.inpaint(S.clip(0,255).astype(np.uint8),m,7,cv2.INPAINT_TELEA).astype(np.float32)
for i in range(N):
    t=(i+1)/(N+1)
    U=E(262+round(13*t)); S=E(300+round(14*t))
    a,top,bot,strip,sa=sprout(S)
    # the real sprout, stretched down to the seed: bud+stem from S, then its own stem texture repeated to the seed
    g=ss(t/.62)
    dy=(1-g)*(SEEDY-30-top)                     # bud tip starts just above the seed top
    SP=np.zeros_like(S);SA=np.zeros(S.shape[:2],np.float32)
    M=np.float32([[1,0,0],[0,1,dy]])
    SP=cv2.warpAffine(S*a[...,None],M,(W,H));SA=cv2.warpAffine(a,M,(W,H))
    yb=int(bot-6+dy)
    hs=strip.shape[0]
    for y in range(max(0,yb),min(H,int(SEEDY)+4)):
        r=(y-yb)%hs;SP[y]=strip[r]*sa[r][:,None];SA[y]=sa[r]
    hide=np.clip((SEEDY+4-yy)/8,0,1)            # still inside the seed coat below its top
    SA=SA*hide;SP=SP*hide[...,None]
    Sbase=inpaint(S,a)
    C=TRAVEL*ss(t); off=C-TRAVEL
    Sy=(yy-off*H); Uy=(yy-C*H)
    Sw=cv2.remap(Sbase,xx,Sy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    Pw=cv2.remap(SP,xx,Sy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    Aw=cv2.remap(SA,xx,Sy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    Uw=cv2.remap(U,xx,Uy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    depth=(Sy/H-(SOIL+wob[None,:]))
    ws=1-ss(depth/.24); dark=1-.55*ss(depth/.18)
    fin=ss((t-.62)/.38)
    ws=ws+(1-ws)*fin; dark=dark+(1-dark)*fin
    out=Sw*(dark*ws)[...,None]+Uw*(1-ws)[...,None]
    vis=np.clip(1-.3*ss(depth/.3),0,1)
    out=out*(1-Aw[...,None])+Pw*vis[...,None]
    # the cross-section closes: settle into the real frame (sprout already in its real place)
    Sreal=cv2.remap(S,xx,Sy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    out=out*(1-fin)+Sreal*fin
    cv2.imwrite('/home/claude/krati/m2/f%03d.webp'%i,out.clip(0,255).astype(np.uint8),[cv2.IMWRITE_WEBP_QUALITY,80])
print('ok')
