"""Server trích xuất link audio/video.  Chạy: python server.py  ->  mở http://localhost:8000
Tuỳ chọn (khuyên dùng, hỗ trợ Zing MP3, YouTube, TikTok, SoundCloud...):  pip install -U yt-dlp
"""
import json, os, re, socket, ipaddress, urllib.request
from urllib.parse import urljoin, urlparse, parse_qs
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from html.parser import HTMLParser
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

AUD = {'mp3','m4a','aac','wav','flac','ogg','oga','opus','wma','weba'}
VID = {'mp4','webm','mkv','mov','avi','m4v','flv','wmv','ogv','3gp','m3u8'}
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
RAW = re.compile(r'https?:\\?/\\?/[^\s"\'<>\\]+?\.(?:%s)(?:\?[^\s"\'<>\\]*)?' % '|'.join(AUD | VID), re.I)

def kind(u):
    ext = urlparse(u).path.rsplit('.', 1)[-1].lower()
    return 'audio' if ext in AUD else 'video' if ext in VID else None

class Attrs(HTMLParser):
    def __init__(self):
        super().__init__(); self.vals = []; self.title = ''; self._t = False
    def handle_starttag(self, tag, attrs):
        self._t = tag == 'title'
        self.vals += [v for _, v in attrs if v]
    def handle_data(self, d):
        if self._t: self.title += d
    def handle_endtag(self, tag): self._t = False

def from_html(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode(r.headers.get_content_charset() or 'utf-8', 'ignore')
    p = Attrs(); p.feed(html)
    cands = [urljoin(url, v) for v in p.vals] + [m.replace('\\', '') for m in RAW.findall(html)]
    out, seen = [], set()
    for c in cands:
        k = kind(c)
        if k and c not in seen:
            seen.add(c); out.append({'url': c, 'type': k, 'title': ''})
    return out

def from_ytdlp(url):
    if not yt_dlp: return []
    with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True, 'noplaylist': True}) as y:
        info = y.extract_info(url, download=False)
    out = []
    for e in (info.get('entries') or [info]):
        for f in (e.get('formats') or []):
            if not f.get('url') or f.get('protocol') in ('mhtml',): continue
            v, a = f.get('vcodec', 'none'), f.get('acodec', 'none')
            t = 'video' if v != 'none' else 'audio' if a != 'none' else None
            if t:
                q = f.get('format_note') or (f"{f.get('height')}p" if f.get('height') else f.get('abr') and f"{int(f['abr'])}kbps") or ''
                out.append({'url': f['url'], 'type': t, 'title': f"{e.get('title','')} [{f.get('ext','')} {q}]".strip()})
    return out

def safe(url):
    try:
        host = urlparse(url).hostname
        return all(not (ipaddress.ip_address(i[4][0]).is_private or ipaddress.ip_address(i[4][0]).is_loopback or ipaddress.ip_address(i[4][0]).is_link_local)
                   for i in socket.getaddrinfo(host, None))
    except Exception:
        return False

def extract(url):
    if not safe(url): return {'items': [], 'errors': ['URL không được phép'], 'ytdlp': bool(yt_dlp)}
    res, errs = [], []
    for fn in (from_html, from_ytdlp):
        try: res += fn(url)
        except Exception as e: errs.append(f'{fn.__name__}: {e}')
    uniq = {r['url']: r for r in res}
    return {'items': list(uniq.values()), 'errors': errs, 'ytdlp': bool(yt_dlp)}

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code); self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/api/extract':
            target = parse_qs(u.query).get('url', [''])[0]
            data = extract(target) if target.startswith('http') else {'items': [], 'errors': ['URL không hợp lệ']}
            return self._send(200, json.dumps(data).encode(), 'application/json')
        self._send(200, (Path(__file__).parent / 'index.html').read_bytes(), 'text/html; charset=utf-8')
    def log_message(self, *a): pass

if __name__ == '__main__':
    print('Mở http://localhost:8000', '(yt-dlp: bật)' if yt_dlp else '(chưa cài yt-dlp: pip install -U yt-dlp)')
    ThreadingHTTPServer((os.environ.get('HOST', '127.0.0.1'), int(os.environ.get('PORT', 8000))), H).serve_forever()
