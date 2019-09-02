:: 保存位置
echo "======================="
set current_path=%cd%
echo SET CURRENT_PATH=%current_path%

:: 任务
taskkill /F /IM redis-server.exe
@ping 127.0.0.1 -n 3 >nul
cd C:\Program Files\Redis
start ./redis-server.exe
echo restart redis server ready
@ping 127.0.0.1 -n 20 >nul
echo config set protected-mode no | redis-cli
echo ping | redis-cli
start ./redis-cli.exe

:: 退出
cd %current_path%
echo RETURN TO %current_path%
echo "======================="