import json, os, inquirer, pathlib
import pyppex as px

from utils.utils import logging, parser, get_projects, get_buckets, download_bucket, upload_bucket



if __name__=='__main__':
    os.makedirs('temp', exist_ok=True)


    project = inquirer.List('item', message='Select a project', choices=get_projects())
    answer = inquirer.prompt([project])
    
    last_answer = [answer['item']]
    while pathlib.Path(answer['item']).suffix not in ['.json', '.jsonl', '.csv']:

        choices, last_answer = get_buckets(answer, last_answer)
        questions = [
            inquirer.List('item', message='Select the bucket', choices=choices)
        ]
        answer = inquirer.prompt(questions)

        if answer['item'] != 'Go back':
            last_answer.append(answer['item'])
    else:
        filename = pathlib.Path(answer['item']).name
        download_bucket(answer, 'temp')



    file = os.path.join('temp', filename)
    logging.info(f'File: {file}')

    with open(file, 'r') as f:
        raw = f.readlines()

        # result = [recursive_parse_json(i) for i in raw] # Recursive
        parallel = px.Parallelize(parser, raw) # Parallel
        result = list(parallel.compute())

        with open(file, 'w') as f:
            for i in result:
                if isinstance(i, dict):
                    # i['rqData'] = str(i['rqData'])
                    json.dump(i, f)
                    f.write('\n')

    print('\n')
    upload_bucket(file, answer)
    os.remove(file)
    print(px.modstring('Done!', mod='green'))