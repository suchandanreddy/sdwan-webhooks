from flask import Flask, request, jsonify
from ciscosparkapi import CiscoSparkAPI, SparkApiError
import json
import os
import time
import datetime
import pytz

bearer_token = os.environ.get("bearer_token")
room_id = os.environ.get("room_id")

if bearer_token is None or room_id is None:
    print("\nWebex Teams Authorization and roomId details must be set via environment variables using below commands on macOS or Ubuntu workstation")
    print("export bearer_token=<authorization bearer token>")
    print("export room_id=<webex teams room-id>")
    print("\nWebex Teams Authorization and roomId details must be set via environment variables using below commands on Windows workstation")
    print("set bearer_token=<authorization bearer token>")
    print("set room_id=<webex teams room-id>")
    exit()

app = Flask(__name__)

@app.route('/',methods=['POST'])
def alarms():
   try:
      PDT = pytz.timezone('America/Los_Angeles')
      data = json.loads(request.data)
      print(data)
      message =  '''Team, Alarm event : **''' + data['rule_name_display'] + '''** is recieved from vManage and here are the complete details <br><br>'''

      temp_time = datetime.datetime.utcfromtimestamp(data['entry_time']/1000.)
      temp_time = pytz.UTC.localize(temp_time)
      message = message + '**Alarm Date & Time:** ' + temp_time.astimezone(PDT).strftime('%c') + ' PDT'
      temp = data['values_short_display']
      for item in temp:
          for key, value in item.items():
              message = message + '<br> **' + key + ':** ' + value

      message = message + '<br> **' + 'Details:' + '** ' + "https://sdwanlab.cisco.com:10000/#/app/monitor/alarms/details/" + data['uuid']
      
      api = CiscoSparkAPI(access_token=bearer_token)
      res=api.messages.create(roomId=room_id, markdown=message)
      print(res)

    
   except Exception as exc:
      print(exc)
      return jsonify(str(exc)), 500
   
   return jsonify("Message sent to Webex Teams"), 200

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5001, debug=True)
