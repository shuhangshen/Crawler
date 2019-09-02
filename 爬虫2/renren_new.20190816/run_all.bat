@echo off
echo "***********************"
echo "START BATCH WORKS"

:: 执行列表中的run.bat脚本批量启动爬虫
set INPUT=./batch_list.txt

for /f %%a in (%INPUT%) do (
echo ">>>>>>>>>>>>"
echo "START "%%a
%%a
)
:: 执行列表中的run.bat脚本批量启动爬虫

echo "BATCH WORKS SUCESS"
echo "***********************"

exit