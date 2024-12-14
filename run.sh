#!/bin/sh

source .venv/bin/activate

python script.py '.gpt-test/' 'data/all_context2.json'

python eval/create_eval_data.py '.gpt-test/'
# python eval/ragas_eval.py
# python eval/ragcheck_eval.py
