:: ����λ��
echo "======================="
set current_path=%cd%
echo SET CURRENT_PATH=%current_path%

:: ����
cd G:\Code\XueKeW\XueKeW\spiders
start scrapy crawl zxxk
:: �˳�
cd %current_path%
echo RETURN TO %current_path%
echo "======================="