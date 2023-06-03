import sqlite3
from typing import Optional, List, Tuple, Dict, Any

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
        db_name = f'/Users/mgaradi/Documents/projects/fiddler-auditor/examples/{DB_NAME}.db'
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

    def create_report(self,
                      original_prompt: str,
                      pre_context: str,
                      post_context: str,
                      reference_generation: str,
                      evaluation_type: str,
                      perturbed_prompts: List[str],
                      perturbed_generations: List[str],
                      test_result: List[int],
                      metric: List[Dict[str, Any]],
                      expected_behavior_desc: Optional[str] = '', ):
        now = datetime.utcnow()
        result_str: str = ''
        for r in test_result:
            result_str += str(r) + '||'
        result_str = result_str[0:len(result_str) - 2]
        row = (str(uuid.uuid4()), 'openai', 0.0, 'text-davinci-003',
               pre_context, post_context, original_prompt, reference_generation,
               expected_behavior_desc, result_str,
               '||'.join(perturbed_prompts), '||'.join(perturbed_generations),
               pickle.dumps(metric), evaluation_type, now.strftime(DATE_FORMAT)
               )
        self.cursor.execute(f'''
        INSERT INTO {TABLE} (id, provider, temperature, model_name, pre_context, post_context, original_prompt, 
        reference_generation, expected_behavior_desc, results, 
        perturbed_prompts, perturbed_generations, metric, evaluation_type, created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?)
        ''', row)
        self._conn.commit()

    def get_reports_by_type(self, evaluation_type: str = '') -> Optional[List[Tuple]]:
        query = 'SELECT * FROM reports'
        if evaluation_type != '':
            query = f'{query} WHERE evaluation_type={evaluation_type}'
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return results
