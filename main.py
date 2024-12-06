from pathlib import Path
from typing import Any
from streamlit_option_menu import option_menu
import streamlit as st
from neo4j import GraphDatabase, Record
import networkx as nx
from grag.rag import GraphRag
from grag.hybridrag import HybirdRag
from grag.utils import RagMode, split_text_into_chunks
from dotenv import load_dotenv
import os
from pyvis.network import Network
import streamlit.components.v1 as components
from pypdf import PdfReader
from tqdm import tqdm


header = st.container()
WORK_DIR = ".embed/"
load_dotenv()

TMP_DIR = Path(__file__).resolve().parent.parent.joinpath("data", "tmp")


def main():
    with st.sidebar:
        choice = option_menu("Navigation", ["Home", "Graph Rag"])

    if choice == "Home":
        _ = st.title("Welcome to UET Mentor")

    elif choice == "Graph Rag":
        with header:
            _ = st.title("Graph Rag")
            st.write(
                """Hello, I'm UET Mentor, a chatbot that will help you answer questions related to your studies at school"""
            )
            hybrid_rag()


def hybrid_rag():
    graph_rag = GraphRag(
        WORK_DIR,
        "openai/gpt-4o-mini",
        os.getenv("BOLT_URI") or "bolt://localhost:7687",
        (os.getenv("NEO4J_USER") or "", os.getenv("NEO4J_PASSWORD") or ""),
        mode=RagMode.Create,
    )

    choice = option_menu("Options", ["Upload document", "Graph(Skip document upload)"])
    flag = 0

    uploaded = False
    if choice == "Upload document":
        flag = 1
        source_docs = st.file_uploader(
            label="Upload document", type=["docx", "pdf"], accept_multiple_files=True
        )

        if not source_docs:
            _ = st.warning("Please upload a document")
        else:
            uploaded = True
            for docs in source_docs:
                # type_extension = docs.name.split(".")[-1]
                file_pdf = PdfReader(docs)
                for page in tqdm(file_pdf.pages):
                    chunks = split_text_into_chunks(page.extract_text())
                    for chunk in chunks:
                        graph_rag.insert(chunk)

                inserted = graph_rag.write_to_db()
                print("Insert ", str(inserted), " value")

    else:
        show_graph()

    hybrid_rag = HybirdRag(graph_rag, vector_model="nomic-embed-text")

    hybrid_rag.reload_vector_store()
    if uploaded:
        hybrid_rag.reload_vector_store()

    st.session_state.messages1: list[Any] = []
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
            response1 = hybrid_rag.chat(prompt1)

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
    RETURN n,r,m
    LIMIT 300
    """
    data, _, _ = graph.execute_query(query)
    return data


def create_networkx_graph(data: list[Record]) -> nx.DiGraph:
    G = nx.DiGraph()
    for record in data:
        n = record["n"]
        m = record["m"]
        r = record["r"]
        G.add_node(n["id"], label=n["id"])
        G.add_node(m["id"], label=m["id"])
        G.add_edge(n["id"], m["id"], label=r["type"])
    return G


def visualize_graph(g: nx.DiGraph):
    net = Network(notebook=True)
    net.from_nx(g)
    _ = net.show("graph.html")


if __name__ == "__main__":
    main()
