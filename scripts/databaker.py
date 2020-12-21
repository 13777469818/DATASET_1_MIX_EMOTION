
import re


def parse_labels_cn(label_file, use_prosody):
  """
  Parse the DataBaker label file and return the list of normalized (basename, text, pinyin)

  Author: johnson.tsing@gmail.com

  Args:
    - label_file: input label file with DataBaker format
    - use_prosody: whether the prosodic structure labeling information will be used

  Returns:
    - A list of tuple (basename, text, pinyin)
  """
  results = []
  content = _read_labels(label_file)
  num = int(len(content)//2)
  for idx in range(num):
    res = _parse_cn_prosody_label(content[idx*2], content[idx*2+1], use_prosody)
    if res is not None:
      results.append(res)
  return results

def parse_labels_en(label_file):
  """
  Parse the DataBaker label file and return the list of normalized (basename, text, phoneme)

  Author: johnson.tsing@gmail.com

  Args:
    - label_file: input label file with DataBaker format

  Returns:
    - A list of tuple (basename, text, phoneme)
  """
  results = []
  content = _read_labels(label_file)
  num = int(len(content)//2)
  for idx in range(num):
    res = _parse_en_prosody_label(content[idx*2], content[idx*2+1])
    if res is not None:
      results.append(res)
  return results


def _read_labels(path):
  """
  Load the text and phoneme prompts from the file
  """
  labels = []
  with open(path, 'r', encoding='utf-8') as f:
    for line in f:
      line = line.strip().strip('\ufeff')
      if line != '': labels.append(line)
  return labels

def _parse_en_prosody_label(text, phoneme):
  """
  Returns:
    - (sen_id, text, phoneme)
  """

  # split into sub-terms
  regex = r"\s*([0-9]+)\s+(.*)"
  match = re.match(regex, text)
  if not match:
    return None

  # split into sub-terms
  sen_id  = match.group(1)
  text    = match.group(2).strip()
  phoneme = phoneme.strip()

  return (sen_id, text, phoneme)

def _parse_cn_prosody_label(text, pinyin, use_prosody=False):
  """
  Parse label from text and pronunciation lines with prosodic structure labelings

  Input  text:   000001	妈妈#1当时#1表示#3，儿子#1开心得#2像花儿#1一样#4。
  Input  pinyin: ma1 ma1 dang1 shi2 biao3 shi4 er2 zi5 kai1 xin1 de5 xiang4 huar1 yi2 yang4
  Return sen_id: 000001
  Return text:   妈妈#1当时#1表示#3,儿子#1开心得#2像花儿#1一样#4.
  Return pinyin: ma1-ma1 dang1-shi2 biao3-shi4, er2-zi5 kai1-xin1-de5/ xiang4-huar1 yi2-yang4.

  Args:
    - text: Chinese characters with prosodic structure labeling, begin with sentence id for wav and label file
    - pinyin: Pinyin pronunciations, with tone 1-5
    - use_prosody: Whether the prosodic structure labeling information will be used

  Returns:
    - (sen_id, text, pinyin&tag): latter contains pinyin string with optional prosodic structure tags
  """

  # split into sub-terms
  regex = r"\s*([0-9]+)\s+(.*)"
  match = re.match(regex, text)
  if not match:
    return None

  # split into sub-terms
  sen_id = match.group(1)
  texts  = match.group(2)
  phones = pinyin.strip().split()

  # normalize the text
  texts = re.sub('[ “”‘’、：；—…·\-（）《》]', '', texts) # remove punctuations
  texts = re.sub('[,，]', ',', texts)            # keep ','
  texts = re.sub('[.。]', '.', texts)            # keep '.'
  texts = re.sub('[?？]', '?', texts)            # keep '?'
  texts = re.sub('[!！]', '!', texts)            # keep '!'
  
  # prosody boundary tag (SYL: 音节, PWD: 韵律词, PPH: 韵律短语, IPH: 语调短语, SEN: 语句)
  SYL = '-'
  PWD = ' '
  PPH = '/ ' if use_prosody==True else ' '
  IPH = ', '
  SEN = '.'

  # parse details
  pinyin = ''
  try:
    i = 0 # texts index
    j = 0 # phones index
    b = 1 # left is boundary
    while i < len(texts):
      if texts[i].isdigit():
        if texts[i] == '1': pinyin += PWD  # Prosodic Word, 韵律词边界
        if texts[i] == '2': pinyin += PPH  # Prosodic Phrase, 韵律短语边界
        if texts[i] == '3': pinyin += IPH  # Intonation Phrase, 语调短语边界
        b  = 1
        i += 1
      elif texts[i] in ['.', '?', '!']:    # Sentence, 语句结束
        pinyin += texts[i]
        b  = 1
        i += 1
      elif texts[i] in [',']:  # 已经在'#3'中处理
        b  = 1;
        i += 1;
      elif texts[i] in ['#']:  # 韵律结构边界标记
        i += 1;
      elif texts[i]!='儿' or j==0 or not _is_erhua(phones[j-1][:-1]): # Chinese segment
        if b == 0: pinyin += SYL  # Syllable, 音节边界（韵律词内部）
        pinyin += phones[j]
        b  = 0
        i += 1
        j += 1
      else: # 儿化音
        i += 1
    pinyin = pinyin.replace('E', 'ev') # 特殊发音E->ev
  except:
    # check
    print('Inconsistent number between text and pinyin:')
    print('sen_id: {}'.format(sen_id))
    print('text  : {}'.format(texts))
    print('pinyin: {}'.format(pinyin))

  return (sen_id, texts, pinyin)

def _is_erhua(pinyin):
  """
  Decide whether pinyin (without tone number) is retroflex (Erhua)
  """
  if len(pinyin)<=1 or pinyin == 'er':
    return False
  elif pinyin[-1] == 'r':
    return True
  else:
    return False
