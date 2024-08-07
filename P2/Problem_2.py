from bs4 import BeautifulSoup
import requests
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import uuid
from langchain_openai import ChatOpenAI
import re
from langchain.agents import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_message_histories import SQLChatMessageHistory
import sys
import os
def vectorize(rawtext, model):
    arr=rawtext.split()
    if (len(arr)>256):
        quit(2)
    vector = model.encode([rawtext])
    return vector[0].tolist()
def text_from_html(body):
        soup = BeautifulSoup(body, 'html.parser')
        [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
        visible_text = soup.getText()
        out = re.sub(r'\s+', ' ', visible_text).strip()
        return out
@tool
def getWebsiteContent(url: str):
    '''
    Takes in a url and returns all of the website Content from that URL 
    '''
    with open("PINECONEAPIKEY.txt", "r") as text_file:
        pineAPI = str(text_file.read())

    pc=Pinecone(api_key=pineAPI)
    index=pc.Index("website-data")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    vec2=vectorize(url, model)
    k = 5
    results = index.query(vector=vec2, top_k=k, include_metadata=True)
    out= (False, None)
    if("matches" in results):
        for i in range(len(results["matches"])):
            if results["matches"][i]["metadata"]["url"] == url:
                out= (True, results["matches"][i]["metadata"])
                break 
    if(out[0] == False):
        try:
            body = requests.get(url).content
        except Exception:
            return "Failed to get page content: Invalid URL"
        a= text_from_html(body)
        insert_text(url, a, vectorize(url,model), index)
        return a
    else:
        return out[1]["message"]
def insert_text(url, message, message_vec, index):
    id =uuid.uuid4()

    async_result = index.upsert(vectors=[
                {
                'id':str(id), 
                'values': message_vec, 
                'metadata':{'message': message, 'url': url},
                }
            ], async_req = True)
    return async_result.get()

def get_session_history(session_id):
    return SQLChatMessageHistory(session_id, "sqlite:///memory.db")
def init_agent():
    with open("OPENAIAPIKEY.txt", "r") as text_file:
        openaiAPI=str(text_file.read())
    with open("OPENAIORGKEY.txt", "r") as txt:
        openaiOrg=str(txt.read())
    model = ChatOpenAI(api_key=openaiAPI, organization=openaiOrg)
    tools = [getWebsiteContent]
    agentExec = create_react_agent(model,tools)
    return agentExec
    # runnable = RunnableWithMessageHistory(model_with_tools, get_session_history)
    # return runnable
def run(model, query):
    template = "Given a tool to get the raw text content from a website, you must determine if the website provides any ai related services and why. Your response should have 1 sentence stating what ai services/tools they offer or 'None' if it is not ai. If you recognize the website, then you can also infer the answers."
    prompt = [SystemMessage(content=template),HumanMessage(content=query)]
    return model.invoke({"messages": prompt})
    # return model.invoke(prompt, config={"configurable": {"session_id": "1"}})
def solution(text,agent):
    output = []
    for item in text:
        response = run(agent, f"Here is the url: {item}")
        output.append(response["messages"][-1].content)
    return output
if __name__ == "__main__":  
    # print(getWebsiteContent("https://huggingface.co/"))
    if(len(sys.argv)< 3):
        print("Please pass in input file path and output file path as arguments")
        sys.exit()
    inFilePath =sys.argv[1]
    outFilePath = sys.argv[2] 
    if not (os.path.exists(inFilePath)):
        print("Error: input file doesn't exist")
        sys.exit()
    inFile = open(inFilePath,'r')
    outFile = open(outFilePath,'w')
    lines = inFile.readlines()
    agent = init_agent()
    inputSet = []
    for line in lines:
        inputSet.append(line.strip())
    output = solution(text=inputSet,agent=agent)
    for i in range(len(output)):
        if(output[i] == "None" or output[i] == "none"):
            outFile.write("not-ai, " + output[i] + "\n")
        else:
            outFile.write("ai, " + output[i] + "\n")
    # agent = init_agent()
    # response = run(agent,"Here is the url: https://huggingface.co/")
    # print(response["messages"][-1].content)
