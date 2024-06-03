from bs4 import BeautifulSoup
import requests
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import uuid
import re

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
            if results["matches"][0]["metadata"]["url"] == url:
                out= (True, results["matches"]["metadata"])
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
if __name__ == "__main__":  
    print(getWebsiteContent("https://huggingface.co/"))
   
