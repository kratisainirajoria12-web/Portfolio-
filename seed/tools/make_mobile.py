"""Sharper frames for phones. A portrait phone only ever sees the middle of each 1280x720 frame, stretched up to 3x.
This takes that middle (x 250..950 of the frame), upscales it 2x with Real-ESRGAN (realesr-animevideov3, CPU via
ncnn) and stores it at 1050x1080 in sheets of four, under m/<sequence>/s###.webp. The page draws it back in place."""
import cv2,numpy as np,os,sys,glob,time
sys.path.insert(0,os.path.dirname(__file__));from sr import SR
X0,X1,OW,OH=250,950,1050,1080
sr=SR('realesr-animevideov3-x2',2)
def frames(d):
    fs=sorted(glob.glob(f'{d}/*.webp'))
    if d=='catch':fs=fs[:109]
    for p in fs:
        im=cv2.imread(p)
        for r in range(im.shape[0]//720):yield im[r*720:(r+1)*720]
seqs=sys.argv[1:] or ['catch','dive','grow','bloom','hold','zoom']
for d in seqs:
    os.makedirs(f'm/{d}',exist_ok=True);buf=[];s=0;t0=time.time();n=0
    for f in frames(d):
        up=sr.run(np.ascontiguousarray(f[:,X0:X1]));buf.append(cv2.resize(up,(OW,OH),interpolation=cv2.INTER_AREA));n+=1
        if len(buf)==4:cv2.imwrite(f'm/{d}/s{s:03d}.webp',np.vstack(buf),[cv2.IMWRITE_WEBP_QUALITY,78]);buf=[];s+=1
    if buf:
        while len(buf)<4:buf.append(np.zeros_like(buf[0]))
        cv2.imwrite(f'm/{d}/s{s:03d}.webp',np.vstack(buf),[cv2.IMWRITE_WEBP_QUALITY,78])
    print(d,n,'frames',round(time.time()-t0),'s',flush=True)
