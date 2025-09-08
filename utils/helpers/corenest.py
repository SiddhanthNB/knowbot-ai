import requests
import utils.constants as constants

def _build_headers():
    return  { 'Authorization': f"Bearer {constants.CORENEST_SECRET_KEY}" }

def _dispatch_request(url='', method='get', params={}, headers={}):
    if url.strip() == '':
        raise ValueError("URL cannot be empty")

    method = method.lower()

    if method not in ['get', 'post']:
        raise ValueError(f"Unsupported HTTP method: {method}")

    response = requests.__dict__[method](url, json=params, headers=headers)
    response.raise_for_status()
    return response.json()

def perform_ping():
    url = f'{constants.CORENEST_API_URL}/ping'
    response = _dispatch_request(url)
    return response == 'pong'

def fetch_embeddings(text):
    url = f'{constants.CORENEST_API_URL}/embeddings'
    params = {'provider': 'google', 'texts': [ text ]}
    response = _dispatch_request(url, 'post', params, _build_headers())
    return response['result']['content'][0]

def fetch_llm_response(question, context):
    url = f'{constants.CORENEST_API_URL}/completions'

    with open('utils/prompts/system_prompt.txt', 'r') as system_prompt_file:
        system_prompt = system_prompt_file.read()

    with open('utils/prompts/user_prompt.txt', 'r') as user_prompt_file:
        user_prompt = user_prompt_file.read()

    user_prompt = user_prompt.format(context=context, question=question)
    params = {'system_prompt': system_prompt, 'user_prompt': user_prompt}
    response = _dispatch_request(url, 'post', params, _build_headers())
    return response['result']['content']
