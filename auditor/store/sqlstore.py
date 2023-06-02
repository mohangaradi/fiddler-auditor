import sqlite3
from typing import Optional, List, Tuple

from auditor.utils.data import StoredLLMEvalResult, LLMEvalResult, LLMEvalType
import uuid
import pickle
from datetime import datetime

DB_NAME = 'fiddler_auditor_db'
TABLE = 'reports'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class SqliteStore:
    def __init__(self):
        self._conn = None
        self._cursor = None
        self._create_db_table()

    def _create_db_table(self):
        db_name = f'{DB_NAME}.db'
        self._conn = sqlite3.connect(db_name)
        table_def = f'CREATE TABLE IF NOT EXISTS {TABLE} (\
          id TEXT PRIMARY KEY,\
          provider TEXT,\
          temperature REAL,\
          model_name TEXT,\
          pre_context TEXT,\
          post_context TEXT,\
          original_prompt TEXT,\
          reference_generation TEXT,\
          expected_behavior_desc TEXT,\
          results TEXT,\
          perturbed_prompts TEXT,\
          perturbed_generations TEXT,\
          metric BLOB,\
          evaluation_type TEXT,\
          created_at TEXT\
        )'
        # Create table
        self.cursor.execute(table_def)

    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self._conn.cursor()

        return self._cursor

    def create_report(self, result: LLMEvalResult):
        now = datetime.utcnow()
        result_str: str = ''
        for r in result.result:
            result_str += str(r) + '||'
        result_str = result_str[0:len(result_str) - 2]
        row = (str(uuid.uuid4()), 'openai', 0.0, 'text-davinci-003',
               result.pre_context, result.post_context,  result.original_prompt, result.reference_generation,
               result.expected_behavior_desc, result_str,
               '||'.join(result.perturbed_prompts), '||'.join(result.perturbed_generations),
               pickle.dumps(result.metric), result.evaluation_type.value, now.strftime(DATE_FORMAT)
               )
        self.cursor.execute(f'''
        INSERT INTO {TABLE} (id, provider, temperature, model_name, pre_context, post_context, original_prompt, 
        reference_generation, expected_behavior_desc, results, 
        perturbed_prompts, perturbed_generations, metric, evaluation_type, created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?)
        ''', row)
        self._conn.commit()

    def get_reports_by_type(self, evaluation_type: LLMEvalType = None) -> Optional[List[StoredLLMEvalResult]]:
        stored_llm_eval_results = list()

        query = 'SELECT * FROM reports'
        if evaluation_type is not None:
            query = f'{query} WHERE evaluation_type={evaluation_type.value}'
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        for result in results:
            s_llm_eval_res = SqliteStore._to_llm_eval_result(result)
            if s_llm_eval_res is not None:
                stored_llm_eval_results.append(s_llm_eval_res)

        return stored_llm_eval_results

    @staticmethod
    def _to_llm_eval_result(result: Tuple):
        if len(result) < 15:
            return None

        model_results = list()
        for model_res in result[9].split('||'):
            model_results.append(int(model_res))

        metric = pickle.loads(result[12])

        eval_type = None
        for le_type in LLMEvalType:
            if le_type.value == result[13]:
                eval_type = le_type

        llm_eval_res = LLMEvalResult(pre_context=result[4], post_context=result[5], original_prompt=result[6],
                                     reference_generation=result[7].split('||'), expected_behavior_desc=result[8],
                                     result=model_results, perturbed_prompts=result[10].split('||'),
                                     perturbed_generations=result[11].split('||'), metric=metric,
                                     evaluation_type=eval_type
                                     )

        stored_llm_res = StoredLLMEvalResult(llm_eval_result=llm_eval_res, created_at=result[14])
        return stored_llm_res
