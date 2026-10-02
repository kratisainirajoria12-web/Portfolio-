import cv2,numpy as np,os,sys
sys.path.insert(0,'.')
from brown2 import brown_E,D
OUT='/home/claude/krati/hold/'
for f in os.listdir(OUT): os.remove(OUT+f)
base=brown_E(440,cv2.imread('vE/f440.png')).astype(np.float32)
H,W=base.shape[:2]
pm=np.load('plantmask.npy').astype(np.uint8)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
sm=lambda e:np.clip(e,0,1)**2*(3-2*np.clip(e,0,1))
x0,y0,R=D[440]
bg=cv2.inpaint(base.astype(np.uint8),cv2.dilate(pm,np.ones((25,25),np.uint8))*255,11,cv2.INPAINT_TELEA).astype(np.float32)
pa=cv2.GaussianBlur(pm.astype(np.float32),(0,0),2.5)
def noise(scale,seed):
    r=np.random.default_rng(seed).random((H//scale+3,W//scale+3)).astype(np.float32)
    return cv2.resize(cv2.GaussianBlur(r,(0,0),1.2),(W,H),interpolation=cv2.INTER_CUBIC)
n1=noise(60,1)*6.28; n2=noise(18,2)*6.28; n3=noise(30,3)*6.28; n4=noise(9,4)*6.28
hsv=cv2.cvtColor(base.astype(np.uint8),cv2.COLOR_BGR2HSV).astype(np.float32)
sky=sm((hsv[...,2]-185)/30)*sm((60-hsv[...,1])/40)
wg=sm((yy-300)/260)**1.2
wt=(1-sm((yy-330)/90))*(1-sky)
wm=1-sm((np.hypot(xx-1160,yy-600)-55)/30); wg*=wm
rr=np.hypot(xx-x0,yy-y0)/R; ang=np.arctan2(yy-y0,xx-x0)
petal=sm((rr-.95)/.15)*(1-sm((rr-2.1)/.3))           # the ray petals around the disc
leaf=sm((yy-(y0+R*1.9))/40)                          # leaves and stem below the head
PX,PY=x0+15,H+260                                    # the plant's pivot, well below the frame
N=96
for k in range(N):
    t=k/N; tw=2*np.pi*t
    # sunflower: a slow pendulum of a few pixels, the head trailing the stem a touch; petals and leaves answer softly
    th=.0042*np.sin(tw)+.0012*np.sin(2*tw+.7)
    pdx=-(yy-PY)*th; pdy=(xx-PX)*th
    pdx+=petal*(.55*np.sin(2*tw+ang*3+n2*.3)); pdy+=petal*(.45*np.cos(2*tw+ang*5))
    pdx+=leaf*(1.6*np.sin(tw-xx/300+.8)+.6*np.sin(3*tw+n3)); pdy+=leaf*(.8*np.sin(2*tw+xx/200+n2))
    # meadow: a gust rolling left to right, every patch with its own timing
    gust=.55+.45*np.sin(tw-xx/1100*2*np.pi+n1*.35)
    sway=np.sin(tw-xx/520*2*np.pi+n1)*.7+np.sin(2*tw+n3)*.3
    gdx=wg*(3.6*gust*sway+.8*np.sin(3*tw+n4)); gdy=wg*(.8*np.abs(sway)*gust)
    # distant canopy: barely breathing
    lift=sm((330-yy)/250)
    gdx+=wt*(.9*np.sin(tw-xx/800*2*np.pi+n1*.5)*(.5+.5*lift)+.35*np.sin(2*tw+n2)); gdy+=wt*.3*np.sin(tw+n3)
    f32=lambda a:a.astype(np.float32)
    mb=cv2.remap(bg,f32(xx-gdx),f32(yy-gdy),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    mp=cv2.remap(base,f32(xx-pdx),f32(yy-pdy),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    ma=cv2.remap(pa,f32(xx-pdx),f32(yy-pdy),cv2.INTER_LINEAR)[...,None]
    out=mb*(1-ma)+mp*ma
    cv2.imwrite(OUT+'f%03d.webp'%k,out.clip(0,255).astype(np.uint8),[cv2.IMWRITE_WEBP_QUALITY,82])
a=cv2.imread(OUT+'f000.webp').astype(float);b=cv2.imread(OUT+'f024.webp').astype(float)
print('mean diff',np.abs(a-b).mean(),'vs base',np.abs(a-base).mean())
d=np.abs(a-b).sum(2);cv2.imwrite('hd.png',cv2.resize(np.clip(d*5,0,255).astype(np.uint8),(640,360)))
