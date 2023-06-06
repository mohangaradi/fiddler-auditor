"""For miscellaneous utilities"""
import os
import ssl
from typing import List
from auditor.utils.data import LLMEvalResult
from langchain.llms import OpenAI
from sentence_transformers.SentenceTransformer import SentenceTransformer
from auditor.evaluation.expected_behavior import SimilarGeneration


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


def runner(type: str, prompt: str, reference_generation: str):
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    # Local import due to ssl requirement above
    from auditor.evaluation.evaluate import LLMEval
    api_key = '<your key here>'
    os.environ["OPENAI_API_KEY"] = api_key
    openai_llm = OpenAI(model_name='text-davinci-003', temperature=0.0)
    pre_context = "Answer the following question in a concise manner.\n"
    sent_xfmer = SentenceTransformer('sentence-transformers/paraphrase-mpnet-base-v2')
    similar_generation = SimilarGeneration(
        similarity_model=sent_xfmer,
        similarity_threshold=0.75,
    )

    llm_eval = LLMEval(
        llm=openai_llm,
        expected_behavior=similar_generation,
    )
    if type == 'correctness':
        test_result = llm_eval.evaluate_prompt_correctness(
            prompt=prompt,
            pre_context=pre_context,
            reference_generation=reference_generation,
            perturbations_per_sample=5,
        )

        test_result.save_to_db()

    if type == 'robustness':
        test_result = llm_eval.evaluate_prompt_robustness(
            prompt=prompt,
            pre_context=pre_context,
        )

        test_result.save_to_db()
