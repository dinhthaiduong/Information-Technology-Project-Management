import json
from tqdm import tqdm
from grag.hybridrag import HybirdRag
from grag.rag import GraphRag
from dotenv import load_dotenv
import asyncio
import os

_ = load_dotenv()

async def main():
    questions_file = open("examples/questions.json")

    questions = json.load(questions_file)
    questions_file.close()

    graph_rag = GraphRag(
        ".embed/",
        "openai/gpt-4o-mini",
        db_uri=os.getenv("BOLT_URI") or "bolt://127.0.0.1:7687",
        auth=(
            os.getenv("NEO4J_USER") or "",
            os.getenv("NEO4J_PASSWORD") or "",
        ),
    )

    hybird_rag = HybirdRag(graph_rag)

    results = {"results": []}
    for idx, question in enumerate(tqdm(questions)):
        ans, retrieved_context = await hybird_rag.chat(question["query"])
        results["results"].append(
            {
                "query_id": idx,
                "query": question.query,
                "gt_answer": question["gt_answer"],
                "response": ans,
                "retrieved_context": [
                    {
                        "doc_id": i,
                        "text": retrieved,
                    }
                    for i, retrieved in enumerate(retrieved_context)
                ],
            }
        )
    file = open("examples/checking_inputs.json", 'w')
    json.dump(results, file)
    file.close()


if __name__ == "__main__":
    asyncio.run(main())
