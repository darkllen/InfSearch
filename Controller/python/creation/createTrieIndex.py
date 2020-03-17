import json
import codecs
import datrie

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