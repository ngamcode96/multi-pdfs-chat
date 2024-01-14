import streamlit as st
from dotenv import load_dotenv
from config.database import init_database, new_chat,get_last_chat, get_all_chats, update_column_value,get_chat_by_id
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter 
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from templates.html import css, user_template, bot_template
from utils import save_object_in_local, load_object_in_local
import os

# create new chat
def createOrNotChat():
    chat = get_last_chat()
    if chat:
        if chat[2] > 0: #check if the chat contain documents
            #create chat
            chat = new_chat()
    else:
        chat = new_chat()
    
    return chat

#extract raw_text from pdfs
def extract_raw_data_from_pdfs(pdfs):
    raw_text = ''
    for pdf in pdfs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            raw_text += page.extract_text()
    return raw_text


#split raw_text into chunks
def get_chunks(raw_data):

    text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
    )

    chunks = text_splitter.split_text(raw_data)
    return chunks

# convert text to vector (embedding) using FAISS et OpenAIEmbedding
def get_vectors_store(chunks):
    vectors_store = None
    embeddings = OpenAIEmbeddings()
    if not os.path.exists('faiss_store'):
        vectors_store = FAISS.from_texts(texts=chunks, embedding=embeddings)
        vectors_store.save_local(st.session_state.chat_directory + "/faiss_store")

    return vectors_store


# load conversation memory from local or create new
def get_conversation_memory(vector_store):
    llm = ChatOpenAI()
    if os.path.exists(st.session_state.chat_directory + "/memory.pkl"):
        st.session_state.memory = load_object_in_local(st.session_state.chat_directory + "/memory.pkl")
    else:
        st.session_state.memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory = st.session_state.memory
    )

    if os.path.exists(st.session_state.chat_directory + '/chat_history.pkl'):
        st.session_state.chat_history = load_object_in_local(st.session_state.chat_directory + '/chat_history.pkl')
    else:
        st.session_state.chat_history = []


    save_object_in_local(st.session_state.memory, file_path=st.session_state.chat_directory + "/memory.pkl")


    return conversation_chain



#documents process 
def docs_process_and_conversation_init(pdfs):
    raw_data = extract_raw_data_from_pdfs(pdfs)
    chunks = get_chunks(raw_data)
    vector_store = get_vectors_store(chunks)
    conversation = get_conversation_memory(vector_store)

    #update chat
    st.session_state.current_chat = update_column_value("number_docs_uploaded", len(pdfs), st.session_state.current_chat[0])
    return conversation


# get stored conversation from local
def get_stored_conversation():
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.load_local(st.session_state.chat_directory + "/faiss_store", embeddings)
    conversation = get_conversation_memory(vector_store)
    return conversation

  

#init all session variables
def init_session_variables():
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None
    if "chat_directory" not in st.session_state:
        st.session_state.chat_directory = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "memory" not in st.session_state:
        st.session_state.memory = None
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

# display conversation
def show_conversation():
    for i, message in enumerate(st.session_state.chat_history):
        if(i % 2 == 0):
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)   

# get response after user query
def get_response_from_query(user_query):
    response = st.session_state.conversation({'question': user_query})
    st.session_state.chat_history = response['chat_history']
    save_object_in_local(response['chat_history'], st.session_state.chat_directory + '/chat_history.pkl')
    save_object_in_local(st.session_state.memory, file_path=st.session_state.chat_directory + "/memory.pkl")


# main function
def main():
    load_dotenv()
    
    st.set_page_config(page_title="Multi PDFs chat")
    st.header("Multi PDFs chat :books:")

    #init session variable
    init_session_variables()

    #init sqlite database
    init_database()

    #load css
    st.write(css, unsafe_allow_html=True)

    if st.session_state.current_chat == None:
        st.session_state.current_chat = createOrNotChat()

    #sidebar
    st_sidebar = st.sidebar
    st_sidebar.subheader("Chat history")

    list_chats = get_all_chats()

    #chat history
    for chat in list_chats:
        btn_chat = st_sidebar.button(chat[1], key=chat[0])
        if btn_chat:
            st.session_state.current_chat = chat
            st.session_state.chat_directory = "saved/chats/" + str(st.session_state.current_chat[0])
            st.session_state.memory = None
            st.session_state.chat_history = []
            st.session_state.conversation = None
    
    st.session_state.chat_directory = "saved/chats/" + str(st.session_state.current_chat[0])

    if st.session_state.current_chat[2] == 0: # if chat doesn't contain documents
        pdfs = st.file_uploader("Upload your documents", accept_multiple_files=True)
        if pdfs:
            btn_process = st.button("Process")
            if btn_process:
                with st.spinner("Processing..."):
                    print(pdfs)
                    st.session_state.conversation = docs_process_and_conversation_init(pdfs=pdfs)
                    createOrNotChat()
    
    if st.session_state.current_chat[2] > 0:
        st.write(f"{st.session_state.current_chat[2]} documents are uploaded. Now you can ask your questions")
        #load stored conversation 
        st.session_state.current_chat = get_chat_by_id(st.session_state.current_chat[0])
        st.session_state.conversation = get_stored_conversation()

        with st.form("Question",clear_on_submit=True):
            user_query = st.text_input("Ask your question", key="input_query")
            submitted = st.form_submit_button("Send")
            if submitted:
                get_response_from_query(user_query=user_query)
                update_column_value("title", user_query, st.session_state.current_chat[0])
           
        show_conversation()

    

    





if __name__ == '__main__':
    main()