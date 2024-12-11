from tqdm import tqdm
from grag.rag import GraphRag
from dotenv import load_dotenv
import os
import sys
import asyncio

from grag.utils import RagMode, batchs, split_text_into_chunks

_ = load_dotenv()

WORK_DIR = ".uet_script/"
NEO4J_AUTH = os.getenv("NEO4J_AUTH") or "neo4j/password"
NEO4J_USER, NEO4J_PASSWORD = NEO4J_AUTH.split("/")

async def main():
    graph_rag = GraphRag(
        WORK_DIR,
        # "ollama/qwen2",
        "openai/gpt4-o1-mini",
        os.getenv("BOLT_URI") or "bolt://localhost:7688",
        (NEO4J_USER, NEO4J_PASSWORD),
        mode=RagMode.Create,
    )

    file = open(sys.argv[1])
    content = file.read()
    chunks = split_text_into_chunks(content)
    total_batchs = list(batchs(chunks, 100))

    for chunk in tqdm(total_batchs):
        _ = await graph_rag.insert_batch(chunk, 100)

        inserted = graph_rag.write_to_db()
        print("Insert ", str(inserted), " value")

if __name__ == "__main__":
    asyncio.run(main())
