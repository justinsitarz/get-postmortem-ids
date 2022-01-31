import requests
import json
import pandas as pd

# Steps to retrieve session token for 'cookie' variable below (in Chrome - other browsers will differ):
# 1) Click into Chrome Settings >> 'Security and Privacy' >> 'Cookie and other site data' >> 'See all cookies and site data'
# 2) Search 'opsgenie', click into result for 'app.opsgenie.com'
# 3) Expand 'cloud.session.token', and copy the value stored in 'Content'
# 4) Either a) enter the copied value in the 'cookie' variable on line 13, or b) enter the copied value when prompted after executing the script

api_key = '' # retrieve key with global access and read permissions from API Key Management
account_name = '' # i.e. 'my-account' if your Opsgenie url is https://my-account.app.opsgenie.com
cookie = '' # see steps above
inc_url = "https://api.opsgenie.com/v1/incidents" # set as https://api.eu.opsgenie.com/v2/users/ if account is in the EU region
csv = "./postmortems.csv"


def get_incidents(url, api_headers):
    incident_ids = []
    try:
        res = requests.get(url=inc_url,headers= api_headers)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)

    response = json.loads(res.text) 
    
    for r in response['data']:
        incident_ids.append(r['id'])

    while 'next' in response['paging']:
        next_url = str(response['paging']['next'])
        res = requests.get(url=next_url, headers=api_headers)
        response = json.loads(res.text)    
        for r in response['data']:
            incident_ids.append(r['id'])
    return incident_ids

def get_postmortem(account, incident_id, web_api_headers):
    url = "https://{}.app.opsgenie.com/webapi/postmortems/web/incident/{}".format(account, incident_id)
    res = requests.get(url=url, headers=web_api_headers)
    response = json.loads(res.text)
    if response.get("postmortemId"):
        return response["postmortemId"]
    else:
        return 0

def generate_csv(data):
    df = pd.DataFrame(data)
    df.to_csv(csv, sep=',', encoding='utf-8')

def main():
    global api_key
    global account_name
    global cookie
    global inc_url
    global csv

    if api_key == '':
        api_key = input("API key: ")
    if account_name == '':
        account_name = input("Account name: ")

    if cookie == '':
        cookie = 'cloud.session.token='
        cookie += input("Cookie (see script comments for where to retrieve): ")
    else:
        cookie = 'cloud.session.token=' + cookie

    api_headers = {'content-type': 'application/json','Authorization':'GenieKey ' + api_key}
    web_api_headers = {'content-type': 'application/json','cookie': cookie}

    incident_ids = get_incidents(inc_url, api_headers)
    print("Count of incidents: {}".format(len(incident_ids)))
    data = []

    for i in incident_ids:
        data.append({"Incident ID": i, "Postmortem ID": get_postmortem(account_name, i, web_api_headers)})

    generate_csv(data)

if __name__ == '__main__':
    main()