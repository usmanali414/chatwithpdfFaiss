import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter,RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.docstore.document import Document
import openai
import rawText
import yaml

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

separator = config['Splitter']['separator']
chunk_size = config['Splitter']['chunk_size']
chunk_overlap = config['Splitter']['chunk_overlap']

model_name = config['LLM_Model']['model_name']
temperature = config['LLM_Model']['temperature']

k = config['Retriever']['k']



class ChatWithDoc:
    def __init__(self, uploads_dir, api_key):
        self.uploads_dir = uploads_dir
        openai.api_key = api_key
        # self.initialize_chains()
    
    def process_documents(self, doc_list = list):
        self.raw_text = ""
        for filename in doc_list:
            if filename.endswith(".pdf"):
                pdfText = rawText.getPDFText(os.path.join("uploads", filename))
                self.raw_text += "\n"+pdfText
            elif filename.endswith(".docx"):
                docxText = rawText.getDocxText(os.path.join("uploads", filename))
                self.raw_text += "\n"+docxText
            elif filename.endswith(".rtf"):
                rtfText = rawText.getRtfText(os.path.join("uploads", filename))
                self.raw_text += "\n"+rtfText
            elif filename.endswith(".txt"):
                text = rawText.getTxtText(os.path.join("uploads", filename))
                self.raw_text += "\n"+text


    def load_documents(self,doc_list):
        self.process_documents(doc_list = doc_list)
        self.initialize_chains()

    def initialize_chains(self):
        self.text_splitter = CharacterTextSplitter(
            separator=separator,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )       
        self.splitting = self.text_splitter.split_text(self.raw_text)

        self.embeddings = OpenAIEmbeddings()
        self.document_search = FAISS.from_texts(self.splitting, self.embeddings)

        self.llm = ChatOpenAI(model_name=model_name,temperature=temperature)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.retriever = self.document_search.as_retriever(search_type="similarity", search_kwargs={"k": k})

        self.qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            chain_type='stuff',
            retriever=self.retriever,
            memory=self.memory,
        )

    def doc_response(self, query):
        result = self.qa({"question": str(query)})
        response = result['answer']
        return response


class DocRetrieval:
    def __init__(self, api_key):
        # self.uploads_dir = uploads_dir
        openai.api_key = api_key
        self.chatGPT = ChatOpenAI(temperature=temperature)
    
    def folderPath(self,path):
        folder_path = path
        resolved_folder_path = os.path.abspath(folder_path)
        self.uploads_dir = resolved_folder_path
        
    
    def loadPdf(self):
        docs_dir = os.listdir(self.uploads_dir)
        # Load PDF
        loaders = []

        for doc in docs_dir:
            if doc.lower().endswith(".pdf"):  # Check if the file has .pdf extension
                loaders.append(PyPDFLoader(os.path.join(self.uploads_dir, doc)))

        self.docs = []
        for loader in loaders:
            self.docs.extend(loader.load())
        return self.docs
    def summary_gen(self,docs: list):
        prompt  =   """You will be given a page_content of a document. Your goal is to give a concise summary of the page_content
        The page_content will be enclosed in triple backtrips (```).

        page_content :
        ```{page_content}```

        Summary:

        """
        prompt_template = ChatPromptTemplate.from_template(prompt)
        self.summary_doc_list = []

        for d in range(len(docs)):
            page_content=docs[d].page_content
            content_metadata=docs[d].metadata

            Summary_Prompt = prompt_template.format_messages(
                                page_content = page_content
                                )
            response = self.chatGPT(Summary_Prompt)


            doc =  Document(page_content = response.content, metadata = content_metadata)
            self.summary_doc_list.append(doc)  

        return self.summary_doc_list

    def vector_db(self,summaryDocs: list):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )

        splits = text_splitter.split_documents(summaryDocs)

        self.embeddings = OpenAIEmbeddings()
        self.vectorDB = FAISS.from_documents(splits, self.embeddings)

    def docs_found(self, query):
        search_docs = self.vectorDB.similarity_search(query, k=k )
        self.path=[]
        for d in search_docs:
            self.path.append(d.metadata['source'])
        return self.path

    def docText(self,found_path):
        loaders = []
        for doc in found_path:
            loaders.append(PyPDFLoader(doc))

        docsRead = []
        for loader in loaders:
            docsRead.extend(loader.load())
        self.docContent=""
        for d in docsRead:
            filename = os.path.basename(d.metadata['source'])
            Text = f"""Documents: {filename}\
            \nDocuments content: {d.page_content} \n \n"""
            self.docContent+=Text
        return self.docContent
