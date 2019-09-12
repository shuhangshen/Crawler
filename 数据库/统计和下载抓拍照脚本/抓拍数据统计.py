# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: shentuxiangrong

import cx_Oracle
f1 = open(r'E:\省人数统计.txt', 'w', encoding='utf-8')
f2 = open(r'E:\市人数统计.txt', 'w', encoding='utf-8')
f3 = open(r'E:\区人数统计.txt', 'w', encoding='utf-8')
conn = cx_Oracle.connect('frsalg/hikfrs@10.65.214.97/orcl')
curs = conn.cursor()


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
            sql = 'SELECT COUNT(*) FROM PERSON_TOTAL_TABLE WHERE ORIGIN_ID LIKE \'%s%s%s___________\' ' % (
                shengfen, shi, qu)
            # sql = 'SELECT ORIGIN_ID FROM PERSON_TOTAL_TABLE WHERE ROWNUM<=%d' % (123)
            rr = curs.execute(sql)
            row = curs.fetchall()
            cnt_qu = row[0][0]
            if cnt_qu != 0:
                f3.write('%s%s%s' % (shengfen, shi, qu) + ' ' + str(cnt_qu) + '\n')
                print('%s%s%s' % (shengfen, shi, qu) + ' ' + str(cnt_qu))
            cnt_shi += cnt_qu
            cnt_qu = 0
        if cnt_shi != 0:
            f2.write('%s%s' % (shengfen, shi) + ' ' + str(cnt_shi) + '\n')
            print('%s%s' % (shengfen, shi) + ' ' + str(cnt_shi))
        cnt_sheng += cnt_shi
        cnt_shi = 0
    if cnt_sheng != 0:
        f1.write('%s' % (shengfen) + ' ' + str(cnt_sheng) + '\n')
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
