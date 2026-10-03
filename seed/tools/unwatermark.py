"""Remove the corner sparkle watermark from every story frame (same screen spot in all of them). Frames/sheet rows
without the mark are left untouched."""
import cv2,numpy as np,glob,sys
M=cv2.imread(sys.argv[1],0)                     # dilated glyph mask, 1280x720
core=cv2.erode(M,np.ones((7,7),np.uint8))>0
ring=(cv2.dilate(M,np.ones((15,15),np.uint8))>0)&~(M>0)
def has_mark(f):
    g=f.mean(2);return g[core].mean()-g[ring].mean()>6
def clean(f):
    f=f.copy();y0,y1,x0,x1=540,660,1100,1220
    sub=f[y0:y1,x0:x1];m=M[y0:y1,x0:x1]
    out=cv2.inpaint(sub,m,7,cv2.INPAINT_TELEA)
    bl=cv2.GaussianBlur(out,(0,0),2.2);mm=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),2)[...,None]
    f[y0:y1,x0:x1]=(out*(1-mm)+bl*mm).astype(np.uint8);return f
tot=fixed=0
for d in ('catch','dive','grow','bloom','hold','zoom'):
    for p in sorted(glob.glob(d+'/*.webp')):
        im=cv2.imread(p);rows=im.shape[0]//720;ch=False
        for r in range(rows):
            fr=im[r*720:(r+1)*720];tot+=1
            if has_mark(fr):im[r*720:(r+1)*720]=clean(fr);ch=True;fixed+=1
        if ch:cv2.imwrite(p,im,[cv2.IMWRITE_WEBP_QUALITY,86])
print('frames',tot,'cleaned',fixed)
