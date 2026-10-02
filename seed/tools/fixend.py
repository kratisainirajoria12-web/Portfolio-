import cv2,numpy as np,sys
U=open('vf_unique.txt').read().split('\n')[228:]
N=len(U); K0=N-60
G0=cv2.imread('/home/claude/krati/grow/f000.webp')
def seedmask(im):
    g=cv2.GaussianBlur(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),(0,0),5).astype(float)
    sub=np.zeros_like(g);sub[120:620,300:980]=g[120:620,300:980]
    thr=max(70,np.percentile(g,92))
    m=(sub>thr).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]);c,_=cv2.findContours((lab==k).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    return cv2.fitEllipse(max(c,key=cv2.contourArea))
def emask(e,grow=1.08,feather=14):
    m=np.zeros((720,1280),np.float32);(x,y),(a,b),ang=e
    cv2.ellipse(m,((x,y),(a*grow,b*grow),ang),1,-1)
    return cv2.GaussianBlur(m,(0,0),feather)
eg=seedmask(G0);mg=emask(eg)
lab0=cv2.cvtColor(G0,cv2.COLOR_BGR2LAB).astype(np.float32)
def stats(L,w):
    w=w[...,None];s=w.sum();mu=(L*w).sum((0,1))/s;sd=np.sqrt(((L-mu)**2*w).sum((0,1))/s)+1e-3;return mu,sd
S_seed=stats(lab0,mg);S_bg=stats(lab0,1-cv2.GaussianBlur((mg>0.02).astype(np.float32),(0,0),20))
eL=seedmask(cv2.imread(U[-1]))
(c1x,c1y),(a1,b1),ang1=eL;(c0x,c0y),(a0,b0),ang0=eg
ss=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
def process(k):
    im=cv2.imread(U[k]);t=ss((k-K0)/(N-1-K0)) if k>=K0 else 0
    if t<=0: return im
    # geometric: about the seed, grow it longer and slimmer and tilt it like the roots clip's seed
    th=np.radians((ang0-ang1))*t; sx=1+(b0/b1*.92-1)*t; sy=1+(a0/a1-1)*t*.75
    cx,cy=c1x,c1y; tx,ty=c1x+(c0x-c1x)*t, c1y+(c0y-c1y)*t
    # seed major axis is ~horizontal: scale x by sx, y by sy, then rotate
    R=np.array([[np.cos(th),-np.sin(th)],[np.sin(th),np.cos(th)]]);Sm=np.diag([sx,sy]);A=R@Sm
    M=np.hstack([A,(np.array([tx,ty])-A@np.array([cx,cy]))[:,None]])
    w=cv2.warpAffine(im,M,(1280,720),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    e=seedmask(w);m=emask(e)
    L=cv2.cvtColor(w,cv2.COLOR_BGR2LAB).astype(np.float32)
    ms,ss_=stats(L,m);mb,sb=stats(L,1-m)
    Ls=(L-ms)/ss_*S_seed[1]+S_seed[0]
    seed=cv2.cvtColor(np.clip(Ls,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
    # background: lift the warm haze off (a very soft blur of the frame) so only the sparks stay, on near-black like the roots clip
    wf=w.astype(np.float32);haze=cv2.GaussianBlur(wf,(0,0),45)
    bg=np.clip(wf-haze*.92,0,255)*1.25+np.array([3,4,6],np.float32)
    mm=m[...,None];out=seed*mm+bg*(1-mm)
    return (w.astype(np.float32)*(1-t)+out*t).clip(0,255).astype(np.uint8)
if __name__=='__main__':
    ims=[cv2.resize(process(k),(320,180)) for k in (K0,K0+20,K0+40,N-10,N-1)]+[cv2.resize(G0,(320,180))]
    cv2.imwrite('fixend.png',np.vstack([np.hstack(ims[:3]),np.hstack(ims[3:])]))
