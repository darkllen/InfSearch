# -*- coding: utf-8 -*-
from app import app
from flask import request
from flask import abort
from app import connection

from contextlib import closing
import json
import codecs
from time import time

import string
import os

import collections
import datrie

import csv

# -*- codecs: utf-8 -*-

import pymysql
from pymysql.cursors import DictCursor
from memory_profiler import memory_usage

from parse import helpParse
from creation import createInvertIndex
from creation import create2WordsIndex
from creation import createCoordIndex
from creation import createGramIndex
from creation import createPermutationIndex
from creation import createTrieIndex
from creation import createInvertIndexByParts
from creation import createDict
from compression import dictionary
from compression import invertIndexCompression



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
    uniqueWords= createDict.createWordsList(FILEPATH,files)
    resTime = time() - startTime

    query = "UPDATE `dictionary` SET `dict`=1 WHERE `name`='"+name+"'"
    con = connection.getConnection()
    with con:
        cur = con.cursor()
        cur.execute(query)
        con.commit()



    with codecs.open(DICTIONARYPATH + name, 'w', 'utf-8') as f:
        json.dump(uniqueWords, f, ensure_ascii=False)

    return {'success':True,'time':resTime}

@app.route('/crDictCompressed',methods=['POST'])
def crDictCompressed():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))
    FILEPATH = '../../Model/books/'
    DICTIONARYPATH = '../../Model/dictionariesCompressed/'


    startTime = time()
    uniqueWords= createDict.createWordsList(FILEPATH,files)
    dictionary.encode(uniqueWords, DICTIONARYPATH + name)
    resTime = time() - startTime

    query = "UPDATE `dictionary` SET `dictCompressed`=1 WHERE `name`='"+name+"'"
    con = connection.getConnection()
    with con:
        cur = con.cursor()
        cur.execute(query)
        con.commit()
    return {'success':True,'time':resTime}

@app.route('/crInvertIndexCompressed',methods=['POST'])
def crInvertIndexCompressed():
    name = request.form['name']
    files = request.form.getlist('files[]')
    files = list(filter(lambda n: n != "", files))
    FILEPATH = '../../Model/books/'
    DICTIONARYPATH = '../../Model/invertIndexCompressed/'


    startTime = time()
    invertIndex = createInvertIndex.createInvertIndex(FILEPATH, files, 0)
    encoded = invertIndexCompression.encodeIndex(invertIndex)
    invertIndexCompression.recordCompressedIndex(encoded, DICTIONARYPATH+name)
    resTime = time() - startTime

    query = "UPDATE `dictionary` SET `invertIndexCompressed`=1 WHERE `name`='"+name+"'"
    con = connection.getConnection()
    with con:
        cur = con.cursor()
        cur.execute(query)
        con.commit()
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
    invertIndex = createInvertIndex.createInvertIndex(FILEPATH, files, 0)
    confMatrix = createInvertIndex.createMatrixFromIndex(invertIndex, len(files))
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
        invertIndex = createInvertIndex.createInvertIndex(FILEPATH, filesCur, startBook)

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
    words2Ind = create2WordsIndex.create2wordsIndex(FILEPATH, files)
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
        coordIndex = createCoordIndex.getCoordIndex(FILEPATH,DICTIONARYPATH,name, files)
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
        gramIndex = createGramIndex.create3GramIndex(DICTIONARYPATH, name)
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
        permutationIndex = createPermutationIndex.createPermutationIndex(DICTIONARYPATH, name)
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
        trieIndex, reverseTrieIndex = createTrieIndex.createPrefixTree(INVERTINDEXPATH, name)
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
    uniqueWords,  sizeOfFiles, uniqueWordsNumber, allWordsNumber = createDict.createWordsListAndInfo(FILEPATH, files)

    DICTIONARYPATH = '../../Model/dictionaries/'
    WORDS2INDPATH = '../../Model/words2Index/'
    COORDINDEX = '../../Model/coordIndex/'
    TRIEINDEX = '../../Model/trieIndex/'
    INVERTINDEXPATH = '../../Model/invertIndex/'
    MATRIXPATH = '../../Model/matrix/'

    #authors
    dictAuthors = createDict.createAuthorsList(FILEPATH, files)
    with codecs.open(DICTIONARYPATH + name + "Author", 'w', 'utf-8') as f:
        json.dump(dictAuthors, f, ensure_ascii=False)
    invIndexAuthors = createInvertIndex.createInvertIndexAuthors(FILEPATH, files)
    with codecs.open(INVERTINDEXPATH + name + "Author", 'w', 'utf-8') as f:
        json.dump(invIndexAuthors, f, ensure_ascii=False)
    matrixAuthors = createInvertIndex.createMatrixFromIndex(invIndexAuthors, len(files))
    with codecs.open(MATRIXPATH + name + "Author", 'w', 'utf-8') as f:
        json.dump(matrixAuthors, f, ensure_ascii=False)
    coordIndAuthors = createCoordIndex.getCoordIndexAuthors(FILEPATH, DICTIONARYPATH, name+"Author",  files)
    with codecs.open(COORDINDEX + name + "Author", 'w', 'utf-8') as f:
        json.dump(coordIndAuthors, f, ensure_ascii=False)
    Words2IndAuthors = create2WordsIndex.create2wordsIndexAuthors(FILEPATH, files)
    with codecs.open(WORDS2INDPATH + name + "Author", 'w', 'utf-8') as f:
        json.dump(Words2IndAuthors, f, ensure_ascii=False)
    trieAuthors, revTrieAuthors = createTrieIndex.createPrefixTree(INVERTINDEXPATH, name+"Author")
    trieAuthors.save(TRIEINDEX + name+ "Author")
    revTrieAuthors.save(TRIEINDEX + "r_" + name+ "Author")
    # title
    dictTitles = createDict.createTitleList(FILEPATH, files)
    with codecs.open(DICTIONARYPATH + name + "Title", 'w', 'utf-8') as f:
        json.dump(dictTitles, f, ensure_ascii=False)
    invIndexTitles = createInvertIndex.createInvertIndexTitles(FILEPATH, files)
    with codecs.open(INVERTINDEXPATH + name + "Title", 'w', 'utf-8') as f:
        json.dump(invIndexTitles, f, ensure_ascii=False)
    matrixTitles = createInvertIndex.createMatrixFromIndex(invIndexTitles, len(files))
    with codecs.open(MATRIXPATH + name + "Title", 'w', 'utf-8') as f:
        json.dump(matrixTitles, f, ensure_ascii=False)
    coordIndTitles = createCoordIndex.getCoordIndexTitles(FILEPATH, DICTIONARYPATH, name+"Title", files)
    with codecs.open(COORDINDEX + name + "Title", 'w', 'utf-8') as f:
        json.dump(coordIndTitles, f, ensure_ascii=False)
    Words2IndTitles = create2WordsIndex.create2wordsIndexTitles(FILEPATH, files)
    with codecs.open(WORDS2INDPATH + name + "Title", 'w', 'utf-8') as f:
        json.dump(Words2IndTitles, f, ensure_ascii=False)
    trieTitles, revTrieTitles = createTrieIndex.createPrefixTree(INVERTINDEXPATH, name+"Title")
    trieTitles.save(TRIEINDEX + name + "Title")
    revTrieTitles.save(TRIEINDEX + "r_" + name + "Title")
    #anotation
    dictAnnotation = createDict.createAnnotationList(FILEPATH, files)
    with codecs.open(DICTIONARYPATH + name + "Annotation", 'w', 'utf-8') as f:
        json.dump(dictAnnotation, f, ensure_ascii=False)
    indAnnotation = createInvertIndex.createInvertIndexAnnotation(FILEPATH, files)
    with codecs.open(INVERTINDEXPATH + name + "Annotation", 'w', 'utf-8') as f:
        json.dump(indAnnotation, f, ensure_ascii=False)
    matrixAnnotation = createInvertIndex.createMatrixFromIndex(indAnnotation, len(files))
    with codecs.open(MATRIXPATH + name + "Annotation", 'w', 'utf-8') as f:
        json.dump(matrixAnnotation, f, ensure_ascii=False)
    coordIndAnnotation = createCoordIndex.getCoordIndexAnnotation(FILEPATH, DICTIONARYPATH, name+"Annotation", files)
    with codecs.open(COORDINDEX + name + "Annotation", 'w', 'utf-8') as f:
        json.dump(coordIndAnnotation, f, ensure_ascii=False)
    Words2IndAnnotation = create2WordsIndex.create2wordsIndexAnnotations(FILEPATH, files)
    with codecs.open(WORDS2INDPATH + name + "Annotation", 'w', 'utf-8') as f:
        json.dump(Words2IndAnnotation, f, ensure_ascii=False)
    trieIndAnnotation, revTrieAnnotation = createTrieIndex.createPrefixTree(INVERTINDEXPATH, name+"Annotation")
    trieIndAnnotation.save(TRIEINDEX + name + "Annotation")
    revTrieAnnotation.save(TRIEINDEX + "r_" + name + "Annotation")




    dictionary.encode(uniqueWords, DICTIONARYPATH + name)
    resTime = time()-startTime

    # record all information
    writeToDBAndToFile(name, allWordsNumber, uniqueWordsNumber, sizeOfFiles, resTime, len(files), ' '.join(ids))

    return json.dumps({'success':True, 'name':name, 'size':sizeOfFiles, 'allWords':allWordsNumber, 'uniqueWords':uniqueWordsNumber,
                       'time':resTime, 'booksNum':len(files)}), 200, {'ContentType':'application/json'}
