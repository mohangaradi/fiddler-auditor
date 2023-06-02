import os
import unittest
import sqlite3
from auditor.store.sqlstore import SqliteStore, DB_NAME
from auditor.utils.data import LLMEvalResult, LLMEvalType

class TestSqlStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db_file = f'{DB_NAME}.db'
        os.remove(db_file)

    @staticmethod
    def get_test_data():
        llm_eval_result = LLMEvalResult(original_prompt='test',
                                        pre_context='text precontext',
                                        post_context='test postcontext',
                                        perturbed_prompts=['test1 perturbed prompt', 'test2 perturbed prompt'],
                                        perturbed_generations=['test1 perturbed gen', 'test2 perturbed gen'],
                                        result=[0, 1],
                                        metric=[{'expected': 0.08}],
                                        expected_behavior_desc='test expected behavior',
                                        evaluation_type=LLMEvalType.correctness,
                                        reference_generation='test reference generation'
                                        )
        return llm_eval_result

    def test_create_report(self):
        sql_store = SqliteStore()
        sql_store.create_report(TestSqlStore.get_test_data())

    def test_get_reports_by_type(self):
        sql_store = SqliteStore()
        res = sql_store.get_reports_by_type()
        assert len(res) == 1
