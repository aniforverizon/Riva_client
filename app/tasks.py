import io
import os
from app import celery
import json
import grpc
import wave
from celery.exceptions import Ignore
import requests
import riva_api.riva_asr_pb2 as rasr
import riva_api.riva_asr_pb2_grpc as rasr_srv
import riva_api.riva_audio_pb2 as ra
from .Transcribe import generator, write_json
from .uploadToS3 import write_output_json
from dotenv import load_dotenv

load_dotenv('.env')

@celery.task(bind = True)
def audio_transcription(self, url):
    tid = self.request.id

    callback_config = rasr.RecognitionConfig(
        encoding=ra.AudioEncoding.LINEAR_PCM,
        sample_rate_hertz=8000,
        language_code='en-US',
        max_alternatives=1,
        enable_automatic_punctuation=True,
        audio_channel_count=1,
        enable_word_time_offsets=True,
        )

    try:
        download_audio = requests.get(url)
        data = io.BytesIO(download_audio.content)
        wf = wave.open(data, 'rb')

    except Exception as ex:
        self.update_state(state = 'FAILURE', meta = {
            'exc_type': type(ex).__name__,
            'exc_message': 'Failed to Load Audio from URL',
            'custom': '...'
        })
        raise Ignore()
    
    try:
        # print(os.getenv('SECURE_RIVA_SERVER'))
        channel = grpc.insecure_channel(os.getenv('SECURE_RIVA_SERVER'))
        client = rasr_srv.RivaSpeechRecognitionStub(channel)

    except Exception as ex:
        self.update_state(state = 'FAILURE', meta = {
            'exc_type': type(ex).__name__,
            'exc_message': 'Failed to open GRPC channel with NVIDIA RIVA',
            'custom': '...'
        })
        raise Ignore()

    try:
        streaming_config = rasr.StreamingRecognitionConfig(config=callback_config, interim_results=True)
        responses = client.StreamingRecognize(generator(wf, streaming_config))

    except Exception as ex:
        self.update_state(state = 'FAILURE', meta = {
            'exc_type': type(ex).__name__,
            'exc_message': 'Failed to Collect Response from NVIDIA RIVA.',
            'custom': '...'
        })
        raise Ignore()

    try:
        output = write_json(responses, url, tid)

    except Exception as ex:
        # print('Inside here')
        self.update_state(state = 'FAILURE', meta = {
            'exc_type': type(ex).__name__,
            'exc_message': 'Failed to write Output to JSON',
            'custom': '...'
        })
        raise Ignore()
        
    if write_output_json(output, tid):
        return json.dumps(
            output
        )
    else:
        return json.dumps({
            'Warning' : 'JSON upload to S3 failed',
            'Output JSON' : output
        })




