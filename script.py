#!/usr/bin/env python3

import asyncio
from grag.async_client import RagAsync
from dotenv import load_dotenv
from langchain.text_splitter import TokenTextSplitter
import os
import sys

_ = load_dotenv()

WORK_DIR = sys.argv[1]
NEO4J_AUTH = os.getenv("NEO4J_AUTH") or "neo4j/password"
NEO4J_USER, NEO4J_PASSWORD = NEO4J_AUTH.split("/")

graph_rag = RagAsync(
    WORK_DIR,
    # "openai/gpt-4o-mini",
    "groq/llama3-70b-8192",
    db_uri=os.getenv("BOLT_URI") or "bolt://localhost:7687",
    db_auth=(NEO4J_USER, NEO4J_PASSWORD),
)

input_file = open(sys.argv[2])
text_spliter = TokenTextSplitter(chunk_size=1000, chunk_overlap=10)

async def main():
    org_text = input_file.read()
    chunks = text_spliter.split_text(org_text)

    await graph_rag.insert(chunks, 100)

asyncio.run(main())

