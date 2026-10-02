import cv2,numpy as np,json
D={int(k):v for k,v in json.load(open('/tmp/claude-0/-home-claude/fdbbf83a-c534-505d-82e9-c0654f5003ec/scratchpad/disk_ref.json')).items()}
def recolor_circle(img,x,y,R,amt=1.0):
    H,W=img.shape[:2]
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    rr=np.hypot(xx-x,yy-y)/R
    f=np.clip((1.0-rr)*R/10.0,0,1); f=f*f*(3-2*f)            # ~10px soft edge just inside the petal line
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(np.float32)
    pet=np.clip((hsv[...,2]-150)/30,0,1)*np.clip((hsv[...,1]-100)/40,0,1)*((hsv[...,0]>=19)&(hsv[...,0]<=36))
    pet=cv2.GaussianBlur(pet.astype(np.float32),(0,0),1.5)
    f=f*(1-pet*np.clip((rr-.84)/.08,0,1))                     # petal bases overlapping the disk stay yellow
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)/255.
    s=max(1.5,R*.012)
    gl=cv2.GaussianBlur(g,(0,0),s*3); tex=np.clip(.5+(g-gl)*2.6,0,1)
    t=tex[...,None]
    dark=np.array([10,17,30],np.float32); mid=np.array([20,40,78],np.float32); hi=np.array([38,88,150],np.float32)
    col=np.where(t<.5,dark+(mid-dark)*(t/.5),mid+(hi-mid)*((t-.5)/.5))
    # outer ring keeps golden pollen-tipped florets; the heart is deep brown with an olive cast
    ring=np.clip((rr-.72)/.22,0,1)[...,None]
    heart=np.clip((.35-rr)/.35,0,1)[...,None]
    gold=img.astype(np.float32)*np.array([.55,.75,.9],np.float32)
    col=col*(1-.25*heart)+np.array([3,9,6],np.float32)*heart
    col=col*(1-.55*ring*t)+gold*(.55*ring*t)
    col=col*np.clip((g/(gl+1e-3))**.6,.6,1.5)[...,None]
    a=(f*amt)[...,None]
    return (img.astype(np.float32)*(1-a)+col*a).clip(0,255).astype(np.uint8)
def brown_E(i,img):
    if i<398: return img
    amt=np.clip((i-398)/12,0,1)
    x,y,R=D[min(max(i,400),479)]
    return recolor_circle(img,x,y,R,amt)
if __name__=='__main__':
    ims=[]
    for i in (402,415,430,446,460,470,475,479):
        ims.append(cv2.resize(brown_E(i,cv2.imread('vE/f%03d.png'%i)),(480,270)))
    cv2.imwrite('brown_test.png',np.vstack([np.hstack(ims[:4]),np.hstack(ims[4:])]))
