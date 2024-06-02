from bs4 import BeautifulSoup
import requests
import pinecone
from sentence_transformers import SentenceTransformer
import uuid
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
        return visible_text
def getWebsiteContent(url: str):
    '''
    Takes in a url and returns all of the website Content from that URL 
    '''
    try:
        body = requests.get(url).content
    except Exception:
        return "Failed to get page content: Invalid URL"
    a= text_from_html(body)
    return a
def insert_text(url, message, message_vec, index):
    id =uuid.uuid4()
    index.upsert(vectors=[
                {
                'id':str(id), 
                'values': message_vec, 
                'metadata':{'message': message, 'url': url},
                }
            ])
def runQuery(text, index_name, k):
    with open("PINECONEAPIKEY.txt", "r") as text_file:
        pineAPI = str(text_file.read())

    pinecone.init(      
        api_key=pineAPI,      
        environment='us-west4-gcp-free'      
    )
    index=pinecone.Index(index_name)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    vec2=vectorize(text, model)
    results = index.query(queries=[vec2], top_k=k, include_metadata=True)
    if("matches" in results):
        for i in range(k):
            if results["matches"][0]["metadata"]["url"] == text:
                return (True, results["matches"]["metadata"])
            return (False, None)
    

if __name__ == "__main__":  
    print(getWebsiteContent("https://www.pinecone.io/"))
   
