@echo off
set HOME=%TEMP%
if not exist "%HOME%\.ssh" mkdir "%HOME%\.ssh"
set GIT_SSH_COMMAND=ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile="%HOME%\.ssh\known_hosts"
git push origin master
