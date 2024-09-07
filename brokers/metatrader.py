from datetime import datetime
import requests
import json
import uuid
import time as tt
import pandas as pd
import matplotlib.pyplot as plt
import stomp
import json

def metatrader_import(inputid, inputpassword, inputtype, inputpassphrase):    
    "type message 'connecting account from metatrader'"
    login = inputid
    password = inputpassword
    meta_type = inputtype
    passphrase = inputpassphrase
    headers = {
        "Content-Type": "application/json",
        "auth-token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI0NjdmNDc0YWIzMzk3ZmQ0NTZjMWU0YzFlYzE1YmEzMiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjQ2N2Y0NzRhYjMzOTdmZDQ1NmMxZTRjMWVjMTViYTMyIiwiaWF0IjoxNzA3NjY4MDI4fQ.UpXWWnXzBQ0r1-FzmAg0dRvE_n4X7MdftJsl2kKvlmooF8oUWrJqibtAo-F2Kq2n4uUAePoTXuefgC53Cg1K1jnhfsNSgJO640OV4y38bGRGc_ezDP3fcW_6yq2RD1gxdt_Z4Ntw6oZUj7DLyw9gvhV0nL9-m0wN-z1X5F_hnaWbd_Q_3oNlP3r1Kk5gDwnyS3F8iYc6fimVcYp0b-m9yeKGgEKu40Ce14Rq7eRoqEZozeYoU1owWldFBD-xDA6CWl9aoT7ODH6x4Mc9AFcorsbxTl9UmyR5thmzr8DpV2OWeQlAK7VFmJ1L8d9Ih08XrSZYhX5tetfUXZlL-sdeqYH67Rn5LBMIfGyt1PxEQpSL8OuZfdB4vO6lm6fEYne2T0h6qjVNVYXTu03U_NdxGM9ShsW71i_08wYpv0AV3z4MRTB0DTFXmz3E2NzxSbCMJNMkIyggrIU8DvF3IUifkFHmLTwZI2U7igMIGf45CcFUDPdD0jaiiqP4tJc-xPl17ZTE5ZINzG0_yRWpKv8B8VX9egnJ65RTvYqdUDNyZtuM9kXgFT23KaXQs7MdfwuDv1yQDr-CHSMVLHVHduSrj0h0FnEc8ojvYn628fZG8eaj70srY6Gk_LueQTh8s8rRZHUQjPW6_R3UVTep9XaYUHdwaNGH8eTYa7FgJOGax9E"
        # "instrument":'SPX500_USD'
    }
    symbol_contract = {}
    # retrieve MetaApi MetaTrader account trades
    response = requests.request(
        "GET", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts?offset=0&limit=1000&endpointVersion=v1", headers=headers).json()
    isCreated = False

    if response != []:
        for trade in response:
            if trade['login'] == login:
                isCreated = True
                account = trade['_id']
                response = requests.request(
                    "GET", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts/"+account, headers=headers).json()
                key = response['version']
                if key == 4:
                    meta_type = 'mt4'
                else:
                    meta_type = 'mt5'
                if response["state"] == "UNDEPLOYED":
                    requests.request("POST", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts/" +
                                     account+"/deploy?executeForAllReplicas=true", headers=headers)
                    cont = 0
                    response = requests.request(
                        "GET", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts/"+account, headers=headers).json()
                    while response["connectionStatus"] != "CONNECTED" and cont != 20:
                        cont += 1
                        tt.sleep(40)
                        response = requests.request(
                            "GET", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts/"+account, headers=headers).json()
                        if response["connectionStatus"] == "CONNECTED":
                            break
                break

    # servers=['GrowthNext-Demo','FinotiveMarkets-Live']
    if not isCreated:
        if passphrase and login and password and meta_type:
            params = {
                "name": 'test',
                "login": login,
                "server": passphrase,
                "application": "MetaApi",
                "region": "new-york",
                "reliability": "high",
                "resourceSlots": 1,
                "type": "cloud-g2",
                "metastatsApiEnabled": True,
                "magic": 0,
                "quoteStreamingIntervalInSeconds": 2.5,
                "manualTrades": False,
                "password": password,
                "platform": meta_type
            }

        data = json.dumps(params)

        res = json.loads(data)
        transaction = str(uuid.uuid4()).replace('-', '')
        headers = {
            "auth-token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI0NjdmNDc0YWIzMzk3ZmQ0NTZjMWU0YzFlYzE1YmEzMiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjQ2N2Y0NzRhYjMzOTdmZDQ1NmMxZTRjMWVjMTViYTMyIiwiaWF0IjoxNzA3NjY4MDI4fQ.UpXWWnXzBQ0r1-FzmAg0dRvE_n4X7MdftJsl2kKvlmooF8oUWrJqibtAo-F2Kq2n4uUAePoTXuefgC53Cg1K1jnhfsNSgJO640OV4y38bGRGc_ezDP3fcW_6yq2RD1gxdt_Z4Ntw6oZUj7DLyw9gvhV0nL9-m0wN-z1X5F_hnaWbd_Q_3oNlP3r1Kk5gDwnyS3F8iYc6fimVcYp0b-m9yeKGgEKu40Ce14Rq7eRoqEZozeYoU1owWldFBD-xDA6CWl9aoT7ODH6x4Mc9AFcorsbxTl9UmyR5thmzr8DpV2OWeQlAK7VFmJ1L8d9Ih08XrSZYhX5tetfUXZlL-sdeqYH67Rn5LBMIfGyt1PxEQpSL8OuZfdB4vO6lm6fEYne2T0h6qjVNVYXTu03U_NdxGM9ShsW71i_08wYpv0AV3z4MRTB0DTFXmz3E2NzxSbCMJNMkIyggrIU8DvF3IUifkFHmLTwZI2U7igMIGf45CcFUDPdD0jaiiqP4tJc-xPl17ZTE5ZINzG0_yRWpKv8B8VX9egnJ65RTvYqdUDNyZtuM9kXgFT23KaXQs7MdfwuDv1yQDr-CHSMVLHVHduSrj0h0FnEc8ojvYn628fZG8eaj70srY6Gk_LueQTh8s8rRZHUQjPW6_R3UVTep9XaYUHdwaNGH8eTYa7FgJOGax9E",
            "transaction-id": transaction
        }
        try:
            response = requests.request(
                "POST", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts", headers=headers, json=params).json()
            if 'error' in response:
                return {"error": "Error connecting account, please verify your credentials"}
            account = response['id']
            tt.sleep(30)
            # print('get spot order')
            headers = {
                "Content-Type": "application/json",
                "auth-token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI0NjdmNDc0YWIzMzk3ZmQ0NTZjMWU0YzFlYzE1YmEzMiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjQ2N2Y0NzRhYjMzOTdmZDQ1NmMxZTRjMWVjMTViYTMyIiwiaWF0IjoxNzA3NjY4MDI4fQ.UpXWWnXzBQ0r1-FzmAg0dRvE_n4X7MdftJsl2kKvlmooF8oUWrJqibtAo-F2Kq2n4uUAePoTXuefgC53Cg1K1jnhfsNSgJO640OV4y38bGRGc_ezDP3fcW_6yq2RD1gxdt_Z4Ntw6oZUj7DLyw9gvhV0nL9-m0wN-z1X5F_hnaWbd_Q_3oNlP3r1Kk5gDwnyS3F8iYc6fimVcYp0b-m9yeKGgEKu40Ce14Rq7eRoqEZozeYoU1owWldFBD-xDA6CWl9aoT7ODH6x4Mc9AFcorsbxTl9UmyR5thmzr8DpV2OWeQlAK7VFmJ1L8d9Ih08XrSZYhX5tetfUXZlL-sdeqYH67Rn5LBMIfGyt1PxEQpSL8OuZfdB4vO6lm6fEYne2T0h6qjVNVYXTu03U_NdxGM9ShsW71i_08wYpv0AV3z4MRTB0DTFXmz3E2NzxSbCMJNMkIyggrIU8DvF3IUifkFHmLTwZI2U7igMIGf45CcFUDPdD0jaiiqP4tJc-xPl17ZTE5ZINzG0_yRWpKv8B8VX9egnJ65RTvYqdUDNyZtuM9kXgFT23KaXQs7MdfwuDv1yQDr-CHSMVLHVHduSrj0h0FnEc8ojvYn628fZG8eaj70srY6Gk_LueQTh8s8rRZHUQjPW6_R3UVTep9XaYUHdwaNGH8eTYa7FgJOGax9E"
                # "instrument":'SPX500_USD'
            }
            response = requests.request(
                "GET", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts/"+account, headers=headers).json()

            cont = 0

            while response["connectionStatus"] != "CONNECTED" and cont != 20:
                cont += 1
                """
                  if cont==6:
                      self.deleteAccount()
                      response = requests.request("POST", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts", headers=headers,json=params).json()
                      self.account=response['id']   
                  """
                tt.sleep(30)
                response = requests.request(
                    "GET", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts/"+account, headers=headers).json()
                if response["connectionStatus"] == "CONNECTED":
                    "type message 'connection success'"
                    break
                if cont == 1:
                    response = requests.request(
                        "POST", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts", headers=headers, json=params).json()
                    account = response['id']
                    response = requests.request(
                        "GET", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts/"+account, headers=headers).json()

        except Exception as err:
            "type message wrong creating the account"
            print(err)
            return {"success": False, "error": "Error occured"}
    return {"success": True}
    # get_orders = get_metatrader_orders(login)
    # if "value" in get_orders:
    #     trade_data = extract_data(
    #         get_orders["value"], login, get_orders["contracts"])
    #     return {'trades': trade_data}
    # else:
    #     return {"error": get_orders["error"]}


def get_metatrader_orders(inputid):   
    login = inputid
    orders = []
    symbol_contract = {}
    "type message 'Get orders from metatrader'"
    # print('get spot order')
    headers = {
        "Content-Type": "application/json",
        "auth-token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI0NjdmNDc0YWIzMzk3ZmQ0NTZjMWU0YzFlYzE1YmEzMiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjQ2N2Y0NzRhYjMzOTdmZDQ1NmMxZTRjMWVjMTViYTMyIiwiaWF0IjoxNzA3NjY4MDI4fQ.UpXWWnXzBQ0r1-FzmAg0dRvE_n4X7MdftJsl2kKvlmooF8oUWrJqibtAo-F2Kq2n4uUAePoTXuefgC53Cg1K1jnhfsNSgJO640OV4y38bGRGc_ezDP3fcW_6yq2RD1gxdt_Z4Ntw6oZUj7DLyw9gvhV0nL9-m0wN-z1X5F_hnaWbd_Q_3oNlP3r1Kk5gDwnyS3F8iYc6fimVcYp0b-m9yeKGgEKu40Ce14Rq7eRoqEZozeYoU1owWldFBD-xDA6CWl9aoT7ODH6x4Mc9AFcorsbxTl9UmyR5thmzr8DpV2OWeQlAK7VFmJ1L8d9Ih08XrSZYhX5tetfUXZlL-sdeqYH67Rn5LBMIfGyt1PxEQpSL8OuZfdB4vO6lm6fEYne2T0h6qjVNVYXTu03U_NdxGM9ShsW71i_08wYpv0AV3z4MRTB0DTFXmz3E2NzxSbCMJNMkIyggrIU8DvF3IUifkFHmLTwZI2U7igMIGf45CcFUDPdD0jaiiqP4tJc-xPl17ZTE5ZINzG0_yRWpKv8B8VX9egnJ65RTvYqdUDNyZtuM9kXgFT23KaXQs7MdfwuDv1yQDr-CHSMVLHVHduSrj0h0FnEc8ojvYn628fZG8eaj70srY6Gk_LueQTh8s8rRZHUQjPW6_R3UVTep9XaYUHdwaNGH8eTYa7FgJOGax9E"
        # "instrument":'SPX500_USD'
    }

    response = requests.request(
        "GET", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts?offset=0&limit=1000&endpointVersion=v1", headers=headers).json()
    if response != []:
        for trade in response:
            if trade['login'] == login:
                region = trade['region']
                account = trade['_id']
                symbols = requests.request(
                    "GET", "https://mt-client-api-v1.new-york.agiliumtrade.ai/users/current/accounts/"+account+"/symbols", headers=headers).json()
                for symbol in symbols:
                    symbol_info = requests.request(
                        "GET", "https://mt-client-api-v1.new-york.agiliumtrade.ai/users/current/accounts/"+account+"/symbols/"+symbol+"/specification", headers=headers).json()
                    symbol_contract[symbol] = symbol_info["contractSize"]
                # print(symbol_contract)
                key = trade['version']
                if key == 4:
                    meta_type = 'mt4'
                else:
                    meta_type = 'mt5'
                    break

    startDate = '2000-01-01'

    now = datetime.now()
    endDate = now.strftime('%Y-%m-%d')
    startHora = '%2000%3A00%3A00.000'
    endHora = '%2023%3A59%3A59.000'

    # url1='https://mt-client-api-v1.new-york.agiliumtrade.ai/users/current/accounts/'+self.account+'/history-deals/time/'+startDate+startHora+'/'+endDate+endHora+'?offset='+offset

    # url2='https://metastats-api-v1.new-york.agiliumtrade.ai/users/current/accounts/'+self.account+'/historical-trades/'+startDate+startHora+'/'+endDate+endHora+'?offset='+offset+'&updateHistory=true'

    url3 = 'https://mt-client-api-uzjylcntlrgwy9nc.new-york.agiliumtrade.ai/users/current/accounts/'+account+'/positions'

    try:
     # response = requests.request("POST", "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts", headers=headers,json=params).json()
     # r = requests.get(url="https://mt-client-api-uzjylcntlrgwy9nc.new-york.agiliumtrade.ai/users/current/accounts/"+self.account+"/connected",headers=headers).json()
        offset = 0
        paginated = True
        ordenesDeals = []
        paramQuery = {
            'limit': 2000,
            'offset': offset
        }
        while (paginated):
            r = requests.get(url='https://mt-client-api-v1.'+region+'.agiliumtrade.ai/users/current/accounts/'+account +
                             '/history-deals/time/'+startDate+startHora+'/'+endDate+endHora, headers=headers, params=paramQuery).json()
            offset += len(r)
            paramQuery = {
                'limit': 2000,
                'offset': offset
            }
            if r != []:
                for i in r:
                    ordenesDeals.append(i)
            else:
                paginated = False

        offset = 0
        paginated = True
        ordenesTrades = []
        paramQuery = {
            'limit': 2000,
            'offset': offset
        }
        while (paginated):
            r2 = requests.get(url='https://metastats-api-v1.'+region+'.agiliumtrade.ai/users/current/accounts/'+account+'/historical-trades/' +
                              startDate+startHora+'/'+endDate+endHora+'?updateHistory=true', headers=headers, params=paramQuery).json()
            if 'trades' in r2:
                offset += len(r2['trades'])
                paramQuery = {
                    'limit': 2000,
                    'offset': offset
                }
                if r2['trades'] != []:
                    for i in r2['trades']:
                        ordenesTrades.append(i)
                else:
                    paginated = False
            else:
                paginated = False

        """
            r3 = requests.get(url=url3,headers=headers).json()
            
            
            if r3 !=[]:
             for k in r3:
              orden={}
              if self.broker.broker_id==128: 
               orden['position']=k['id']
              else:
               orden['ticket']=k['id']
              orden['open_time']=k['time']
              orden['type']='Buy' if 'POSITION_TYPE_BUY' in k['type'] else 'Sell'
              orden['size']=str(k['volume']) 
              orden['item']=k['symbol']
              orden['open_price']=str(k['openPrice']) 
              orden['close_time']=k['updateTime'] if 'updateTime' in k else ''
              orden['closed_price']=str(k['currentPrice'])  if 'currentPrice' in k else ''
              orden['taxes']=str(k['taxes'])  if 'taxes' in k else '0.0'
              orden['profit']=str(k['profit'])
              orden['commission']=str(k['commission'])
              orden['swap']=str(k['swap'])
              orden['sl']=k['stopLoss'] if 'stopLoss' in k else 0
              orden['tp']=k['takeProfit'] if 'takeProfit' in k else 0
              self.orders.append(orden)
              """
        count = 0
        c = 0
        """
            if ordenesTrades !=[]:  
                self.orders=ordenesTrades
                self.save_files(file_type='json')
            if ordenesDeals !=[]: 
                self.orders=ordenesDeals                 
                self.save_files(file_type='json')
            self.orders=[]
            broker=self.get_broker_key()
            """
        if ordenesTrades != []:
            for i in ordenesTrades:
                count += 1
                c += 1
                "type message 'Get orders from metatrader'"
                try:
                    comission = 0.0
                    swap = 0.0
                    count = 0
                    countBuy = 0
                    openPrice = 0.0
                    countSell = 0
                    closePrice = 0.0
                    orden = {}
                    orden['id'] = str(i['_id']).split("+")[1]
                    if meta_type == 'mt5':
                        orden['position'] = i['positionId'] if "positionId" in i else ""
                    else:
                        orden['ticket'] = i['positionId'] if "positionId" in i else ""
                    orden['open_time'] = i['openTime']
                    orden['type'] = 'Buy' if 'DEAL_TYPE_BUY' in i['type'] else 'Sell'
                    orden['size'] = str(i['volume']) if "volume" in i else ""
                    orden['item'] = i['symbol'] if "symbol" in i else ""
                    orden['open_price'] = str(
                        i['openPrice']) if "openPrice" in i else ""
                    orden['close_time'] = i['closeTime']
                    orden['closed_price'] = str(
                        i['closePrice']) if "closePrice" in i else ""
                    orden['taxes'] = str(i['taxes']) if 'taxes' in i else '0.0'
                    if "marketValue" not in i:
                        continue
                    orden['profit'] = str(
                        i['marketValue']) if "marketValue" in i else ""
                except Exception as err:
                    # print(err)
                    pass
                if ordenesDeals != []:
                    for j in ordenesDeals:
                        if 'positionId' in j:
                            if orden['id'] == j['positionId'] and (j['entryType'] == "DEAL_ENTRY_OUT" or j['entryType'] == "DEAL_ENTRY_IN"):
                                count += 1
                                comission += float(j['commission'])
                                swap += float(j['swap'])
                                if j['entryType'] == "DEAL_ENTRY_IN":
                                    countBuy += 1
                                    openPrice += float(j['price'])
                                if j['entryType'] == "DEAL_ENTRY_OUT":
                                    countSell += 1
                                    closePrice += float(j['price'])
                                if count == 1:
                                    orden['magic'] = j['magic']
                                    orden['sl'] = j['stopLoss'] if 'stopLoss' in j else 0
                                    orden['tp'] = j['takeProfit'] if 'takeProfit' in j else 0
                                orden['commission'] = str(comission)
                                orden['swap'] = str(swap)
                    if 'commission' not in orden:
                        orden['commission'] = str(0.0)
                        orden['swap'] = str(0.0)
                    if openPrice != 0.0 and countBuy != 0:
                        orden['open_price'] = str(openPrice/countBuy)
                    if closePrice != 0.0 and countSell != 0:
                        orden['closed_price'] = str(closePrice/countSell)
                    orders.append(orden)

        return {"success": True, "value": orders, "contracts": symbol_contract}

    except Exception as err:
        print(err)
        "type message 'Error when obtaining the orders, verify that your account is connected to the broker'"
        tt.sleep(5)
        return {"success": False, "error": "Error when obtaining the orders, verify that your account is connected to the broker"}


def extract_data(orders, loginId, contract):
    return_value = []
    data=[]
    for trade in orders:
        if float(trade["profit"]) > 0:
            status = "WIN"
            if float(trade["open_price"]) > float(trade["closed_price"]):
                side = "SHORT"
            else:
                side = "LONG"
        else:
            status = "LOSS"
            if float(trade["open_price"]) < float(trade["closed_price"]):
                side = "SHORT"
            else:
                side = "LONG"
        instrument = '$' + trade["item"]
        if side == "LONG":
            action = "Buy"
            action_2 = "Sell"
        else:
            action = "Sell"
            action_2 = "Buy"
            trade['size'] = "-" + trade['size']
        contract_size = contract[trade["item"]]
        if contract_size >= 100:
            pips = (float(trade["closed_price"]) -
                    float(trade["open_price"])) * float(trade["size"]) * contract_size
            valueP = 100
        else:
            pips = (float(trade["closed_price"]) -
                    float(trade["open_price"])) * float(trade["size"]) * contract_size * contract_size
            valueP = contract_size
        if action == "Buy":
            returnP = abs(float(trade["profit"]) * valueP * 500 / float(trade["open_price"]) / (
                float(trade["profit"]) / abs(pips)) / float(trade["size"]) / contract_size)
        else:
            returnP = abs(float(trade["profit"]) * valueP * 500 / float(trade["closed_price"]) / (
                float(trade["profit"]) / abs(pips)) / float(trade["size"]) / contract_size)
        if float(trade["profit"]) < 0:
            returnP = 0 - returnP
        return_value.append(
            {"account_id": loginId, "broker": "Metatrader", "trade_id": trade["id"], "status": status, "open_date": trade["open_time"], "symbol": instrument, "entry": trade["open_price"], "exit": trade["closed_price"], "size": trade["size"], "pips": str(format(pips, '.5f')), "ret_pips": str(format(float(trade["profit"]) / abs(pips), '.10f')), "ret": trade["profit"], "ret_percent": str(format(returnP, '.4f')), "ret_net": str(format(float(trade["profit"]) + float(trade["commission"]) + float(trade["swap"]), '.10f')), "side": side, "setups": "", "mistakes": "", "subs": [{"action": action, "spread": "SINGLE", "type": "FOREX", "date": trade["open_time"], "size": str(abs(float(trade["size"]))), "position": trade["size"], "price": trade["open_price"]}, {"action": action_2, "spread": "SINGLE", "type": "FOREX", "date": trade["close_time"], "size": str(abs(float(trade["size"]))), "position": "0", "price": trade["closed_price"]}]})
    #data=return_value
    #data_ai(data)
    return return_value

def pie_chart(df,col, title):
    """
    Parametros:
    ----------
    df : pandas dataframe
    col (string): nombre de la columna del dataframe 
    title (string): título del gráfico 
    
    Resultado:
    -------
    Despliega un gráfico de torta con las etiquetas y la proporción 
    (%) de los datos
    """
    counts = df[col].value_counts()
    counts.plot(kind='pie',autopct='%.0f%%',fontsize=20, figsize=(6, 6))
    plt.title(title)
    plt.show() 
    
def pie_chart_2(df,col, title):
    """
    Parametros:
    ----------
    df : pandas dataframe
    col (string): nombre de la columna del dataframe 
    title (string): título del gráfico 
    
    Resultado:
    -------
    Despliega un gráfico de torta con las etiquetas y la proporción 
    (%) de los datos
    """
    counts = df[col].sum()
    counts.plot(kind='pie',autopct='%.0f%%',fontsize=20, figsize=(6, 6))
    plt.title(title)
    plt.show() 
    
def data_ai(orders):
    print(orders)
    df=pd.DataFrame(orders)
    
    #df=df.drop(0)
    #print(df[5])
    #print(df[6])
    df['open_date'] = df['open_date'].astype(str)
    #df[3] = pd.datetime.strptime(df[3], '%b %d, %Y')
    df['open_date']=pd.to_datetime(df['open_date']).dt.date
    df['open_date'] = pd.to_datetime(df['open_date'], errors='coerce')
    #print(df.head())
    #print(df.info())
    dias=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    df["dia"] = df['open_date'].dt.dayofweek
    df["dia"] = df["dia"].astype(str)
    df["dia"] = df["dia"].str.replace('0', 'Monday')
    df["dia"] = df["dia"].str.replace('1', 'Tuesday')
    df["dia"] = df["dia"].str.replace('2', 'Wednesday')
    df["dia"] = df["dia"].str.replace('3', 'Thursday')
    df["dia"] = df["dia"].str.replace('4', 'Friday')
    df["dia"] = df["dia"].str.replace('5', 'Saturday')
    df["dia"] = df["dia"].str.replace('6', 'Sunday')
    df_win = df[df['status'] == 'WIN']
    df_loss = df[df['status'] == 'LOSS']
    print(df_win)
    #recurrencia de los dias en los trades ganadores
    df2 = df_win.groupby(['dia'], as_index=False).size()
    pie_chart(df_win,'dia','Proporción de las muestras benignas/malignas')
    print(df2)
    #decir el dia donde mas es recurrente la ganancia
    dia_mas_ganador=str(df2.iloc[df2['size'].idxmax()][0])
    #hacer diagrama de torta con la recurrencia de los dias ganadores
    print(df['ret'])
    df_win['ret']=df_win['ret'].astype(float)
    print(df_win['ret'])
    dia_mas_profit = df_win.groupby('dia').agg({'ret': 'sum'})
    
    dia_mas_profit.plot(kind='bar', legend=None)
    plt.title('Ventas a lo largo del tiempo')
    plt.xlabel('dia')
    plt.ylabel('retorno')
    plt.tight_layout();
    plt.show()
    valor=float(dia_mas_profit.max())
    dia_mas_profit['ret']=dia_mas_profit['ret'].astype(float)
    dia_mas_profit = dia_mas_profit[dia_mas_profit['ret'] == valor]
    print(dia_mas_profit)
    #Recurrencia de los symbolos winners
    symbolos_winners = df_win.groupby(['symbol'], as_index=False).size()
    pie_chart(df_win,'symbol','recurrencia de los activos winners')
    print(df2)
    symbolo_recurrente_winners=str(symbolos_winners.iloc[symbolos_winners['size'].idxmax()][0])
    
    symbolo_mas_profit = df_win.groupby('symbol').agg({'ret': 'sum'})
    
    symbolo_mas_profit.plot(kind='bar', legend=None)
    plt.title('retorno total por activo')
    plt.xlabel('symbol')
    plt.ylabel('retorno')
    plt.tight_layout();
    plt.show()
    
    valor=float(symbolo_mas_profit.max())
    symbolo_mas_profit['ret']=symbolo_mas_profit['ret'].astype(float)
    dia_mas_profit = symbolo_mas_profit[symbolo_mas_profit['ret'] == valor]
    print(dia_mas_profit)
    
    symbolos_dias_winners = df_win.groupby(['symbol','dia'], as_index=False).size()
    symbolos_dias_winners_mas_profit = df_win.groupby(by=['symbol', 'dia']).agg({'ret': 'sum'})
    
    symbolos_dias_winners_mas_profit.plot(kind='bar', legend=None)
    plt.title('retorno total por dia y simbolo')
    plt.xlabel('symbol')
    plt.ylabel('retorno')
    plt.tight_layout();
    plt.show()
    
    print(symbolos_dias_winners)
    print(symbolos_dias_winners_mas_profit)
    valor=float(symbolos_dias_winners_mas_profit.max())
    symbolo_dia_winners_mas_recurrente = symbolos_dias_winners_mas_profit[symbolos_dias_winners_mas_profit['ret'] == valor]
    print(symbolo_dia_winners_mas_recurrente)
    #pie_chart(df_win,'symbol','recurrencia de los activos winners')
    
    
    df['open_date'] = df['open_date'].astype(str)
    df['hour']=pd.to_datetime(df['open_date']).dt.hour
    #df['open_date'] = pd.to_datetime(df['open_date'], errors='coerce')
    print(df['hour'])
    df2 = df.groupby(['hour'], as_index=False).size()
    df_hour=df2.sort_values(by=["size"],axis=0,ascending=False)
    print(df_hour)
    print(df_hour.iloc[0]['hour'])
    print(df_hour.iloc[1]['hour'])
    print("tienes mas ganancias entre estos horarios para la fecha de apertura "+str(df_hour.iloc[1]['hour'])+" y "+str(df_hour.iloc[0]['hour'])+" horas")
    pie_chart(df,'hour','Proporción de las muestras benignas/malignas')
    print(df2)
    print("")
    
    
    df_orders_subs=df['subs']
    lista_subs=df_orders_subs.values
    lista_fechas=[]
    for i in lista_subs:
        if i[0]['action']=='Sell':
            my_diccionario= {'hour_open': i[1]['date'], 'hour_close': i[0]['date']}
            lista_fechas.append(my_diccionario)
        else:
            my_diccionario= {'hour_open': i[0]['date'], 'hour_close': i[1]['date']}
            lista_fechas.append(my_diccionario)
    
    df_fechas=pd.DataFrame(lista_fechas)
    print(df_fechas.head(5))
    
    print("")
    
    df_fechas['hour_open']=pd.to_datetime(df_fechas['hour_open']).dt.hour
    df_fechas['hour_close']=pd.to_datetime(df_fechas['hour_close']).dt.hour
    
    
    print(df_fechas.head(5))
    print("")
    
    
    df2 = df_fechas.groupby(by=['hour_open','hour_close'], as_index=False).size()
    print(df2)
    df_hour=df2.sort_values(by=["size"],axis=0,ascending=False)
    print("tienes mas ganancias entre las "+str(df_hour.iloc[0]['hour_open'])+" horas y "+str(df_hour.iloc[0]['hour_close'])+" horas")
    