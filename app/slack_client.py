# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 21:17:05 2017

@author: Edmilson Santana
"""

from slackclient import SlackClient
from bitcoin_analysis import plot
import time

BOT_NAME = "zig"
API_TOKEN = ""
AT_BOT = "<@" + "U4XD64PBR" + ">"
READ_WEBSOCKET_DELAY = 1
START_GET = "START"
STOP = "STOP"

slack_client = SlackClient(API_TOKEN)
      
      
def handle_command(command, channel):
    
    parameters = command.split(" ")
    file_path = plot(parameters[0].strip(), parameters[1].strip())
    upload_file(file_path, channel)
        
def upload_file(file_path, channel):
        
        ret = slack_client.api_call("files.upload",
                                         channels=channel,
                                         file=open(file_path, 'rb'))
        if not 'ok' in ret or not ret['ok']:
            print('fileUpload failed %s', ret['error'])
            
def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None             
        

        
def get_bot_id():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)
      
        
if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("Bot connected and running!")
        
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                try:
                    handle_command(command, channel)
                except Exception as e:
                    print(e)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
    
    
    
