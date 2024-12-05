from ragas import EvaluationDataset
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, SemanticSimilarity
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
import os
import json

ragas_file = open("examples/ragas_input.json", 'r')
eval_dataset = json.load(ragas_file)

eval_dataset = EvaluationDataset.from_list(eval_dataset)

evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
metrics = [
    LLMContextRecall(llm=evaluator_llm), 
    FactualCorrectness(llm=evaluator_llm), 
    Faithfulness(llm=evaluator_llm),
    SemanticSimilarity(embeddings=evaluator_embeddings)
]

results = evaluate(dataset=eval_dataset, metrics=metrics)

if not os.path.exists("metric"):
    os.mkdir("metric")

results_df = results.to_pandas()
results_df.to_csv("metric/ragas.csv")
