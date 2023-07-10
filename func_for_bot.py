import openai
import boto3
import json
from smart_open import open
from secure.utils import aws_access_key_id, aws_secret_access_key, s3_endpoint_url, bucket_name


def write_json_to_s3(data, folder_name, file_name):
    with open(f'{folder_name}_{file_name}', 'a', encoding='utf-8') as fout:
        res = json.dumps(data, ensure_ascii=False, indent=4)
        fout.writelines(res + '\n')
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    client_s3 = session.client('s3', endpoint_url=s3_endpoint_url)
    client_s3.upload_file(f'{folder_name}_{file_name}', bucket_name, f'raw_data/{folder_name}_{file_name}')


def clean_data(response):
    array_start = ['{', 'Промежуточный', 'промежуточный', '```']
    test_a = []
    for el in array_start:
        test_a.append(response.find(el) if response.find(el) != -1 else 1000)
    del_text = min(test_a) if min(test_a) != 1000 else None
    return response[:del_text]


def send_message(message_log, model_type="gpt-3.5-turbo-16k"):
    response = openai.ChatCompletion.create(
        model=model_type,
        messages=message_log,
        stop=None,
        temperature=0.9,
    )

    for choice in response.choices:
        if "text" in choice:
            return choice.text

    return response.choices[0].message.content


def main_start():
    message_log = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    user_input = open("prompt.txt").read()
    message_log.append({"role": "user", "content": user_input})
    response = send_message(message_log)
    message_log.append({"role": "assistant", "content": response})
    print(f"AI assistant: {response}")
    # -------------------------------
    user_input = open("prompt2.txt").read()
    message_log.append({"role": "user", "content": user_input})
    response = send_message(message_log)
    message_log.append({"role": "assistant", "content": response})
    print(f"AI assistant: {response}")
    # -------------------------------
    if response.find('{') == -1:
        message_log =[]
        main_start()
    message_log.append({"role": "user", "content": "Старт. Представься и предложи начать заполнять заявку"})
    response = send_message(message_log)
    message_log.append({"role": "assistant", "content": response})
    print(f"AI assistant: {response}")

    return response, message_log
