from flask import Flask, request, jsonify, render_template
import json
from slacker import Slacker
import datetime

slack = Slacker('xoxp-179782686228-179782686244-179174111329-ee520d7b9c4bd85e4a3c4eed4fa87beb')
app = Flask(__name__)
filters = set()
weightage = {}
messages = []


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/busy',methods=['POST'])
def test_conn():
    return 'Test'


@app.route('/testEvents',methods=['POST'])
def test_event():
    print(request)
    print(request.data)
    in_req = json.loads(request.data.decode('utf-8'))
    # print(request.data)
    # slack.chat.post_message('#general', in_req['event']['text'])
    try:
        message = in_req['event']['text']
        user_id = in_req['event']['user']
        user_details = slack.users.profile.get(user_id).body
        user_profile = user_details['profile']['real_name']
        user_pic_url = user_details['profile']['image_72']
        timestamp = in_req['event_time']
        time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        channel_id = in_req['event']['channel']
        if channel_id.startswith('C'):
            channel = slack.channels.info(channel_id).body['channel']['name']
        else:
            channel = 'Direct Message'
        messages.append({'message':message,'user':user_profile,'pic':user_pic_url, 'time':time,'level':compute_levels(message), 'channel':channel})
        # messages[message] = compute_levels(message)
        print(messages)#,user_profile,user_pic_url,timestamp)
    except:
        pass
    return 'Ok'
    # return in_req['event']['text']
    # return jsonify({'challenge':in_req['challenge']})
    # return 'Test'


@app.route('/set/<topic>/<int:level>', methods=['GET'])
# @require_post_data
def set_topic(topic,level):
    filters.add(topic)
    weightage[topic] = level
    print(filters, weightage)
    # print(request.args)#, repr(level), topic)
    return 'Ok'

@app.route('/tell/rules')
def tell_rules():
    return jsonify(weightage)

@app.route('/show/<int:level>')
def filter_messages(level):
    filtered = []
    for message in messages:
        key = message['message']
        value = message['level']
        print(key,value)
        if value >= level:
            filtered.append(message)
    return render_template('dashboard.html', response=filtered)

def compute_levels(message):
    weight = 0
    count = 0
    for word in filters:
        if word in message:
            weight += weightage[word]
            count += 1
    if count !=0:
        return weight/count
    else:
        return 0

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
