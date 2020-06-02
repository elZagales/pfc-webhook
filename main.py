from flask import Response
from google.cloud import pubsub_v1
import json
import os


VERIFY_TOKEN = os.environ['verify_token']
PROJECT_ID = os.environ['project_id']
TOPIC_NAME = os.environ['topic_name']


def main(request):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

    if request.method == 'POST':
        request_json = request.get_json()
        print('request', request)
        print("webhook event received", request_json)

        try:
            request_json_string = json.dumps(request_json)
            # data = bytes(request_json_string, 'utf-8')
            data = request_json_string.encode('utf-8')
            future = publisher.publish(topic_path, data=data)
            print('Published message {} now has message ID {}'.format(data, future.result()))

        except Exception:
            print('A problem occured when publishing {}: {}\n'.format(data, future.exception()))

        return Response('EVENT RECEIVED', status=200)

    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get("hub.challenge")

        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK_VERIFIED')
                print(challenge)
                d = {'hub.challenge': challenge}
                print(d)
                return Response(json.dumps(d))
            else:
                return Response(status=403)
