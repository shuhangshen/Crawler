# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: shentuxiangrong

import cx_Oracle

f1 = open(r'E:\民族url.txt', 'w', encoding='utf-8')
conn = cx_Oracle.connect('frsalg/hikfrs@10.108.81.113/orcl')
curs = conn.cursor()

minzuDic = {'苗族': '430529', '蒙古族': '622124', '壮族': '450122', '土家族': '500240', '维吾尔族': '650102',
             '彝族': '511133', '回族': '620525', '布依族': '522701', '侗族': '431227', '满族': '130321',
             '朝鲜族': '220623', '哈尼族': '532723', '藏族': '533421'}


for minzu, daima in minzuDic.items():
    sql = 'SELECT PERSON_ID,DB_ID,PERSON_MD5 FROM PERSON_TOTAL_TABLE WHERE ORIGIN_ID LIKE \'%s___________\'' % daima
    rr = curs.execute(sql)
    row = curs.fetchall()
    cnt_ren = 0
    cnt_zhang = 0
    dlsuccess = 0
    for per_db in row:
        dlsuccess = 0
        cnt_zhang = 0
        if cnt_ren > 999:
            break
        if per_db[1] != None:
            DB_IDList = list(per_db[1].strip(',').split(','))
            for DB_ID in DB_IDList:
                sql_exist = 'SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME=UPPER(\'SNAPIMG_%s\')' % DB_ID
                r_exist = curs.execute(sql_exist)
                row_exist = curs.fetchall()
                if row_exist[0][0] == 1:
                    sql_snap = 'SELECT ORIGIN_IMAGE FROM SNAPIMG_%s WHERE PERSON_ID=\'%s\'' % (
                        DB_ID, per_db[0])
                    rl = curs.execute(sql_snap)
                    row2 = curs.fetchall()
                    for item in row2:
                        f1.write('%s %s\\%s %s_%s_%d.jpg\n' % (item[0], minzu, per_db[2], minzu, per_db[2], cnt_zhang+1))
                        #print('%s %s\\md5 %s_%d_%d.jpg\n' % (item[0], minzu, minzu, cnt_ren+1, cnt_zhang+1))
                        cnt_zhang += 1
                        if not cnt_zhang < 50:
                            dlsuccess = 1
                            cnt_zhang = 0
                            break
                if dlsuccess == 1:
                    cnt_ren += 1
                    break
            if dlsuccess == 0:
                cnt_ren += 1

    print('%s处理完啦,一共%d人' % (minzu, cnt_ren))



curs.close()
conn.close()
f1.close()











