#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import urllib
import urllib2
import json
import sys
import os
from os.path import getsize,splitext,isfile,abspath


class Shooter(object):

    def getHash(self, fileName):
        fileLength = getsize(fileName)
        if fileLength < 8192:
            print fileName + ': pass'
            return None
        f = open(fileName, 'r')
        offsets = [4096, fileLength / 3 * 2, fileLength / 3, fileLength - 8192]
        hash = ''
        for offset in offsets:
            f.seek(offset)
            b = f.read(4096)
            md5obj = hashlib.md5()
            md5obj.update(b)
            hash += md5obj.hexdigest() + ';'
        f.close()
        return hash[:-1]

    def getSub(self, fileName):
        url = 'http://www.shooter.cn/api/subapi.php'
        filehash = self.getHash(fileName)
        if not filehash:
            return
        value = {
            'filehash': filehash,
            'pathinfo': fileName,
            'format': 'json',
            'lang': 'Chn'
        }
        post = urllib.urlencode(value)
        response = urllib2.urlopen(url, post)
        try:
            content = unicode(response.read(),'utf-8')
        except UnicodeDecodeError, e:
            print fileName + ': pass'
            content = '[]'
        self.download(content, fileName)

    def download(self, subInfo, fileName):
        subJson = json.loads(subInfo)
        fileNum = 0
        for x in subJson:
            fileInfos = x['Files']
            for fileInfo in fileInfos:
                if fileInfo['Ext'] == 'srt':
                    if fileNum == 0:
                        subName = splitext(fileName)[0] + '.srt'
                    else:
                        subName = (splitext(fileName)[0] + '.%d.srt') % fileNum
                    f = open(subName,'w')
                    response = urllib2.urlopen(fileInfo['Link'])
                    f.write(response.read())
                    f.close()
                    fileNum += 1
                    print '%s downloaded' % subName

if __name__ == '__main__':
    tool = Shooter()
    currentpath = os.getcwd()
    if len(sys.argv) == 1:
        # 下载当前目录下所有视频字幕，不包括子目录
        for subject in os.listdir(currentpath):
            if isfile(subject):
                tool.getSub(abspath(subject))
    else:
        # 否则下载参数文件
        for fileName in sys.argv[1:]:
            if isfile(fileName):
                tool.getSub(abspath(fileName))