import pymysql
import  pymysql.cursors
from pymysql.cursors import DictCursor

def getConnection():
    con = pymysql.connect(host='193.111.0.203',
                          user='darklen',
                          password='qwerty',
                          db='lendro',
                          charset='utf8mb4',
                          cursorclass = DictCursor)
    return con

def selectAllFrom(tableName):
    con = getConnection()
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM `"+tableName+"`")
        rows = cur.fetchall()
        count = 1
        res = {}
        for row in rows:
            res[count] = row
            count += 1
        return res