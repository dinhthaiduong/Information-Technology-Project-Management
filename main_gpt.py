import asyncio
from pathlib import Path
from streamlit_option_menu import option_menu
import streamlit as st
from neo4j import GraphDatabase, Record
import networkx as nx
from grag.rag import GraphRag
from grag.hybridrag import HybirdRag
from grag.utils import RagMode, batchs, split_text_into_chunks
from dotenv import load_dotenv
import os
from pyvis.network import Network
import streamlit.components.v1 as components
from pypdf import PdfReader
from tqdm import tqdm

header = st.container()

_ = load_dotenv()

WORK_DIR = ".uet_gpt/"
NEO4J_AUTH = os.getenv("NEO4J_AUTH") or "neo4j/httt@2022"
os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"] = NEO4J_AUTH.split("/")

TMP_DIR = Path(__file__).resolve().parent.parent.joinpath("data", "tmp")


async def main():
    with st.sidebar:
        choice = option_menu("Navigation", ["Graph Rag"])

    if choice == "Graph Rag":
        with header:
            _ = st.title("Graph Rag")
            st.write(
                """Hello, I'm UET Mentor, a chatbot that will help you answer questions related to your studies at school"""
            )
            await hybrid_rag()


async def hybrid_rag():
    graph_rag = GraphRag(
        WORK_DIR,
        # "ollama/qwen2",
        "openai/gpt-4o-mini",
        # "ollama/llama3.2",
        os.getenv("BOLT_URI") or "bolt://localhost:7687",
        (os.getenv("NEO4J_USER") or "", os.getenv("NEO4J_PASSWORD") or ""),
        mode=RagMode.Create,
    )

    choice = option_menu("Options", ["Upload document", "Chat"])
    flag = 0

    uploaded = False
    if choice == "Upload document":
        flag = 1
        files = st.file_uploader(
            label="Upload document",
            type=["pdf", "json", "jsonl", "txt", "html"],
            accept_multiple_files=True,
        )

        if not files:
            _ = st.warning("Please upload a document")
        else:
            uploaded = True
            for file in files:
                file_extension = file.name.split(".")[-1]
                if file_extension == "pdf":
                    file_pdf = PdfReader(file)
                    page_batchs = list(batchs(file_pdf.pages, 10))
                    bar_progress = st.progress(0)
                    for idx, pages in enumerate(tqdm(page_batchs)):
                        _ = bar_progress.progress(idx / len(page_batchs))
                        chunks = split_text_into_chunks(
                            "\n".join([page.extract_text() for page in pages])
                        )
                        _ = await graph_rag.insert_batch(chunks, 100)

                        inserted = graph_rag.write_to_db()
                        print("Insert ", str(inserted), " value")

                else:
                    content = file.read().decode()
                    chunks = split_text_into_chunks(content)
                    total_batchs = list(batchs(chunks, 100))
                    bar_progress = st.progress(0)
                    for idx, chunk in enumerate(tqdm(total_batchs)):
                        _ = bar_progress.progress(idx / len(total_batchs))
                        _ = await graph_rag.insert_batch(chunk, 100)

                        inserted = graph_rag.write_to_db()
                        print("Insert ", str(inserted), " value")

                inserted = graph_rag.write_to_db()
                print("Insert ", str(inserted), " value")
    else:
        show_graph()

    hybrid_rag = HybirdRag(graph_rag)

    if uploaded:
        hybrid_rag.reload_vector_store()

    st.session_state.messages1 = []
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages1 = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages1:
        with st.chat_message(message["role"]):
            _ = st.markdown(message["content"])

    # React to user input
    if flag == 0:
        if prompt1 := st.chat_input("Ask question to document assistant"):
            st.session_state.messages1.append({"role": "user", "context": prompt1})
            for message in st.session_state.messages1:
                _ = st.chat_message("user").markdown(message["context"])

            response1 = f"Echo: {prompt1}"
            response1, _ = await hybrid_rag.chat(prompt1)

            with st.chat_message("assistant"):
                _ = st.markdown(response1)

            st.session_state.messages1.append(
                {"role": "assistant", "content": response1}
            )


def show_graph():
    _ = st.title("Neo4j Graph Visualization")

    # user input for Neo4J credential
    uri = os.getenv("BOLT_URI") or "bolt://localhost:7687"
    user = os.getenv("NEO4J_USER") or ""
    password = os.getenv("NEO4J_PASSWORD") or ""

    # Create a load graph button
    if st.button("Load Graph"):
        try:
            data = get_graph_data(uri, user, password)
            graph = create_networkx_graph(data)
            visualize_graph(graph)

            html_file = open("graph.html", "r", encoding="utf-8")
            source_code = html_file.read()
            _ = components.html(source_code, height=600, scrolling=True)
        except Exception as e:
            _ = st.error(f"Error loading page:  {e}")


def get_graph_data(uri: str, user: str, password: str) -> list[Record]:
    graph = GraphDatabase.driver(uri, auth=(user, password))
    query = """
    MATCH (n)-[r]->(m)
    RETURN n,TYPE(r),m
    LIMIT 300
    """
    data, _, _ = graph.execute_query(query)
    return data


def create_networkx_graph(data: list[Record]) -> nx.DiGraph:
    G = nx.DiGraph()
    for record in data:
        n = record["n"]
        m = record["m"]
        r = record["TYPE(r)"]

        G.add_node(n["id"], label=n["id"])
        G.add_node(m["id"], label=m["id"])
        G.add_edge(n["id"], m["id"], label=r)
    return G


def visualize_graph(g: nx.DiGraph):
    net = Network(notebook=True)
    net.from_nx(g)
    _ = net.show("graph.html")


if __name__ == "__main__":
    asyncio.run(main())
