import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete
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

header = st.container()

_ = load_dotenv()

WORK_DIR = ".demo/"
NEO4J_AUTH = os.getenv("NEO4J_AUTH") or "neo4j/password"
NEO4J_USER, NEO4J_PASSWORD = NEO4J_AUTH.split("/")

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
    WORKING_DIR = "./dickens"
    graph_rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        embedding_func_max_async = 5,
        llm_model_max_async = 5,
        # llm_model_func=gpt_4o_complete  # Optionally, use a stronger model
    )

    choice = option_menu("Options", ["Upload document", "Chat"])
    flag = 0

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
            for file in files:
                file_extension = file.name.split(".")[-1]
                if file_extension == "pdf":
                    file_pdf = PdfReader(file)
                    pages_text = [page.extract_text() for page in file_pdf.pages]
                    await graph_rag.ainsert(pages_text)
                else:
                    content = file.read().decode()
                    await graph_rag.ainsert(content)

    else:
        show_graph()

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
            response1 = await graph_rag.aquery(prompt1, QueryParam(mode="hybrid"))

            with st.chat_message("assistant"):
                _ = st.markdown(response1)

            st.session_state.messages1.append(
                {"role": "assistant", "content": response1}
            )


def show_graph():
    _ = st.title("Neo4j Graph Visualization")

    uri = os.getenv("BOLT_URI") or "bolt://localhost:7687"
    user = NEO4J_USER
    password = NEO4J_PASSWORD

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
