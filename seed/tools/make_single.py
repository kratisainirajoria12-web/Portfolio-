"""One-file copy of the site: every page, frame, image and video packed into a single HTML that opens by double-click.

Files live in an in-page store (text as-is, binaries as base64). Each one becomes a blob: URL the first time it is
asked for; pages inside it get their relative src/href/poster pointed at those URLs. The main page asks for frames
through a small hook on img.src and iframe.src. Phones use the desktop frames here (the sharper phone set would
push the file well past GitHub's 100 MB limit). Fonts still come from Google Fonts when online.

usage: python3 tools/make_single.py <site dir> <out.html> <three.min.js>"""
import base64, json, os, re, sys

SITE, OUT, THREE = sys.argv[1:4]
TEXT = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript'}
BIN = {'.webp': 'image/webp', '.jpg': 'image/jpeg', '.png': 'image/png', '.mp4': 'video/mp4', '.webm': 'video/webm'}

def rd(p): return open(os.path.join(SITE, p), encoding='utf-8').read()

# more.js (standalone and inlined in the Beauty by Bie bundle) builds paths from the page location; send them to the store
# Pages inside the viewer can't load the main page's blob: URLs, so thumbnails go in as data: URLs and a card asks
# the main page (postMessage) to open the other case study.
def r_def():
    m = ','.join(f"'thumbs/{n}':'data:image/webp;base64,{base64.b64encode(open(os.path.join(SITE, 'work/thumbs', n), 'rb').read()).decode()}'"
                 for n in sorted(os.listdir(os.path.join(SITE, 'work/thumbs'))))
    return ("const R=x=>{const M={" + m + "};if(M[x])return M[x];if(/\\.html$/.test(x))return '#vfs:work/'+x;return BASE+x};"
            "document.addEventListener('click',e=>{const a=e.target.closest&&e.target.closest('a');"
            "if(a&&(a.getAttribute('href')||'').startsWith('#vfs:')){e.preventDefault();top.postMessage({type:'vfs-open',path:a.getAttribute('href').slice(5)},'*');}});")
def patch_more(s, q):
    r = r_def() if q == "'" else r_def().replace('\\', '\\\\')   # inside the bundle it sits in a JSON string
    s = s.replace("let H=window,BASE='';", "let H=window,BASE='';" + r)
    s = s.replace('${BASE}thumbs/${p.id}.webp', "${R('thumbs/'+p.id+'.webp')}")
    s = s.replace('${BASE}${p.href}', '${R(p.href)}')
    return s

def localize(html, base):
    """point relative src/href/poster at store entries: vfs:<path> tokens, swapped for blob URLs at runtime"""
    def sub(m):
        attr, v = m.group(1), m.group(2)
        if re.match(r'^(https?:|mailto:|tel:|#|data:|blob:)', v): return m.group(0)
        p = os.path.normpath(os.path.join(base, v)).replace('\\', '/')
        return f'{attr}="vfs:{p}"' if os.path.isfile(os.path.join(SITE, p)) else m.group(0)
    return re.sub(r'\b(src|href|poster)="([^"]*)"', sub, html)

files = {}
for root, _, names in os.walk(SITE):
    for n in names:
        p = os.path.relpath(os.path.join(root, n), SITE).replace('\\', '/')
        if p == 'index.html' or p.startswith('m/'): continue
        ext = os.path.splitext(n)[1].lower()
        if ext in TEXT:
            s = rd(p)
            if p == 'work/more.js': s = patch_more(s, "'")
            if p == 'work/beauty-by-bie.html':
                assert "let H=window,BASE='';" in s
                s = patch_more(s, '"')
            elif ext == '.html':
                s = localize(s, os.path.dirname(p))
            files[p] = [TEXT[ext], 0, s]
        elif ext in BIN:
            files[p] = [BIN[ext], 1, base64.b64encode(open(os.path.join(SITE, p), 'rb').read()).decode()]

page = rd('index.html')
seed = 'data:image/webp;base64,' + files['assets/seed.webp'][2]
page = page.replace('url(assets/seed.webp)', f'url({seed})')
page = page.replace('const MOB=', 'const MOB=false&&', 1)
cdn = '<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>'
assert cdn in page
three = open(THREE, encoding='utf-8').read()
assert '</script' not in three
page = page.replace(cdn, '<script>' + three + '</script>')

boot = r"""<script>
/* the store: path -> blob: URL on first use; html pages get their vfs: references swapped in */
(()=>{const D=JSON.parse(document.getElementById('vfsdata').textContent),U={};
  function vfs(p){p=p.replace(/^\.\//,'');if(U[p])return U[p];const f=D[p];if(!f)return null;let body;
    if(f[1]){const b=atob(f[2]),a=new Uint8Array(b.length);for(let i=0;i<b.length;i++)a[i]=b.charCodeAt(i);body=a;}
    else body=f[0]==='text/html'?f[2].replace(/vfs:([^"]+)/g,(m,q)=>durl(q)||m):f[2];
    return U[p]=URL.createObjectURL(new Blob([body],{type:f[0]}));}
  // inside a page the viewer opens, references become data: URLs (it may not load the main page's blob: URLs)
  function durl(p){const f=D[p];if(!f)return null;
    return 'data:'+f[0]+(f[1]?';base64,'+f[2]:';charset=utf-8,'+encodeURIComponent(f[2]));}
  window.__vfs=vfs;
  // a "More projects" card inside a case study opens that case in the viewer
  addEventListener('message',e=>{if(!e.data||e.data.type!=='vfs-open')return;
    const a=[...document.querySelectorAll('a[data-case]')].find(x=>x.getAttribute('href')===e.data.path);if(a)a.click();});
  // the main page sets frames, the macro plate and the case viewer by relative path
  const hook=(C,prop)=>{const d=Object.getOwnPropertyDescriptor(C.prototype,prop);
    Object.defineProperty(C.prototype,prop,{configurable:true,get(){return d.get.call(this)},
      set(v){if(typeof v==='string'&&!/^(https?:|data:|blob:)/.test(v)){const u=vfs(v);if(u)v=u;}d.set.call(this,v);}});};
  hook(HTMLImageElement,'src');hook(HTMLIFrameElement,'src');
})();
</script>"""
data = json.dumps(files, separators=(',', ':')).replace('</', '<\\/')
head_end = page.index('<title>')
page = page[:head_end] + '<script type="application/json" id="vfsdata">' + data + '</script>\n' + boot + '\n' + page[head_end:]
open(OUT, 'w', encoding='utf-8').write(page)
print(len(files), 'files,', round(os.path.getsize(OUT) / 1e6, 1), 'MB')
