# -*- coding: utf-8 -*-
import time
import argparse
import requests
import json
import os


def get_models(token, _model, headers):
    response = requests.get('https://3i-vox.ru/api/v1/asr/models', headers=headers)
    if check_response_status(response):
        print("----------------Models id------------------")
        models = [model['model_id'] for model in json.loads(response.text)['models']]
        for model in models:
            print(model)
        if _model in models:
            return True
    return False


def prepare_result(resp):
    data = resp['result']
    results = []

    for sgm_elem in data:
        results.append({'result': '', 'speaker': ''})
        data_arr = sgm_elem['data']
        words = []
        for word_elem in data_arr:
            words.append(word_elem['alternatives'][0]['word'])

        results[sgm_elem['id']]['result'] += " ".join(words).replace(" .",".")
        results[sgm_elem['id']]['speaker'] = sgm_elem['channel']
    return results


def create_asr_task(file_id, model_id, enable_automatic_punctuation):
    asr_task = {
        "file_id": file_id,
        "model_id": model_id,
        "enable_automatic_punctuation": enable_automatic_punctuation,
        "max_alternatives": 1,
        "word_to_number": False,
        "interruption_word_threshold": 2,
        "interruption_duration_threshold": 300,
        "process_as_mono": False,
        "diarization": False,
        "sentiment_analysis": False,
        "thresholds": {
            "greedy": 75,
            "am": 1,
            "lm": 0,
            "sentiment_word_number": 3,
            "sentiment_confidence": 0.8
        }
    }
    return asr_task


def check_response_status(response):
    if response.status_code >= 200 and response.status_code < 300:
        return True
    else:
        print('--------------Request Error----------------')
        print(response.text)
        return False


def recognize(model_name, file_path, token, off_print_result, on_save_result, enable_automatic_punctuation):
    vox_address = "https://3i-vox.ru/api/v1"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    if not get_models(token, model_name, headers):
        print('-------Model was entered incorrectly-------')
        return

    file = os.path.basename(file_path)

    file_name = os.path.splitext(file)[0]
    file_type = os.path.splitext(file)[1]

    asr_id_task = ''

    files = {
        'parameters': ('parameters.json', b'{}', 'application/json'),
        'file': (file_name + file_type, open(file_path, 'rb'), 'audio/wav'),
    }
    print('-------------Uploading a file--------------')
    response = requests.post(f'{vox_address}/storage/files', headers=headers, files=files)
    data_response = json.loads(response.text)
    if check_response_status(response):
        file_id = data_response['id']
        print('-------------File is uploaded--------------')
        headers['Content-Type'] = 'application/json'

        print('-----------Add recognition task------------')
        response = requests.post(f'{vox_address}/asr/tasks',
                                 headers=headers,
                                 json=create_asr_task(file_id, model_name, enable_automatic_punctuation)
                                 )
        asr_id_task = json.loads(response.text)['id']
        if check_response_status(response):
            print('------------Task has been added------------')

            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            print('----Waiting for processing to complete-----')
            time.sleep(1)
            response = requests.get(f'{vox_address}/asr/tasks/{asr_id_task}',
                                    headers=headers)
            data_response = json.loads(response.text)

            if check_response_status(response):
                while data_response['status'] != 'complete':
                    time.sleep(5)
                    response = requests.get(f'{vox_address}/asr/tasks/{asr_id_task}',
                                            headers=headers)
                    data_response = json.loads(response.text)
                    if not check_response_status(response):
                        return
            else:
                return

            print('----------Processing is completed----------')

            params = {
                'result': 'true',
                'output_format': 'segmented_confusion_network',
            }

            response = requests.get(f'{vox_address}/asr/tasks/{asr_id_task}',
                                    params=params,
                                    headers=headers)
            
            print (response.text)
            
            if not check_response_status(response):
                return

            result_list = prepare_result(json.loads(response.text))
            result = ""

            for index, value in enumerate(result_list):
                if len(value['result']) > 0:
                    result += f'[Phrase ID: {index}][Chanel: {value["speaker"]}]\t{value["result"]}\n'

            print('----------Delete recognition task----------')
            response = requests.delete(f'{vox_address}/asr/tasks/{asr_id_task}',
                                       headers=headers)
            if check_response_status(response):
                print('-----------Task has been deleted-----------')

            print('--------------Deleting a file--------------')
            response = requests.delete(f'{vox_address}/storage/files/{file_id}',
                                       headers=headers)
            if check_response_status(response):
                print('-----------File has been deleted-----------')

            if not off_print_result:
                print(result, end="")

            if on_save_result:
                print('-------------Start save result-------------')
                with open(f'asr_{file_name}.txt', 'w', encoding='utf8') as f:
                    f.write(result)
                print('--------------End save result--------------')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True, help='Model name')
    parser.add_argument('--file', required=True, help='File name')
    parser.add_argument('--token', required=False, help='OAuth access token')
    parser.add_argument('--off_print_result', action='store_true', help='Disables console output')
    parser.add_argument('--on_save_result', action='store_true', help='Enable saving the result to a file')
    parser.add_argument('--punctuation', action='store_true', help='Enable automatic punctuation')

    args = parser.parse_args()

    recognize(args.model, args.file, args.token, args.off_print_result, args.on_save_result, args.punctuation)
