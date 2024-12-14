import json
from accelerate.utils import tqdm
from grag.async_client import RagAsync
from dotenv import load_dotenv
import asyncio
import sys
import os

_ = load_dotenv()


async def main():
    questions_file = open("examples/questions.json")

    questions = json.load(questions_file)
    questions_file.close()
    NEO4J_AUTH = os.getenv("NEO4J_AUTH") or "neo4j/password"
    NEO4J_USER, NEO4J_PASSWORD = NEO4J_AUTH.split("/")

    graph_rag = RagAsync(
        sys.argv[1],
        # "openai/gpt-4o-mini",
        "groq/llama3-70b-8192",
        os.getenv("BOLT_URI") or "bolt://127.0.0.1:7687",
        (NEO4J_USER, NEO4J_PASSWORD),
    )

    eval_ragcheck = {"results": []}
    eval_ragas = []
    for idx, question in enumerate(tqdm(questions)):
        ans, retrieved_context = await graph_rag.chat(question["Q"])

        eval_ragcheck["results"].append(
            {
                "query_id": idx,
                "query": question["Q"],
                "gt_answer": question["A"],
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

        eval_ragas.append(
            {
                "user_input": question["Q"],
                "retrieved_contexts": retrieved_context,
                "response": ans,
            }
        )
    ragcheck_file = open("examples/ragcheck_input.json", "w")
    ragas_file = open("examples/ragas_input.json", "w")
    json.dump(eval_ragcheck, ragcheck_file)
    json.dump(eval_ragas, ragas_file)
    ragcheck_file.close()
    ragas_file.close()


if __name__ == "__main__":
    asyncio.run(main())
