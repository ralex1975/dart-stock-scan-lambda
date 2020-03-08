import json
import datetime

# try comment to push


def handler(event, context):
    data = {
        'output': 'Hello World 1',
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    return {'statusCode': 200,
            'body': json.dumps(data),
            'headers': {'Content-Type': 'application/json'}}
