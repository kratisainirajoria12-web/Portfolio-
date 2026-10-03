import cv2,numpy as np
b='zip/krati-project/bloom'
S=cv2.imread(f'{b}/f063.webp')
X0,Y0,X1,Y1=570,95,700,470
crop=S[Y0:Y1,X0:X1]
hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
h,s,v=[hsv[...,i].astype(int) for i in range(3)]
B,G,R=[crop[...,i].astype(int) for i in range(3)]
m=((h>24)&(h<70)&(s>45)&(v>35)&(G>R-5)).astype(np.uint8)
n,l,st,c=cv2.connectedComponentsWithStats(m);k=1+np.argmax(st[1:,4]);m=(l==k).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
# fill holes
ff=m.copy();cv2.floodFill(ff,np.zeros((m.shape[0]+2,m.shape[1]+2),np.uint8),(0,0),1);m=m|(1-ff)
ys=np.nonzero(m)[0];print('rows',ys.min()+Y0,ys.max()+Y0)
for y in range(0,m.shape[0],15):
    xs=np.nonzero(m[y])[0];print(y+Y0,(xs.min()+X0,xs.max()+X0) if len(xs) else '-')
a=cv2.GaussianBlur(cv2.erode(m,np.ones((2,2),np.uint8)).astype(np.float32),(0,0),.8)
np.save('spr_a.npy',a);cv2.imwrite('spr_c.png',crop)
vis=(crop*a[...,None]).astype(np.uint8);cv2.imwrite('spr_vis.png',cv2.resize(vis,None,fx=2,fy=2))
