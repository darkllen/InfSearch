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
import collections
import datrie

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

def getCoordIndex(FILEPATH, files, uniqueWords):
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

def createWordsList(FILEPATH, files):
    sizeOfFiles = 0
    allWordsNumber = 0
    uniqueWords = []
    uniqueWordsForEachFile = []

    for i in files:
        allText = getAllTextFromFb2(FILEPATH + i)
        sizeOfFiles += os.path.getsize(FILEPATH + i) / 1024
        splitedText = splitByTags(allText)
        words = getWordsList(splitedText)
        allWordsNumber += len(words)

        lists = getListUnique(words)

        uniqueWords += lists
        uniqueWordsForEachFile.append(lists)

    uniqueWords.sort()
    uniqueWords = getListUnique(uniqueWords)
    uniqueWordsNumber = len(uniqueWords)
    return uniqueWords, uniqueWordsForEachFile,  sizeOfFiles, uniqueWordsNumber, allWordsNumber

def createInvertIndexAndMatrix(uniqueWords, uniqueWordsForEachFile):
    indexesArray = [0]*len(uniqueWordsForEachFile)

    dictOfWords = {i: [] for i in uniqueWords}
    confMatrix = {i: "" for i in uniqueWords}

    for key, value in dictOfWords.items():
        for currList in range(0, len(uniqueWordsForEachFile)):
            if len(uniqueWordsForEachFile[currList]) > indexesArray[currList]:
                if uniqueWordsForEachFile[currList][indexesArray[currList]] == key:
                    indexesArray[currList] += 1
                    dictOfWords[key].append(currList)
                    confMatrix[key] += "1"
                else:
                    confMatrix[key] += "0"
            else:
                confMatrix[key] += "0"

    return dictOfWords, confMatrix

def create2wordsIndex(FILEPATH, files):
    size = 0
    allWordsNumber = 0
    listArray = []
    allFilesList = []
    indexesArray = []

    for i in files:
        indexesArray.append(0)
        allText = getAllTextFromFb2(FILEPATH + i)
        size += os.path.getsize(FILEPATH + i) / 1024
        text = splitByTags(allText)
        words = get2WordsList(text)
        allWordsNumber += len(words)

        lists = getListUnique(words)
        lists.sort()

        allFilesList += lists
        listArray.append(lists)

    allFilesList.sort()
    allFilesList = getListUnique(allFilesList)
    dictOfWords = {i: [] for i in allFilesList}

    for key, value in dictOfWords.items():
        for currList in range(0, len(listArray)):
            if len(listArray[currList]) > indexesArray[currList]:
                if listArray[currList][indexesArray[currList]] == key:
                    indexesArray[currList] += 1
                    dictOfWords[key].append(currList)
    return dictOfWords

def createPrefixTree(invertIndex):
    trie = datrie.Trie("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    reverseTrie = datrie.Trie("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    for k, v in invertIndex.items():
        trie[k] = v
        reverseTrie[k[::-1]] = v
    return trie, reverseTrie


def create3GramIndex(uniqueWords):
  index = {}
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

def createPermutationIndex(uniqueWords):
    permutationIndex = {}
    for i in uniqueWords:
        val = []

        for j in range(0,len(i)):
          val.append(i[j::]+"$"+i[:j:])
        val.append("$"+i)
        permutationIndex[i]=val
    return permutationIndex




def writeToDBAndToFile(list, dictPath, name, allWords, uniqueWords, collectionSize, timeToCreate, booksNum, ids, invertIndexes, invertIndexPath, confMatrix, matrixPath, words2Ind, words2IndPath
                       ,coordIndex, COORDINDEX, trie,reverseTrie, TRIEINDEX, gramIndex, GRAMINDEX, permutationIndex, PERMUTATIONINDEX):
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
    with codecs.open(words2IndPath + name, 'w', 'utf-8') as f:
        json.dump(words2Ind, f, ensure_ascii=False)
    with codecs.open(COORDINDEX + name, 'w', 'utf-8') as f:
        json.dump(coordIndex, f, ensure_ascii=False)
    with codecs.open(GRAMINDEX + name, 'w', 'utf-8') as f:
        json.dump(gramIndex, f, ensure_ascii=False)
    with codecs.open(PERMUTATIONINDEX + name, 'w', 'utf-8') as f:
        json.dump(permutationIndex, f, ensure_ascii=False)
    trie.save(TRIEINDEX + name)
    reverseTrie.save(TRIEINDEX +"r_"+ name)



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
    WORDS2INDPATH = '../../Model/words2Index/'
    COORDINDEX = '../../Model/coordIndex/'
    TRIEINDEX = '../../Model/trieIndex/'
    GRAMINDEX = '../../Model/gramIndex/'
    PERMUTATIONINDEX = '../../Model/permutationIndex/'

    # get all dicts and lists for record
    startTime = time()
    uniqueWords, uniqueWordsForEachFile,  sizeOfFiles, uniqueWordsNumber, allWordsNumber = createWordsList(FILEPATH, files)
    invertIndex, confMatrix = createInvertIndexAndMatrix(uniqueWords, uniqueWordsForEachFile)
    coordIndex = getCoordIndex(FILEPATH, files, uniqueWords)
    trie, reverseTrie = createPrefixTree(invertIndex)
    gramIndex = create3GramIndex(uniqueWords)
    permutationIndex = createPermutationIndex(uniqueWords)
    words2Ind = create2wordsIndex(FILEPATH, files)
    resTime = time()-startTime

    # record all information
    writeToDBAndToFile(uniqueWords, DICTIONARYPATH, name, allWordsNumber, uniqueWordsNumber, sizeOfFiles, resTime, len(files), ' '.join(ids),
                       invertIndex, INVERTINDEXPATH, confMatrix, MATRIXPATH, words2Ind, WORDS2INDPATH
                       ,coordIndex, COORDINDEX, trie, reverseTrie, TRIEINDEX, gramIndex, GRAMINDEX, permutationIndex, PERMUTATIONINDEX)

    return json.dumps({'success':True, 'name':name, 'size':sizeOfFiles, 'allWords':allWordsNumber, 'uniqueWords':uniqueWordsNumber,
                       'time':resTime, 'booksNum':len(files)}), 200, {'ContentType':'application/json'}
