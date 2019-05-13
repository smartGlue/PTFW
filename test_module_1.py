import pdb
import sys
import requests
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth
from requests.exceptions import ConnectionError
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def login_sso(username, pwd, url):
    # for ssl certificate verification
    sslverification = False

    session = requests.Session()
    session.auth = HttpNtlmAuth(username, pwd, session)
    headers = {'User-Agent': 'Mozilla/5.0 (compatible, MSIE 9.0, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}

    response = {}

    response = session.get(url, verify=sslverification, headers=headers)


    return response.status_code


def test_login():
    username = 'Administrator'
    pwd = '8Wi;JRpD9wm'
    url = 'https://win-4jqeli4m6ah.myeventarena.com/adfs/ls/IdpInitiatedSignon.aspx?loginToRp=https://ssomyeventarena-dev-ed.my.salesforce.com'
    status_value = 200
    assert status_value == login_sso(username, pwd, url)

def test_invalid_login():
    username = 'Administrator'
    pwd = '8WiJRpD9wm'
    url = 'https://win-4jqeli4m6ah.myeventarena.com/adfs/ls/IdpInitiatedSignon.aspx?loginToRp=https://ssomyeventarena-dev-ed.my.salesforce.com'
    status_value = 401
    assert status_value == login_sso(username, pwd, url)

def test_invalid_status():
    username = 'Administrator'
    pwd = '8WiJRpD9wm'
    url = 'https://win-4jqeli4m6ah.myeventarena.com/adfs/ls/IdpInitiatedSignon.aspx?loginToRp=https://ssomyeventarena-dev-ed.my.salesforce.com'
    status_value = 200
    assert status_value == login_sso(username, pwd, url)

def test_homepage():
    username = 'Administrator'
    pwd = '8Wi;JRpD9wm'
    url = 'https://win-4jqeli4m6ah.myeventarena.com/adfs/ls/IdpInitiatedSignon.aspx?loginToRp=https://ssomyeventarena-dev-ed.my.salesforce.com'
    json_data = get_assertion(username, pwd, url)
    status_value = 200
    assert status_value == post_call(json_data)


def get_assertion(username, pwd, url):
    
    #for ssl certificate verification
    sslverification = False

    session = requests.Session()
    session.auth = HttpNtlmAuth(username, pwd, session)
    headers = {'User-Agent': 'Mozilla/5.0 (compatible, MSIE 9.0, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
    
    responseObj = {}
    responseObj['url'] = url
    
    try:
        response = session.get(url, verify=sslverification, headers=headers)
        responseObj['code'] = response.status_code
        
        #if response is success
        if response.status_code == 200:
            responseObj['status'] = 'success'
        
            #parsing the response
            soup = BeautifulSoup(response.text, 'lxml')
            assertion = 'empty'
            form = soup.find_all('form')[0]
            post_url = form.get('action')
            responseObj['post_url'] = post_url

            for inputtag in soup.find_all('input'):
                if(inputtag.get('name') == 'SAMLResponse'):
                    assertion = inputtag.get('value')
                    responseObj['message'] = assertion
        elif response.status_code == 401:
            #response failed due to authentication
            responseObj['status'] = 'error'
            responseObj['message'] = 'Invalid Username and Password'
            responseObj['post_url'] = 'None'
    except ConnectionError as e:
        #unable to connect to sso server
        responseObj['code'] = 404
        responseObj['status'] = 'error'
        responseObj['message'] = 'Unable to connect to SSO server'
    
    
    json_object = json.dumps(responseObj)
    return json_object

def post_call(json_data):
    call_data = json.loads(json_data)
    #print call_data["post_url"]
    #print call_data["message"]

    if call_data['status'] == 'success':
        data = {'SAMLResponse' : call_data["message"]}

        r = requests.post(url = call_data["post_url"], data=data)

    return r.status_code


test_login()
test_homepage()
