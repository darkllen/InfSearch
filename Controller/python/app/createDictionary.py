# -*- coding: utf-8 -*-
from app import app
from flask import request
from contextlib import closing
import json
from lxml import etree
from time import time
import re
import string
import os
import connection
import json

# -*- codecs: utf-8 -*-
import codecs
import pymysql
from pymysql.cursors import DictCursor

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

def getListUnique(list):
  unique = []
  for i in range(len(list)-1):
    if list[i] != list[i+1]:
      unique.append(list[i])
  return unique

def createInvertIndexAndDictionaryAndMatrixFromFiles(FILEPATH, files):
  size = 0
  allWordsNumber = 0
  listArray = []
  allFilesList = []
  indexesArray = []

  start_time = time()
  for i in files:
    indexesArray.append(0)
    allText = getAllTextFromFb2(FILEPATH+i)
    size +=os.path.getsize(FILEPATH+i)/1024
    text = splitByTags(allText)
    words = getWordsList(text)
    allWordsNumber +=len(words)

    lists = getListUnique(words)
    lists.sort()

    allFilesList+=lists
    listArray.append(lists)

  allFilesList.sort()
  allFilesList = getListUnique(allFilesList)
  dictOfWords = {i: [] for i in allFilesList}
  confMatrix = {i: "" for i in allFilesList}


  for key, value in dictOfWords.items():
      for currList in range(0, len(listArray)):
          if len(listArray[currList]) > indexesArray[currList]:
            if listArray[currList][indexesArray[currList]] == key:
              indexesArray[currList]+=1
              dictOfWords[key].append(currList)
              confMatrix[key] +="1"
            else:
              confMatrix[key] += "0"
          else:
              confMatrix[key] += "0"
  return allFilesList, allWordsNumber, size, len(allFilesList), time()-start_time, dictOfWords, confMatrix



def writeToDBAndToFile(list, dictPath, name, allWords, uniqueWords, collectionSize, timeToCreate, booksNum, ids, invertIndexes, invertIndexPath, confMatrix, matrixPath):
    with codecs.open(dictPath + name, 'w', 'utf-8') as f:
        json.dump(list, f, ensure_ascii=False)
    con = connection.getConnection()
    with con:
        cur = con.cursor()
        query = "INSERT INTO `dictionary`(`name`, `allWords`, `uniqueWords`, `collectionSize`, `timeToCreate`, `booksNum`, `ids`) VALUES ('"+name+"',"+str(allWords)+","+str(uniqueWords)+","+str(collectionSize)+","+str(timeToCreate)+","+str(booksNum)+",'"+ids+"')"
        cur.execute(query)
        con.commit()
    with codecs.open(invertIndexPath + name, 'w', 'utf-8') as f:
        json.dump(invertIndexes, f, ensure_ascii=False)
    with codecs.open(matrixPath + name, 'w', 'utf-8') as f:
        json.dump(confMatrix, f, ensure_ascii=False)



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
    print(row)
    if row is not None:
        return "Dict is already exist"
    # get books
    for i in ids:
        with con:
            cur.execute("SELECT * FROM `books`  where id="+i)
            row = cur.fetchone()
            files.append(row['name'])


    print(files)
    FILEPATH = '../../Model/books/'
    DICTIONARYPATH = '../../Model/dictionaries/'
    INVERTINDEXPATH = '../../Model/invertIndex/'
    MATRIXPATH = '../../Model/matrix/'

    # get all dicts and lists for record
    list, allWords, size, uniqueWords, time, invertIndex, confMatrix = createInvertIndexAndDictionaryAndMatrixFromFiles(FILEPATH, files)

    # record all information
    writeToDBAndToFile(list, DICTIONARYPATH, name, allWords, uniqueWords, size, time, len(files), ' '.join(ids), invertIndex, INVERTINDEXPATH, confMatrix, MATRIXPATH)

    return json.dumps({'success':True, 'name':name, 'size':size, 'allWords':allWords, 'uniqueWords':uniqueWords, 'time':time, 'booksNum':len(files)}), 200, {'ContentType':'application/json'}
