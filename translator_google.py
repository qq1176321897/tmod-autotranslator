'''
Terraria Mod Auto Translator
Author qq:1176321897
Version 1.4

This program aims to localize mods for terraria automatically using baidu translate engine.
This program are allowed to be used and changed as you wish, so long as you are not a member
of the '黎执' translation group.

*****requirement******
ModLocalizer (test with version 0.2)
Python3 (test with version 3.6.7rc2)
windows (test with version 10.1803)
pyexecjs (test with version 1.5.1)
*********note*********
1. This priogram should be put in the modlocalizer directory (with the file Mod.Localizer.exe)
2. The patched file will be name by the mod name followed by "_patched"
3. Usage : translator_google.py <Mod filename>

'''

import time
starttime = time.time()

import sys
import os
import threading
import ctypes
import json
import urllib.request
import urllib.parse
import hashlib
import shutil
import random
import google_api

std_out_handle = ctypes.windll.kernel32.GetStdHandle(-11)
color_lock = threading.Lock()

cinf = 7
cerr = 4
csuc = 2
thread_max = 24

url='https://translate.google.cn/translate_a/single'

changable = ['Name', 'Tip', 'Value', 'SetBonus', 'ToolTip', 'Contents', 'TownNpcNames']

def setcolor(color, handle=std_out_handle):
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)

def info0(inf):
    print('modtranslator : {}'.format(inf))

def info(inf, color):
    color_lock.acquire()
    setcolor(color)
    print('modtranslator : {}'.format(inf))
    setcolor(cinf)
    color_lock.release()

target_lang = 'zh-TW'

if len(sys.argv) < 2:
    info('fatal : filename not provided', cerr)
    exit(1)
filename = os.path.join('..',sys.argv[1])

try:
    shutil.rmtree('temp')
except:
    pass
os.makedirs('temp')
os.chdir('temp')
info('info : dumping tmod with mod localizer...', cinf)
os.system('..\\Mod.Localizer.exe -m dump {}'.format(filename))
info('dump complete.', csuc)

info('extracting word list from target file...', cinf)
folder = ''
queue = []
jsonfilelist = []
for temp in os.listdir('.'):
    if not os.path.isfile(temp):
        folder = temp
        break

for root, _, filelist in os.walk(folder):
    for x in filelist:
        jsonfile = os.path.join(root, x)
        jsonfilelist.append(jsonfile)
        fin = open(jsonfile, 'r')
        dic = json.load(fin)
        fin.close()
        for element in dic:
            for key in changable:
                if key in element.keys():
                    if type(element[key]) == list:
                        queue += element[key]
                    else:
                        queue.append(element[key])

info('{} dscriptions found.'.format(len(queue)), csuc)
info('translation running in {} threads'.format(thread_max), csuc)

thread_list = []
length = len(queue)

def translate(index, full):
    thread_list.append(index)
    if random.random() < 0.1:
        info('thread : translating...{}% ({} of {})'.format(int(100 * index / full), index, full), cinf)
    origin = queue[index]
    omit = 0
    if origin == '':
        omit = 1
    if '$' in origin:
        info('thread : omitted due to special character ''$''', csuc)
        omit = 1
    if not omit:
        try:
            queue[index] = google_api.translate(origin)
        except:
            info('thread : fatal : error when trying to translate through google.cn, please check your network status.', cerr)
            info('thread : omitted due to failure in translarion.', cerr)
    thread_list.remove(index)

for index in range(length):
    while(len(thread_list) >= thread_max):1
    t = threading.Thread(target = lambda : translate(index, length))
    t.setDaemon(True)
    t.start()

last = len(thread_list)
this = last
while(this):
    this = len(thread_list)
    if this != last:
        info('main : waiting for thread...{} left'.format(len(thread_list)), cinf)
        last = this
info('translating completed.', csuc)

qindex = 0
info('applying to json...', cinf)

for jsonfile in jsonfilelist:
    fin = open(jsonfile, 'r')
    dic = json.load(fin)
    fin.close()
    for element_index in range(len(dic)):
        for key in changable:
            if key in dic[element_index].keys():
                if type(dic[element_index][key]) == list:
                    for index in range(len(dic[element_index][key])):
                        dic[element_index][key][index] = queue[qindex]
                        qindex += 1
                else:
                    dic[element_index][key] = queue[qindex]
                    qindex += 1
    fout = open(jsonfile, 'wb')
    fout.write('{}'.format(dic).encode('utf-8'))
    fout.close()
info('json updated.', csuc)
info('packing to tmod...', cinf)
os.system('..\\Mod.Localizer --mode patch --folder {} {}'.format(folder, filename))
patchname = folder + '_patched.tmod'
shutil.move(patchname, filename[:-5] + '_patched.tmod')
info('mod packed.', csuc)
info('removing rubbish files...', cinf)
os.chdir('..')
shutil.rmtree('temp')
info('all operation done successfully in {} secs.'.format(int(time.time() - starttime)), csuc)
