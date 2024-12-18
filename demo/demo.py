import asyncio
from streamlit_option_menu import option_menu
import streamlit as st
from neo4j import GraphDatabase, Record
import networkx as nx
from grag.async_client import RagAsync
from grag.utils import split_text_into_chunks
from dotenv import load_dotenv
import os
from pyvis.network import Network
import streamlit.components.v1 as components
from pypdf import PdfReader

async def main(work_dir: str, model: str, n_async_client: int):
    header = st.container()
    _ = load_dotenv()
    with st.sidebar:
        choice = option_menu("Navigation", ["Graph Rag"])

    if choice == "Graph Rag":
        with header:
            _ = st.title("Graph Rag")
            st.write(
                """Hello, I'm UET Mentor, a chatbot that will help you answer questions related to your studies at school"""
            )
            await hybrid_rag(work_dir, model, n_async_client)


async def hybrid_rag(work_dir: str, model: str, n_async_client: int):
    NEO4J_AUTH = os.getenv("NEO4J_AUTH") or "neo4j/password"
    NEO4J_USER, NEO4J_PASSWORD = NEO4J_AUTH.split("/")

    graph_rag = RagAsync(
        work_dir,
        model,
        # "google/gemini-1.5-flash-8b",
        # "ollama/qwen2",
        # "groq/llama3-70b-8192",
        # "openai/gpt-4o-mini",
        # "ollama/llama3.2",
        db_uri=os.getenv("BOLT_URI") or "bolt://localhost:7687",
        db_auth=(NEO4J_USER, NEO4J_PASSWORD),
    )

    choice = option_menu("Options", ["Upload document", "Chat"])
    flag = 0

    if choice == "Upload document":
        flag = 1
        files = st.file_uploader(
            label="Upload document",
            type=["pdf", "json", "jsonl", "txt", "html", "md"],
            accept_multiple_files=True,
        )

        if not files:
            _ = st.warning("Please upload a document")
        else:
            for file in files:
                file_extension = file.name.split(".")[-1]
                if file_extension == "pdf":
                    file_pdf = PdfReader(file)
                    pages_text = [page.extract_text() for page in file_pdf.pages]
                    await graph_rag.insert(pages_text, n_async_client)
                else:
                    content = file.read().decode()
                    chunks = split_text_into_chunks(content)
                    await graph_rag.insert(chunks, n_async_client)

    else:
        show_graph((NEO4J_USER, NEO4J_PASSWORD))

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
            response1, _ = await graph_rag.chat(prompt1)

            with st.chat_message("assistant"):
                _ = st.markdown(response1)

            st.session_state.messages1.append(
                {"role": "assistant", "content": response1}
            )


def show_graph(auth: tuple[str, str]):
    _ = st.title("Neo4j Graph Visualization")

    uri = os.getenv("BOLT_URI") or "bolt://localhost:7687"
    user = auth[0]
    password = auth[1]

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


def demo(work_dir: str, model: str, n_async_client: int):
    asyncio.run(main(work_dir, model, n_async_client))

