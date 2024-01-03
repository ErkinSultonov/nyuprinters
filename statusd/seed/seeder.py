import os
import sys
import json
import random

models_dir = os.path.abspath(os.path.join(os.path.dirname(__name__), '../statusd/models'))
sys.path.append(models_dir)

from dbmodel import app, db, Printer, Location, Settings
from sqlalchemy.sql import func

with app.app_context():
    db.drop_all()
    db.create_all()

with open('seed/locations.json', 'r') as file:
    location_sample_data = json.load(file)

with open('seed/printers.json', 'r') as file:
    printer_sample_data = json.load(file)

with open('seed/settings.json', 'r') as file:
    settings_sample_data = json.load(file)

printers = []
locations = []
settings = []

for raw_resp in location_sample_data:
    loc = Location(name=raw_resp['name'], short_name=raw_resp['short_name'], description=raw_resp['description'])
    locations.append(loc)

with app.app_context():
    db.session.add_all(locations)
    db.session.commit()

with app.app_context():
    locations = Location.query.all()

for raw_resp in printer_sample_data:
    resp = raw_resp['response']
    if resp.get('status') == 'success':
        p = resp['message']
        printer = Printer(name=p['name'],
                          model=p['model'],
                          ip_address=p['host'],
                          last_status=json.dumps(p),
                          last_online=func.now(),
                          location=random.choice(locations)
                          )

    else:
        resp = raw_resp['request']
        printer = Printer(name=f"Printer {resp['ip']}",
                          ip_address=resp['ip'],
                          location=random.choice(locations)
                          )

    printers.append(printer)

with app.app_context():
    db.session.add_all(printers)
    db.session.commit()

for pref in settings_sample_data:
    setting = Settings(key=pref['key'],
                       value=pref['value'],
                       default_value=pref['default_value'],
                       type=pref['type'],
                       description=pref['description']
                       )
    settings.append(setting)

with app.app_context():
    db.session.add_all(settings)
    db.session.commit()
