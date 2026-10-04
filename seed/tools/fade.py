import cv2,numpy as np,sys
from fixend import seedmask,emask
U=open('vf_unique.txt').read().split('\n')[228:]
KC=150; NB=44; SIGN=float(sys.argv[1]) if len(sys.argv)>1 else 1
A=cv2.imread(U[KC]).astype(np.float32);G0=cv2.imread('/home/claude/krati/grow/f000.webp').astype(np.float32)
eA=seedmask(A.astype(np.uint8));eG=seedmask(G0.astype(np.uint8))
mA=emask(eA,grow=1.0,feather=4)
(ax,ay),_,aa=eA;(gx,gy),_,ga=eG;LA=max(eA[1]);LG=max(eG[1])
ss=lambda x:float(np.clip(x,0,1))**2*(3-2*float(np.clip(x,0,1)))
yy,xx=np.mgrid[0:720,0:1280].astype(np.float32)
def frame(t):
    # camera keeps creeping in on the seed the whole time
    z=1+.12*t
    Mz=cv2.getRotationMatrix2D((ax,ay),0,z)
    base=cv2.warpAffine(A,Mz,(1280,720),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    mb=cv2.warpAffine(mA,Mz,(1280,720))
    # soil sinks into black from the edges inward
    f=ss(t/.5);r=np.hypot((xx-ax)/1280*1.78,(yy-ay)/720)
    keep=np.clip(1-(r-(1-f)*1.1)/.25,0,1)*(1-f)
    soil=base*keep[...,None]
    seedA=base*mb[...,None]
    # seed alone on black turns, grows and slides into the roots seed's pose
    m=ss((t-.25)/.55)
    WA=min(eA[1]);WG=min(eG[1])
    sl=1+(LG/LA-1)*m; sw=1+(WG/WA-1)*m
    cx,cy=ax+(gx-ax)*m,ay+(gy-ay)*m
    # in the seed's own axes (major axis along u at image angle aa, clockwise from vertical): stretch, then turn to the target angle
    def axis(deg):
        r=np.radians(deg);return np.array([np.sin(r),-np.cos(r)]),np.array([np.cos(r),np.sin(r)])
    u0,v0=axis(aa);u1,v1=axis(aa+(ga-aa)*m)
    B0=np.stack([u0,v0],1);B1=np.stack([u1,v1],1)
    L=B1@np.diag([sl,sw])@B0.T
    M=np.hstack([L,(np.array([cx,cy])-L@np.array([ax,ay]))[:,None]]).astype(np.float32)
    sd=cv2.warpAffine(seedA,M,(1280,720),flags=cv2.INTER_CUBIC);md=cv2.warpAffine(mb,M,(1280,720))[...,None]
    out=soil*(1-md)+sd
    # roots frame rises out of the black
    c=ss((t-.8)/.2)
    return (out*(1-c)+G0*c).clip(0,255).astype(np.uint8)
if __name__=='__main__':
    ims=[cv2.resize(frame(t),(320,180)) for t in (0,.2,.4,.55,.7,.85,.95,1)]
    cv2.imwrite('fade.png',np.vstack([np.hstack(ims[:4]),np.hstack(ims[4:])]))
