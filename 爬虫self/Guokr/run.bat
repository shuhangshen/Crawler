:: ����λ��
echo "======================="
set current_path=%cd%
echo SET CURRENT_PATH=%current_path%

:: ����
cd C:\Users\YJY\Desktop\workspace\Guokr\Guokr\spiders
start scrapy crawl guokr
:: �˳�
cd %current_path%
echo RETURN TO %current_path%
echo "======================="