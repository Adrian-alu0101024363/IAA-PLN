import pandas as pd
import os
import json
import math
import re
from symspellpy import SymSpell, Verbosity
import pkg_resources
import time
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from vocabfromxlsx import parse

sym_spell = SymSpell()
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt"
)
sym_spell.load_dictionary(dictionary_path, 0, 1)
lemmatizer = WordNetLemmatizer()
en_stops = set(stopwords.words('english'))
punctuations = '''!()-[]{};:'"\,<>./?@#|―=$%^&*_~'''
#nltk.download('omw-1.4')

def calculateProbOfLine(tokens, r1, r2, sizeN, sizeP, sizeO):
  probabilityN = 0
  probabilityP = 0
  #print(tokens)
  for token in tokens:
    if token in r1:
      #print(r1[token])
      probabilityN += r1[token]
    else:
      probabilityN += r1['unknow']
  for token in tokens:
    if token in r2:
      #print(r2[token])
      probabilityP += r2[token]
    else:
      probabilityP += r2['unknow']
  probabilityN += math.log(sizeN /sizeO)
  #print(f'Final Negative: {probabilityN}')
  probabilityP += math.log(sizeP /sizeO)
  #print(f'Final Positive: {probabilityP}')
  return probabilityN, probabilityP

def generateTokensOfLine(line):
  if not isinstance(line, str): line = ''
  parsed = parse(line) #si no parseo empora 
  nltk_token = nltk.word_tokenize(parsed)
  list_tokens = []
  for element in nltk_token:
    #Comprobar que no es una stopword
    text = element.lower()
    #text = element
    if text not in en_stops:
      final = lemmatizer.lemmatize(text, 'v')
      if(len(final) > 1):
        suggestions = sym_spell.lookup(final, Verbosity.CLOSEST,max_edit_distance=2)
        if (len(suggestions) > 0):
          final = suggestions[0].term
      list_tokens.append(final)
  return list_tokens

def languageDicts():
  N = 57226
  with open('positive_corpus.json') as json_file:
    data = json.load(json_file)
  resultDictP = {}
  for key in data:
    resultP = (data.get(key) + 1) / (len(data)+N)
    probability = math.log(resultP)
    resultDictP.update({key: probability})
  resultDictN = {}
  with open('negative_corpus.json') as json_file:
    dataN = json.load(json_file)
  #numberOfTweets = len(originalN)
  for key in dataN:
    resultN = (dataN.get(key) + 1) / (len(dataN)+N)
    probabilityN = math.log(resultN)
    resultDictN.update({key: probabilityN})
  #print(f'N: {len(dataN)} S: {len(data)}')
  return resultDictN, resultDictP

def printResult():
  df = pd.read_excel('COV_train.xlsx', header=None)
  #df = pd.read_excel('Negative.xlsx')
  #df = pd.read_excel('Positive.xlsx')
  r1 , r2 = languageDicts()
  count = 0
  countP = 0
  originalN = pd.read_excel('Negative.xlsx',header=None)
  originalP = pd.read_excel('Positive.xlsx',header=None)
  original = pd.read_excel('COV_train.xlsx',header=None)
  numberOfTweetsN = len(originalN)
  numberOfTweetsP = len(originalP)
  numberOfTweetsO = len(original)
  #print(f'N: {numberOfTweetsN} P: {numberOfTweetsP}')
  results = open("resumen_alu0101024363.txt", "w", encoding="utf8")
  clasification = open("clasificacion_alu0101024363.txt", "w", encoding="utf8")
  for index, data in df.iterrows():
    tokens =generateTokensOfLine(data[0])
    #print(tokens)
    tempN , tempP = calculateProbOfLine(tokens, r1, r2, numberOfTweetsN, numberOfTweetsP, numberOfTweetsO)
    if (tempN >= tempP): 
      count +=1
      results.write("N" + "\n")
      clasification.write(f'{data[0][0:10]},{tempP},{tempN},N\n')
    else:
      countP +=1
      results.write("P" + "\n")
      clasification.write(f'{data[0][0:10]},{round(tempP,2)},{round(tempN,2)},P\n')

def checkResult():
  salida = open("resumen_alu0101024363.txt", "r")
  corpus = pd.read_excel('COV_train.xlsx',header=None)
  #corpus = pd.read_excel('Negative.xlsx')
  aciertosTotal = 0
  aciertosN = 0
  aciertosP = 0
  for index, data in corpus.iterrows():
    line = salida.readline()
    if ((data[1] == "Negative") & (line[0] == 'N')):
      aciertosN += 1
    if ((data[1] == "Positive") & (line[0] == 'P')):
      aciertosP += 1
  aciertosTotal = aciertosN + aciertosP
  print(f'Negative aciertos: {aciertosN} Positive aciertos: {aciertosP}')
  print(f'Aciertos: {aciertosTotal} Precision: {round(aciertosTotal/33444,2)}')
  salida.close()

printResult()
checkResult()

''''
r1 , r2 = languageDicts()
originalN = pd.read_excel('Negative.xlsx')
originalP = pd.read_excel('Positive.xlsx')
original = pd.read_excel('COV_train.xlsx')
numberOfTweetsN = len(originalN)
numberOfTweetsP = len(originalP)
numberOfTweetsO = len(original)
example = "CHECK VIDEO ?? https://t.co/1ksn9Brl02 ??No food ? in USA market due to coronavirus panic we gonna die from starvation #CoronavirusOutbreak #coronavirus #houston #nofood #Notoiletpaper #NoHandShakes #nohandsanitizer #COVID19 #pandemic #totallockdown #COVID2019usa #walmart https://t.co/ztN3iMkgpD"
jisho = generateTokensOfLine(example)
calculateProbOfLine(jisho, r1, r2, numberOfTweetsN, numberOfTweetsP, numberOfTweetsO)
'''