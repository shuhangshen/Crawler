:: ����λ��
echo "======================="
set current_path=%cd%
echo SET CURRENT_PATH=%current_path%

:: ����
cd C:\Users\YJY\Desktop\workspace\Jianshu\Jianshu\spiders
start scrapy crawl jianshu1
:: �˳�
cd %current_path%
echo RETURN TO %current_path%
echo "======================="