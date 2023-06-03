import os
import unittest
from auditor.store.sqlstore import SqliteStore, DB_NAME


class TestSqlStore(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        db_file = f'{DB_NAME}.db'
        if os.path.exists(db_file):
            os.remove(db_file)

    def test_create_report(self):
        sql_store = SqliteStore()
        sql_store.create_report(original_prompt='test',
                                pre_context='text precontext',
                                post_context='test postcontext',
                                perturbed_prompts=['test1 perturbed prompt', 'test2 perturbed prompt'],
                                perturbed_generations=['test1 perturbed gen', 'test2 perturbed gen'],
                                test_result=[0, 1],
                                metric=[{'expected': 0.08}],
                                expected_behavior_desc='test expected behavior',
                                evaluation_type='correctness',
                                reference_generation='test reference generation')

    def test_get_reports_by_type(self):
        sql_store = SqliteStore()
        res = sql_store.get_reports_by_type()
        assert len(res) == 1
