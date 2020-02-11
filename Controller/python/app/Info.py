# -*- coding: utf-8 -*-
from app import app
from contextlib import closing
from flask import send_file
from flask import request
import connection



@app.route('/getFile',methods=['GET'])
def getFile():
    name = request.args['name']
    return send_file('C:\\Server\\data\\htdocs\\InfSearch\\Model\\dictionaries\\'+name)

@app.route('/getIndex',methods=['GET'])
def getIndex():
    name = request.args['name']
    return send_file('C:\\Server\\data\\htdocs\\InfSearch\\Model\\invertIndex\\'+name)

@app.route('/get2WordIndex',methods=['GET'])
def get2WordIndex():
    name = request.args['name']
    return send_file('C:\\Server\\data\\htdocs\\InfSearch\\Model\\words2Index\\'+name)
@app.route('/getCoordIndex',methods=['GET'])
def getCoordIndex():
    name = request.args['name']
    return send_file('C:\\Server\\data\\htdocs\\InfSearch\\Model\\coordIndex\\'+name)

@app.route('/getPermutationIndex',methods=['GET'])
def getPermutationIndex():
    name = request.args['name']
    return send_file('C:\\Server\\data\\htdocs\\InfSearch\\Model\\permutationIndex\\'+name)

@app.route('/getGramIndex',methods=['GET'])
def getGramIndex():
    name = request.args['name']
    return send_file('C:\\Server\\data\\htdocs\\InfSearch\\Model\\gramIndex\\'+name)

@app.route('/getMatrix',methods=['GET'])
def getMatrix():
    name = request.args['name']
    return send_file('C:\\Server\\data\\htdocs\\InfSearch\\Model\\matrix\\'+name)

@app.route('/getBooks',methods=['GET'])
def getBooksList():
    return connection.selectAllFrom("books")

@app.route('/getDictionaries', methods=['GET'])
def getDictionariesList():
    return connection.selectAllFrom("dictionary")


