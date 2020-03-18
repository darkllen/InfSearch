from parse import helpParse
import collections

def createInvertIndex(FILEPATH, files, startBook):
    invertIndex = {}
    for i in range(len(files)):
        allText = helpParse.getAllTextFromFb2(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.getWordsListWithIndex(splitedText, i, startBook)
        helpParse.addLists(invertIndex, words)
    invertIndex = collections.OrderedDict(sorted(invertIndex.items()))
    return invertIndex

def createMatrixFromIndex(index, num):
    matrix = {k: helpParse.transformIndexToMatrix(v, num) for k, v in index.items()}
    matrix = collections.OrderedDict(sorted(matrix.items()))
    return matrix





def createInvertIndexAuthors(FILEPATH, files):
    invertIndex = {}
    for i in range(len(files)):
        allText = helpParse.getAuthor(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.getWordsListWithIndex(splitedText, i, 0)
        helpParse.addLists(invertIndex, words)
    invertIndex = collections.OrderedDict(sorted(invertIndex.items()))
    return invertIndex
def createInvertIndexTitles(FILEPATH, files):
    invertIndex = {}
    for i in range(len(files)):
        allText = helpParse.getBookTitle(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.getWordsListWithIndex(splitedText, i, 0)
        helpParse.addLists(invertIndex, words)
    invertIndex = collections.OrderedDict(sorted(invertIndex.items()))
    return invertIndex

def createInvertIndexAnnotation(FILEPATH, files):
    invertIndex = {}
    for i in range(len(files)):
        allText = helpParse.getBookAnnotation(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.getWordsListWithIndex(splitedText, i, 0)
        helpParse.addLists(invertIndex, words)
    invertIndex = collections.OrderedDict(sorted(invertIndex.items()))
    return invertIndex