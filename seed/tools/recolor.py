"""Sunflower disc -> the dark brown of the reference video (ring-wise quantile colour transfer).
The reference video starts on the same framing as the last bloom frame, so its first frame is the palette."""
import cv2,numpy as np
from disc import find_disc
RINGS=[0,.35,.7,.92]
def ring_w(rr):
    c=[(RINGS[i]+RINGS[i+1])/2 for i in range(3)]
    w=np.stack([np.exp(-((rr-ci)/.18)**2) for ci in c],-1);return w/w.sum(-1,keepdims=True)
def lum(img):return cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
def build_lut(ref,x,y,R):
    H,W=ref.shape[:2];yy,xx=np.mgrid[0:H,0:W];rr=np.hypot(xx-x,yy-y)/R;L=lum(ref)
    luts=[]
    for i in range(3):
        m=(rr>=RINGS[i])&(rr<RINGS[i+1]);l=L[m];c=ref[m].astype(np.float32);o=np.argsort(l)
        q=np.linspace(0,1,64);idx=(q*(len(o)-1)).astype(int)
        # mean colour of a small window around each quantile
        cs=np.cumsum(np.concatenate([np.zeros((1,3)),c[o]],0),0);w=max(3,len(o)//128)
        lo=np.clip(idx-w,0,len(o));hi=np.clip(idx+w,0,len(o));luts.append((cs[hi]-cs[lo])/(hi-lo)[:,None])
    return luts
def petals(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(np.float32)
    p=np.clip((hsv[...,2]-150)/30,0,1)*np.clip((hsv[...,1]-110)/40,0,1)*((hsv[...,0]>=19)&(hsv[...,0]<=36))
    return cv2.GaussianBlur(p.astype(np.float32),(0,0),1.2)
def recolor(img,luts,x,y,R,amt=1.0):
    H,W=img.shape[:2]
    x0,x1=int(max(0,x-R-4)),int(min(W,x+R+5));y0,y1=int(max(0,y-R-4)),int(min(H,y+R+5))
    if x1<=x0 or y1<=y0:return img
    sub=img[y0:y1,x0:x1];yy,xx=np.mgrid[y0:y1,x0:x1];rr=np.hypot(xx-x,yy-y)/R
    L=lum(sub);out=np.zeros(sub.shape,np.float32);wr=ring_w(rr)
    for i in range(3):
        m=(rr>=RINGS[i]-.1)&(rr<RINGS[i+1]+.1)
        if m.sum()<20:
            col=np.zeros_like(out)
        else:
            # rank of each pixel's luminance inside its ring (local quantile)
            l=L[m];srt=np.sort(l);q=np.searchsorted(srt,L)/max(1,len(srt)-1)
            qi=np.clip(q*63,0,63);a=np.floor(qi).astype(int);b=np.minimum(a+1,63);f=(qi-a)[...,None]
            col=luts[i][a]*(1-f)+luts[i][b]*f
        out+=col*wr[...,i:i+1]
    f=np.clip((1-rr)*R/max(4,R*.06),0,1);f=f*f*(3-2*f)
    pet=petals(sub);f=f*(1-pet*np.clip((rr-.8)/.1,0,1))
    a=(f*amt)[...,None]
    res=img.copy();res[y0:y1,x0:x1]=np.clip(sub*(1-a)+out*a,0,255).astype(np.uint8);return res
REF=cv2.imread('reff/v001.png');RX,RY,RR=find_disc(REF);LUTS=build_lut(REF,RX,RY,RR*.97)
