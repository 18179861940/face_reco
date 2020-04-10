import requests


# 百度API key
client_id = 'xuEi2EgOsewf7ryhjZHlfRPx'  # ak
# 百度secret key
client_secret = 'W7tngvTsuL5bGKkuW8lo7UjN15tFq1Wl'  # sk


# 获取token方法
def getAccessToken():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' \
           + client_id + '&client_secret=' + client_secret
    response = requests.get(host)
    if response:
        tokenResult = response.json()
        access_token = tokenResult['access_token']
        return access_token
    return ""