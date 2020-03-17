import os
import re
import codecs


def numToGamma(num):
  un = "1"*(len(bin(num))-3)+"0"
  return un + bin(num)[3:]

def encodeIndex(ind):
  res = []
  for i in ind.values():
    r = ""
    for j in i:
      r+=numToGamma(j+2)
    res.append(r)
  return res

def recordCompressedIndex(encodedInd, path):
  f = codecs.open(path, 'w', 'utf-8')
  for i in encodedInd:
    l = 8 - (len(i)%8)
    while l!=8:
      i+='0'
      l+=1
    ascii_string = ""
    for l in ["1"+i[x:x+7] for x in range (0, len(i), 7)]:
        an_integer = int(l, 2)
        ascii_character = chr(an_integer)
        ascii_string += ascii_character
    f.write(ascii_string)
    f.write("\n")

def decodeIndex(path):
  f = codecs.open(path, 'r', 'utf-8')
  return InvertIndex(f.read())

class InvertIndex:
  def __init__(self, line):
    self.inds = line.split("\n")
  def get(self, i):
    res = []
    r = ""
    for j in self.inds[i]:
      a = str(bin(ord(j)))[3:]
      r+=a
    count = 0
    l = 0
    while count < len(r):
      if r[count] == '1':
        l+=1
        count+=1
      else:
        count+=1
        n = ''
        for h in range(l):
          n+=r[count]
          count+=1
        n = '0b1'+n
        n = int(n,2)
        l=0
        res.append(n-2)
        if count< len(r):
          if r[count]=='0':
            return res
    return res