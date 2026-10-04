import ncnn,numpy as np,cv2,time,sys
M='/usr/local/lib/python3.11/dist-packages/realesrgan_ncnn_py/models/'
class SR:
    def __init__(self,name,scale,threads=4):
        self.net=ncnn.Net();self.net.opt.use_vulkan_compute=False;self.net.opt.num_threads=threads
        self.net.load_param(M+name+'.param');self.net.load_model(M+name+'.bin');self.s=scale
        p=open(M+name+'.param').read().split('\n');self.inp='data';self.out='output'
    def run(self,bgr,tile=256,pad=10):
        h,w=bgr.shape[:2];s=self.s;out=np.zeros((h*s,w*s,3),np.float32)
        rgb=bgr[...,::-1].astype(np.float32)/255.
        for y in range(0,h,tile):
            for x in range(0,w,tile):
                y0,x0=max(0,y-pad),max(0,x-pad);y1,x1=min(h,y+tile+pad),min(w,x+tile+pad)
                t=np.ascontiguousarray(rgb[y0:y1,x0:x1].transpose(2,0,1))
                ex=self.net.create_extractor();ex.input(self.inp,ncnn.Mat(t));r,o=ex.extract(self.out)
                o=np.array(o).transpose(1,2,0)
                yy,xx=(y-y0)*s,(x-x0)*s;th,tw=min(tile,h-y)*s,min(tile,w-x)*s
                out[y*s:y*s+th,x*s:x*s+tw]=o[yy:yy+th,xx:xx+tw]
        return (np.clip(out,0,1)*255+.5).astype(np.uint8)[...,::-1]
if __name__=='__main__':
    im=cv2.imread('/home/user/Portfolio-/seed/catch/f020.webp')[:,250:950]
    for name,s in (('realesr-animevideov3-x2',2),):
        sr=SR(name,s);t=time.time();o=sr.run(im);print(name,time.time()-t,o.shape);cv2.imwrite(name+'.png',o)
    cv2.imwrite('lanczos.png',cv2.resize(im,None,fx=2,fy=2,interpolation=cv2.INTER_LANCZOS4))
