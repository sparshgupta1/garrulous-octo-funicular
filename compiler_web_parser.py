#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
from lxml import etree
import datetime
import urllib2
from urlparse import urljoin
from collections import namedtuple

Installer = namedtuple('Installer', 'name url')
Compiler_Latest_Builds_URL = \
    'http://fossil.microchip.com/latest_builds.php'
Compiler_Shared_Location = \
    '//idc-ws-isparbs.mchp-main.com/compiler_installers/Installers/Installer_test' #ToDo:Change to correct address in shared folder


def ObtainInstallerURLsDictionary(installer_page):
    parser = etree.HTMLParser()
    tree = etree.parse(installer_page, parser)
    xpath2 = \
        "//div[@class='content']/table[position()=1]/tbody/tr/td[1]/a/child::text()|//div[@class='content']/table[position()=1]/tbody/tr/td[1]/a/attribute::*"
    filtered_html = tree.xpath(xpath2)
    installer_dict = {}
    for i in range(0, len(filtered_html), 2):
        if '.run' in filtered_html[i]:
            if  not ('Linux' in installer_dict):
                installer_dict['Linux'] = Installer(name=filtered_html[i
                    + 1], url=urljoin(installer_page, filtered_html[i]))
        elif '.exe' in filtered_html[i]:
            if not('Windows' in installer_dict):
                installer_dict['Windows'] = Installer(name=filtered_html[i
                    + 1], url=urljoin(installer_page, filtered_html[i]))
        elif '.dmg' in filtered_html[i]:
            if not('Mac' in installer_dict):
                installer_dict['Mac'] = Installer(name=filtered_html[i
                    + 1], url=urljoin(installer_page, filtered_html[i]))
    return installer_dict

def ParseCompilerPublicReleaseWebPage():
    parser = etree.HTMLParser()
    tree = etree.parse(Compiler_Latest_Builds_URL, parser)
    xpath1 = \
        "//div[@id='t-1']/table[@class='internal']/tr[td]/td[position()=1]/a/child::text()|//div[@id='t-1']/table[@class='internal']/tr[td]/td[position()=1]/a/attribute::*|//div[@id='t-1']/table[@class='internal']/tr[td]/td[position()=3]/child::text()"
    filtered_html = tree.xpath(xpath1)
    dict_allitems = {}
    for i in range(0, len(filtered_html), 3):
        dict_allitems[filtered_html[i + 1]] = \
            ('http://compilers.microchip.com' + filtered_html[i],
             filtered_html[i + 2])
    return dict_allitems

def ParseCompilerInternalBuildsWebPage():
    parser = etree.HTMLParser()
    tree = etree.parse(Compiler_Latest_Builds_URL, parser)
    xpath1 = \
        "//div[@id='t-3']/table[@class='internal']/tr[td]/td[position()=1]/a/child::text()|//div[@id='t-3']/table[@class='internal']/tr[td]/td[position()=1]/a/attribute::*|//div[@id='t-3']/table[@class='internal']/tr[td]/td[position()=3]/child::text()"
    filtered_html = tree.xpath(xpath1)
    dict_allitems = {}
    for i in range(0, len(filtered_html), 3):
        dict_allitems[filtered_html[i + 1]] = \
            ('http://compilers.microchip.com' + filtered_html[i],
             filtered_html[i + 2])
    return dict_allitems

def ObtainLatestFullInstallerDictionary(dict_prgm):
    list_prgm = filter(lambda x: ('full' in x[0].lower()),sorted(dict_prgm.items(), key=lambda x: x[1][1],reverse=True))
    if 0 == len(list_prgm):
        return {}
    return ObtainInstallerURLsDictionary(list_prgm[0][1][0])

def ObtainLatestInternalFullInstallerDictionary(dict_prgm):
    list_prgm = filter(lambda x: ('rc' in x[0].lower() or 'tc' in x[0].lower()),
                       sorted(dict_prgm.items(), key=lambda x: x[1][1],reverse=True))
    if 0 == len(list_prgm):
        return {}
    return ObtainInstallerURLsDictionary(list_prgm[0][1][0])

def ObtainLatestPublicReleasedPartSupportInstallerDictionary(dict_prgm):
    list_prgm = filter(lambda x: 'part support' in x[0],
                       sorted(dict_prgm.items(), key=lambda x: x[1][1],
                       reverse=True))
    if 0 == len(list_prgm):
        return {}
    return ObtainInstallerURLsDictionary(list_prgm[0][1][0])

def DownloadInstaller(desinationDirectory, destinationFileName,
                      sourceURL):
    fileExtension = (sourceURL.split('/')[-1])[-4:]
    u = urllib2.urlopen(sourceURL)
    f = open(os.path.abspath(os.path.join(os.sep, desinationDirectory,
             destinationFileName + fileExtension)), 'wb')
    meta = u.info()
    installerSize = int(meta.getheaders('Content-Length')[0])
    print 'Downloading from %s' % sourceURL
    print 'FileName: %s FileSize:%s' % (destinationFileName
            + fileExtension, installerSize)
    fileSizeDownloaded = 0
    while True:
        buffer_read = u.read(8192)
        if not buffer_read:
            break
        fileSizeDownloaded += len(buffer_read)
        f.write(buffer_read)
        #status = r"%10d [%3.2f%%]" % (fileSizeDownloaded,
        #        fileSizeDownloaded * 100. / installerSize)
        #print status,
        sys.stdout.write('Downloading %s [%3.2f%%] \r'
                             % (os.path.basename(destinationFileName),
                             fileSizeDownloaded * 100. / installerSize))
        sys.stdout.flush()
    f.close()

def DownloadInstaller(destinationPath,sourceURL):
    f = open(destinationPath, 'wb')
    u = urllib2.urlopen(sourceURL)
    meta = u.info()
    installerSize = int(meta.getheaders('Content-Length')[0])
    print 'Downloading from %s' % sourceURL
    print 'FileName: %s FileSize:%s' % (destinationPath, installerSize)
    fileSizeDownloaded = 0
    print 'Starting Download'
    while True:
        buffer_read = u.read(8192)
        if not buffer_read:
            break
        fileSizeDownloaded += len(buffer_read)
        f.write(buffer_read)
        #status = r"%10d [%3.2f%%]" % (fileSizeDownloaded,
        #        fileSizeDownloaded * 100. / installerSize)
        #print status,
        sys.stdout.write('Downloading %s [%3.2f%%] \r'
                             % (os.path.basename(destinationPath),
                             fileSizeDownloaded * 100. / installerSize))
        sys.stdout.flush()
    f.close()
    print 'Download Completed and installer copied to %s' % destinationPath

def ParseWebPageAndObtainBaseInstallerUrlForLatestPartSupport(compilerType='xc16',os=sys.platform):
    if not (compilerType == 'xc8' or compilerType == 'xc16'
         or compilerType == 'xc32' or compilerType == 'c18'):
        print 'Invalid Program Type'
        sys.exit()
        
    dict_temp = ParseCompilerPublicReleaseWebPage()
    dict_prgm = {}

    #Filter the dictionary to the specified compiler type
    for (k, v) in dict_temp.items():
        if re.search('^xc8', k.lower()) and compilerType == 'xc8':
            dict_prgm[k] = (v[0], datetime.datetime.strptime(v[1],'%B %d, %Y %H:%M:%S'))
        elif re.search('^xc16', k.lower()) and compilerType == 'xc16':
            dict_prgm[k] = (v[0], datetime.datetime.strptime(v[1],'%B %d, %Y %H:%M:%S'))
        elif re.search('^xc32', k.lower()) and compilerType == 'xc32':
            dict_prgm[k] = (v[0], datetime.datetime.strptime(v[1],'%B %d, %Y %H:%M:%S'))
        elif re.search('^c18', k.lower()) and compilerType == 'c18':
            dict_prgm[k] = (v[0], datetime.datetime.strptime(v[1],'%B %d, %Y %H:%M:%S'))

    if len(dict_prgm.items()) == 0:
        print 'No installers found for required program'
        sys.exit()
        
    base_prgm = None
    temp_prgm_list = filter(lambda x: 'part support' in x[0],
                       sorted(dict_prgm.items(), key=lambda x: x[1][1],
                       reverse=True))
    partSupportVersion = temp_prgm_list[0][0][temp_prgm_list[0][0].index('v') + 1:temp_prgm_list[0][0].index('v') + 1 + 4]
    temp_prgm_list = filter(lambda x: 'full install' in x[0],dict_prgm.items())
    for i in range(len(temp_prgm_list)):
        if (('v' + str(partSupportVersion)) in (temp_prgm_list[i][0])):
            base_prgm = dict_prgm[temp_prgm_list[i][0]]
            break

    if base_prgm == None:
        return (None,None)
    else:        
        installer_dict = ObtainInstallerURLsDictionary(base_prgm[0])
        verOsCatInfo = ''
        localFileName = compilerType
        prgm = None
        if 'linux2' == os:
            if 'Linux' in installer_dict:
                prgm = installer_dict['Linux']
                verOsCatInfo = 'v' + prgm.name[prgm.name.index('v') + 1 : prgm.name.index('v') + 1 + 4].replace('.', '') + 'linux'
        elif 'win32' == os:
            if 'Windows' in installer_dict:
                prgm = installer_dict['Windows']
                verOsCatInfo = 'v' + prgm.name[prgm.name.index('v') + 1 : prgm.name.index('v') + 1 + 4].replace('.', '') + 'win'
        elif 'darwin' == os:
            if 'Mac' in installer_dict:
                prgm = installer_dict['Mac']
                verOsCatInfo = 'v' + prgm.name[prgm.name.index('v') + 1 : prgm.name.index('v') + 1 + 4].replace('.', '') + 'osx'
        else:
            print 'Invalid OS'
            return (None,None)

    if prgm != None:
        import os #ToDo:If I don't import, then unable to join paths
        localDirectory = Compiler_Shared_Location + '/' + compilerType.upper()
        localFileName = localFileName + verOsCatInfo + (prgm.url.split('/')[-1])[-4:]        
        return (os.path.abspath(os.path.join(os.path.sep,localDirectory,localFileName)),prgm.url)        
    else:
        return (None,None)

def ParseWebPageIntoDictionary(compilerType='xc16',programCategory='LastMajorRelease',os=sys.platform):
    if not (compilerType == 'xc8' or compilerType == 'xc16'
         or compilerType == 'xc32' or compilerType == 'c18'):
        print 'Invalid Program Type'
        sys.exit()
        
    if not (programCategory == 'LastReleaseWithPartSupport' or programCategory == 'LastMajorRelease'
            or programCategory == 'LatestMajorRelease' or programCategory == 'LastReleaseWithDailyPartSupport'
            or programCategory == 'LatestReleaseWithDailyPartSupport'):
        print 'Invalid Category'
        sys.exit()

    #Parse the appropriate webpage and get all the information from the tables    
    if (programCategory == 'LastMajorRelease' or programCategory == 'LastReleaseWithPartSupport' or
        programCategory == 'LastReleaseWithDailyPartSupport'):
        dict_temp = ParseCompilerPublicReleaseWebPage()
    elif (programCategory == 'LatestMajorRelease' or programCategory == 'LatestReleaseWithDailyPartSupport'):
        dict_temp = ParseCompilerInternalBuildsWebPage()
    else:
        print 'Invalid Category'
    dict_prgm = {}

    #Filter the dictionary to the specified compiler type
    for (k, v) in dict_temp.items():
        if re.search('^xc8', k.lower()) and compilerType == 'xc8':
            dict_prgm[k] = (v[0], datetime.datetime.strptime(v[1],'%B %d, %Y %H:%M:%S'))
        elif re.search('^xc16', k.lower()) and compilerType == 'xc16':
            dict_prgm[k] = (v[0], datetime.datetime.strptime(v[1],'%B %d, %Y %H:%M:%S'))
        elif re.search('^xc32', k.lower()) and compilerType == 'xc32':
            dict_prgm[k] = (v[0], datetime.datetime.strptime(v[1],'%B %d, %Y %H:%M:%S'))
        elif re.search('^c18', k.lower()) and compilerType == 'c18':
            dict_prgm[k] = (v[0], datetime.datetime.strptime(v[1],'%B %d, %Y %H:%M:%S'))    
    return dict_prgm

def ObtainVersionNumbers(compilerType='xc16',programCategory='LastMajorRelease',os=sys.platform):
    dict_prgm = ParseWebPageIntoDictionary(compilerType, programCategory, os)

    if len(dict_prgm.items()) == 0:
        print 'No installers found for required program'
        sys.exit()
    
    if (programCategory == 'LastMajorRelease' or programCategory == 'LatestMajorRelease' or
        programCategory == 'LastReleaseWithDailyPartSupport' or programCategory == 'LatestReleaseWithDailyPartSupport'):
        list_prgm = sorted(dict_prgm.items(), key=lambda x: x[1][1],reverse=True)
        if 0 == len(list_prgm):
            return 'VERSION_INDETERMINED'
        else:
            return list_prgm[0][0].split(' ')[1]
    elif programCategory == 'LastReleaseWithPartSupport':
        list_prgm = filter(lambda x:('part support' in x[0].lower()),sorted(dict_prgm.items(), key=lambda x: x[1][1],reverse=True))
        if 0 == len(list_prgm):
            return 'VERSION_INDETERMINED'
        else:
            return list_prgm[0][0].split(' ')[1]+'_PartSupport'
        pass          
    
def ParseWebPageAndObtainUrl(compilerType='xc16',programCategory='LastMajorRelease',os=sys.platform):

    dict_prgm = ParseWebPageIntoDictionary(compilerType, programCategory, os)

    if len(dict_prgm.items()) == 0:
        print 'No installers found for required program'
        sys.exit()
    localFileName = compilerType
    verOsCatInfo = ''
    prgm = None
    if (programCategory == 'LastMajorRelease' or programCategory == 'LastReleaseWithDailyPartSupport'):
        if 'linux2' == os:
            if 'Linux' in ObtainLatestFullInstallerDictionary(dict_prgm):
                prgm = ObtainLatestFullInstallerDictionary(dict_prgm)['Linux']
                verOsCatInfo = 'v' + prgm.name[prgm.name.index('v') + 1 : prgm.name.index('v') + 1 + 4].replace('.', '') + 'linux'
        elif 'win32' == os:
            if 'Windows' in ObtainLatestFullInstallerDictionary(dict_prgm):
                prgm = ObtainLatestFullInstallerDictionary(dict_prgm)['Windows']
                verOsCatInfo = 'v' + prgm.name[prgm.name.index('v')+ 1 : prgm.name.index('v') + 1 + 4].replace('.', '') + 'win'
        elif 'darwin' == os:
            if 'Mac' in ObtainLatestFullInstallerDictionary(dict_prgm):
                prgm = ObtainLatestFullInstallerDictionary(dict_prgm)['Mac']
                verOsCatInfo = 'v' + prgm.name[prgm.name.index('v')+ 1 : prgm.name.index('v') + 1 + 4].replace('.', '') + 'osx'
    elif (programCategory == 'LatestMajorRelease' or programCategory == 'LatestReleaseWithDailyPartSupport'):
        if 'linux2' == os:
            if 'Linux' in ObtainLatestInternalFullInstallerDictionary(dict_prgm):
                prgm = ObtainLatestInternalFullInstallerDictionary(dict_prgm)['Linux']
                verOsCatInfo = 'v' + prgm.name[prgm.name.index('v') + 1 : prgm.name.index('v') + 1 + 4].replace('.', '') + prgm.url.split('/')[-2].split('_')[-1] + 'linux'
        elif 'win32' == os:
            if 'Windows' in ObtainLatestInternalFullInstallerDictionary(dict_prgm):
                prgm = ObtainLatestInternalFullInstallerDictionary(dict_prgm)['Windows']
                verOsCatInfo = 'v' + prgm.name[prgm.name.index('v')+ 1 : prgm.name.index('v') + 1 + 4].replace('.', '') + prgm.url.split('/')[-2].split('_')[-1] + 'win'
        elif 'darwin' == os:
            if 'Mac' in ObtainLatestInternalFullInstallerDictionary(dict_prgm):
                prgm = ObtainLatestInternalFullInstallerDictionary(dict_prgm)['Mac']
                verOsCatInfo = 'v' + prgm.name[prgm.name.index('v')+ 1 : prgm.name.index('v') + 1 + 4].replace('.', '') + prgm.url.split('/')[-2].split('_')[-1] + 'osx'
    elif programCategory == 'LastReleaseWithPartSupport':
        if 'linux2' == os:
            if 'Linux' in ObtainLatestPublicReleasedPartSupportInstallerDictionary(dict_prgm):
                prgm =  ObtainLatestPublicReleasedPartSupportInstallerDictionary(dict_prgm)['Linux']
                versionNumberPartSupport = prgm.name[prgm.name.index('v') + 1 : prgm.name.index('v') + 1 + 4]
                verOsCatInfo = 'v' + versionNumberPartSupport.replace('.', '') + 'linux_ps'
                if 'Linux' in ObtainLatestFullInstallerDictionary(dict_prgm):
                    prgm_temp = ObtainLatestFullInstallerDictionary(dict_prgm)['Linux']
                    versionNumberMajor = prgm_temp.name[prgm_temp.name.index('v') + 1 : prgm_temp.name.index('v') + 1 + 4]
                    if (versionNumberMajor > versionNumberPartSupport):
                        prgm = prgm_temp
                        verOsCatInfo = 'v' + versionNumberMajor.replace('.', '') + 'linux'
        elif 'win32' == os:
            if 'Windows'in ObtainLatestPublicReleasedPartSupportInstallerDictionary(dict_prgm):
                prgm = ObtainLatestPublicReleasedPartSupportInstallerDictionary(dict_prgm)['Windows']
                versionNumberPartSupport = prgm.name[prgm.name.index('v') + 1 : prgm.name.index('v') + 1 + 4]
                verOsCatInfo = 'v' + versionNumberPartSupport.replace('.', '') + 'win_ps'
                if 'Windows'in ObtainLatestFullInstallerDictionary(dict_prgm):
                    prgm_temp = ObtainLatestFullInstallerDictionary(dict_prgm)['Windows']
                    versionNumberMajor = prgm_temp.name[prgm_temp.name.index('v') + 1 : prgm_temp.name.index('v') + 1 + 4]
                    if (versionNumberMajor > versionNumberPartSupport):
                        prgm = prgm_temp
                        verOsCatInfo = 'v' + versionNumberMajor.replace('.', '') + 'win'
        elif 'darwin' == os:
            if 'Mac' in ObtainLatestPublicReleasedPartSupportInstallerDictionary(dict_prgm):
                prgm = ObtainLatestPublicReleasedPartSupportInstallerDictionary(dict_prgm)['Mac']
                versionNumberPartSupport = prgm.name[prgm.name.index('v') + 1 : prgm.name.index('v') + 1 + 4]
                verOsCatInfo = 'v' + versionNumberPartSupport.replace('.', '') + 'osx_ps'
                if 'Mac' in ObtainLatestFullInstallerDictionary(dict_prgm):
                    prgm_temp = ObtainLatestFullInstallerDictionary(dict_prgm)['Mac']
                    versionNumberMajor = prgm_temp.name[prgm_temp.name.index('v') + 1 : prgm_temp.name.index('v') + 1 + 4]
                    if (versionNumberMajor > versionNumberPartSupport):
                        prgm = prgm_temp
                        verOsCatInfo = 'v' + versionNumberMajor.replace('.', '') + 'osx'
    if None != prgm:
        import os #ToDo:If I don't import, then unable to join paths
        localDirectory = Compiler_Shared_Location + '/' + compilerType.upper()
        localFileName = localFileName + verOsCatInfo + (prgm.url.split('/')[-1])[-4:]        
        return (os.path.abspath(os.path.join(os.path.sep,localDirectory,localFileName)),prgm.url)        
    else:
        return (None,None)