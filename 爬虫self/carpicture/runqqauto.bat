:: ����λ��
echo "======================="
set current_path=%cd%
echo SET CURRENT_PATH=%current_path%

:: ����
cd C:\Users\YJY\Desktop\workspace\carpicture\carpicture\spiders
start scrapy crawl qqatuo
:: �˳�
cd %current_path%
echo RETURN TO %current_path%
echo "======================="