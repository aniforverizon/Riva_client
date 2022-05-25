from flask import Blueprint, request
import os
import json
import requests
import validators
from .tasks import audio_transcription
from app import celery
bp = Blueprint("all", __name__)


@bp.route('/transcript', methods = ['POST'])
def transcribe():
    if request.headers.get('AuthenticationToken'):
        # print('I am Inside')
        headers = {"Range": "bytes=0-1024"}
        data = request.get_json()
        audio_url = data.get('RecordingUrl')
        media = requests.get(audio_url, headers=headers, timeout=3.00)
        if validators.url(audio_url):
            if media.ok :
                res = audio_transcription.delay(audio_url)

                return json.dumps({
                    'ID' : res.id,
                    'Status' : 'Queued',
                    'Audio_URL' : audio_url
                })
            
            else:
                return json.dumps({
                'Audio URL': audio_url,
                'Error Status' : media.status_code,
                'Error Msg' : 'Failed to Load Audio from URL'
                })

        else:
            return json.dumps({
                'Audio URL': audio_url,
                'Error Msg' : 'Invalid URL'
            })


    else:
        return json.dumps({
            'Error' : 'Authentication Failed'
        })

@bp.route('/transcript/<task_id>')
def result(task_id):
    output = celery.AsyncResult(task_id)
    if output.state == 'SUCCESS':
        return json.dumps({
            'Task Id' : task_id,
            'Queue Status' : 'Completed',
            'Transcriptions' : output.get()
        })

    elif output.state == 'PENDING':
        print(output.status)
        return json.dumps({
            'TaskId' : task_id,
            'Queue Status' : 'Queued'
        })
    else:
        return json.dumps({
            'TaskId' : task_id,
            'Queue State' : output.state,
            'Details' : str(output.info)
        })
