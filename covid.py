from collections import namedtuple

import csv
import requests
import json

from lxml import html  # type: ignore
from datetime import datetime

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

def gouv_stats(url : str = "https://raw.githubusercontent.com/rozierguillaume/vaccintracker/main/data/output/vacsi-fra.json") -> gouv_data:
    data_json = json.loads(requests.get(url).text)
#    print(data_json)

    return gouv_data(data_json['n_dose1_cumsum'][-1], data_json['n_dose2_cumsum'][-1])

print(gouv_stats())

now = datetime.now()
timestamp = datetime.timestamp(now)
timestamp = datetime.fromtimestamp(timestamp)

print("timestamp = {}".format(timestamp))

with open('covid_stats.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    value = (timestamp,) + gouv_stats()[:2]
    writer.writerow(value)
