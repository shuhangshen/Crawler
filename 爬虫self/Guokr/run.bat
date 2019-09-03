:: 保存位置
echo "======================="
set current_path=%cd%
echo SET CURRENT_PATH=%current_path%

:: 任务
cd C:\Users\YJY\Desktop\workspace\Guokr\Guokr\spiders
start scrapy crawl guokr
:: 退出
cd %current_path%
echo RETURN TO %current_path%
echo "======================="