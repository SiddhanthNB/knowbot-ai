import json
import requests
import utils.constants as constants

def _build_headers():
    auth = {
        'client-name': constants.CLIENT_NAME,
        'client-id': constants.CLIENT_ID,
        'client-secret': constants.CLIENT_SECRET
    }
    return { 'auth': json.dumps(auth) }

def _dispatch_request(url, params={}, headers={}, method='get'):
    method = method.upper()

    if method == 'GET':
        response = requests.get(url, json=params, headers=headers)
    elif method == 'POST':
        response = requests.post(url, json=params, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    response.raise_for_status()
    return response.json()

def perform_ping():
    url = f'{constants.CORENEST_API_URL}/ping'
    response = _dispatch_request(url)
    return response == 'pong'

def fetch_embeddings(text):
    url = f'{constants.CORENEST_API_URL}/embed'

    params = { 'texts': [ text ] }

    response = _dispatch_request(url, params, _build_headers())

    return response['result'][0]

def fetch_llm_response(question, context):
    url = f'{constants.CORENEST_API_URL}/generate'

    with open('utils/prompts/system_prompt.txt', 'r') as system_prompt_file:
        system_prompt = system_prompt_file.read()

    with open('utils/prompts/user_prompt.txt', 'r') as user_prompt_file:
        user_prompt = user_prompt_file.read()

    user_prompt = user_prompt.format(context=context, question=question)

    params = {
        'system_prompt': system_prompt,
        'user_prompt': user_prompt
    }

    response = _dispatch_request(url, params, _build_headers())

    return response['result']['content']
