# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: shentuxiangrong

import cx_Oracle
f1 = open(r'E:\省抓拍统计.txt', 'w', encoding='utf-8')
f2 = open(r'E:\市抓拍统计.txt', 'w', encoding='utf-8')
f3 = open(r'E:\区抓拍统计.txt', 'w', encoding='utf-8')
conn = cx_Oracle.connect('frsalg/hikfrs@10.65.214.97/orcl')
curs = conn.cursor()

#59937829
shengfenList = ['11', '12', '13', '14', '15', '21', '22', '23', '31', '32', '33', '34', '35', '36', '37', '41', '42',
                '43', '44', '45', '46', '50', '51', '52', '53', '54', '61', '62', '63', '64', '65']
cnt_sheng = 0
for shengfen in shengfenList:
    for j in range(1, 99):
        if j < 10:
            shi = '0'+str(j)
        else:
            shi = str(j)
        cnt_shi = 0
        for k in range(1, 99):
            if k < 10:
                qu = '0' + str(k)
            else:
                qu = str(k)
            sql = 'SELECT PERSON_ID,DB_ID FROM PERSON_TOTAL_TABLE WHERE ORIGIN_ID LIKE \'%s%s%s___________\' ' % (
                shengfen, shi, qu)
            # sql = 'SELECT ORIGIN_ID FROM PERSON_TOTAL_TABLE WHERE ROWNUM<=%d' % (123)
            rr = curs.execute(sql)
            row = curs.fetchall()
            cnt_qu = 0
            for per_db in row:
                if per_db[1] != None:
                    DB_IDList = list(per_db[1].strip(',').split(','))
                    for DB_ID in DB_IDList:
                        sql_exist = 'SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME=UPPER(\'SNAPIMG_%s\')' % (DB_ID)
                        r_exist = curs.execute(sql_exist)
                        row_exist = curs.fetchall()
                        if row_exist[0][0] == 1:
                            sql_snap = 'SELECT COUNT(PERSON_ID) FROM SNAPIMG_%s WHERE PERSON_ID=\'%s\'' % (
                                DB_ID, per_db[0])  # [(14,)]
                            rl = curs.execute(sql_snap)
                            row2 = curs.fetchall()
                            cnt_qu += row2[0][0]
            if cnt_qu != 0:
                f3.write('%s%s%s' % (shengfen, shi, qu) + ' ' + str(cnt_qu))
                print('%s%s%s' % (shengfen, shi, qu) + ' ' + str(cnt_qu))
            cnt_shi += cnt_qu
            cnt_qu = 0
        if cnt_shi != 0:
            f2.write('%s%s' % (shengfen, shi) + ' ' + str(cnt_shi))
            print('%s%s' % (shengfen, shi) + ' ' + str(cnt_shi))
        cnt_sheng += cnt_shi
        cnt_shi = 0
    if cnt_sheng != 0:
        f1.write('%s' % (shengfen) + ' ' + str(cnt_sheng))
        print('%s' % (shengfen) + ' ' + str(cnt_sheng))
    cnt_sheng = 0
            #for i in row:
                #if i[0] > 10:
                    #f.write(shengfen + shi + qu + ' ' + str(i[0]) + '\n')

curs.close()
conn.close()
f1.close()
f2.close()
f3.close()

'''
sql = 'SELECT PERSON_ID,DB_ID FROM PERSON_TOTAL_TABLE WHERE ORIGIN_ID LIKE \'%s%s%s___________\'' % ('11', '01', '10')
#sql = 'SELECT PERSON_ID,DB_ID FROM PERSON_TOTAL_TABLE WHERE PERSON_ID=\'2021\''
rr = curs.execute(sql)
row1 = curs.fetchall()
#print(row1)
'''
'''

for per_db in row1:
    if per_db[0] == 418595011:
        print(per_db[1] == None)
'''
'''
cnt = 0
for per_db in row1:
    if per_db[1] != None:
        DB_IDList = list(per_db[1].strip(',').split(','))
        for DB_ID in DB_IDList:
            sql_exist = 'SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME=UPPER(\'SNAPIMG_%s\')'% (DB_ID)
            r_exist = curs.execute(sql_exist)
            row_exist = curs.fetchall()
            if row_exist[0][0] == 1:
                sql_snap = 'SELECT COUNT(PERSON_ID) FROM SNAPIMG_%s WHERE PERSON_ID=\'%s\'' % (
                DB_ID, per_db[0])  # [(14,)]
                rl = curs.execute(sql_snap)
                row2 = curs.fetchall()
                cnt += row2[0][0]
print('%s%s%s' % ('11', '01', '10') + ' ' + str(cnt))
'''
'''
sql1= 'SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME=UPPER(\'SNAPIMG_162\')'
rl = curs.execute(sql1)
row2 = curs.fetchall()
print(row2)
'''
'''
DB_IDList = list(row[0][0].split(','))
print(DB_IDList)
'''



#[(2015, '45,88,91')](418595011, None)
#[(2021, '91')]




