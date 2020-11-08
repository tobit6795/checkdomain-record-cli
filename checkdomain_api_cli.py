#!/usr/bin/python3
# encoding: utf8
#
# ============================================================================================
#          FILE: XXX.py
#         USAGE: ./XXX.py --help
#   DESCRIPTION:
#       OPTIONS:
#  REQUIREMENTS: python3.8 + libs:
#        AUTHOR: Tobias Kem (kem.tobias@gmail.com)
#  ORGANIZATION:
#       VERSION: 0.1
#       CREATED: 05.09.2020 13:38
#       CHANGES:
#
# ===========================================================================================

import argparse, json, requests, sys

token = ""
domain_id = ""

defaults={
         'type':'CNAME',
         'ttl':180,
         'priority':0,
         'value':''
        }
try:
    import pandas as pd
except ImportError:
    from pip._internal import main as pip
    pip(['install', '--user', 'pandas'])
    import pandas as pd

def get_cli_arguments():
    parser = argparse.ArgumentParser(
        description='')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--get-records',
                        default=None,
                        action='store_true',
                        dest='get_records',
                        help='')
    group.add_argument('--set-record',
                        default=None,
                        action='store_true',
                        dest='set_record',
                        help='')
    group.add_argument('--remove-record',
                        default=None,
                        action='store_true',
                        dest='remove_record',
                        help='')
    parser.add_argument('--record-name',
                        nargs='?', const=None,
                        dest='record_name',
                        default='None',
                        required='--set-record' in sys.argv or '--remove-record' in sys.argv,
                        help='')
    parser.add_argument('--record-type',
                        default=defaults['type'],
                        nargs='?', const=None,
                        dest='record_type',
                        help='')
    parser.add_argument('-ttl', '--time-to-live',
                        default=defaults['ttl'],
                        nargs='?', const=None,
                        dest='ttl',
                        help='')
    parser.add_argument('-pr', '--priority',
                        default=defaults['priority'],
                        nargs='?', const=None,
                        dest='priority',
                        help='')
    parser.add_argument('-rv', '--record_value',
                        default=defaults['value'],
                        nargs='?', const=None,
                        dest='record_value',
                        help='')
    args = {"args": parser.parse_args(), "help": parser.print_help}
    return args

args = get_cli_arguments()["args"]

class api_request():
    url = f"https://api.checkdomain.de/v1/domains/{domain_id}"
    headers = {
        'Authorization': "Bearer %s" % token,
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'User-Agent': ""
    }
    labels=['name', 'priority', 'ttl', 'type', 'value'] 

    def get_data(self, endpoint="/nameservers/records?limit=100"):
        url = self.url + endpoint
        response = requests.get(url, headers=self.headers, allow_redirects=False)
        data = response.json()['_embedded']['records'][5:None]
        return data
    
    def print_data(self):
        #print(json.dumps(self.get_data(), indent=4))
        df = pd.DataFrame(self.get_data(),columns=self.labels)
        print(df)

    def set_record(self, data, endpoint="/nameservers/records"):
        current=self.get_data()
        for i in range(len(current)):
            if data['name'] in current[i].values(): 
                print("Record %s already exists, exiting" %data['name'])
                exit(1)
        url = self.url + endpoint
        json_object = json.dumps(data, indent = 4)   
        response = requests.post(url, headers=self.headers, data=json_object, allow_redirects=False)
        if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
            print("Status-Code: %s => Something went wrong" %response.status_code)
        elif response.status_code == 201:
            print("Status-Code: %s => Created" %response.status_code)
        elif response.status_code == 204:
            print("Status-Code: %s => Updated" %response.status_code)
        else:
            print("Status-Code: %s => OK" %response.status_code)
        df = pd.DataFrame(self.get_data(),columns=self.labels)
        print(df.tail(1))

    def remove_record(self, data, endpoint="/nameservers/records"):
        current=self.get_data()
        for i in range(len(current)):
            if data['name'] in current[i].values(): 
                print("Record %s found and removed" %data['name'])
                found = True
                to_be_deleted = current[i]
                del current[i]
                df = pd.DataFrame(current, columns=self.labels).to_dict('r')
                json_object = json.dumps(df, indent=4)
                url = self.url + endpoint + "?root" + f"[{json_object}]" 
                response = requests.put(url, headers=self.headers, data=json_object)
                if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
                    print("Status-Code: %s => Something went wrong" %response.status_code)
                elif response.status_code == 201:
                    print("Status-Code: %s => Created" %response.status_code)
                elif response.status_code == 204:
#----not working
                    df = pd.DataFrame(to_be_deleted, columns=self.labels).to_dict('r')
#----
                    print('%s removed' %df)
                    print("Status-Code: %s => Updated" %response.status_code)
                else:
                    print("Status-Code: %s => OK" %response.status_code)
                exit(0)
            else:
                found = False
        if found == False:
            print('Record %s not found!' %data['name'])
            exit(1)

def main():
    client = api_request()
    data = {
        'name': args.record_name,
        'type': args.record_type,
        'ttl': args.ttl,
        'priority': args.priority,
        'value': args.record_value
    }
    if args.get_records == True:
        client.print_data()
    if args.set_record== True:
        client.set_record(data)
    if args.remove_record == True:
        client.remove_record(data)
    exit(0)

if __name__ == '__main__':
    main()
