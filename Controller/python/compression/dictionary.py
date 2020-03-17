import os
import re
import codecs

def encode(dict, path):
  res = ""
  for i in dict:
    res+= (str(len(i)))
    for x in i:
      res+= x
  f = codecs.open(path, 'w', 'utf-8')
  f.write(res)

def decode(path):
  f = codecs.open(path, 'r', 'utf-8')
  pointers = [0]
  line = f.readline()
  k = 0
  i = 0
  while i < (len(line)):
    while i<len(line) and '0' <= line[i] <= '9':
      i+=1
    while i<len(line) and (line[i]<'0' or line[i]>'9'):
      i+=1
    k=(k+1)%4
    if k == 0:
      pointers.append(i)
    #print("a")
  return Dictionary(pointers, line)

class Dictionary:
  def __init__(self, pointers, line):
    self.pointers = pointers
    self.line = line
  def get(self, i):
    block= int(i/4)
    num = i%4
    bl = 0
    if (block+1) < len(self.pointers):
      bl = self.line[int(self.pointers[block]):int(self.pointers[block+1])]
    else:
      bl = self.line[int(self.pointers[block]):]
    return re.split("[0-9]*", bl)[num+1]