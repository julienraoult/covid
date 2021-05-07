
import csv
import requests
import json
import tweepy
import os

from collections import namedtuple
from lxml import html  # type: ignore
from datetime import datetime

#from config import *

# Twitter keys
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

# authenticate and call twitter api
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# https://stackoverflow.com/questions/37248958/tweepy-wait-on-rate-limit-not-working

covid_data = namedtuple("covid_data", "cases deaths recovered")

def covid_stats(url: str = "https://www.worldometers.info/coronavirus/") -> covid_data:
    xpath_str = '//div[@class = "maincounter-number"]/span/text()'
    return covid_data(*html.fromstring(requests.get(url).content).xpath(xpath_str))


fmt = """Total COVID-19 cases in the world: {}
Total deaths due to COVID-19 in the world: {}
Total COVID-19 patients recovered in the world: {}"""
print(fmt.format(*covid_stats()))
print(covid_stats())

covidtracker_data = namedtuple("covidtracker_data", "premiere_dose")

def covidtracker_stats(url: str = "https://covidtracker.fr/vaccintracker/") -> covidtracker_data:
    xpath_str = '//*[@id="nb_doses_injectees"]/text()'
    print(html.fromstring(requests.get(url).content).xpath(xpath_str))

    return covidtracker_data(*html.fromstring(requests.get(url).content).xpath(xpath_str))

print(covidtracker_stats())

gouv_data = namedtuple("gouv_data", "premiere_dose seconde_dose")

def gouv_stats(url : str = "https://raw.githubusercontent.com/rozierguillaume/vaccintracker/main/data/output/vacsi-fra.json") -> (gouv_data, gouv_data):
    data_json = json.loads(requests.get(url).text)
#    print(data_json)

#    return gouv_data(data_json['n_dose1_cumsum'][-1], data_json['n_dose2_cumsum'][-1])
    return (gouv_data(data_json['n_cum_dose1'][-1], data_json['n_cum_complet'][-1]),
            gouv_data(data_json['n_cum_dose1'][-2], data_json['n_cum_complet'][-2])) 

if __name__ == "__main__":
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    timestamp = datetime.fromtimestamp(timestamp)

    # print("timestamp = {}".format(timestamp))

    # log stats
    with open('covid_stats.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        value = (timestamp,) + gouv_stats()[:2]
        writer.writerow(value)

    PEOPLE_NB = {'french': 67407241}
    
    ratio = 100 * gouv_stats()[0].premiere_dose / PEOPLE_NB['french']
    ascii = '\u2593'*int(ratio/5) + '\u2591'*int(20-ratio/5)
    delta = gouv_stats()[0].premiere_dose - gouv_stats()[1].premiere_dose
    remain = int((PEOPLE_NB['french'] - gouv_stats()[0].premiere_dose) / delta) if delta > 0 else "infinity"

    ratio2 = 100 * gouv_stats()[0].seconde_dose / PEOPLE_NB['french']
    ascii2 = '\u2593'*int(ratio2/5) + '\u2591'*int(20-ratio2/5)
    delta2 = gouv_stats()[0].seconde_dose - gouv_stats()[1].seconde_dose
    remain2 = int((PEOPLE_NB['french'] - gouv_stats()[0].seconde_dose) / delta2) if delta2 > 0 else "infinity"

    #print(gouv_stats().premiere_dose)

    tweet  = "#covid #covid19 #vaccin #ViteMaDoseDeVaccin\n"
    tweet += "[FR] 1st dose : {} {:.5f}"+"%"+"\n► {:,} peoples ({:+,}"
    tweet += " ► rdv in {} days)"
    tweet  = tweet.format(ascii, ratio, gouv_stats()[0].premiere_dose, delta, remain)
    tweet += "\n\n[FR] 2nd dose : {} {:.5f}"+"%"+"\n► {:,} peoples ({:+,}"
    tweet += " ► rdv in {} days)"
    tweet  = tweet.format(ascii2, ratio2, gouv_stats()[0].seconde_dose, delta2, remain2)

    print(tweet)

    #api.update_status(tweet)
