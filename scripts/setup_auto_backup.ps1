# setup_auto_backup.ps1 — 设置 Windows 自动备份任务
# 以管理员身份运行: powershell -ExecutionPolicy Bypass .\scripts\setup_auto_backup.ps1

$taskName = "ReasonixAutoBackup"
$batPath = "D:\Reasonix\scripts\baidu_backup.bat"
$argument = "/c `"$batPath`""

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $argument
$trigger = New-ScheduledTaskTrigger -Daily -At 20:00

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Description "Reasonix workspace auto backup to Baidu Netdisk" -Force

Write-Output "✅ 自动备份任务已创建: 每天 20:00"
Write-Output "   执行: cmd.exe $argument"
Write-Output "   备份到: D:\BaiduSyncdisk\百度网盘同步空间\Reasonix_backup"
