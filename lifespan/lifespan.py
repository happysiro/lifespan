import os
import time
import requests
import argparse
import numpy as np
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--hostid', '-i', help='host id')
parser.add_argument('--start', '-s', help='first time to get metrics from mackrel')
parser.add_argument('--end', '-e', help='end time to get metrics from mackrel')
parser.add_argument('--deadline', '-d', help='deadline of disk capacity')
parser.add_argument('--partition_name', '-p', help='partition name')
args = parser.parse_args()

start = int(time.mktime(time.strptime(args.start, '%Y/%m/%d')))
end = int(time.mktime(time.strptime(args.end, '%Y/%m/%d')))

api_key = os.getenv("MACKEREL_API_KEY")
headers = {'X-Api-Key': api_key}
params  = {'name': f'filesystem.{args.partition_name}.used', 'from': start, 'to': end}

r = requests.get(
    f'https://mackerel.io/api/v0/hosts/{args.hostid}/metrics',
    headers=headers,
    params=params
)

if r.status_code == 401:
    print('environment variable MACKEREL_API_KEY is empty')
    exit(-1)

data = r.json()
x = [x['time']  for x in data['metrics']]
y = [y['value']/ 1024 / 1024 /1024 for y in data['metrics']]

# 最小二乗法で一次で係数を求める
np.polyfit(x, y, 1)

d = int(time.mktime(time.strptime(args.start, "%Y/%m/%d")))
for i in range(365):
    d = d + 86400
    if np.poly1d(np.polyfit(x, y, 1))(d) > int(args.deadline):
        print(time.strftime('%Y/%m/%d', time.gmtime(d)))
        exit(0)

print('this server will not die one year')
exit(0)
