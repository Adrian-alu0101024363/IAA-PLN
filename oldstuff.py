''''
def check(token, options = (1,1,1,1,1,1,1,1)):
  param = list(options)
  if (token.is_digit and param[7]): return False
  if (token.is_punct and param[0]): return False
  if (token.is_stop and param[1]): return False
  if (token.like_num and param[2]): return False
  if (token.is_space and param[3]): return False
  if (token.like_url and param[4]): return False
  if (token.is_quote and param[5]): return False
  if ((token.is_left_punct or token.is_right_punct) and param[6]): return False
  return True

def generateTokens(case_flag = True):
  list_tokens = []
  ignore = ('@','-','+','.',',','~','','"','\'','/','(',')','$','&',':','?','^','=','|')
  nlp = spacy.load("en_core_web_sm")
  #nlp.add_pipe('emoji', first=True)
  print("Parsing file")
  original = pd.read_excel('COV_train.xlsx')
  lines = original.iloc[:,0]
  for line in lines:
    emoji_pattern = re.compile("["
          u"\U0001F600-\U0001F64F"  # emoticons
          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
          u"\U0001F680-\U0001F6FF"  # transport & map symbols
          u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags=re.UNICODE)
    line = emoji_pattern.sub(r'', line)
    doc = nlp(line)
    #if (doc._.has_emoji): doc._.emoji_desc
    for token in doc:
      suggestions = sym_spell.lookup(token.lemma_, Verbosity.CLOSEST,max_edit_distance=2)
      if (len(suggestions) > 0):
        token.lemma_ = suggestions[0].term
      if (check(token)):
        if (not token.lemma_.startswith(ignore) and not token.text[0].isdigit()):
          if (case_flag):
            list_tokens.append(token.lemma_.lower())
          else:
            list_tokens.append(token.lemma_)
  return list_tokens

def generateTokensDict(filename = 'COV_train.xsl', case_flag = True):
  list_tokens = {}
  ignore = ('@','-','+','.',',','~','','"','\'','/','(',')','$','&',':','?','^','=')
  nlp = spacy.load("en_core_web_sm")
  print("Parsing file")
  original = pd.read_excel(filename)
  lines = original.iloc[:,0]
  for line in lines:
    #line = bytes(line, 'utf-8').decode('utf-8', 'ignore')
    if not isinstance(line, str): line = ''
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                          "]+", flags=re.UNICODE)
    line = emoji_pattern.sub(r'', line)
    doc = nlp(line)
    for token in doc:
      suggestions = sym_spell.lookup(token.lemma_, Verbosity.CLOSEST,max_edit_distance=2)
      if (len(suggestions) > 0):
        token.lemma_ = suggestions[0].term
      if (check(token)):
        if (not token.lemma_.startswith(ignore) and not token.text[0].isdigit()):
          if (case_flag):
            if (token.lemma_.lower() in list_tokens):
              iter = list_tokens.get(token.lemma_.lower())
              list_tokens.update({token.lemma_.lower(): iter+1})
            else:
              list_tokens.update({token.lemma_.lower(): 1})
          else:
            if (token.lemma_ in list_tokens):
              iter = list_tokens.get(token.lemma_)
              list_tokens.update({token.lemma_: iter+1})
            else:
              list_tokens.update({token.lemma_: 1})
  return list_tokens

'''

''''
#para generar diccionario del tweet osea que palabras tiene
def generateTokensOfLine(line, case_flag = True):
  list_tokens = []
  ignore = ('@','-','+','.',',','~','','"','\'','/','(',')','$','&',':','?','^','=')
  nlp = spacy.load("en_core_web_sm")
  #print("Parsing line")
  #line = bytes(line, 'utf-8').decode('utf-8', 'ignore')
  if not isinstance(line, str): line = ''
  emoji_pattern = re.compile("["
      u"\U0001F600-\U0001F64F"  # emoticons
      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
      u"\U0001F680-\U0001F6FF"  # transport & map symbols
      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        "]+", flags=re.UNICODE)
  line = emoji_pattern.sub(r'', line)
  doc = nlp(line)
  for token in doc:
    suggestions = sym_spell.lookup(token.lemma_, Verbosity.CLOSEST,max_edit_distance=2)
    if (len(suggestions) > 0):
      token.lemma_ = suggestions[0].term
    if (check(token)):
      if (not token.lemma_.startswith(ignore) and not token.text[0].isdigit()):
        if (case_flag):
          list_tokens.append(token.lemma_.lower())
        else:
          list_tokens.append(token.lemma_)
  return list_tokens
'''