import os
import json
import boto3
from os import path
from dotenv import load_dotenv

load_dotenv('.env')

def write_output_json(op_json, tid):
    s3 = boto3.resource('s3',
        endpoint_url = os.getenv('S3_ENDPOINT_URL'),
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'))

    output_folder = os.getenv('OUTPUT_FOLDER')
    output_file = tid+'/'+tid+'.json'
    print(path.join(output_folder, output_file))
    try:
        s3object = s3.Object(os.getenv('S3_BUCKET'), path.join(output_folder, output_file))
        s3object.put(Body = bytes(json.dumps(op_json).encode('UTF-8')))
        return True
    except Exception as e:
        print(e)
        return False

