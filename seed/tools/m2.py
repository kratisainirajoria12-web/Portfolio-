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
for i in range(N):
    t=(i+1)/(N+1)
    U=E(262+round(13*t)); S=E(300+round(14*t))
    C=TRAVEL*ss(t)                       # camera rise, in frame heights
    off=C-TRAVEL                          # S frame screen offset (S-world y -> screen y = y+off)
    # sample S at y-off, U at y-C
    Sy=(yy-off*H); Uy=(yy-C*H)
    Sw=cv2.remap(S,xx,Sy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    Uw=cv2.remap(U,xx,Uy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    # depth below the soil line in S-world
    depth=(Sy/H-(SOIL+wob[None,:]))
    ws=1-ss(depth/.24)
    dark=1-.55*ss(depth/.18)
    fin=ss((t-.62)/.38)
    ws=ws+(1-ws)*fin; dark=dark+(1-dark)*fin
    out=Sw*(dark*ws)[...,None]+Uw*(1-ws)[...,None]
    # also the U plate fades toward soil colour just under the surface (cross-section)
    # stem pushing up from the seed to the surface
    g=ss(t/.32)
    yb=(SEEDTOP+TRAVEL)+0.0; yt=lerp(yb,SOIL-.01,g)       # S-world
    if g>0.01:
        col,al=stem_layer((yb+off)*H+18,(yt+off)*H,.50*W,.496*W)
        vis=np.clip(1-.35*ss(depth/.3),0,1)               # deeper = slightly dimmer
        al=al*.92*(1-fin)
        out=out*(1-al[...,None])+col*(al*vis)[...,None]+out*0
    cv2.imwrite('/home/claude/krati/m2/f%03d.webp'%i,out.clip(0,255).astype(np.uint8),[cv2.IMWRITE_WEBP_QUALITY,80])
print('ok')
