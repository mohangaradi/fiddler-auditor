from flask import Flask, render_template, request
from auditor.utils.misc import get_stored_runs, runner
from auditor.utils.data import LLMEvalResult

app = Flask(__name__)

res = get_stored_runs()
run_results = list()
for prompt in res:
    run_result = dict()
    statuses = list()
    values = res[prompt]
    for value in values:
        id_status = dict()
        status = f'Run {value["created_at"]}  for {value["eval_type"]}]'
        id_status['id'] = value["uuid"]
        id_status['status'] = status
        statuses.append(id_status)
    run_result['prompt'] = prompt
    run_result['statuses'] = statuses
    run_results.append(run_result)

print(run_results)


# Define a route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html', run_results=run_results)


@app.route('/result', methods=['GET'])
def result():
    uuid = request.args.get('selectedValue')
    result = LLMEvalResult.render_db_result_by_uuid(uuid)
    rendered_template = render_template('result.html', run_result=result['llm_eval_res'])
    return rendered_template, 200, {'Content-Type': 'text/html'}


@app.route('/run', methods=['GET'])
def run():
    prompt = request.args.get('prompt')
    if prompt is None:
        return render_template('run.html')

    reference_gen = request.args.get('reference_gen')
    if reference_gen is not None:
        runner('correctness', prompt, reference_gen)
        return render_template('run.html',
                               status='Request for correctness evaluation is processing. Go to the results page <a href=\'http://127.0.0.1:5000/\'>here</a> and check the status')
    else:
        runner('robustness', prompt, '')
        return render_template('run.html',
                               status='Request for robustness evaluation is processing. Go to the results page <a href=\'http://127.0.0.1:5000/\'>here</a> and check the status')


if __name__ == '__main__':
    app.run()
