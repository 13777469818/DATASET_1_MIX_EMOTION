#!/bin/python3

# 作者黎静北

# 注意事项
# (1) 有关儿化音的处理，直接去掉了
# (2) 有π这种字符的原因
# (3) 4层韵律标注都按1层处理的: 标注#1, #2, #3, #4，都按#1做的，即认为#1就是分词; #4基本和逗号句号一致; 中间的没有再细分

import sys
sys.path.append('../../')
import pickle
import re
from collections import Counter
import logging
import json
from mjrc.thirdparty.nicelogger import enable_pretty_logging
from mjrc.split_pinyin_sp.split_pinyin import split_pinyin
from mjrc.tools.gen_inputs import split_keys
logger = logging.getLogger(__name__)
enable_pretty_logging('INFO')

remove_symbols_regex = re.compile('[0-9“”…（），：、—；]')
remove_stops_regex = re.compile('[。！？]')
has_alphabets_regex = re.compile('[a-zA-Zａ-ｚＡ-Ｚ]')
a = open('./000001-010000.txt', encoding='cp936').readlines()
a = [i.strip('\t\r\n') for i in a]
a = [a[i].split('\t') + [a[i + 1]] for i in range(0, len(a), 2)]
phoneme_list = {}
phoneme_dict = set(['__PAD', ])
errors = []
for line in a:
    if len(has_alphabets_regex.findall(line[1])) > 0:
        errors.append('有字母')
        logger.error(line[:-1])
        continue
    b = remove_symbols_regex.sub('', line[1]).split('#')
    pinyin = line[2].split(' ')
    if not b[-1] in '。！？':
        logger.error(b)
        errors.append('末尾为其他标点')
        continue
    if b[-1] == '':
        errors.append('末尾缺少标点')
        b[-1] = '。'
    if line[0] == '001464':
        b = [re.sub(r'([这明])儿', '\1', i) for i in b]
    elif line[0] == '009197':
        b = [re.sub(r'([会])儿', '\1', i) for i in b]
    tmp = remove_stops_regex.sub('', ''.join(b))
    if len(tmp) != len(pinyin):
        if tmp.count('儿') == len(tmp) -len(pinyin):
            b = [i.replace('儿', '') for i in b]
        else:
            errors.append('音节数量不匹配')
            logger.error(line)
            continue
    for i, j in enumerate([(i, j) for i, j in enumerate(''.join(b)) if j in '。！？']):
        pinyin.insert(i + j[0], j[1])
    if sum([len(i) for i in b]) != len(pinyin):
        errors.append('对齐错误')
        logger.error(line)
        continue
    for i, j in enumerate(b):
        if i > 0 and not j in '。！？':
            pinyin.insert(i + len(''.join(b[:i])) - 1, '/')

    pinyin = [split_pinyin(i) if not i in '/。！？' else i for i in pinyin]
    phoneme_list[line[0]] = []
    for i in pinyin:
        for j in i:
            if j != '':
                phoneme_list[line[0]].append(str(j))
    phoneme_dict.update(phoneme_list[line[0]])

phoneme_dict = phoneme_set_to_dict(phoneme_set)

print(phoneme_list)
print(phoneme_dict)

pickle.dump(phoneme_list, open('./phoneme_list.pkl', 'wb'))
pickle.dump(phoneme_dict, open('./phoneme_dict.pkl', 'wb'))

logger.info(Counter(errors))

split_keys(phoneme_list.keys())
