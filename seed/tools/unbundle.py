# Unbundle work/beauty-by-bie.html: the page shipped as a 9 MB self-extracting bundle (all images base64 inside
# one HTML file, decoded in the browser before anything shows). This writes the page as plain HTML with its
# assets as separate files, images re-encoded to WebP, so the browser can show it as soon as the HTML arrives.
import re, json, base64, gzip, os, io, sys
from PIL import Image

SRC = sys.argv[1]            # bundled html
OUT_HTML = sys.argv[2]       # plain html to write
ASSET_DIR = sys.argv[3]      # folder for assets (next to OUT_HTML)
REL = os.path.relpath(ASSET_DIR, os.path.dirname(OUT_HTML))

s = open(SRC, encoding='utf-8').read()
def block(t):
    return re.search(r'<script type="__bundler/%s">\s*(.*?)\s*</script>' % t, s, re.S).group(1)
man = json.loads(block('manifest')); tpl = json.loads(block('template')); ext = json.loads(block('ext_resources'))
os.makedirs(ASSET_DIR, exist_ok=True)

names = {'8260c0eb-6ff1-408c-a6cd-8f1f7623a5bc': 'dc-runtime.js', '973bef79-6b76-4d74-934d-53b2f2240be1': 'image-slot.js',
         '03ac4e63-3790-4465-9ac2-f5489c111806': 'react.production.min.js', '5d614713-dd29-40fe-a7a2-7716021c8bd7': 'react-dom.production.min.js'}
paths = {}
img_n = font_n = 0
for u, e in man.items():
    b = base64.b64decode(e['data'])
    if e['compressed']: b = gzip.decompress(b)
    mime = e['mime']
    if mime.startswith('image/') and mime != 'image/svg+xml':
        img_n += 1
        im = Image.open(io.BytesIO(b)); im.load()
        if im.mode not in ('RGB', 'RGBA'): im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
        name = f'img{img_n:02d}.webp'
        im.save(os.path.join(ASSET_DIR, name), 'WEBP', quality=88, method=6)
    elif mime.startswith('font/'):
        font_n += 1; name = f'font{font_n}.woff2'; open(os.path.join(ASSET_DIR, name), 'wb').write(b)
    else:
        name = names.get(u, u + '.bin'); open(os.path.join(ASSET_DIR, name), 'wb').write(b)
    paths[u] = REL + '/' + name

for u, p in paths.items():
    tpl = tpl.replace(u, p)
tpl = re.sub(r'\s+integrity="[^"]*"', '', tpl); tpl = re.sub(r'\s+crossorigin="[^"]*"', '', tpl)

# React comes from the local copies instead of unpkg; the runtime looks these up by their CDN URL.
res = {x['id']: paths[x['uuid']] for x in ext}
inject = '<script>window.__resources = ' + json.dumps(res).replace('</', '<\\/') + ';</script>'
m = re.search(r'<head[^>]*>', tpl, re.I)
tpl = tpl[:m.end()] + inject + tpl[m.end():]
open(OUT_HTML, 'w', encoding='utf-8').write(tpl)
left = [u for u in man if u in tpl]
print('written', OUT_HTML, len(tpl), 'bytes; assets', len(paths), '; uuids left', left)
