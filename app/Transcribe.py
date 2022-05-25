import wave
import grpc
import riva_api.riva_asr_pb2 as rasr
import riva_api.riva_asr_pb2_grpc as rasr_srv
import riva_api.riva_audio_pb2 as ra
import json
from dotenv import load_dotenv

load_dotenv('.env')



CHUNK = 1024

def generator(w, s):
    yield rasr.StreamingRecognizeRequest(streaming_config=s)
    d = w.readframes(CHUNK)
    while len(d) > 0:
        yield rasr.StreamingRecognizeRequest(audio_content=d)
        d = w.readframes(CHUNK)

def write_json(responses, url, recording_SID):
    output = dict()
    text = ""
    output['Source URL'] = url
    output['Task Id'] = recording_SID
    buff = []
    for response in responses:
        for result in response.results:
            if result.is_final:
                data = dict()
                text  = text+(result.alternatives[0].transcript)
                output['combinedRecognizedPhrases'] = text
                data['Confidence'] = result.alternatives[0].confidence
                data['transcript'] = result.alternatives[0].transcript
                data['Start_time in Sec'] = result.alternatives[0].words[0].start_time/1000
                data['End_time in Sec'] = result.alternatives[0].words[-1].end_time/1000
                word_info = []
                for word in result.alternatives[0].words:
                    word_data = {
                        'Word' : word.word,
                        'Start_time in Sec' : word.start_time/1000,
                        'End_time in Sec' : word.end_time/1000
                    }
                    word_info.append(word_data)
                data['Word Info'] = word_info
                buff.append(data)
    output['RecognizedPhrases'] = buff
    output_json = recording_SID+'.json'
    with open(output_json, "w") as outfile:
        json.dump(output, outfile)
    return output
