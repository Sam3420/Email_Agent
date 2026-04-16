from langchain.agents import create_agent
from extract_data import extract
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from retrieve import Retrieve
# from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()


# prompt_template = ChatPromptTemplate.from_messages([
#     ("system", "Extract the following entities from the email: {entities}"),
#     ("user", "{email_text}")
# ])
def extract_entities(state:Retrieve)->dict:
    print("-----------------------entity extraction has began--------------------------")
    llm = ChatOpenAI(model="cisai-pro-2" , base_url=os.getenv("OPENAI_BASE_URL") , api_key=os.getenv("api_key"))
    new_dict={}
    print(f"----------------------------------------------length:--{len(state.messages)}-----------------------------------------------------")
    for i in state.messages:
        agent = llm.with_structured_output(extract)
        res=agent.invoke(i["messages"])
        new_dict[i["msg_id"]]=res.model_dump()
    state.extracted_entities=new_dict
        
    return state







# if __name__ =="__main__":
#     email_text="hi Sam here  ,this email is being sent to you from CISAI , you have successfully got the internship at CISAI  , in Amritapuri , Kerala ,now reply to this email with accept to accept the offer letter which, please respond by 12pm 31st jan"
#     res=extract_entities(llm , email_text)
#     print(res)
#     add_data_to_db(res)


 
