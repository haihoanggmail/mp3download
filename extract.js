// Vercel / Node 18+ serverless function: quét HTML tìm file audio/video (không có yt-dlp)
const AUD = ['mp3','m4a','aac','wav','flac','ogg','oga','opus','wma','weba'];
const VID = ['mp4','webm','mkv','mov','avi','m4v','flv','wmv','ogv','3gp','m3u8'];
const EXT = [...AUD, ...VID].join('|');
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36';

const kind = (u) => {
  try {
    const e = new URL(u).pathname.split('.').pop().toLowerCase();
    return AUD.includes(e) ? 'audio' : VID.includes(e) ? 'video' : null;
  } catch { return null; }
};
// chặn truy cập mạng nội bộ (SSRF)
const blocked = (h) =>
  !h.includes('.') || /^(localhost|127\.|10\.|0\.|192\.168\.|169\.254\.|172\.(1[6-9]|2\d|3[01])\.)/.test(h) || h.startsWith('[');

module.exports = async (req, res) => {
  let u;
  try { u = new URL(req.query.url || ''); }
  catch { return res.status(400).json({ items: [], errors: ['URL không hợp lệ'] }); }
  if (!/^https?:$/.test(u.protocol) || blocked(u.hostname))
    return res.status(400).json({ items: [], errors: ['URL không được phép'] });

  try {
    const r = await fetch(u.href, { headers: { 'User-Agent': UA }, signal: AbortSignal.timeout(15000) });
    const html = (await r.text()).slice(0, 3_000_000).replace(/\\\//g, '/');
    const found = new Set();
    for (const m of html.matchAll(/(?:src|href|content|data-[\w-]+)=["']([^"']+)["']/gi)) {
      try { found.add(new URL(m[1], u).href); } catch {}
    }
    for (const m of html.matchAll(new RegExp(`https?://[^\\s"'<>\\\\]+?\\.(?:${EXT})(?:\\?[^\\s"'<>\\\\]*)?`, 'gi'))) found.add(m[0]);
    const items = [...found].map((url) => ({ url, type: kind(url), title: '' })).filter((x) => x.type);
    res.setHeader('Cache-Control', 's-maxage=300');
    res.status(200).json({ items, errors: [] });
  } catch (e) {
    res.status(200).json({ items: [], errors: [String(e.message || e)] });
  }
};
