:: ����λ��
echo "======================="
set current_path=%cd%
echo SET CURRENT_PATH=%current_path%

:: ����
cd C:\Users\YJY\Desktop\workspace\cnki\cnki\spiders
start scrapy crawl cnki_idata
:: �˳�
cd %current_path%
echo RETURN TO %current_path%
echo "======================="