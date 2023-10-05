from fastapi import FastAPI, Request, File, UploadFile,Form,HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from typing import List

from chatbot import ChatWithDoc ,DocRetrieval
import tiktoken
import re
import yaml
from plotgraph import PlotGraph
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

uploads = config['Upload_Dir']


def countTokens(string: str, encoding_name= "gpt-3.5-turbo") -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

obj = ChatWithDoc(uploads,os.getenv("OPENAI_API_KEY"))

doc_retrieval = DocRetrieval(os.getenv("OPENAI_API_KEY"))

plot_generator = PlotGraph(os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def show_Docs():
    
    loaded_files_list=[]
    loaded_files = [filename for filename in os.listdir(uploads)]
    if len(loaded_files) == 0:
        loaded_files = "No Document Found"
    else:
        loaded_files_list = loaded_files
        loaded_files = ", ".join(loaded_files)

    return loaded_files,loaded_files_list

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    
    return templates.TemplateResponse("base.html", {"request": request, "loaded_files":show_Docs()})


ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'rtf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.post("/chat", response_class=HTMLResponse)
async def userInput(request: Request):
    global response_for_plot
    user_input = await request.form()
    query = user_input["msg"]
    
    has_documents = any(filename.endswith(('.pdf', '.docx', '.txt', '.rtf'))
                        for filename in os.listdir(uploads))
    if has_documents:

        input_tokens = countTokens(query)
        if query:
            try:
                chat_response = obj.doc_response(query=query)
                output_tokens = countTokens(chat_response)
                total_tokens = input_tokens + output_tokens
                response = f"{chat_response} $in input: {input_tokens} %out output: {output_tokens} &t total: {total_tokens}"
                response_for_plot = chat_response
            except:
                response = " Process Documents "
                response_for_plot = "False"

    else:
        
        
        response = f"No Document Found, Please Upload pdf, rtf, docx or text files"
        response_for_plot = "False"
        # response = """graphPlotTRUE&
        #             {
        #             "type": "pie",
        #             "values": [75, 25],
        #             "labels": ["Product A", "Product B"]
        #             }

        #             """
    return str(response)

@app.post("/plot-graph", response_class=HTMLResponse)
async def lastChat(request: Request):
    # print(response_for_plot)
    if response_for_plot != "False":
        print(response_for_plot)
        response = plot_generator.generate_plot(response_for_plot=response_for_plot)
        # response = """{
        #                 "type": "pie",
        #                 "values": [75, 25],
        #                 "labels": ["Product A", "Product B"]
        #                 }
        #         """
        print(response)
        pattern = r'```javascript(.*?)```'
        try:
            javascript_code = re.search(pattern, response, re.DOTALL).group(1)
            print(javascript_code)
        except:
            javascript_code = response
        
        return javascript_code
    else:
        response = "False"
    return response


@app.get("/delete-files")
async def delete_files():
    
    try:

        for filename in os.listdir(uploads):
            file_path = os.path.join(uploads, filename)
            os.remove(file_path)
        return {"deleted": True}
    except Exception as e:
        return {"deleted": False}




YOUTUBE_LINK_PATTERN="^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+&?|^(https?://)?(www\.)?youtu\.be/[\w-]+&?$"
@app.post("/youtube-video", response_class=HTMLResponse)
async def userInput(request: Request,link: str = Form(...)):
    link_error=False
    if link:
        if not re.match(YOUTUBE_LINK_PATTERN, link):
            # raise HTTPException(status_code=400, detail="Invalid YouTube link")
            link_error=True
        
        else:
            print("start processing youtube video")
    
    return templates.TemplateResponse("base.html", {"request": request, "link_error": link_error,"link": link,"loaded_files":show_Docs()})
    # return {"link": link}
    
    



@app.get("/process-data")
async def processing_data():
    doc_list = [filename for filename in os.listdir(uploads)]
    obj.load_documents(doc_list=doc_list)

    return {"working": "well"}


"""
Data Retrival

""" 

@app.get("/data-retrival", response_class=HTMLResponse)
async def data_retrival(request: Request):
    
    return templates.TemplateResponse("data-retrival/index.html", {"request": request, "loaded_files":show_Docs()})



def Doc_Path_list(loaded_files):
    loaded_filenames = []
    
    if len(loaded_files) == 0:
        loaded_files = "No Document Found"
    else:
        loaded_filenames = [os.path.basename(file_path) for file_path in loaded_files]
        loaded_files = ", ".join(loaded_filenames)

    return loaded_files, loaded_filenames


@app.post("/data-retrival", response_class=HTMLResponse)
async def upload_file_path(request: Request, link: str = Form(...)):
    link_error = False
    pdf_files = []
    
    if link:
        file_path = link
        if os.path.exists(file_path):
            for filename in os.listdir(file_path):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(file_path, filename)
                    pdf_files.append(file_path)
            doc_retrieval.folderPath(link)
           
        else:
            link_error = True
        # fileNames = list_pdf_filenames(file_path)
    print(doc_retrieval.folderPath(link))
    print(doc_retrieval.uploads_dir)
    # print(pdf_files)
    return templates.TemplateResponse("data-retrival/index.html", {"request": request, "link_error": link_error, "link": link, "loaded_files_path": Doc_Path_list(pdf_files)})
    

@app.get("/load-docs")
async def load_docs():
    loaded_docs = doc_retrieval.loadPdf()
    summary_docs = doc_retrieval.summary_gen(docs=loaded_docs)
    doc_retrieval.vector_db(summaryDocs=summary_docs)
    return {"working": "well"}

@app.post("/doc-text", response_class=HTMLResponse)
async def userInput(request: Request):
    user_input = await request.form()
    query = user_input["msg"]
    
    has_documents = any(filename.endswith(('.pdf'))
                        for filename in os.listdir(doc_retrieval.uploads_dir))
    if has_documents:
        if query:
            try:
                found_path = doc_retrieval.docs_found(query=query)
                response = doc_retrieval.docText(found_path=found_path)
            except:
                response = "Process Data"

    else:
        response = f"No Document Found, Please Upload pdf, rtf, docx or text files"
    return str(response)


"""
Data Documents Files

""" 

@app.get("/documents", response_class=HTMLResponse)
async def documents(request: Request):
    
    return templates.TemplateResponse("documents/index.html", {"request": request, "loaded_files":show_Docs()})

@app.post("/document", response_class=HTMLResponse)
async def upload_file(request: Request, files: list[UploadFile ]= File(...)):
    
    os.makedirs(uploads, exist_ok=True)
    file_error=False
    for file in files:
        if file:
            if allowed_file(file.filename):
                file_path = os.path.join(uploads, file.filename)
                with open(file_path, "wb") as f:
                    f.write(file.file.read())

                doc_list = [filename for filename in os.listdir(uploads)]
                # obj.load_documents(doc_list=doc_list)
                file_error=True

                uploaded_true = file.filename
            
            else:
                file_error=False
                # filetype = ', '.join(ALLOWED_EXTENSIONS)
                # uploaded_fileType = f"Only {filetype} files are allowed."
                
    return templates.TemplateResponse("documents/index.html", {"request": request, "file_error": file_error,"file": file,"loaded_files":show_Docs()})


"""
Data Youtube

""" 

@app.get("/youtube", response_class=HTMLResponse)
async def youtube(request: Request):
    
    return templates.TemplateResponse("youtube/index.html", {"request": request, "loaded_files":show_Docs()})
