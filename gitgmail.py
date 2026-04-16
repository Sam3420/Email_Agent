import base64
import os
from dotenv import load_dotenv 
from langgraph.graph import StateGraph , START , END

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from sqlalchemy import create_engine
import psycopg2
import base64
# from langchain_ollama import ChatOllama
# from datetime import datetime,date
from email.utils import parsedate_to_datetime
from psycopg2.extras import Json


from extract import extract_entities
from retrieve import Retrieve
from priority_agent import prioritise , add_priority_to_db
import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


host=os.getenv("host")
port=os.getenv("port")
username=os.getenv("username")
db_name=os.getenv("db_name")
password=os.getenv("password")


engine=create_engine(os.getenv("engine"))
load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
llm = ChatOpenAI(model="cisai-pro-2" , base_url=os.getenv("OPENAI_BASE_URL") , api_key=os.getenv("api_key"))


conn=psycopg2.connect(
    host=host,
    port=port,
    dbname=db_name,
    user=username,
    password=password
)
cursor=conn.cursor()



def __init__(self):
    self.datalist=[]


def fetch_email(state: Retrieve):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail messages.
    """
    datalist=[]
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        
        service = build("gmail", "v1", credentials=creds)
        results = (
            service.users().messages().list(userId="me", labelIds=state.labelId, maxResults=state.maxRes , pageToken=state.pageToken , q=state.q, includeSpamTrash=state.includeSpamTrash).execute()
        )
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return state

        print("Messages:")
        print(messages)
        for message in messages:
            
            # print(f'Message ID: {message["id"]}')
            
            msg = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            msg_id=message["id"]
            payload = msg['payload']
            headers = payload['headers']
            sender = extract_sender(headers)
            time=next(h['value'] for h in headers if h['name'] == 'Date')
            
            # if re.search("^Domo", sender):
            try:
                parts = payload.get('parts')
            except Exception as e:
                print(f"Error accessing parts: {e}")
                
            
            if parts is not None:
                print("---------------reaches parts-----------------")
                parts = parts[0]
                data = parts['body']['data']
                decoded_data = base64.urlsafe_b64decode(data).decode('UTF8')
                print("----------------------decode executes---------------------------------")
                print("------------------------------------------")
                print(decoded_data)
                print("--------------------------------------------")
            else:
                print("--------------------------------------------------------------------------thsi decode is none-------------------------------------------------------------------")
                decoded_data=None
            
            # header=msg['payload']['headers']
            # print(header)
            # from_addr=next(h['value'] for h in header if h['name'] == 'From')
            
            # payload=msg['payload']
            # body=payload['body'].get('data', '')
            # decoded_bytes=base64.b64decode(body.encode('UTF-8'))
            # final_body=decoded_bytes.decode('utf-8' , errors='ignore')
            # print("----------------------------------------------------------")
            # print(decoded_bytes)
            # print("----------------------------------------------------------")


            # print("msg is being printed from here....")
            # print(msg)
            # print(f'  Subject: {msg["snippet"]}')

            subject=msg["snippet"]
            print("---------------------------------time---------------------------------")
            # dt = datetime.strptime(time, "%a, %d %b %Y %H:%M:%S %z (%Z)")
            dt=parsedate_to_datetime(time)
            print(type(dt))
            print(dt)
            print("---------------------------------------------------------------")
            if decoded_data is not None:
                datalist.append({"msg_id": msg_id, "subject": subject, "sender": sender, "time": dt ,"messages": decoded_data})

    except HttpError as error:
        print(f"An error occurred: {error}")
    state.messages=datalist
    return state

def decode_base64_data(data):
    data = data.replace("-", "+").replace("_", "/")
    decoded_data = base64.b64decode(data)
    return decoded_data


def extract_sender(headers):
    for header in headers:
        if header['name'] == 'From':
            return header['value']
    return ''

def process_list_db(state:Retrieve):
    for i in state.messages:
        res=llm.invoke(f"summarise this text{i['messages']} into max three line short summary")
        print("----------------------res------------------------------")
        print("processed" ,res.content)
        print("----------------------res------------------------------")
        i['messages']=res.content
        insert_qeury="INSERT INTO emails (message_id  , email_subject ,sender  , body  , dt ) VALUES(%s , %s , %s , %s ,%s) ON CONFLICT (message_id) DO NOTHING;"
        data=(i['msg_id'],i['subject'],i['sender'],i['messages'],i['time'])
        try:
            cursor.execute(insert_qeury, data)
            conn.commit()
        except Exception as e:
            print(f"Error inserting data: {e}")
        print("---------------------------------data_insertion_succesfull------------------------------")
    return {}


def add_to_db(state:Retrieve):
    for i in state.extracted_entities:
        insert_qeury="INSERT INTO processed_emails (message_id , entities) VALUES(%s , %s ) ON CONFLICT (message_id) DO NOTHING;"
        print("::::::::::::::::::::::::::::::::::::::::::::::")
        print(i)
        print(":::::::::::::::::::::::::::::::::::::::::::::")
        data=(i ,Json(state.extracted_entities[i]))
        try:
            cursor.execute(insert_qeury, data)
            conn.commit()
        except Exception as e:
            print(f"Error inserting data: {e}")
    print("---------------------------------------data insertion completed------------------------------------")





builder = StateGraph(Retrieve)
builder.add_node("fetch" , fetch_email)
builder.add_node("summarise" , process_list_db)
builder.add_node("entity_extraction_agent", extract_entities)
builder.add_node("add_to_db",add_to_db)
builder.add_node("priority_intent_agent", prioritise)
builder.add_node("add_priority_to_db", add_priority_to_db)

builder.add_edge(START ,"fetch")
builder.add_edge("fetch" , "entity_extraction_agent")
builder.add_edge("fetch","summarise")
builder.add_edge("entity_extraction_agent","add_to_db")
builder.add_edge("add_to_db","priority_intent_agent")
builder.add_edge("summarise","priority_intent_agent")
builder.add_edge("priority_intent_agent","add_priority_to_db")
builder.add_edge("add_priority_to_db", END)

graph=builder.compile()
graph.invoke({"maxRes":2, "pageToken":None , "q":"", "labelId":["UNREAD"], "includeSpamTrash":False , "extracted_entities":{}})

# png_bytes=graph.get_graph().draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(png_bytes)

