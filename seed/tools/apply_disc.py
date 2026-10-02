import cv2,numpy as np,json
from recolor import *
from head import place,push_in
O='zip/krati-project/'; R='/home/user/Portfolio-/seed/'
# late bloom: repo files 240..279 = original files 120..159
idx=list(range(240,280));det=[]
for i in idx:det.append(find_disc(cv2.imread(O+'bloom/f%03d.webp'%(i-120))))
P=np.array(det,float)
for c in range(3):                                   # steady the circle from frame to frame
    v=P[:,c].copy()
    for k in range(len(v)):v[k]=np.median(P[max(0,k-2):k+3,c])
    P[:,c]=v
for k,i in enumerate(idx):
    im=cv2.imread(O+'bloom/f%03d.webp'%(i-120));x,y,r=P[k]
    amt=float(np.clip((i-239)/7,0,1))
    im=recolor(im,LUTS,x,y,r*.97,amt)
    im=petal_fix(im,x,y,r,amt=float(np.clip((i-245)/6,0,1)))      # petal bases back to yellow
    if i>=248:im=place(im,x,y,r,amt=float(np.clip((i-248)/6,0,1)))   # her reference flower from here on
    cv2.imwrite(R+'bloom/f%03d.webp'%i,im,[cv2.IMWRITE_WEBP_QUALITY,88])
# zoom: disc from the saved track (zoom i ~ E442..479)
D={int(k):v for k,v in json.load(open(O+'tools/disk_ref.json')).items()}
for i in range(22):
    e=442+i*37/21;a=int(np.floor(e));b=min(a+1,479);f=e-a
    x,y,r=[D[a][j]*(1-f)+D[b][j]*f for j in range(3)]
    im=cv2.imread(O+'zoom/f%03d.webp'%i)
    d=find_disc(im)
    if d and abs(d[2]-r)<.15*r and abs(d[0]-x)<.1*r and abs(d[1]-y)<.1*r:x,y,r=d          # measured when the whole disc is in view
    # close-ups keep their own petal bases (the fix stretches petals too far once the flower fills the frame)
    im=petal_fix(recolor(im,LUTS,x,y,r*.97),x,y,r,amt=float(np.clip((11-i)/5,0,1)))
    im=push_in(x,y,r)                                               # a push into her reference frame
    cv2.imwrite(R+'zoom/f%03d.webp'%i,im,[cv2.IMWRITE_WEBP_QUALITY,88])
print('ok')
