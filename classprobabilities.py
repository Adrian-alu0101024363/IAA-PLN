import pandas as pd
import os
from vocabfromxlsx import generateTokensDict 
import json
import math


def separate():
  df = pd.read_excel('COV_train.xlsx',header=None)
  unique_values = df.iloc[:,1].unique()
  print(unique_values)
  for unique_value in unique_values:
    df_output = df[df.iloc[:,1].str.contains(unique_value)]
    #output_path = os.path.join('output', unique_value + '.xlsx')
    output_path = unique_value + '.xlsx'
    df_output.to_excel(output_path, sheet_name=unique_value, index=False)
  #p = pd.read_excel('Positive.xlsx')
  #p = p.drop([0])
  #p.to_excel('Positive.xlsx', sheet_name=unique_value, index=False)


def generateJsons():
  with open('negative.json', 'w') as json_file:
    json.dump(generateTokensDict('Negative.xlsx'), json_file)
  with open('positive.json', 'w') as json_file:
    json.dump(generateTokensDict('Positive.xlsx'), json_file)

def generateCorpus(file):
  with open(file) as json_file:
    data = json.load(json_file)
  print(len(data))
  fo = open("vocabulario.txt", "r")
  header = fo.readline()
  lines = fo.readlines()
  result = {}
  i = 0
  for line in lines:
    check = line[:-1]
    if check not in data or data.get(check) < 3:
      i = i + 1
      result.update({'unknow': i})
    else:
      result.update({check: data.get(check)})
  print(result)
  output = file[:-5] + '_corpus.json'
  with open(output, 'w') as json_file:
    json.dump(result, json_file)

def languageModel():
  N = 40297
  with open('positive_corpus.json') as json_file:
    data = json.load(json_file)
  original = pd.read_excel('Positive.xlsx',header=None)
  outputing = open('modelo_lenguaje_P.txt', "w")
  outputing.write(f'Numero de documentos: {len(original)} \nNumero de palabras del corpus: {len(data)}\n' )
  for key in data:
    result = (data.get(key) + 1) / (len(data)+N)
    line = f'Palabra: {key} Frec: {data.get(key)} LogProb: {math.log(result)}\n'
    #print(line)
    outputing.write(line)
  outputing.close()
  with open('negative_corpus.json') as json_file:
    dataN = json.load(json_file)
  originalN = pd.read_excel('Negative.xlsx', header=None)
  outputingN = open('modelo_lenguaje_N.txt', "w")
  outputingN.write(f'Numero de documentos: {len(originalN)} \nNumero de palabras del corpus: {len(dataN)}\n' )
  for key in dataN:
    resultN = (dataN.get(key) + 1) / (len(dataN)+N)
    lineN = f'Palabra: {key} Frec: {dataN.get(key)} LogProb: {math.log(resultN)}\n'
    #print(line)
    outputingN.write(lineN)
  outputingN.close()

#separate()
generateJsons()
generateCorpus('positive.json')
generateCorpus('negative.json')
languageModel()
