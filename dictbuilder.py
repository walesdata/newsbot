# Here we will run through the examples downloaded and build out a table with a dictionary of all of the 
# words. 

import os, sys, re, time

proj_path = "/home/jwales/eclipse-workspace/crowdnews/"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdnews.settings")
sys.path.append(proj_path)
os.chdir(proj_path)
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from django.contrib.gis.views import feed
from newsbot.models import *
from newsbot.util import *

print("Loading dictionary...")
cDict = loadCanonDict()

qs_Examples = ArticleExample.objects.all()
print("Examples: " + str(qs_Examples.count()))

for ex in qs_Examples:
    cwords = ex.body_text.split()
    for cwrd in cwords:
        if(cwrd in cDict.keys()):
            print('.', end='', flush=True)
        else:
            print('X', end='', flush=True)
            nde = DictEntry(canonWord = cwrd)
            nde.save()
            cDict[cwrd] = nde.pk

