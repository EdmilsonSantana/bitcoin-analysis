# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 21:17:05 2017

@author: Edmilson Santana
"""

from slackclient import SlackClient
from bitcoin_analysis import plot, has_trend_reversal
import time
from util import RepeatedTimer

BOT_NAME = "zig"
API_TOKEN = ""
AT_BOT = "<@" + "U4XD64PBR" + ">"
READ_WEBSOCKET_DELAY = 1

timers = []

COMMAND_START_NOTIFY = "notify"
COMMAND_STOP_NOTIFY = "stop"
COMMAND_PLOT = "plot"
NOTIFICATION_TIMEOUT = 15
NOTIFICATION_MESSAGE = "Ocorreu uma reversão de tendência para o cenário: %s %s %s %s"
MESSAGE_INVALID_PARAMETERS = "Parâmetros inválidos." 
MESSAGE_NOTIFICATIONS_REMOVED = "As notificações foram removidas"

slack_client = SlackClient(API_TOKEN)
      
      
def handle_command(command, channel):
    
    parameters = get_parameters(command)
    action = parameters[0]
    
    if(action == COMMAND_START_NOTIFY):
        send_message(channel, "Notificação adicionada.")
        timers.append(RepeatedTimer(NOTIFICATION_TIMEOUT, 
                                    send_notification, 
                                    channel,
                                    parameters[1],
                                    parameters[2],
                                    (parameters[3].upper(), 
                                     parameters[4].upper())))
        
    elif(action == COMMAND_STOP_NOTIFY):
        remove_notifications()
    elif(action == COMMAND_PLOT):
        file_path = plot(parameters[1], parameters[2])
        upload_file(file_path, channel)
        

def get_parameters(command):
    return [parameter.strip() for parameter in command.split(" ")]
    
    
def send_notification(channel, bitcoin_attr, bitcoin_freq, moving_averages):
    
    has_trend = has_trend_reversal(bitcoin_attr, 
                                   bitcoin_freq, 
                                   moving_averages)
    if(has_trend):
        send_message(channel, 
                     NOTIFICATION_MESSAGE % 
                     (bitcoin_attr, bitcoin_freq, 
                      moving_averages[0], moving_averages[1]))
    

def send_message(channel, message): 
   slack_client.api_call("chat.postMessage", 
                         channel=channel,
                         text=message)
   
def remove_notifications():
    for timer in timers:
        timer.stop()
        
    del timers[:]
    
    send_message(channel, MESSAGE_NOTIFICATIONS_REMOVED)
    
        
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
                    send_message(channel, MESSAGE_INVALID_PARAMETERS)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
    
    
    
