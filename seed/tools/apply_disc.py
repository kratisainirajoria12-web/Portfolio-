import cv2,numpy as np,json
from recolor import *
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
    cv2.imwrite(R+'bloom/f%03d.webp'%i,recolor(im,LUTS,x,y,r*.97,amt),[cv2.IMWRITE_WEBP_QUALITY,88])
# zoom: disc from the saved track (zoom i ~ E442..479)
D={int(k):v for k,v in json.load(open(O+'tools/disk_ref.json')).items()}
for i in range(22):
    e=442+i*37/21;a=int(np.floor(e));b=min(a+1,479);f=e-a
    x,y,r=[D[a][j]*(1-f)+D[b][j]*f for j in range(3)]
    im=cv2.imread(O+'zoom/f%03d.webp'%i)
    cv2.imwrite(R+'zoom/f%03d.webp'%i,recolor(im,LUTS,x,y,r*.97),[cv2.IMWRITE_WEBP_QUALITY,88])
print('ok')
