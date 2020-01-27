from app import app
from flask import request
import codecs
import json
import re
import connection
from time import time

@app.route('/boolSearch',methods=['POST'])
def boolSearch():
    # get request params
    timeStart = time()
    name = request.form['name']
    req = request.form['request']
    booksNum = int(request.form['num'])

    # get matrix
    f = codecs.open( '../../Model/matrix/'+name, 'r', 'utf-8')
    dict = json.load(f)

    req = req.lower()
    # get operations and words
    words = re.findall("[^&|\^ ]+", req)
    operations = re.findall("[&|\^]", req)

    # make not operation and transfer matrix into 0b
    for i in range(len(words)):
        if words[i].startswith("!"):
            words[i] = words[i].replace("!", "")
            words[i] = int(dict[words[i]].replace("1","2").replace("0","1").replace("2","0"), 2)
        else:
            words[i] = int(dict[words[i]], 2)

    res = words[0]

    # make all other operations
    for i in range(len(operations)):
        if operations[i]=="&":
            res&=words[i+1]
        if operations[i]=="|":
            res|=words[i+1]
        if operations[i]=="^":
            res^=words[i+1]

    # record final result
    res = bin(res).replace("0b", "")
    if len(res)!=booksNum:
        for i in range(booksNum-len(res)):
            res = "0"+res

    con = connection.getConnection()
    #
    cur = con.cursor()
    cur.execute("SELECT `ids` FROM `dictionary` where `name` = '"+name+"'")
    row = cur.fetchone()['ids'].split(" ")
    # change 0b result to names
    names = []
    for i in range (len(res)):
        if res[i]=="1":
            cur.execute("SELECT `name` FROM `books` where `id` = " + row[i])
            names.append(cur.fetchone()['name'])


    print (names)
    resTime = time()-timeStart
    return json.dumps({'success':True, 'names':names, 'time':resTime}), 200, {'ContentType':'application/json'}