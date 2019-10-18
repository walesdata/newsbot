# Harvester.py: 
# Grab, parse, and store the examples provided by ad fontes media and apply their scores to the articles.

import os, sys, re, time

proj_path = "/home/jwales/eclipse-workspace/crowdnews/"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdnews.settings")
sys.path.append(proj_path)
os.chdir(proj_path)
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from django.contrib.gis.views import feed

import pandas as pd
from newsbot.strainer import *
from newsbot.models import *

ss = SoupStrainer()
print("Initializing dictionary...")
ss.init()

def harvest_Politifact_data():
    print("Ready to harvest Politifact data.")
    input("[Enter to continue, Ctl+C to cancel]>>")
    print("Reading URLs file")
    df_csv = pd.read_csv("newsbot/politifact_data.csv", error_bad_lines=False, quotechar='"', thousands=',', low_memory=False)
    for index, row in df_csv.iterrows():
        print("Attempting URL: " + row['news_url'])
        if(ss.loadAddress(row['news_url'])):
            print("Loaded OK")
            # some of this data loads 404 pages b/c it is a little old, some load login pages. I've found that
            # ignoring anything under 500 characters is a decent strategy for weeding those out.
            if(len(ss.extractText)>500):
                ae = ArticleExample()
                ae.body_text = ss.extractText
                ae.origin_url = row['news_url']
                ae.origin_source = 'politifact data'
                ae.bias_score = 0 # Politifact data doesn't have this
                ae.bias_class = 5 # on this 1 to 4 scale, 5 is 'no data'
                ae.quality_score = row['score']
                ae.quality_class = row['class']
                ae.save()
                print("Saved, napping for 1...")
                time.sleep(1)
            else:
                print("**** This URL produced insufficient data.")
        else:
            print("**** Error on that URL ^^^^^")
    
    
    
def harvest_MBC_data():
    print("Ready to harvest Media Bias Chart data.")
    input("[Enter to continue, Ctl+C to cancel]>>")
    print("Reading URLs file")
    df_csv = pd.read_csv("newsbot/MediaBiasChartData.csv", error_bad_lines=False, quotechar='"', thousands=',', low_memory=False)
    for index, row in df_csv.iterrows():
        print("Attempting URL: " + row['Url'])
        if(ss.loadAddress(row['Url'])):
            print("Loaded OK")
            ae = ArticleExample()
            ae.body_text = ss.extractText
            ae.origin_url = row['Url']
            ae.origin_source = row['Source']
            ae.bias_score = row['Bias']
            ae.quality_score = row['Quality']
            ae.bias_class = 5
            if(ae.quality_score <= 16.25):
                ae.quality_class = 1
            elif(ae.quality_score <= 32.50):
                ae.quality_class = 2
            elif(ae.quality_score <= 48.75):
                ae.quality_class = 3
            else:
                ae.quality_class = 4
            ae.save()
            print("Saved, napping for 1...")
            time.sleep(1)
        else:
            print("Error on that URL ^^^^^")
    
    

harvest_MBC_data()
harvest_Politifact_data()