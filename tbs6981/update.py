#!/usr/bin/python2

# imports
import os
import re
import urllib
from os.path import expanduser

# settings
home = expanduser("~")
workdir = '/tmp/tbsdtv/'
weburl = 'http://www.tbsdtv.com/download/'

# load site
source = urllib.urlopen(weburl).read()

# find links
pattern = 'tbs-linux-drivers_v[0-9]+.zip'
foundLinks = re.findall(pattern, source)
foundLinks.sort()
usefile = foundLinks[-1] 
webfile = weburl + 'document/common/' + usefile
locfile = os.path.realpath(workdir + usefile)

# downloaded already?
if(not os.path.isfile(locfile)):
    print 'downloading file "%s".' % webfile
    os.system('mkdir -p ' + workdir)
    urllib.urlretrieve (webfile, locfile)
else:
    print 'file "%s" was found already.' % usefile

print 'start compile...'
script = os.path.join(os.path.dirname(__file__), 'compile.sh')
command = script + ' "' + workdir + '" "' + usefile + '"'
os.system(command)
