# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 21:17:05 2017

@author: Edmilson Santana
"""

from slackclient import SlackClient
from cryptocurrency_analysis import get_trend, get_currencies
import time
from helper import RepeatedTimer

BOT_NAME = "zig"
API_TOKEN = ""
AT_BOT = "<@" + "U4XD64PBR" + ">"
READ_WEBSOCKET_DELAY = 1

timers = []

COMMAND_SEPARATOR = " "
COMMAND_START_NOTIFY = "notify"
COMMAND_STOP_NOTIFY = "stop"
COMMAND_INITIALIZE = "initialize"
NOTIFICATION_TIMEOUT = 60
ADDED_ALERT_MESSAGE = "Uma alerta foi adicionado para o cenário: %s %s %s"
NOTIFICATION_MESSAGE = "Ocorreu uma %s para o cenário: %s %s %s"
MESSAGE_INVALID_PARAMETERS = "Um erro ocorreu ou os parâmetros informados são inválidos." 
MESSAGE_NOTIFICATIONS_REMOVED = "As notificações foram removidas"

slack_client = SlackClient(API_TOKEN)
      
      
def handle_command(command, channel):
    
    parameters = get_parameters(command)
    action = parameters.get("action")
    time_frame = parameters.get("time_frame")
    periods = parameters.get("periods")
    currency = parameters.get("currency")
    
    if(action == COMMAND_START_NOTIFY):
        
        timers.append(RepeatedTimer(NOTIFICATION_TIMEOUT, 
                                    send_notification, 
                                    channel,
                                    time_frame,
                                    periods,
                                    currency))
                                    
        send_message(channel, "Notificação adicionada.")
    elif(action == COMMAND_INITIALIZE):
        notify_all_currencies(channel)
    elif(action == COMMAND_STOP_NOTIFY):
        remove_notifications()
    
def notify_all_currencies(channel):
    
    for currency in get_currencies():
        for k, v in currency.items():
            if(not (k.endswith("btc") or k.endswith("eth"))):
                set_repeated_timer(channel, "5m", 288, v)
                set_repeated_timer(channel, "1h", 120, v)
    
def set_repeated_timer(channel, time_frame, periods, currency):
    
    timers.append(RepeatedTimer(NOTIFICATION_TIMEOUT, 
                                    send_notification, 
                                    channel,
                                    time_frame,
                                    periods,
                                    currency))
    send_message(channel, 
                     ADDED_ALERT_MESSAGE % 
                     (time_frame,  periods, currency))
    
def get_parameters(command):
    
    parameters = {}
    
    for i, parameter in enumerate(command.split(COMMAND_SEPARATOR)):
        parameter = parameter.strip()
        
        if  (i == 0):
            parameters["action"] = parameter
        elif(i == 1):
            parameters["time_frame"] = parameter.upper()
        elif(i == 2):
            parameters["periods"] = int(parameter)
        elif(i == 3):
            parameters["currency"] = parameter
    
    return parameters
        
def send_notification(channel, time_frame, periods, currency):
    
    trend = get_trend(time_frame, periods, currency)
    if(trend):
        send_message(channel, 
                     NOTIFICATION_MESSAGE % 
                     (trend.name.lower(), time_frame,  periods, currency))
    

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
                except ValueError as e:
                    send_message(channel, e.message)
                except Exception as e:
                    send_message(channel, MESSAGE_INVALID_PARAMETERS)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
    
    
    
