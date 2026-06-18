# setup_auto_backup.ps1
# 设置 Windows 任务计划程序, 每天自动备份到百度网盘
# 以管理员身份运行: powershell -ExecutionPolicy Bypass .\scripts\setup_auto_backup.ps1

$taskName = "Reasonix百度网盘自动备份"
$scriptPath = "D:\Reasonix\scripts\baidu_backup.bat"

# 创建每天 20:00 执行的任务
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Daily -At 20:00
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

try {
    Register-ScheduledTask -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Description "Reasonix workspace backup to Baidu Netdisk" `
        -Force
    Write-Output "✅ 自动备份任务已创建: 每天 20:00"
    Write-Output "   备份到: D:\BaiduSyncdisk\百度网盘同步空间\Reasonix_backup"
} catch {
    Write-Output "❌ 创建失败: $_"
    Write-Output "请以管理员身份运行此脚本"
}
