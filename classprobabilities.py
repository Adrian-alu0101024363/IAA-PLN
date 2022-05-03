import pandas as pd
import os
from vocabfromxlsx import generateTokensDict 
import json
import math

def separate():
  df = pd.read_excel('COV_train.xlsx')
  unique_values = df.iloc[:,1].unique()
  print(unique_values)
  for unique_value in unique_values:
    df_output = df[df.iloc[:,1].str.contains(unique_value)]
    output_path = os.path.join('output', unique_value + '.xlsx')
    df_output.to_excel(output_path, sheet_name=unique_value, index=False)

def generateJsons():
  original = pd.read_excel('Negative.xlsx')
  original.to_csv('Negative.csv',header=None, index=False)
  with open('negative.json', 'w') as json_file:
    json.dump(generateTokensDict('Negative.csv'), json_file)
  original = pd.read_excel('Positive.xlsx')
  original.to_csv('Positive.csv',header=None, index=False)
  with open('positive.json', 'w') as json_file:
    json.dump(generateTokensDict('Positive.csv'), json_file)

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
    if check not in data or data.get(check) < 2:
      i = i + 1
      result.update({'unknow': i})
    else:
      result.update({check: data.get(check)})
  print(result)
  output = file[:-5] + '_corpus.json'
  with open(output, 'w') as json_file:
    json.dump(result, json_file)

def languageModel():
  with open('positive_corpus.json') as json_file:
    data = json.load(json_file)
  original = pd.read_excel('Positive.xlsx')
  outputing = open('modelo_lenguaje_P.txt', "w")
  outputing.write(f'Numero de documentos: {len(original)} \nNumero de palabras del corpus: {len(data)}\n' )
  for key in data:
    result = (data.get(key) + 1) / (len(data)*2)
    line = f'Palabra: {key} Frec: {data.get(key)} LogProb: {math.log(result)}\n'
    #print(line)
    outputing.write(line)
  outputing.close()
  with open('negative_corpus.json') as json_file:
    dataN = json.load(json_file)
  originalN = pd.read_excel('Negative.xlsx')
  outputingN = open('modelo_lenguaje_N.txt', "w")
  outputingN.write(f'Numero de documentos: {len(originalN)} \nNumero de palabras del corpus: {len(dataN)}\n' )
  for key in dataN:
    resultN = (dataN.get(key) + 1) / (len(dataN)*2)
    lineN = f'Palabra: {key} Frec: {dataN.get(key)} LogProb: {math.log(resultN)}\n'
    #print(line)
    outputingN.write(lineN)
  outputingN.close()

#separate()
#generateJsons()
#generateCorpus('positive.json')
#generateCorpus('negative.json')
languageModel()
