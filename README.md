## Muti-pdfs Chats
### Description
Website where users can upload PDF documents and ask questions in a chat
format. The system use LLM and different tools to extract and provide relevant
answers from the content of the documents

### 1. To run the project locally:
1. Clone the project
   ```cd multi-pdfs-chat/```
2. Create virtual environnement i you want et activated it
   
 ```python -m venv venv```
 
 ```source venv/bin/activate ```  for linux to activate venv
 
 ```.\venv\Scripts\activate ```  for windows to activate venv

4. Install packages
    ```pip install -r requirements.txt``` 
5. Create .env file
   
      Add openai key : OPENAI_API_KEY="sk-"

6. Finally to run the app
```streamlit run app.py``` 
