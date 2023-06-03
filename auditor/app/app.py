from flask import Flask, render_template
from auditor.utils.misc import get_stored_runs

app = Flask(__name__)


res = get_stored_runs()
run_results = list()
for prompt in res:
    run_result = dict()
    statuses = list()
    values = res[prompt]
    for value in values:
        status = f'Run {value["created_at"]}  for {value["eval_type"]}'
        statuses.append(status)
    run_result['test_name'] = prompt
    run_result['statuses'] = statuses
    run_results.append(run_result)

print(run_results)
# Define a sample test data
# run_results = [
#     {'test_name': 'Test 1', 'statuses': ['Passed', 'Failed']},
#     {'test_name': 'Test 2', 'statuses': ['Passed', 'Failed', 'Skipped']},
#     {'test_name': 'Test 3', 'statuses': ['Passed', 'Failed', 'Skipped', 'Pending']}
# ]


# Define a route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html', run_results=run_results)


if __name__ == '__main__':
    app.run()
