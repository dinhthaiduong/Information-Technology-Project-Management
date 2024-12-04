#This python code will create an interactive Chatbot to talk to documents.
import streamlit as st
import os
import sys
import tempfile
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain,RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings

# Vietnam Embedding
from sentence_transformers import SentenceTransformer
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import Ollama

from langchain.chat_models import ChatOpenAI
from streamlit_option_menu import option_menu
#Tích hợp Langsmith
from dotenv import load_dotenv, find_dotenv
from langsmith import Client
#Phần này cho Knowledge Graph
from py2neo import Graph
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

from KnowledgeGraph_Neo4j import RAG_Graph
from Adaptive_RAG import build_graph, get_vectore_retriever
from langchain_groq import ChatGroq
#Reranking documents 
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

#Tải API key của Langsmith
load_dotenv(find_dotenv())
os.environ["GROQ_API_KEY"]=str(os.getenv("GROQ_API_KEY"))
os.environ["COHERE_API_KEY"]=str(os.getenv("COHERE_API_KEY"))



#Initialize the Client

#Create temporary folder location for document storage
TMP_DIR = Path(__file__).resolve().parent.parent.joinpath('data','tmp')
llm = ChatGroq(temperature = 0.5,groq_api_key=os.environ["GROQ_API_KEY"],model_name="llama3-70b-8192")


header = st.container()

def streamlit_ui():

    with st.sidebar:
        choice = option_menu('Navigation',["Home",'Simple RAG','RAG with Neo4J'])

    if choice == 'Home':
        st.title("Welcome to UET Mentor")

    elif choice == 'Simple RAG':
        with header:
            st.title('RAG using Vector Storage')  
            st.write("""Hello, I'm UET Mentor, a chatbot that will help you answer questions related to your studies at school""")
            source_docs = st.file_uploader(label ="Upload a document", type=['pdf'], accept_multiple_files=True)
            if not source_docs:
                st.warning('Please upload a document')
            else:
                RAG(source_docs)
    
    elif choice == 'RAG with Neo4J':
        with header:
            st.title('RAG using Knowledge Graph')
            st.write("""THello, I'm UET Mentor, a chatbot that will help you answer questions related to your studies at school""")
            RAG_Neo4j()
             
def RAG(docs):
    # Tải tài liệu
    for source_docs in docs:
        with tempfile.NamedTemporaryFile(delete=False,dir=TMP_DIR.as_posix(),suffix='.pdf') as temp_file:
            temp_file.write(source_docs.read())

    loader = DirectoryLoader(TMP_DIR.as_posix(), glob='**/*.pdf', show_progress=True)
    documents = loader.load()

    # Chia nhỏ văn bản
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    text = text_splitter.split_documents(documents)

    # Chọn mô hình Embedding và lưu vào Vector Storage
    DB_FAISS_PATH = 'vectorestore/faiss'
    embedding = HuggingFaceEmbeddings(model_name ='sentence-transformers/all-MiniLM-L6-v2',
                                         model_kwargs={'device':'cpu'})
    #embedding_model = SentenceTransformer("dangvantuan/vietnamese-embedding")
    #embedding = embedding_model.encode(text)
    db = FAISS.from_documents(text,embedding)
    db.save_local(DB_FAISS_PATH)

    # Sử dụng LLM Local (cần tải LM Studio hoặc Ollama)
    #llm = ChatOpenAI(base_url="http://localhost:1234/v1",api_key='lm-studio')
    #llm = Ollama(model="vinallama-7b-chat")

    llm = ChatGroq(temperature = 0.5,groq_api_key=os.environ["GROQ_API_KEY"],model_name="llama3-70b-8192")

    # Tạo chuỗi hỏi đáp
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        db.as_retriever(search_kwargs={'k':20}),
        return_source_documents=True
    )
    chat_history = []
    # Initialize lịch sử chat 
    if "messages" not in st.session_state:
        st.session_state.messages =[]
    
    # Màn hình hỏi đáp
    if prompt := st.chat_input("Ask question to document assistant"):
        # Hiển thi câu hỏi của người dùng
        st.chat_message("user").markdown(prompt)
        # Thêm câu hỏi của người dùng vào lịch sử chat
        st.session_state.messages.append({"role":"user","context":prompt})

        response = f"Echo: {prompt}"
        # Hiển thị câu trả lời của chatbot
        response = qa_chain({'question':prompt,'chat_history':chat_history})

        with st.chat_message("assistant"):
            st.markdown(response['answer'])
            # Nhả ra tài liệu gốc
            st.markdown(response['source_documents'])

        st.session_state.messages.append({'role':"assistant", "content":response})
        chat_history.append({prompt,response['answer']})

def RAG_Neo4j():
    rag_graph = RAG_Graph()
    choice = option_menu('Options',["Upload document",'Graph(Skip document upload)'])
    #flag = 0

    # Tải tài liệu
    if choice == 'Upload document':
        #flag = 1
        source_docs = st.file_uploader(label="Upload document", type=['pdf'],accept_multiple_files=True)
        if not source_docs:
            st.warning("Please upload a document")
        else:
            rag_graph.create_graph(source_docs,TMP_DIR)
    else:
        show_graph()

    st.session_state.messages1 = []
    # Initialize lịch sử chat
    if "messages" not in st.session_state:
        st.session_state.messages1 =[]
    
    #Display chat messages from history on app rerun
    for message in st.session_state.messages1:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    #React to user input
    #if flag == 0:
    if prompt1 := st.chat_input("Ask question to document assistant"):
        # Hiển thi câu hỏi của người dùng
        st.chat_message("user").markdown(prompt1)
        # Thêm câu hỏi của người dùng vào lịch sử chat
        st.session_state.messages1.append({"role":"user","context":prompt1})

        response1 = f"Echo: {prompt1}"
        # Hiển thị câu trả lời của chatbot
        response1 = rag_graph.ask_question_chain(prompt1)
        #response1 = rag_graph.retriever1(prompt1)

        with st.chat_message("assistant"):
            st.markdown(response1)
            st.markdown(response1['source_documents'])

        st.session_state.messages1.append({'role':"assistant", "content":response1})

def show_graph():
    st.title("Neo4j Graph Visualization")

    # Nhập user name và password của Neo4j
    uri = st.text_input("Neo4j URI", "bolt://localhost:7690")
    user = st.text_input("Neo4j username", "neo4j")
    password = st.text_input("Neo4j password", type="password")

    # Visualize đồ thị
    if st.button("Load Graph"):
        try:
            data = get_graph_data(uri,user,password)
            G = create_networkx_graph(data)
            visualize_graph(G)

            HtmlFile = open("graph.html", "r", encoding="utf-8")
            source_code = HtmlFile.read()
            components.html(source_code,height=600, scrolling=True)
        except Exception as e:
            st.error(f"Error loading page:  {e}")

# Lấy dữ liệu đồ thị từ Neo4j bằng Cypher query
def get_graph_data(uri,user,password):
    graph = Graph(uri,auth=(user,password))
    query = """
    MATCH (n)-[r]->(m)
    RETURN n,r,m
    LIMIT 100
    """

    data = graph.run(query).data()
    return data

def create_networkx_graph(data):
    G = nx.DiGraph()
    for record in data:
        n = record['n']
        m = record['m']
        r = record['r']
        G.add_node(n['id'], label=n['name'])
        G.add_node(m['id'], label=m['name'])
        G.add_edge(n['id'], m['id'], label=r['type'])
    return G

def visualize_graph(G):
    net = Network(notebook=True)
    net.from_nx(G)
    net.show("graph.html")


streamlit_ui()




