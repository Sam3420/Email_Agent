# use pandas ai to take decesions and 
# langchain chatollama and with structured output
# plus pydantic for strctured output
#  
# 
# or prcoess find the priorty 
# insert the prioroity into the db 


from sqlalchemy import create_engine
import psycopg2
# from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import BaseModel , Field 
from typing import Literal,Optional
from retrieve import Retrieve
import os
from dotenv import load_dotenv

load_dotenv()

class decide(BaseModel):
    priority:Literal["High_Priority" , "Medium_Priority" , "Low_Priority"]=Field(description="""The priority levels are defined as follows:
        1. High_Priority: Emails that require immediate attention, such as those containing urgent requests, deadlines, or critical information.
        2. Medium_Priority: Emails that are important but do not require immediate action, such as those containing important updates, meetings, or non-urgent requests.
        3. Low_Priority: Emails that are informational or can be addressed at a later time, such as newsletters, promotional content, or routine communications.

        Based on the email content and the extracted entities, please determine the priority level of this email (High Priority, Medium Priority, or Low Priority) and provide a brief explanation for your decision.""")
    
    intent:Optional[str]=Field(description="the intent of the email like whether it is a request , a query , a complaint , an update or a job opportunity   , make sure the intent is relevant to the content of the email and the extracted entities and must strictly be short" , max_length=50)


def prioritise(state:Retrieve)->dict:
    llm=ChatOpenAI(model="cisai-pro-2" , base_url=os.getenv("OPENAI_BASE_URL") , api_key=os.getenv("api_key"))
    engine=create_engine(os.getenv("engine"))
    conn=psycopg2.connect(
        host=os.getenv("host"),
        port=os.getenv("port"),
        dbname=os.getenv("db_name"),
        user=os.getenv("username"),
        password=os.getenv("password")
    )
    cursor=conn.cursor()
    query="SELECT emails.body, emails.message_id ,processed_emails.entities from emails inner join processed_emails on emails.message_id=processed_emails.message_id ;"
    cursor.execute(query)
    results=cursor.fetchall()
    new_dict={}
    for email_content , message_id , entities in results:
        agent=llm.with_structured_output(decide)
        response=agent.invoke(f"this is body of the email:{email_content} , these are the entities from this email:{entities}")
        new_dict[message_id]=response
        print(new_dict)
    state.intent_priority=new_dict
    return state
    

def add_priority_to_db(state:Retrieve):
    for message_id , priority_info in state.intent_priority.items():
        print(f"Updating priority for message_id: {message_id}")
        priority=priority_info.priority
        intent=priority_info.intent
        update_query="UPDATE processed_emails SET priority=%s , intent=%s WHERE message_id=%s"
        cursor.execute(update_query , (priority , intent , message_id))
        # conn.commit()
    conn.commit()
    print("-----------------------priorities added to db successfully-------------------------")


if __name__=="__main__":
    print("running main")
    result=prioritise(Retrieve)
    add_priority_to_db(result)
    






