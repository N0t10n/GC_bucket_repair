import logging, re, subprocess, json
from logging.handlers import RotatingFileHandler
from functools import wraps

rfh = RotatingFileHandler(
    filename='main.log', 
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=1,
    encoding=None,
    delay=0
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime).19s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[rfh]
)

def logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            print(e)
            with open('errors.txt', 'a+') as f:
                f.write(args[0])
                f.write('\n')

            try:
                s = re.search(r'"rqId"', args[0]).span()
                id = re.findall(r'\d+', args[0][s[0]:])[0]
                logging.error('An error occurred at rqId: {}: {}'.format(id, e))
            except:
                logging.error('An error occurred at rqId: {}: {}'.format("unknown", e))

    return wrapper

@logger
def parser(input):
    input = json.loads(input)
    return input

@logger
def recursive_parse_json(input:str) -> dict:
    if isinstance(input, str) and '}' in input:
        data = json.loads(input)
    else:
        return input

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = recursive_parse_json(v)
    
    return data

def get_projects():
    out = subprocess.run(['gsutil', 'ls'], capture_output=True, text=True).stdout.split('\n')
    return out

def get_buckets(bucket, last_answer):
    if bucket['item'] != 'Go back':
        out = subprocess.run(['gsutil', 'ls', bucket['item']], capture_output=True, text=True).stdout.split('\n')
        out = list(filter(lambda x: True if bucket['item']!=x else False, out))
        out.insert(0, 'Go back')
        return out, last_answer
    else:
        if len(last_answer)==1:
            return get_projects(), []
        last_answer = last_answer[:-1]
        out = subprocess.run(['gsutil', 'ls', last_answer[-1]], capture_output=True, text=True).stdout.split('\n')
        out = list(filter(lambda x: True if last_answer[-1]!=x else False, out))
        out.insert(0, 'Go back')
        return out, last_answer

def download_bucket(bucket, folder):
    subprocess.run(['gsutil', 'cp', bucket['item'], folder])

def upload_bucket(file, bucket):
    subprocess.run(['gsutil', 'rm', bucket['item']])
    subprocess.run(['gsutil', 'cp', file, bucket['item']])