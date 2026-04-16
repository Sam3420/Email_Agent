# Gmail Agent
This project uses a LangGraph-based agent pipeline to automatically fetch unread Gmail emails, extract structured information, summarize content, classify priority/intent, and persist results into a local database.
[!image](graph.png)

- Node Fecth emails : uses readonly endpoint to extract unread emails from inbox (currently hardcoded to get 10 unread emails)
- Node entity_extarction_agent : agent that extracts entities like name  ,organisation ,phone  ,url ,financial_address ,if_attachment_exists ,actionable items,deadlines , unique_identifier .Now the database is updated with the new entity information
- Node summarize : summarizes the email
- Node priority_intent_agent : the extracted entities and the summary is fed to this agent to categorize the email (low , medium , high) and to extract the intent .
- Node add_priority_to_db :Updates the database with priority and intent specified for each email


## Pre-requisites:
- downlaoding the credentials.json file from cloud console fro gmail agent (refer :https://developers.google.com/workspace/gmail/api/quickstart/python)

## Usage :
- run the command : docker compose up -d

## Points to note:
- Database is automatically set up if not present in the environment
- Multiple agents were used to overcome the context window limitations
- SOLID principals applied 