from parse import helpParse
import json
import codecs

from compression import dictionary

def getCoordIndex(FILEPATH, DICTIONARYPATH, name,  files):
    jsonFile = codecs.open(DICTIONARYPATH + name, 'r', 'utf-8')
    jsonStr = jsonFile.read()
    uniqueWords = json.loads(jsonStr)
    #uniqueWords = dictionary.decode(DICTIONARYPATH + name)
    wordsWithCoordsForEachFile = []
    print("a")
    for i in range(len(files)):
        allText = helpParse.getAllTextFromFb2(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        wordsWithCoordsForEachFile.append(helpParse.getWordsWithCoords(splitedText, i))
    coordIndex = helpParse.mergeDicts(wordsWithCoordsForEachFile, uniqueWords)
    print("b")
    return coordIndex