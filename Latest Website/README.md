# chat and plot graph
![image](https://github.com/usmanali414/chatwithpdfFaiss/assets/102586850/5e5d3ae1-4ced-4431-bac7-981184572fce)


# chatwithpdfFaiss
chat with pdf document using long-chain and Faiss vector store

In this project, I have performed several tasks like chatting with documents like PDF, Docx, Rtf, and Txt files and Reteriving documents on the basis of given queries to chatbot

![image](https://github.com/usmanali414/chatwithpdfFaiss/assets/102586850/6d870e84-b6d7-44a1-8c17-6b06e9a80488)

as it has a side nav-bar that shows navigation to other tasks in the Task section and loaded document files in the Document Files section
and on the right side, it has a chatbox interface that takes queries and provides answers

if I Press Delete it will delete all loaded files in the Upload Directory

## Chat with Documents
![image](https://github.com/usmanali414/chatwithpdfFaiss/assets/102586850/2a1a560b-f223-4bd9-b03f-23f12618ccbb)

navigating to documents you can see if we upload documents it uploads documents to the `upload directory` and shows an `alert on the top-right side` and shows in the navigation bar what documents are loaded in `green tags`

![image](https://github.com/usmanali414/chatwithpdfFaiss/assets/102586850/dbe8fa2f-8d0b-4aae-8c2e-900c056ee48d)


If I process documents It will process documents and show an alert your documents are processed in the nav bar and then you can start the chat
In processing it first creates a splitting of documents and then stores them into Faiss Vector DataBase. In the next step user asks a query that retrieves similar results having k = 2 and then passes to the `llm model` that fetches certain answers on the basis of the query provided from documents that are uploaded

In the nav bar, it has a `Delete button` that deletes data from the uploaded directory.

## Data Retrieval 

![image](https://github.com/usmanali414/chatwithpdfFaiss/assets/102586850/cbd66afe-6005-468f-9f9b-40675cc1f0eb)

navigating to retrieval it takes input from the directory that has files in it. If there are pdf files in the Directory it will show them in  `green tag` with an alert if data is not processed it will say process data in chatbot

![image](https://github.com/usmanali414/chatwithpdfFaiss/assets/102586850/40d5f193-74d9-4d0a-911c-a0fd383c2e8c)

Then pressing the process data, It will process those documents by first loading documents generating a summary of provided documents storing them in Faiss Vector DataBase, and querying to the chatbot It will return the similar  2 documents text into the chatbot with name of that pdf file




