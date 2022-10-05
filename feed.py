#!/usr/bin/env python3.9

import requests
import yaml
import argparse
from datetime import datetime, date
import logging
from ics import Calendar, Event

logging.basicConfig(level=logging.ERROR)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='Enable debug mode')

options = parser.parse_args()

logger = logging.getLogger('waste_feed')
logger.setLevel(level=logging.INFO)

if options.debug:
  logger.setLevel(level=logging.DEBUG)

session = requests.Session()
session.headers['user-agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'

with open('config.yml', 'r') as config_data:
  config = yaml.load(config_data,
                     Loader=yaml.SafeLoader)


class WastePickup(Event):
  """Waste Pickup Event."""

  def __init__(self, date: date, type:str):
    super().__init__()
    if type.lower() in config['translations']:
      self.name = config['translations'][type.lower()]
    else:
      self.name = type
    self.begin = datetime.strptime(date, '%Y-%m-%d')
    self.make_all_day()


def get_waste_url(url: str) -> dict:
  url = url.replace('{identifier}', config['identifier'])\
    .replace('{street}', str(config['street']))
  logger.debug('Getting %s', url)
  return session.get(url).json()


descriptions = {description['identifier']: description['title'] for description in get_waste_url(config['descriptions_tpl'])}
pickups = get_waste_url(config['waste_pickups_tpl'])

calendar = Calendar()
for pickup in pickups:
  for list in ['garbages', 'onDemand']:
    for item in pickup[list]:
      calendar.events.add(WastePickup(
        pickup['date'],
        descriptions[item]
      ))


with open('feed.ics', 'w') as file:
  file.writelines(calendar)
