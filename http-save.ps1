# http-save.ps1 v2 — 安全保存监听器（带自动校验与备份）
# 用法：右键 -> "用 PowerShell 运行"
# 端口: 7788，路径: POST /save
# 接收 base64 编码的 index.html 内容，校验后自动备份再写入

$port = 7788
$projectRoot = Split-Path -Parent $PSCommandPath
$endpoint = Join-Path $projectRoot 'index.html'
$backupDir = Join-Path $projectRoot 'versions'
if (-not (Test-Path $backupDir)) { New-Item -ItemType Directory -Path $backupDir -Force | Out-Null }

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://localhost:$port/")
Write-Host "🏛️ 钱币收藏保存服务器 v2 — 带自动校验与备份" -ForegroundColor Cyan
Write-Host "   端口: $port  |  浏览器 [💾 保存到文件] 可用"
Write-Host "   按 Ctrl+C 停止" -ForegroundColor Gray

try {
    $listener.Start()
    while ($true) {
        $ctx = $listener.GetContext()
        $req = $ctx.Request
        $resp = $ctx.Response
        
        # CORS
        $resp.AddHeader("Access-Control-Allow-Origin", "*")
        $resp.AddHeader("Access-Control-Allow-Methods", "POST, OPTIONS")
        $resp.AddHeader("Access-Control-Allow-Headers", "Content-Type")
        
        if ($req.HttpMethod -eq "OPTIONS") {
            $resp.StatusCode = 204; $resp.Close(); continue
        }
        
        if ($req.HttpMethod -eq "POST" -and $req.Url.AbsolutePath -eq "/save") {
            try {
                $len = $req.ContentLength64
                $buf = [byte[]]::new($len)
                $req.InputStream.Read($buf, 0, $len)
                $content = [System.Text.Encoding]::UTF8.GetString($buf)
                $data = $content | ConvertFrom-Json
                $html = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($data.html))
                
                # ===== 多重校验 =====
                $errors = @()
                if ($html.Length -lt 10000) { $errors += "文件过小: $($html.Length) bytes" }
                if ($html -notmatch '<!DOCTYPE html>') { $errors += "缺少 DOCTYPE" }
                if ($html -notmatch '<div class="coin-grid"') { $errors += "缺少 coin-grid" }
                if ($html -notmatch 'data-number=') { $errors += "没有钱币卡片" }
                if ($html -notmatch '</html>') { $errors += "缺少 </html>" }
                
                if ($errors.Count -gt 0) {
                    $errMsg = "VALIDATION_FAILED: " + ($errors -join '; ')
                    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ❌ $errMsg" -ForegroundColor Red
                    $resp.StatusCode = 422
                    $out = [System.Text.Encoding]::UTF8.GetBytes($errMsg)
                    $resp.ContentType = "text/plain"
                    $resp.ContentLength64 = $out.Length
                    $resp.OutputStream.Write($out, 0, $out.Length)
                    $resp.Close()
                    continue
                }
                
                # ===== 自动备份 =====
                $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
                $backupFile = Join-Path $backupDir "index.html.v$timestamp"
                if (Test-Path $endpoint) {
                    Copy-Item $endpoint $backupFile -Force
                }
                
                # ===== 写入 =====
                [System.IO.File]::WriteAllText($endpoint, $html, [System.Text.Encoding]::UTF8)
                
                # 统计钱币数量
                $coinCount = [regex]::Matches($html, 'data-number="').Count
                $fileSize = (Get-Item $endpoint).Length
                
                $resp.StatusCode = 200
                $resultMsg = "OK ($coinCount 枚, ${fileSize} bytes)"
                $out = [System.Text.Encoding]::UTF8.GetBytes($resultMsg)
                $resp.ContentType = "text/plain"
                $resp.ContentLength64 = $out.Length
                $resp.OutputStream.Write($out, 0, $out.Length)
                
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✅ 已保存: $coinCount 枚, ${fileSize}B | 备份: v$timestamp" -ForegroundColor Green
                
            } catch {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ❌ 错误: $($_.Exception.Message)" -ForegroundColor Red
                $resp.StatusCode = 500
                $err = [System.Text.Encoding]::UTF8.GetBytes($_.Exception.Message)
                $resp.ContentType = "text/plain"
                $resp.ContentLength64 = $err.Length
                $resp.OutputStream.Write($err, 0, $err.Length)
            }
        } else {
            $resp.StatusCode = 404
        }
        $resp.Close()
    }
} finally {
    $listener.Stop()
}
