:: 保存位置
echo "======================="
set current_path=%cd%
echo SET CURRENT_PATH=%current_path%

:: 任务
cd C:\Users\YJY\Desktop\workspace\carpicture\carpicture\spiders
start scrapy crawl sinaauto
:: 退出
cd %current_path%
echo RETURN TO %current_path%
echo "======================="