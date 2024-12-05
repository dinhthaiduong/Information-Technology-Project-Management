from ragchecker import RAGResults, RAGChecker
from ragchecker.metrics import all_metrics
import json

# initialize ragresults from json/dict
with open("examples/checking_inputs.json") as fp:
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

result_file = open("examples/metrics_results.json", "w")
json.dump(results, result_file)
result_file.close()

