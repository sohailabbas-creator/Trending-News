<?php
// Upload to site root. Needs PHP 7.4+ with cURL (default on most hosts).
$a = $_GET['a'] ?? '';
function http_get($url, $stream = false) {
  $ch = curl_init($url);
  curl_setopt_array($ch, [CURLOPT_FOLLOWLOCATION=>true, CURLOPT_TIMEOUT=>30, CURLOPT_USERAGENT=>'Mozilla/5.0', CURLOPT_RETURNTRANSFER=>!$stream]);
  if ($stream) curl_setopt($ch, CURLOPT_WRITEFUNCTION, function($c,$d){ echo $d; return strlen($d); });
  $r = curl_exec($ch); curl_close($ch); return $r;
}
function proxy($u, $n) { return 'api.php?a=file&n=' . urlencode($n) . '&u=' . urlencode($u); }

if ($a === 'resolve') {
  header('Content-Type: application/json');
  $in = json_decode(file_get_contents('php://input'), true);
  preg_match('~https?://[^\s]+~i', $in['url'] ?? '', $m); $url = preg_replace('~^http:~i','https:', $m[0] ?? '');
  $h = parse_url($url, PHP_URL_HOST);
  if (!$h || parse_url($url, PHP_URL_SCHEME) !== 'https' || !preg_match('/(^|\.)(tiktok\.com|tiktokv\.com|tiktokv\.us|musical\.ly)$/i', $h)) {
    http_response_code(400); echo json_encode(['error'=>'Paste a valid TikTok link (https://www.tiktok.com/... or https://vm.tiktok.com/...).']); exit;
  }
  // simple per-IP rate limit: 20 requests / minute
  $f = sys_get_temp_dir().'/ttdl_'.md5($_SERVER['REMOTE_ADDR']); $t = array_filter(@json_decode(@file_get_contents($f), true) ?: [], fn($x)=>$x>time()-60);
  if (count($t) >= 20) { http_response_code(429); echo json_encode(['error'=>'Too many requests. Wait a minute and try again.']); exit; }
  $t[] = time(); file_put_contents($f, json_encode(array_values($t)));
  $r = json_decode(http_get('https://www.tikwm.com/api/?hd=1&url='.urlencode($url)), true);
  if (!$r || ($r['code'] ?? 1) !== 0 || empty($r['data'])) { http_response_code(502); echo json_encode(['error'=>"Couldn't fetch this video. It may be private, removed, or region-locked."]); exit; }
  $d = $r['data'];
  echo json_encode(['title'=>$d['title'] ?? 'TikTok video', 'author'=>$d['author']['nickname'] ?? '', 'cover'=>$d['cover'] ?? '',
    'video'=>!empty($d['play'])?proxy($d['play'],'tiktok-video-no-watermark.mp4'):null,
    'videoHD'=>!empty($d['hdplay'])?proxy($d['hdplay'],'tiktok-video-hd.mp4'):null,
    'audio'=>!empty($d['music'])?proxy($d['music'],'tiktok-audio.mp3'):null,
    'images'=>array_map(fn($i)=>proxy($i,'tiktok-image.jpg'), $d['images'] ?? [])]);
  exit;
}
if ($a === 'file') {
  $u = $_GET['u'] ?? ''; $h = parse_url($u, PHP_URL_HOST);
  // only allow TikTok media hosts / the resolver's CDN (prevents use as an open proxy)
  if (!$h || parse_url($u, PHP_URL_SCHEME) !== 'https' || !preg_match('/(^|\.)(tikwm\.com|tiktokcdn\.com|tiktokcdn-us\.com|tiktokv\.com|byteoversea\.com|ibytedtos\.com|ibyteimg\.com)$/i', $h)) { http_response_code(403); exit('Not allowed'); }
  $n = preg_replace('/[^a-z0-9._-]/i', '', $_GET['n'] ?? 'tiktok.mp4');
  header('Content-Disposition: attachment; filename="'.$n.'"');
  header('Content-Type: application/octet-stream');
  http_get($u, true); exit;
}
http_response_code(404);
