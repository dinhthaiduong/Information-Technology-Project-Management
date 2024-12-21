#!/bin/sh

source .venv/bin/activate

python script.py '.gpt-da/' 'data/all_context2.json'
python create_eval_data.py '.gpt-da/'

python eval/ragas_eval.py
python eval/ragcheck_eval.py
