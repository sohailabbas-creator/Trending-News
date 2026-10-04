<?php
// SohilAbbas.site TikTok downloader API
// Requires PHP 7.4+ and cURL.

$a = $_GET['a'] ?? '';

function json_response($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    exit;
}

function fetch_url($url, $timeout = 30) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS => 5,
        CURLOPT_TIMEOUT => $timeout,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36',
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_RETURNTRANSFER => true,
    ]);
    $body = curl_exec($ch);
    $error = curl_error($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return [$body, $error, $code];
}

function media_url($url, $filename) {
    return '/api.php?a=file&n=' . rawurlencode($filename) . '&u=' . rawurlencode($url);
}

if ($a === 'resolve') {
    $raw = file_get_contents('php://input');
    $input = json_decode($raw ?: '', true);
    $url = trim($input['url'] ?? '');

    if (!$url || !filter_var($url, FILTER_VALIDATE_URL)) {
        json_response(['success'=>false,'error'=>'Please paste a valid TikTok link.'], 400);
    }

    $parts = parse_url($url);
    $scheme = strtolower($parts['scheme'] ?? '');
    $host = strtolower($parts['host'] ?? '');
    $allowed = ['tiktok.com','www.tiktok.com','m.tiktok.com','vm.tiktok.com','vt.tiktok.com','tiktokv.com','www.tiktokv.com','tiktokv.us','musical.ly','www.musical.ly'];
    $valid = false;
    foreach ($allowed as $domain) {
        if ($host === $domain || substr($host, -strlen('.'.$domain)) === '.'.$domain) { $valid = true; break; }
    }
    if ($scheme !== 'https' || !$valid) {
        json_response(['success'=>false,'error'=>'Paste a valid TikTok link.'], 400);
    }

    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $rateFile = sys_get_temp_dir() . '/ttdl_' . md5($ip);
    $times = file_exists($rateFile) ? json_decode(@file_get_contents($rateFile), true) : [];
    $times = is_array($times) ? array_values(array_filter($times, fn($x) => $x > time()-60)) : [];
    if (count($times) >= 20) json_response(['success'=>false,'error'=>'Too many requests. Please wait one minute.'], 429);
    $times[] = time(); @file_put_contents($rateFile, json_encode($times));

    $api = 'https://www.tikwm.com/api/?hd=1&url=' . rawurlencode($url);
    [$body,$curlError,$httpCode] = fetch_url($api, 40);
    if ($body === false || $body === '' || $curlError) {
        json_response(['success'=>false,'error'=>'Could not connect to the downloader API.','details'=>$curlError], 502);
    }
    $data = json_decode($body, true);
    if (!is_array($data)) json_response(['success'=>false,'error'=>'Downloader API returned invalid JSON.'], 502);
    if (($data['code'] ?? 1) != 0 || empty($data['data'])) {
        json_response(['success'=>false,'error'=>$data['msg'] ?? 'Could not fetch this TikTok video. It may be private, removed, or unavailable.'], 502);
    }
    $d = $data['data'];
    $images=[];
    foreach (($d['images'] ?? []) as $img) if (is_string($img) && filter_var($img,FILTER_VALIDATE_URL)) $images[]=media_url($img,'tiktok-image.jpg');

    json_response([
        'success'=>true,
        'title'=>$d['title'] ?? 'TikTok video',
        'author'=>$d['author']['nickname'] ?? ($d['author']['unique_id'] ?? ''),
        'cover'=>$d['cover'] ?? ($d['origin_cover'] ?? ''),
        'video'=>!empty($d['play']) ? media_url($d['play'],'tiktok-video-no-watermark.mp4') : null,
        'videoHD'=>!empty($d['hdplay']) ? media_url($d['hdplay'],'tiktok-video-hd.mp4') : null,
        'audio'=>!empty($d['music']) ? media_url($d['music'],'tiktok-audio.mp3') : null,
        'images'=>$images
    ]);
}

if ($a === 'file') {
    $u = $_GET['u'] ?? '';
    if (!$u || !filter_var($u,FILTER_VALIDATE_URL)) { http_response_code(400); exit('Invalid media URL'); }
    $parts=parse_url($u); $scheme=strtolower($parts['scheme']??''); $host=strtolower($parts['host']??'');
    $allowed=['tikwm.com','www.tikwm.com','tiktokcdn.com','tiktokcdn-us.com','tiktokv.com','tiktokv.us','byteoversea.com','ibytedtos.com','ibyteimg.com'];
    $ok=false; foreach($allowed as $domain){ if($host===$domain || substr($host,-strlen('.'.$domain))==='.'. $domain){$ok=true;break;} }
    if($scheme!=='https'||!$ok){http_response_code(403);exit('Media host not allowed');}
    $name=preg_replace('/[^a-zA-Z0-9._-]/','',$_GET['n']??'tiktok.mp4') ?: 'tiktok.mp4';
    $ch=curl_init($u);
    curl_setopt_array($ch,[CURLOPT_FOLLOWLOCATION=>true,CURLOPT_MAXREDIRS=>5,CURLOPT_TIMEOUT=>120,CURLOPT_CONNECTTIMEOUT=>15,CURLOPT_USERAGENT=>'Mozilla/5.0',CURLOPT_SSL_VERIFYPEER=>true,CURLOPT_SSL_VERIFYHOST=>2,CURLOPT_RETURNTRANSFER=>false,CURLOPT_WRITEFUNCTION=>function($ch,$chunk){echo $chunk;return strlen($chunk);}]);
    header('Content-Disposition: attachment; filename="'.$name.'"');
    header('Content-Type: application/octet-stream');
    header('X-Content-Type-Options: nosniff');
    curl_exec($ch); curl_close($ch); exit;
}

json_response(['success'=>false,'error'=>'Invalid API request.'],404);
