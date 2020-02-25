# -*- coding: utf-8 -*-
from app import app
from flask import request
from flask import abort

from contextlib import closing
import json
from lxml import etree
from time import time
import re
import string
import os
import connection
import json
import collections
import datrie

import csv

# -*- codecs: utf-8 -*-
import codecs
import pymysql
from pymysql.cursors import DictCursor
from memory_profiler import memory_usage


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


def getAllTextFromFb2(path):
  node = etree.parse(path)
  return str(etree.tostring(node.getroot().getchildren()[1], encoding='utf8', method='xml'),'utf-8')

def splitByTags(string):
  pattern = re.compile(r'<[^>]+>')
  return re.split(pattern, string)

def getWordsList(text):
    list = []
    for line in text:
        words = re.findall("[a-zA-Zа-яА-Я0-9]+[^ ]*[a-zA-Zа-яА-Я0-9]+|[a-zA-Zа-яА-Я0-9]+", line)
        words = map(lambda x: x.lower(), words)
        list += words
    list.sort()
    return list

def getWordsListWithIndex(text, num, startBook):
    list = {}
    for line in text:
        words = re.findall("[a-zA-Zа-яА-Я0-9]+[^ ]*[a-zA-Zа-яА-Я0-9]+|[a-zA-Zа-яА-Я0-9]+", line)
        words = map(lambda x: x.lower(), words)
        for w in words:
            if w not in list:
                list[w] = [num+startBook]
    return list

def get2WordsListWithIndex(text, num):
    res = {}
    line = " ".join(text)

    words = re.findall("[a-zA-Zа-яА-Я0-9]+[^ ]*[a-zA-Zа-яА-Я0-9]+|[a-zA-Zа-яА-Я0-9]+", line)
    words = list(map(lambda x: x.lower(), words))
    for w in range(len(words)-1):
        if words[w]+" "+words[w+1] not in res:
            res[words[w]+" "+words[w+1]] = [num]
    return res

def addLists(b, c):
  for k, v in c.items():
    if k not in b:
      b[k] = v
    else:
      b[k]+=v

def getWordsWithCoords(text, fileNum):
    list = {}
    wordCounter = 1
    for line in text:
        words = re.findall("[a-zA-Zа-яА-Я0-9]+[^ ]*[a-zA-Zа-яА-Я0-9]+|[a-zA-Zа-яА-Я0-9]+", line)
        words = map(lambda x: x.lower(), words)
        for w in words:
            if w in list:
              list[w][fileNum].append(wordCounter)
            else:
              list[w] = {fileNum:[wordCounter]}
            wordCounter+=1
    return list

def mergeDicts(dicts, uniqueWords):
  dicts = [collections.OrderedDict(sorted(i.items())) for i in dicts]
  merged = {}
  for i in uniqueWords:
    for j in dicts:
      if i in j:
        if i in merged:
          merged[i].update(j[i])
        else:
          merged[i] = j[i]

  return merged

def getCoordIndex(FILEPATH, DICTIONARYPATH, name,  files):
    jsonFile = codecs.open(DICTIONARYPATH + name, 'r', 'utf-8')
    jsonStr = jsonFile.read()
    uniqueWords = json.loads(jsonStr)

    wordsWithCoordsForEachFile = []
    for i in range(len(files)):
        allText = getAllTextFromFb2(FILEPATH + files[i])
        splitedText = splitByTags(allText)
        wordsWithCoordsForEachFile.append( getWordsWithCoords(splitedText, i))
    coordIndex = mergeDicts(wordsWithCoordsForEachFile, uniqueWords)
    return coordIndex

def get2WordsList(text):
    list = []
    finalList = []
    for line in text:
        words = re.findall("[a-zA-Zа-яА-Я0-9]+[^ ]*[a-zA-Zа-яА-Я0-9]+|[a-zA-Zа-яА-Я0-9]+", line)
        words = map(lambda x: x.lower(), words)
        list += words
    for i in range(len(list)-1):
        finalList.append(list[i]+ " " +list[i+1])
    finalList.sort()
    return finalList

def getListUnique(list):
  unique = []
  for i in range(len(list)-1):
    if list[i] != list[i+1]:
      unique.append(list[i])
  return unique

def createWordsListAndInfo(FILEPATH, files):
    sizeOfFiles = 0
    allWordsNumber = 0
    uniqueWords = []

    for i in files:
        allText = getAllTextFromFb2(FILEPATH + i)
        sizeOfFiles += os.path.getsize(FILEPATH + i) / 1024
        splitedText = splitByTags(allText)
        words = getWordsList(splitedText)
        allWordsNumber += len(words)

        lists = getListUnique(words)

        uniqueWords += lists

    uniqueWords.sort()
    uniqueWords = getListUnique(uniqueWords)
    uniqueWordsNumber = len(uniqueWords)
    return uniqueWords, sizeOfFiles, uniqueWordsNumber, allWordsNumber

def createWordsList(FILEPATH, files):
    allText = ""
    for i in files:
        allText += getAllTextFromFb2(FILEPATH + i)

    splitedText = splitByTags(allText)
    words = getWordsList(splitedText)
    uniqueWords = getListUnique(words)

    return uniqueWords

def createInvertIndex(FILEPATH, files, startBook):
    invertIndex = {}
    for i in range(len(files)):
        allText = getAllTextFromFb2(FILEPATH + files[i])
        splitedText = splitByTags(allText)
        words = getWordsListWithIndex(splitedText, i, startBook)
        addLists(invertIndex, words)
    invertIndex = collections.OrderedDict(sorted(invertIndex.items()))
    return invertIndex
def createMatrixFromIndex(index, num):
    matrix = {k: transformIndexToMatrix(v, num) for k, v in index.items()}
    matrix = collections.OrderedDict(sorted(matrix.items()))
    return matrix

def create2wordsIndex(FILEPATH, files):
    words2Index = {}
    for i in range(len(files)):
        allText = getAllTextFromFb2(FILEPATH + files[i])
        splitedText = splitByTags(allText)
        words = get2WordsListWithIndex(splitedText, i)
        addLists(words2Index, words)
    words2Index = collections.OrderedDict(sorted(words2Index.items()))
    return words2Index

def createPrefixTree(INVPATH, name):

    jsonFile = codecs.open(INVPATH + name, 'r', 'utf-8')
    jsonStr = jsonFile.read()
    invertIndex = json.loads(jsonStr)

    trie = datrie.Trie("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    reverseTrie = datrie.Trie("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    for k, v in invertIndex.items():
        trie[k] = v
        reverseTrie[k[::-1]] = v
    return trie, reverseTrie


def create3GramIndex(DICTIONARYPATH, name):
  index = {}

  jsonFile = codecs.open(DICTIONARYPATH + name, 'r', 'utf-8')
  jsonStr = jsonFile.read()
  uniqueWords = json.loads(jsonStr)

  for word in uniqueWords:
    t = None
    if len(word)!=1:
      t = [word[i:i+3] for i in range(0, len(word)-1)]
      t[-1]+="$"
      t.insert(0, "$"+t[0][0:2])
    else:
      t = ["$"+word[0]+"$"]
    for i in t:
      if i in index:
        index[i].append(word)
      else:
        index[i] = [word]
  return index

def createPermutationIndex(DICTIONARYPATH, name):
    permutationIndex = {}

    jsonFile = codecs.open(DICTIONARYPATH + name, 'r', 'utf-8')
    jsonStr = jsonFile.read()
    uniqueWords = json.loads(jsonStr)

    for i in uniqueWords:
        val = []

        for j in range(0,len(i)):
          val.append(i[j::]+"$"+i[:j:])
        val.append("$"+i)
        permutationIndex[i]=val
    return permutationIndex


def writeToDBAndToFile(name, allWords, uniqueWords, collectionSize, timeToCreate, booksNum, ids):
    con = connection.getConnection()
    with con:
        cur = con.cursor()
        query = "INSERT INTO `dictionary`(`name`, `allWords`, `uniqueWords`, `collectionSize`, `timeToCreate`, `booksNum`, `ids`) VALUES ('"+name+"',"+str(allWords)+","+str(uniqueWords)+","+str(collectionSize)+","+str(timeToCreate)+","+str(booksNum)+",'"+ids+"')"
        cur.execute(query)
        con.commit()

@app.route('/crDict',methods=['POST'])
def crDict():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))
    FILEPATH = '../../Model/books/'
    DICTIONARYPATH = '../../Model/dictionaries/'


    startTime = time()
    uniqueWords= createWordsList(FILEPATH,files)
    resTime = time() - startTime

    query = "UPDATE `dictionary` SET `dict`=1 WHERE `name`='"+name+"'"
    con = connection.getConnection()
    with con:
        cur = con.cursor()
        cur.execute(query)
        con.commit()


    with codecs.open(DICTIONARYPATH + name, 'w', 'utf-8') as f:
        json.dump(uniqueWords, f, ensure_ascii=False)

    print( memory_usage())
    return {'success':True,'time':resTime}

@app.route('/crInvertIndex',methods=['POST'])
def crInvertIndex():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))

    FILEPATH = '../../Model/books/'
    INVERTINDEXPATH = '../../Model/invertIndex/'
    MATRIXPATH = '../../Model/matrix/'


    startTime = time()
    invertIndex = createInvertIndex(FILEPATH, files, 0)
    confMatrix = createMatrixFromIndex(invertIndex, len(files))
    resTime = time() - startTime

    query = "UPDATE `dictionary` SET `invertIndex`=1 WHERE `name`='"+name+"'"
    con = connection.getConnection()
    with con:
        cur = con.cursor()
        cur.execute(query)
        con.commit()

    with codecs.open(INVERTINDEXPATH + name, 'w', 'utf-8') as f:
        json.dump(invertIndex, f, ensure_ascii=False)
    with codecs.open(MATRIXPATH + name, 'w', 'utf-8') as f:
        json.dump(confMatrix, f, ensure_ascii=False)
    return {'success':True,'time':resTime}

@app.route('/crInvertIndexByParts',methods=['POST'])
def crInvertIndexByParts():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))

    SIZE_LIMIT = 10000000


    FILEPATH = '../../Model/books/'
    INVERTINDEXBYPARTSPATH = '../../Model/invertIndexByParts/'

    count = 0

    startTime = time()

    step = 0
    while count<len(files):
        sizeCur = 0
        filesCur = []
        step+=1
        startBook = count
        while sizeCur<SIZE_LIMIT and count<len(files):
            sizeCur+=os.path.getsize(FILEPATH + files[count])
            filesCur.append(files[count])
            count+=1
        invertIndex = createInvertIndex(FILEPATH, filesCur, startBook)

        with codecs.open(INVERTINDEXBYPARTSPATH + name+"_"+str(step), 'w', 'utf-8') as out_file:
            s = ""
            for k,v in invertIndex.items():
                s += str(k) + ":" + str(v) + "\n"
            out_file.write(s)


    output = codecs.open(INVERTINDEXBYPARTSPATH+name, 'w', 'utf-8')
    output.write("{")
    readers = [codecs.open(INVERTINDEXBYPARTSPATH+name +"_"+ str(i + 1), 'r', 'utf-8') for i in range(step)]
    lines = [i.readline().replace("\n", "") for i in readers]

    while  len(lines)!=0:
        currWord = sorted(lines)[0].split(":")[0]
        arr = []
        for i in range(len(lines)):
            if lines[i].split(":")[0] == currWord:
                arr += json.loads(lines[i].split(":")[-1])
                lines[i] = readers[i].readline().replace("\n", "")
        arr.sort()
        output.write('"' + currWord + '": ' + str(arr))
        if "" in lines:
            lines.remove("")
        if  len(lines)!=0:
            output.write(", ")
    output.write("}")
    output.close()

    for i in range(step):
        readers[i].close()
        os.remove(INVERTINDEXBYPARTSPATH+name +"_"+ str(i + 1))
    resTime = time() - startTime

    query = "UPDATE `dictionary` SET `invertIndexByParts`=1 WHERE `name`='"+name+"'"
    con = connection.getConnection()
    with con:
        cur = con.cursor()
        cur.execute(query)
        con.commit()


    return {'success':True,'time':resTime}


@app.route('/cr2WordIndex',methods=['POST'])
def cr2WordIndex():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))

    FILEPATH = '../../Model/books/'
    WORDS2INDPATH = '../../Model/words2Index/'

    startTime = time()
    words2Ind = create2wordsIndex(FILEPATH, files)
    resTime = time() - startTime

    query = "UPDATE `dictionary` SET `2WordsIndex`=1 WHERE `name`='"+name+"'"
    con = connection.getConnection()
    with con:
        cur = con.cursor()
        cur.execute(query)
        con.commit()

    with codecs.open(WORDS2INDPATH + name, 'w', 'utf-8') as f:
        json.dump(words2Ind, f, ensure_ascii=False)
    return {'success':True,'time':resTime}

@app.route('/crCoordIndex',methods=['POST'])
def crCoordIndex():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))

    FILEPATH = '../../Model/books/'
    COORDINDEX = '../../Model/coordIndex/'
    DICTIONARYPATH = '../../Model/dictionaries/'
    try:
        startTime = time()
        coordIndex = getCoordIndex(FILEPATH,DICTIONARYPATH,name, files)
        resTime = time() - startTime

        query = "UPDATE `dictionary` SET `coordIndex`=1 WHERE `name`='"+name+"'"
        con = connection.getConnection()
        with con:
            cur = con.cursor()
            cur.execute(query)
            con.commit()

        with codecs.open(COORDINDEX + name, 'w', 'utf-8') as f:
            json.dump(coordIndex, f, ensure_ascii=False)
        return {'success':True,'time':resTime}
    except:
        abort(500)

@app.route('/crGramIndex',methods=['POST'])
def crGramIndex():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))

    GRAMINDEX = '../../Model/gramIndex/'
    DICTIONARYPATH = '../../Model/dictionaries/'
    try:
        startTime = time()
        gramIndex = create3GramIndex(DICTIONARYPATH, name)
        resTime = time() - startTime

        query = "UPDATE `dictionary` SET `gramIndex`=1 WHERE `name`='"+name+"'"
        con = connection.getConnection()
        with con:
            cur = con.cursor()
            cur.execute(query)
            con.commit()

        with codecs.open(GRAMINDEX + name, 'w', 'utf-8') as f:
            json.dump(gramIndex, f, ensure_ascii=False)
        return {'success':True,'time':resTime}
    except:
        abort(500)

@app.route('/crPermutationIndex',methods=['POST'])
def crPermutationIndex():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))

    PERMUTATIONINDEX = '../../Model/permutationIndex/'
    DICTIONARYPATH = '../../Model/dictionaries/'
    try:
        startTime = time()
        permutationIndex = createPermutationIndex(DICTIONARYPATH, name)
        resTime = time() - startTime

        query = "UPDATE `dictionary` SET `permutationIndex`=1 WHERE `name`='"+name+"'"
        con = connection.getConnection()
        with con:
            cur = con.cursor()
            cur.execute(query)
            con.commit()

        with codecs.open(PERMUTATIONINDEX + name, 'w', 'utf-8') as f:
            json.dump(permutationIndex, f, ensure_ascii=False)
        return {'success':True,'time':resTime}
    except:
        abort(500)

@app.route('/crTrieIndex',methods=['POST'])
def crTrieIndex():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))

    TRIEINDEX = '../../Model/trieIndex/'
    INVERTINDEXPATH = '../../Model/invertIndex/'


    try:
        startTime = time()
        trieIndex, reverseTrieIndex = createPrefixTree(INVERTINDEXPATH, name)
        resTime = time() - startTime

        query = "UPDATE `dictionary` SET `trieIndex`=1 WHERE `name`='" + name + "'"
        con = connection.getConnection()
        with con:
            cur = con.cursor()
            cur.execute(query)
            con.commit()

        trieIndex.save(TRIEINDEX + name)
        reverseTrieIndex.save(TRIEINDEX + "r_" + name)
        return {'success': True, 'time': resTime}
    except:
        abort(500)


@app.route('/createDictionary',methods=['POST'])
def createDictionary():
    # get params
    name = request.form['name']
    ids = request.form.getlist('id[]')
    con = connection.getConnection()
    files = []

    # check if dictionary with this name is already exist
    cur = con.cursor()
    cur.execute("Select `name` from `dictionary` where `name`='"+name+"'")
    row = cur.fetchone()
    if row is not None:
        return "Dict is already exist"
    # get books
    for i in ids:
        with con:
            cur.execute("SELECT * FROM `books`  where id="+i)
            row = cur.fetchone()
            files.append(row['name'])

    FILEPATH = '../../Model/books/'


    # get all dicts and lists for record
    startTime = time()
    uniqueWords,  sizeOfFiles, uniqueWordsNumber, allWordsNumber = createWordsListAndInfo(FILEPATH, files)
    resTime = time()-startTime

    # record all information
    writeToDBAndToFile(name, allWordsNumber, uniqueWordsNumber, sizeOfFiles, resTime, len(files), ' '.join(ids))

    return json.dumps({'success':True, 'name':name, 'size':sizeOfFiles, 'allWords':allWordsNumber, 'uniqueWords':uniqueWordsNumber,
                       'time':resTime, 'booksNum':len(files)}), 200, {'ContentType':'application/json'}
