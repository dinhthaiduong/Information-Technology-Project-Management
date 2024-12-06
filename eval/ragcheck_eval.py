from ragchecker import RAGResults, RAGChecker
from ragchecker.metrics import all_metrics
import os
import json

# initialize ragresults from json/dict
with open("examples/ragcheck_input.json") as fp:
    rag_results = RAGResults.from_json(fp.read())

# set-up the evaluator
evaluator = RAGChecker(
    extractor_name="openai/gpt-4o-mini",
    checker_name="openai/gpt-4o-mini",
    batch_size_extractor=32,
    batch_size_checker=32
)

# evaluate results with selected metrics or certain groups, e.g., retriever_metrics, generator_metrics, all_metrics
results = evaluator.evaluate(rag_results, all_metrics)

if not os.path.exists("metric"):
    os.mkdir("metric")

result_file = open("metric/ragcheck_metrics_results.json", "w")
json.dump(results, result_file)
result_file.close()

