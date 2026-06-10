# workspace/activate.ps1 — Eon-Taiji 五项目工作空间环境激活
#
# 用法:
#   .\workspace\activate.ps1
#
# 功能:
#   - 添加项目路径到 Python sys.path (等效 workspace.py)
#   - 设置工作空间根目录环境变量

Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Eon-Taiji 工作空间环境激活             ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$WorkspaceRoot = Split-Path -Parent $PSScriptRoot

# 验证工作区结构
$Required = @(
    "coordination.yaml",
    "VERSION.yaml",
    "workspace.py",
    "cognitive-search-engine",
    "fish-ecology-assistant",
    "porpoise-agent",
    "coilia-agent",
    "eon-core"
)

$Missing = @()
foreach ($Item in $Required) {
    $Path = Join-Path $WorkspaceRoot $Item
    if (-not (Test-Path $Path)) {
        $Missing += $Item
    }
}

if ($Missing.Count -gt 0) {
    Write-Host "⚠️  缺失项目: $($Missing -join ', ')" -ForegroundColor Yellow
    Write-Host "请确保在工作区根目录运行此脚本。"
    exit 1
}

# 设置环境变量
$env:EON_WORKSPACE_ROOT = $WorkspaceRoot
$env:EON_WORKSPACE_VERSION = "v8.0.0"

Write-Host "✅ 工作空间就绪!" -ForegroundColor Green
Write-Host "  根目录: $WorkspaceRoot"
Write-Host "  版本:   v8.0.0"
Write-Host "  项目:   7"
Write-Host ""
Write-Host "可用入口:"
Write-Host "  python workspace/launch_all.py      — 启动所有项目"
Write-Host "  python -c ""from workspace import search_species; print(search_species('鳤'))"""
Write-Host "  python workspace/__init__.py        — 包导入"
