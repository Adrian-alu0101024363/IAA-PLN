import re
import pandas as pd
import xlrd
import pkg_resources
from symspellpy import SymSpell, Verbosity
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
import demoji
import string
from nltk.tag import pos_tag

sym_spell = SymSpell()
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt"
)
sym_spell.load_dictionary(dictionary_path, 0, 1)
lemmatizer = WordNetLemmatizer()
en_stops = set(stopwords.words('english'))
#nltk.download('omw-1.4')
#nltk.download('wordnet')

def remove_noise(tweet_tokens, stop_words = ()):

  cleaned_tokens = []

  sym_spell = SymSpell()
  for token, tag in pos_tag(tweet_tokens):
    #token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
     #               '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
    token = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', token)
    token = re.sub("(@[A-Za-z0-9_]+)","", token)
    token = re.sub(r'\d+', '', token)
    token = re.sub(r'[^\w\s]', '', token)
    token = token.replace('_', '')
    " ".join(token.split())
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        "]+", flags = re.UNICODE)
    token = regrex_pattern.sub(r'',token)               
    if tag.startswith("NN"):
        pos = 'n'
    elif tag.startswith('VB'):
        pos = 'v'
    else:
        pos = 'a'

    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()
    token = lemmatizer.lemmatize(token, pos)
    if(len(token) > 1):
      suggestions = sym_spell.lookup(token, Verbosity.CLOSEST,max_edit_distance=2)
      if (len(suggestions) > 0):
        token = suggestions[0].term
    token = stemmer.stem(token)
    if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
      cleaned_tokens.append(token.lower())
  return cleaned_tokens

def generateTokensDict(filename = 'COV_train.xlsx'):
  list_tokens = {}
  print("Generating Tokens Dictionary")
  stop_words = stopwords.words('english')
  original = pd.read_excel(filename,header=None)
  for index, data in original.iterrows():
    line = ''
    if isinstance(data[0], str): line = data[0]
    nltk_token = nltk.word_tokenize(line)
    tokens = remove_noise(nltk_token,stop_words)
    for final in tokens:
        if (final in list_tokens):
          iter = list_tokens.get(final)
          list_tokens.update({final: iter + 1})
        else:
          list_tokens.update({final: 1})
  return list_tokens

def generateTokens():
  print("Parsing file")
  original = pd.read_excel('COV_train.xlsx',header=None)
  list_tokens = []   
  stop_words = stopwords.words('english')
  for index, data in original.iterrows():
    nltk_token = nltk.word_tokenize(data[0])
    tokens = remove_noise(nltk_token,stop_words)
    for final in tokens:
      list_tokens.append(final)
  return list_tokens

def generateVocab():
  tokens = generateTokens()
  print("Removing duplicates")
  finalTokens = list(set(tokens))
  print("Sorting by alphabetical order")
  finalTokens.sort()
  return finalTokens

def printVocab(finalTokens):
  vocabulary = open("vocabulario.txt", "w", encoding="utf8")
  print("Writting vocabulary to file")
  vocabulary.write("Numero de palabras: " + str(len(finalTokens)) + "\n")
  for element in finalTokens:
    vocabulary.write(element + "\n")
  vocabulary.close()

#printVocab(generateVocab())
