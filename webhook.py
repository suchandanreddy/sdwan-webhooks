from flask import Flask, request, jsonify
from ciscosparkapi import CiscoSparkAPI, SparkApiError
import json
import os
from json2html import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

bearer_token = os.environ.get("bearer_token")
room_id = os.environ.get("room_id")
gmail_username = os.environ.get("gmail_username")
gmail_password = os.environ.get("gmail_password")
sender_address = os.environ.get("sender_address")
to_address = os.environ.get("to_address")

if bearer_token is None or room_id is None or gmail_username is None or gmail_password is None or sender_address is None or to_address is None:
    print("\nWebex Teams Authorization and roomId details must be set via environment variables using below commands on macOS or Ubuntu workstation")
    print("export bearer_token=<authorization bearer token>")
    print("export room_id=<webex teams room-id>")
    print("export gmail_username=<gmail username>")
    print("export gmail_password=<gmail password>")
    print("export sender_address=<email sender address>")
    print("export to_address=<email receiver address>")
    print("\nWebex Teams Authorization and roomId details must be set via environment variables using below commands on Windows workstation")
    print("set bearer_token=<authorization bearer token>")
    print("set room_id=<webex teams room-id>")
    print("set gmail_username=<gmail username>")
    print("set gmail_password=<gmail password>")
    print("set sender_address=<email sender address>")
    print("set to_address=<email receiver address>")
    exit()

app = Flask(__name__)

@app.route('/',methods=['POST'])
def alarms():
   try:
      data = json.loads(request.data)
      print(data)
      message =  '''Team, alarm event : **''' + data['eventname'] + '** ------ **' + data['message'] + '''** is recieved from vManage and here are the complete details <br><br>'''  + str(data)
      api = CiscoSparkAPI(access_token=bearer_token)
      res=api.messages.create(roomId=room_id, markdown=message)
      print(res)

      server = smtplib.SMTP('smtp.gmail.com',587)
      server.starttls()

      server.login(gmail_username,gmail_password)
      
      mail_data=dict()

      headers = ['values','receive_time','severity','message','component','type','cleared_events','uuid']

      
      for item in headers:
          mail_data[item]=data.get(item)

      if mail_data['receive_time'] is not None:
          mail_data['receive_time'] = time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(mail_data['receive_time']/1000.)) + ' UTC'

      mail_body = json2html.convert(json = mail_data)
      print(mail_body)

      msg = MIMEMultipart('alternative')
      msg['Subject'] = 'Network Event: ' + data['severity'] + '<------>' + data['rule_name_display']
      msg['From'] = sender_address
      msg['To'] = to_address
      Message=str(mail_body)

      part2 = MIMEText(Message,'html')
      print(part2)
      msg.attach(part2)
      server.sendmail(sender_address,to_address,msg.as_string())
      server.quit()
   except Exception as exc:
      print(exc)
      return jsonify(str(exc)), 500
   
   return jsonify("Message sent to Webex Teams"), 200

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5001, debug=True)