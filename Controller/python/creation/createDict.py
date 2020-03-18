from parse import helpParse
import os

def createWordsListAndInfo(FILEPATH, files):
    sizeOfFiles = 0
    allWordsNumber = 0
    uniqueWords = []

    for i in files:
        allText = helpParse.getAllTextFromFb2(FILEPATH + i)
        sizeOfFiles += os.path.getsize(FILEPATH + i) / 1024
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.getWordsList(splitedText)
        allWordsNumber += len(words)

        lists = helpParse.getListUnique(words)

        uniqueWords += lists

    uniqueWords.sort()
    uniqueWords = helpParse.getListUnique(uniqueWords)
    uniqueWordsNumber = len(uniqueWords)
    return uniqueWords, sizeOfFiles, uniqueWordsNumber, allWordsNumber

def createWordsList(FILEPATH, files):
    allText = ""
    for i in files:
        allText += helpParse.getAllTextFromFb2(FILEPATH + i)

    splitedText = helpParse.splitByTags(allText)
    words = helpParse.getWordsList(splitedText)
    uniqueWords = helpParse.getListUnique(words)
    return uniqueWords


def createAuthorsList(FILEPATH, files):
    allText = ""
    for i in files:
        allText += helpParse.getAuthor(FILEPATH + i)

    splitedText = helpParse.splitByTags(allText)
    words = helpParse.getWordsList(splitedText)
    uniqueWords = helpParse.getListUnique(words)
    return uniqueWords
def createTitleList(FILEPATH, files):
    allText = ""
    for i in files:
        allText += helpParse.getBookTitle(FILEPATH + i)

    splitedText = helpParse.splitByTags(allText)
    words = helpParse.getWordsList(splitedText)
    uniqueWords = helpParse.getListUnique(words)
    return uniqueWords
def createAnnotationList(FILEPATH, files):
    allText = ""
    for i in files:
        allText += helpParse.getBookAnnotation(FILEPATH + i)

    splitedText = helpParse.splitByTags(allText)
    words = helpParse.getWordsList(splitedText)
    uniqueWords = helpParse.getListUnique(words)
    return uniqueWords