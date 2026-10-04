"""Put her reference sunflower head (first frame of her clip) on the late bloom frames and the zoom-in,
sized and placed on each frame's own flower, so the flower looks the same before, during and after the pause."""
import cv2,numpy as np
from disc import find_disc
REF=cv2.imread('reff/v001.png');RX,RY,RR=find_disc(REF)
def head_mask(img,x,y,R):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV);h,s,v=[hsv[...,i].astype(int) for i in range(3)]
    H,W=img.shape[:2];yy,xx=np.mgrid[0:H,0:W];rr=np.hypot(xx-x,yy-y)/R
    yel=((h>=14)&(h<=38)&(s>90)&(v>110)).astype(np.uint8)
    m=((yel==1)|(rr<1.0)).astype(np.uint8)&(rr<2.4).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,l,st,c=cv2.connectedComponentsWithStats(m);k=l[int(min(H-1,max(0,y))),int(min(W-1,max(0,x)))]
    if k==0:k=1+np.argmax(st[1:,4])
    m=(l==k).astype(np.uint8);ff=m.copy();cv2.floodFill(ff,np.zeros((H+2,W+2),np.uint8),(0,0),1);m=m|(1-ff)
    return m
REFM=head_mask(REF,RX,RY,RR)
def place(img,x,y,R,amt=1.0,keep_old=None):
    H,W=img.shape[:2];s=R/RR
    M=np.float32([[s,0,x-s*RX],[0,s,y-s*RY]])
    flag=cv2.INTER_LANCZOS4 if s>1 else cv2.INTER_AREA
    hd=cv2.warpAffine(REF,M,(W,H),flags=flag,borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    if s>1.25:                                                   # enlarged: give back a little crispness
        bl=cv2.GaussianBlur(hd,(0,0),1.2*s/2);hd=np.clip(hd+(hd-bl)*.6,0,255)
    hm=cv2.warpAffine(REFM.astype(np.float32),M,(W,H),flags=cv2.INTER_LINEAR)
    a=cv2.GaussianBlur(cv2.erode((hm>.5).astype(np.uint8),np.ones((3,3),np.uint8)).astype(np.float32),(0,0),max(.8,s*.7))
    # the old head's petals that stick out past the new one: fill with the background
    old=keep_old if keep_old is not None else head_mask(img,x,y,R)
    left=(old&(1-cv2.dilate((hm>.5).astype(np.uint8),np.ones((3,3),np.uint8)))).astype(np.uint8)
    left=cv2.dilate(left,np.ones((7,7),np.uint8))*(1-cv2.erode((hm>.5).astype(np.uint8),np.ones((9,9),np.uint8)))
    base=cv2.inpaint(img,(left*255).astype(np.uint8),6,cv2.INPAINT_TELEA).astype(np.float32) if left.any() else img.astype(np.float32)
    base=img.astype(np.float32)*(1-amt)+base*amt
    a=(a*amt)[...,None]
    return np.clip(base*(1-a)+hd*a,0,255).astype(np.uint8)

def push_in(x,y,R,W=1280,H=720):
    """The zoom-in as a camera push into her reference frame: the whole frame, scaled so its flower matches (x,y,R)."""
    s=R/RR;M=np.float32([[s,0,x-s*RX],[0,s,y-s*RY]])
    im=cv2.warpAffine(REF,M,(W,H),flags=cv2.INTER_LANCZOS4 if s>1 else cv2.INTER_AREA,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    if s>1.25:
        bl=cv2.GaussianBlur(im,(0,0),1.2*s/2);im=im+(im-bl)*.6
    return np.clip(im,0,255).astype(np.uint8)
