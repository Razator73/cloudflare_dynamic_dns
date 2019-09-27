#! /usr/bin/python
import json
import os
from pathlib import Path

import requests


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
                print(f'IP updated to {ip_address} for {record["name"]}')
            else:
                print(f'{record["name"]} IP ok')


if __name__ == '__main__':
    creds_path = Path.home() / '.creds' / 'cloudflare.json'
    try:
        with open(creds_path) as json_data_file:
            config = json.load(json_data_file)
        cf = Cloudflare(config['key'])
        cf.check_ip(config['zone_id'])
    except IOError:
        print("Unable to find config file.")
