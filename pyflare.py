#!/usr/bin/env pipenv-shebang
import json
import logging
import os
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = Path.home() / '.logs' / 'pyflare.log'
log_file.parent.mkdir(exist_ok=True)
ch = RotatingFileHandler(log_file, mode='a', maxBytes=102400, backupCount=2)
formatter = logging.Formatter('\n%(asctime)s - %(levelname)s - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
formatter.converter = time.gmtime
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.debug(log_file)


def getmyip():
    r = requests.get("https://api.ipify.org/")
    return r.text


class Cloudflare:
    def __init__(self, key):
        self.endpoint = "https://api.cloudflare.com/client/v4"
        self.headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

    def dns_records(self, zone_id):
        r = requests.get(self.endpoint + "/zones/" + zone_id + "/dns_records", headers=self.headers)
        r.raise_for_status()
        res_data = r.json()
        assert res_data['success'], 'Error in pulling the DNS records'
        return res_data

    def update_record(self, zone_id, record, ip_address):
        payload = {'type': record['type'], 'name': record['name'], 'content': ip_address,
                   'ttl': record['ttl'], 'proxied': record['proxied']}
        r = requests.put(self.endpoint + "/zones/" + zone_id + "/dns_records/" + record['id'], headers=self.headers,
                         data=json.dumps(payload))
        r.raise_for_status()
        res_data = r.json()
        assert res_data['success'], f'Error in updating the record {record}'
        return res_data

    def check_ip(self, zone_id):
        records = self.dns_records(zone_id)['result']
        ip_address = getmyip()
        for record in records:
            if ip_address != record['content']:
                self.update_record(zone_id, record, ip_address)
                logger.info(f'IP updated to {ip_address} for {record["name"]}')


if __name__ == '__main__':
    load_dotenv()
    try:
        cf = Cloudflare(os.environ['CLOUDFLARE_KEY'])
        cf.check_ip(os.environ['CLOUDFLARE_ZONE_ID'])
    except KeyError as error:
        logger.exception(f"Unable to find proper env variables please check the .env file")
    except IOError as error:
        logger.warning(error)
