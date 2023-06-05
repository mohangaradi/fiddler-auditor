"""For miscellaneous utilities"""
from typing import List
from auditor.utils.data import LLMEvalResult

def round_list(nums: List[float], precision=2):
    return [round(n, precision) for n in nums]


def get_stored_runs():
    # Stored as {"prompt": [{"eval_type": "Correctness", "created_at": "2023-05-01", "uuid": uuid}]}
    stored_eval_results = LLMEvalResult.render_all_db_results()
    sorted_results = dict()
    if len(stored_eval_results) > 1:
        for eval_res in stored_eval_results:
            llm_eval_res = eval_res['llm_eval_res']
            prompt = llm_eval_res.original_prompt
            if prompt not in sorted_results:
                sorted_results[prompt] = list()
            value = dict()
            value["eval_type"] = llm_eval_res.evaluation_type.value
            value["created_at"] = eval_res['created_at']
            value["uuid"] = eval_res['uuid']
            sorted_results[prompt].append(value)

    for prompt in sorted_results:
        sorted_list = sorted(sorted_results[prompt], key=lambda x: x['created_at'])
        sorted_results[prompt] = sorted_list

    return sorted_results
