# -*- coding: utf-8 -*-
from app import app
from flask import request
import codecs
import json
import re
from app import connection
from time import time
import datrie
import collections

def joker(word, name, booksNum, zone):
    word = word.split("*")
    inRequest = []
    resWords = []
    if word[0] != "" and word[1] != "":

        trie = datrie.Trie.load('../../Model/trieIndex/'+name+zone)
        revTrie = datrie.Trie.load('../../Model/trieIndex/r_' + name+zone)
        items = trie.keys(word[0])
        revItems = revTrie.keys(word[1][::-1])
        inRequest1 = {k:trie.get(k, 0) for k in set(items) & set(map(lambda x:x[::-1], revItems)) }

        for k,v in inRequest1.items():
            inRequest.append (transformIndexToMatrix(v,booksNum))
            resWords.append(k)

    elif word[0] != "":
        trie = datrie.Trie.load('../../Model/trieIndex/'+name+zone)
        items = trie.items(word[0])
        for k, v in items:
            inRequest.append(transformIndexToMatrix(v,booksNum))
            resWords.append(k)
    else:
        trie = datrie.Trie.load('../../Model/trieIndex/r_' + name+zone)
        items = trie.items(word[1][::-1])
        for k, v in items:
            inRequest.append(transformIndexToMatrix(v, booksNum))
            resWords.append(k)
    res = int('0',2)
    if len(inRequest)!=0:
        res = int(inRequest[0], 2)
    for i in range(1, len(inRequest) - 1):
        res |= int(inRequest[i], 2)
    return res, resWords


def replaceSpace(word):
  if word.startswith(" "):
    word = word[1::]
  if word.endswith(" "):
    word = word[:len(word)-1:]
  return word

def transformIndexToMatrix(ind, num):
  res = ""
  count = 0
  i = 0
  for i in range(num):
    if count>=len(ind):
      while len(res) != num:
        res += "0"
      break
    if i==ind[count]:
      count+=1
      res+="1"
    else:
      res+="0"
  return res

def fraseSearch(req, name, booksNum, zone):
    regexp = re.compile(r'/[0-9]+')

    f = codecs.open('../../Model/words2Index/' + name+zone, 'r', 'utf-8')
    dict = json.load(f)


    inRequest = []
    if req.count(" ")>1:
      if regexp.search(req):
          f = codecs.open('../../Model/coordIndex/' + name+zone, 'r', 'utf-8')
          coord = json.load(f)
          inRequest = set()
          words = req.split(" ")
          word1 = words[0]
          word2 = words[2]
          num = int(words[1].replace("/", ""))
          for k, v in coord[word1].items():
              for i in v:
                  if k in coord[word2]:
                    for j in coord[word2][k]:
                      if abs(j - i) <= num:
                          inRequest.add(int(k))

          inRequest = list(inRequest)
          inRequest.sort()
          inRequest = [transformIndexToMatrix(inRequest, booksNum)]
      else:
        req = req.split(" ")
        for i in range(len(req)-1):
          phrase = req[i] +" "+ req[i+1]
          inRequest.append(transformIndexToMatrix(dict[phrase],booksNum))
    else:
      if req in dict:
        inRequest.append(transformIndexToMatrix(dict[req],booksNum))
      else:
        inRequest.append('0')
    res = int(inRequest[0],2)
    for i in range(1, len(inRequest)-1):
       res&=int(inRequest[i], 2)
    return res

def boolSearch(name, req, booksNum, zone):
    # get request params

    # get matrix
    f = codecs.open( '../../Model/matrix/'+name+zone, 'r', 'utf-8')
    dict = json.load(f)

    req = req.lower()
    # get operations and words
    words = re.findall("[^&|\^]+", req)
    words = list(map(replaceSpace, words))
    operations = re.findall("[&|\^]", req)

    resWords = None
    # make not operation and transfer matrix into 0b
    for i in range(len(words)):
        words[i] = replaceSpace(words[i])
        if words[i].count(" ") > 0:
            words[i] = fraseSearch(words[i], name, booksNum, zone)
        elif words[i].startswith("!"):
            words[i] = words[i].replace("!", "")
            if words[i] in dict:
                words[i] = int(dict[words[i]].replace("1","2").replace("0","1").replace("2","0"), 2)
            else:
                words[i] = 0
        elif "*" in words[i]:
            words[i], resWords = joker(words[i], name, booksNum, zone)
        else:
            if words[i] in dict:
                words[i] = int(dict[words[i]], 2)
            else:
                words[i] = 0
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
    return res, resWords

def searchInAuthors():
    return ""

@app.route('/search',methods=['POST'])
def search():
    # get request params
    timeStart = time()
    name = request.form['name']
    req = request.form['request']
    booksNum = int(request.form['num'])

    res1, resWords1 = boolSearch(name,req,booksNum, "")
    print(res1)
    res2, resWords2 = boolSearch(name,req,booksNum, "Author")
    res3, resWords3 = boolSearch(name,req,booksNum, "Title")
    res4, resWords4 = boolSearch(name,req,booksNum, "Annotation")

    res = res1
    con = connection.getConnection()
    #
    cur = con.cursor()
    cur.execute("SELECT `ids` FROM `dictionary` where `name` = '"+name+"'")
    row = cur.fetchone()['ids'].split(" ")
    # change 0b result to names
    names = {}
    for i in range (len(res)):
        if res1[i]=="1" or res2[i]=='1' or res3[i]=='1' or res4[i]=='1':
            cur.execute("SELECT `name` FROM `books` where `id` = " + row[i])
            names[cur.fetchone()['name']] = float(res1[i])*0.1 + float(res2[i])*0.2 + float(res3[i])*0.35 + float(res4[i])*0.35
    names = collections.OrderedDict(sorted(names.items(), reverse=True, key=lambda kv: kv[1]))

    names["jokers"] = resWords1

    resTime = time()-timeStart
    return json.dumps({'success':True, 'names':names, 'time':resTime}), 200, {'ContentType':'application/json'}