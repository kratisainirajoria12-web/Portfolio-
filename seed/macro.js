/* ================= the seed head: 3D macro over the last zoom frame =================
   World units: the video frame is a plane 16/9 wide x 1 high at z=0 (1 unit = frame height).
   Seeds sit on the brown disc of that frame; the camera starts exactly at the 2D cover framing. */
function makeMacro(canvas,frameImg){
  const T=THREE,mob=innerWidth<760;
  const R=new T.WebGLRenderer({canvas,antialias:true,alpha:true,premultipliedAlpha:true,powerPreference:'high-performance'});
  R.setClearColor(0x000000,0);R.outputColorSpace=T.SRGBColorSpace;R.toneMapping=T.ACESFilmicToneMapping;R.toneMappingExposure=1.3;
  const scene=new T.Scene(),cam=new T.PerspectiveCamera(30,1,.01,60);
  const FW=16/9,DX=(602/1280-.5)*FW,DY=.5-398/720,DR=447/720*.965;   // disc centre + radius in the last frame
  // background plate = the last zoom frame, with a soft alpha fade at the bottom for the fall
  const pc=document.createElement('canvas');pc.width=1280;pc.height=720;const px=pc.getContext('2d');
  const plateTex=new T.CanvasTexture(pc);plateTex.colorSpace=T.SRGBColorSpace;
  function setFrame(img){if(!img||!img.naturalWidth)return false;px.clearRect(0,0,1280,720);px.drawImage(img,0,0,1280,720);
    plateTex.needsUpdate=true;return true;}
  let plateOK=setFrame(frameImg);
  const PE=1.7;
  const plate=new T.Mesh(new T.PlaneGeometry(FW*PE,PE),new T.ShaderMaterial({transparent:true,uniforms:{map:{value:plateTex},uFade:{value:0},uA:{value:1},uDk:{value:0}},
    vertexShader:`varying vec2 vUv;void main(){vUv=(uv-.5)*${PE.toFixed(2)}+.5;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader:`uniform sampler2D map;uniform float uFade,uA,uDk;varying vec2 vUv;
      void main(){vec4 c=texture2D(map,clamp(vUv,.002,.998));float a=mix(1.,smoothstep(.0,.24,vUv.y),uFade);gl_FragColor=vec4(c.rgb*(1.-uDk),a*uA);
      #include <colorspace_fragment>
      }`}));
  // a little bleed beyond the frame so a moving camera never sees an edge
  scene.add(plate);
  // receptacle under the seeds: deep brown, so the gaps between seeds read as shadow
  const rec=new T.Mesh(new T.CircleGeometry(DR*1.02,96),new T.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{opacity:{value:0},uFade:{value:0}},
    vertexShader:`varying vec3 vW;varying vec2 vP;void main(){vP=position.xy;vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}`,
    fragmentShader:`uniform float opacity,uFade;varying vec3 vW;varying vec2 vP;
      float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5);}
      void main(){float r=length(vP)/${(DR*1.02).toFixed(4)};
        float n=h(floor(vP*260.))*.5+h(floor(vP*90.))*.5;
        vec3 c=mix(vec3(.05,.028,.014),vec3(.11,.065,.03),n*.6+.4*(1.-r));
        float a=opacity*smoothstep(1.,.96,r)*mix(1.,smoothstep(-.5,-.27,vW.y),uFade);
        gl_FragColor=vec4(c,a);
        #include <colorspace_fragment>
      }`}));
  rec.position.set(DX,DY,.002);scene.add(rec);

  // ---- seeds (Vogel phyllotaxis) ----
  const N=mob?720:1150,GA=Math.PI*(3-Math.sqrt(5));
  const unit=DR*Math.sqrt(Math.PI/N);                    // spacing between neighbours
  const geo=new T.SphereGeometry(1,22,14);
  // seed texture: matte charcoal coat, pale stripes along the long axis, light rim
  const st=document.createElement('canvas');st.width=512;st.height=128;const sx=st.getContext('2d');
  sx.fillStyle='#3a3a3a';sx.fillRect(0,0,512,128);
  for(let i=0;i<1400;i++){sx.fillStyle=`rgba(${Math.random()<.5?0:255},${Math.random()<.5?0:255},${Math.random()<.5?0:255},.05)`;sx.fillRect(Math.random()*512,Math.random()*128,2,8);}
  const stripe=(u,w,a)=>{const g=sx.createLinearGradient((u-w)*512,0,(u+w)*512,0);g.addColorStop(0,'rgba(235,225,205,0)');g.addColorStop(.5,`rgba(235,225,205,${a})`);g.addColorStop(1,'rgba(235,225,205,0)');sx.fillStyle=g;sx.fillRect((u-w)*512,0,w*1024,128);};
  stripe(.25,.010,1);stripe(.212,.006,.7);stripe(.288,.006,.7);stripe(.175,.007,.45);stripe(.325,.007,.45);
  const seedTex=new T.CanvasTexture(st);seedTex.colorSpace=T.SRGBColorSpace;seedTex.anisotropy=4;
  const mat=new T.MeshStandardMaterial({map:seedTex,roughness:.62,metalness:0,envMapIntensity:0});
  const mesh=new T.InstancedMesh(geo,mat,N);mesh.instanceMatrix.setUsage(T.DynamicDrawUsage);scene.add(mesh);
  const S=[];const col=new T.Color();
  const rnd=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11);
  for(let i=0;i<N;i++){
    const r=Math.sqrt((i+.5)/N),a=i*GA,rr=r*DR;
    const size=unit*.58*(.93+.14*r)*(.94+.12*rnd());
    const dome=.075*DR*Math.sqrt(Math.max(0,1-r*r));
    // seeds lean along the dome and point their long axis around the spiral
    const s={i,r,a,x:DX+Math.cos(a)*rr,y:DY+Math.sin(a)*rr,z:.004+dome,size,
      yaw:a+Math.PI/2+(rnd()-.5)*.5,tilt:-r*.55,rnd:rnd(),
      delay:(1-r)*.75+rnd()*.25,                         // outer rings loosen first
      wind:rnd()<.22,spinAx:new T.Vector3(rnd()-.5,rnd()-.5,rnd()-.5).normalize(),
      drift:[(rnd()-.5)*.9,(rnd()-.2)*.35,.2+rnd()*1.6]};
    // colour: centre seeds younger and warmer, outer seeds near-black with variation (like a real head)
    const young=Math.pow(Math.max(0,1-r/.3),.8);
    col.setRGB(.2,.16,.13).lerp(new T.Color(.95,.55,.24),young).multiplyScalar(.45+.75*s.rnd*(1-young*.4));
    if(rnd()<.12)col.multiplyScalar(.5);else if(rnd()<.08)col.setRGB(.5,.33,.2);
    mesh.setColorAt(i,col);S.push(s);}
  mesh.instanceColor.needsUpdate=true;
  // the one seed we follow down to Krati: close to the centre, last to let go
  const HERO=S.reduce((b,s)=>(s.r>.06&&s.r<.12&&(!b||s.r<b.r))?s:b,null);HERO.delay=1.02;HERO.wind=false;
  // the one seed that falls is its own mesh, so the head can sink into darkness while it stays lit
  const hcol=new T.Color();mesh.getColorAt(HERO.i,hcol);
  const heroMesh=new T.Mesh(geo,new T.MeshStandardMaterial({map:seedTex,roughness:.55,color:hcol.clone().multiplyScalar(1.15)}));
  heroMesh.matrixAutoUpdate=false;heroMesh.renderOrder=10;heroMesh.material.transparent=true;heroMesh.material.depthTest=false;scene.add(heroMesh);
  // a black veil drawn over everything except the falling seed
  const veil=new T.Mesh(new T.PlaneGeometry(2,2),new T.ShaderMaterial({transparent:true,depthTest:false,depthWrite:false,uniforms:{uO:{value:0}},
    vertexShader:`void main(){gl_Position=vec4(position.xy,0.,1.);}`,fragmentShader:`uniform float uO;void main(){gl_FragColor=vec4(.02,.016,.012,uO);}`}));
  veil.frustumCulled=false;veil.renderOrder=5;scene.add(veil);
  const ZERO=new T.Matrix4().makeScale(0,0,0);

  // ---- light: warm low sun from the upper left, soft sky fill ----
  const sun=new T.DirectionalLight(0xffd29a,4.6);sun.position.set(-1.2,1.4,1.6);scene.add(sun);
  scene.add(new T.HemisphereLight(0xfff1d8,0x2a1a10,1.7));
  const rim=new T.DirectionalLight(0xffb060,1.2);rim.position.set(1.5,-.6,.8);scene.add(rim);

  // ---- gold bokeh motes ----
  const NM=mob?70:150,mp=new Float32Array(NM*3),ms=new Float32Array(NM),mph=new Float32Array(NM);
  for(let i=0;i<NM;i++){mp[i*3]=DX+.04+(rnd()-.5)*.62;mp[i*3+1]=DY+.03+(rnd()-.5)*.42;mp[i*3+2]=.012+Math.pow(rnd(),1.4)*.2;ms[i]=.5+rnd();mph[i]=rnd()*6.28;}
  const mg=new T.BufferGeometry();mg.setAttribute('position',new T.BufferAttribute(mp,3));mg.setAttribute('aS',new T.BufferAttribute(ms,1));mg.setAttribute('aP',new T.BufferAttribute(mph,1));
  const motes=new T.Points(mg,new T.ShaderMaterial({transparent:true,depthWrite:false,blending:T.AdditiveBlending,
    uniforms:{uT:{value:0},uA:{value:0},uH:{value:800},uF:{value:1}},
    vertexShader:`attribute float aS;attribute float aP;uniform float uT,uH,uF;varying float vA;varying float vR;
      void main(){vec3 p=position;p.x+=sin(uT*.21+aP)*.012;p.y+=sin(uT*.17+aP*1.7)*.012+mod(uT*.004*aS+aP,.12)-.06;
      vec4 mv=modelViewMatrix*vec4(p,1.);float d=-mv.z;
      float coc=abs(d-uF)/d*120.;                         // out of focus = bigger, dimmer
      gl_PointSize=clamp((5.+coc*1.6)*aS*uH/900.,3.,uH*.075);vR=gl_PointSize;
      vA=(.6+.4*sin(uT*1.3+aP*3.))*clamp(30./(gl_PointSize+8.),.28,1.);gl_Position=projectionMatrix*mv;}`,
    fragmentShader:`uniform float uA;varying float vA;varying float vR;
      void main(){float d=length(gl_PointCoord-.5)*2.;if(d>1.)discard;
      float disc=smoothstep(1.,.82,d)*(.75+.25*smoothstep(.55,.95,d));
      float a=disc*vA*uA;gl_FragColor=vec4(vec3(1.,.78,.36)*a,a);}`}));
  scene.add(motes);

  const M4=new T.Matrix4(),Q=new T.Quaternion(),Q2=new T.Quaternion(),E=new T.Euler(),V=new T.Vector3(),SC=new T.Vector3(),Z=new T.Vector3(0,0,1);
  let W=0,H=0;
  function size(){const d=Math.min(devicePixelRatio||1,mob?1.5:1.75);W=innerWidth;H=innerHeight;R.setPixelRatio(d);R.setSize(W,H,false);cam.aspect=W/H;}
  size();
  // camera distance that reproduces the 2D "cover" framing of the frame (plane at z=0)
  const coverDist=fov=>{const vh=Math.min(1,FW/(W/H));return vh/2/Math.tan(fov*Math.PI/360);};
  const ss=t=>t*t*(3-2*t),sat=x=>Math.min(1,Math.max(0,x));
  /* state: {ripen 0..1, push 0..1, drop 0..1, fall 0..1, t time, mx,my mouse, heroTo:{x,y,px} screen target for the followed seed} */
  function render(st){
    if(!plateOK)plateOK=setFrame(frameImg);
    const fov=lerpN(30,23,ss(st.push));cam.fov=fov;
    const d0=coverDist(fov);
    // push in towards the disc with a slow orbit/tilt, a little roll and SEED-style idle breathing
    const e=ss(st.push),idle=st.reduce?0:1;
    const dist=d0*lerpN(1,.34,e);
    const az=.24*e+(Math.sin(st.t*.13)*.012*e+st.mx*.05*e)*idle, el=-.22*e+(Math.sin(st.t*.17+1.3)*.008*e-st.my*.03*e)*idle;
    let tx=lerpN(0,DX+.04,e),ty=lerpN(0,DY+.03,e)+Math.sin(st.t*.21)*.004*dist*idle;
    // the fall: the camera sinks below the head, following the seeds down
    const visH=2*dist*Math.tan(fov*Math.PI/360);
    const fy=st.fall*(ty+.5+visH*.62+.04);ty-=fy;
    cam.position.set(tx+dist*Math.cos(el)*Math.sin(az),ty+dist*Math.sin(el),dist*Math.cos(el)*Math.cos(az));
    cam.up.set(Math.sin(-.04*e),Math.cos(-.04*e),0);cam.lookAt(tx,ty,0);
    cam.updateProjectionMatrix();cam.updateMatrixWorld();
    const dk=st.dark||0;veil.material.uniforms.uO.value=dk*(1-(st.reveal||0));
    const gone=dk>.98&&st.fall>.02;mesh.visible=plate.visible=rec.visible=!gone;
    rec.material.uniforms.opacity.value=(.25+.7*ss(sat((st.drop-.05)/.5)))*st.ripen*st.ripen;rec.material.uniforms.uFade.value=st.fade||0;plate.material.uniforms.uFade.value=st.fade||0;plate.material.opacity=1;plate.material.uniforms.uA.value=1;
    const MU=motes.material.uniforms;MU.uT.value=st.t;MU.uA.value=st.motes;MU.uH.value=H*R.getPixelRatio();MU.uF.value=dist;
    motes.position.y=-fy*.85;
    let hero=null;
    if(st.heroScreen&&st.heroScreen.k>0){const h=st.heroScreen;hero=heroTarget(h.x,h.y,h.w);hero.k=h.k;}
    for(const s of S){
      const grow=ss(sat((st.ripen*1.35-(1-s.r))/.35));      // outer rings ripen first
      let x=s.x,y=s.y,z=s.z,sc=s.size*grow;
      Q.setFromEuler(E.set(s.tilt*Math.sin(s.a)*.6,-s.tilt*Math.cos(s.a)*.6,s.yaw));
      // falling: scrubbed and fully reversible, no physics — gravity curve, flutter, tumble, some carried by the wind
      const dt=sat((st.drop-s.delay*.72)/.28);
      if(dt>0&&s!==HERO&&st.rain){
        const g=dt*dt;
        x+=s.drift[0]*dt*(s.wind?1.5:.35)+Math.sin(dt*11+s.a)*.03*Math.sin(Math.PI*dt);
        y-=g*(2.2+s.rnd*1.6)*(1+st.fall*.6)+(s.wind?-.22*Math.sin(Math.PI*dt):0);
        z+=s.drift[2]*dt*.1;
        Q2.setFromAxisAngle(s.spinAx,dt*(6+s.rnd*6));Q.premultiply(Q2);
        sc*=1-ss(sat((dt-.8)/.2))*.0;
      }
      if(s===HERO){
        // the one we follow lets go last, drifts down with the camera and settles exactly where the catch footage picks it up
        const ht=sat((st.drop-.22)/.78);
        if(ht>0){x+=Math.sin(ht*5)*.012*ht;y-=ss(ht)*.07+fy+ss(sat((st.fall-.3)/.4))*visH*.75;z+=.12*ss(ht);Q2.setFromAxisAngle(s.spinAx,ht*7);Q.premultiply(Q2);}
        if(hero){x=lerpN(x,hero.x,hero.k);y=lerpN(y,hero.y,hero.k);z=lerpN(z,hero.z,hero.k);
          Q2.setFromEuler(E.set(0,0,Math.PI/2));Q.slerp(Q2,hero.k);}
      }
      SC.set(sc*.7,sc*1.12,sc*.45);
      M4.compose(V.set(x,y,z),Q,SC);
      if(s===HERO){heroMesh.matrix.copy(M4);heroMesh.matrixWorldNeedsUpdate=true;mesh.setMatrixAt(s.i,ZERO);}else mesh.setMatrixAt(s.i,M4);}
    mesh.instanceMatrix.needsUpdate=true;
    R.render(scene,cam);
  }
  // world point where the followed seed shows at screen (sx,sy) with a pixel length pw (it lies horizontal, like the seed in the footage)
  function heroTarget(sx,sy,pw){
    const len=HERO.size*1.12*2,d=len*H/(2*Math.tan(cam.fov*Math.PI/360)*pw);
    V.set(sx/W*2-1,-(sy/H*2-1),.5).unproject(cam).sub(cam.position).normalize();
    return{x:cam.position.x+V.x*d,y:cam.position.y+V.y*d,z:cam.position.z+V.z*d};}
  function lerpN(a,b,t){return a+(b-a)*t;}
  return{render,size,setFrame,heroTarget,cam,DX,DY,DR};
}
