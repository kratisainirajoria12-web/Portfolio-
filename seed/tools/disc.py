import cv2,numpy as np
def find_disc(img,hint=None):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV);h,s,v=[hsv[...,i].astype(int) for i in range(3)]
    yel=((h>=18)&(h<=36)&(s>120)&(v>140)).astype(np.uint8)
    yel=cv2.morphologyEx(yel,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,l,st,c=cv2.connectedComponentsWithStats(yel)
    if n<2:return None
    k=1+np.argmax(st[1:,4]);fl=(l==k).astype(np.uint8)
    if st[k,4]<400:return None
    cnts,_=cv2.findContours(fl,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    hull=np.zeros_like(fl);cv2.fillPoly(hull,[cv2.convexHull(max(cnts,key=cv2.contourArea))],1)
    d=(hull&(1-fl)&((v<150)|(h<18)).astype(np.uint8))
    d=cv2.morphologyEx(d,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    d=cv2.morphologyEx(d,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    n,l,st,c=cv2.connectedComponentsWithStats(d)
    if n<2:return None
    k=1+np.argmax(st[1:,4]);x,y,w,hh,a=st[k]
    return float(x+w/2),float(y+hh/2),float((w+hh)/4)

if __name__=='__main__':
    import sys
    B='/home/user/Portfolio-/seed/'
    for dr,i in [('bloom',240),('bloom',245),('bloom',250),('bloom',260),('bloom',279),('zoom',0),('zoom',10),('zoom',21)]:
        print(dr,i,find_disc(cv2.imread(f'{B}{dr}/f{i:03d}.webp')))
    r=cv2.imread('refF.png');print('ref',find_disc(r))
