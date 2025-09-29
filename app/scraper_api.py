from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import os
import uuid
import json
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField
from openai import AzureOpenAI

load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "web-index")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class URLRequest(BaseModel):
    url: str

class Pregunta(BaseModel):
    texto: str
    tono: str = "neutral"
    tipo_respuesta: str = "explicacion detallada"

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2023-07-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def scrapear_texto(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GarajeBot/1.0; +https://tu-dominio.com/bot)"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=" ", strip=True)

def chunk_text(texto: str, max_chars=1000):
    palabras = texto.split()
    chunks, actual = [], []
    for palabra in palabras:
        if len(" ".join(actual + [palabra])) <= max_chars:
            actual.append(palabra)
        else:
            chunks.append(" ".join(actual))
            actual = [palabra]
    if actual:
        chunks.append(" ".join(actual))
    return chunks

def crear_indice_vacio():
    index_client = SearchIndexClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(AZURE_SEARCH_KEY)
    )
    if AZURE_SEARCH_INDEX in [i.name for i in index_client.list_indexes()]:
        index_client.delete_index(AZURE_SEARCH_INDEX)

    fields = [
        SimpleField(name="id", type="Edm.String", key=True),
        SearchableField(name="title", type="Edm.String"),
        SearchableField(name="content", type="Edm.String"),
        SimpleField(name="metadata", type="Edm.String")
    ]
    index = SearchIndex(name=AZURE_SEARCH_INDEX, fields=fields)
    index_client.create_index(index)

def subir_chunks(chunks, source_url):
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX,
        credential=AzureKeyCredential(AZURE_SEARCH_KEY)
    )
    docs = []
    for i, chunk in enumerate(chunks):
        doc = {
            "id": str(uuid.uuid4()),
            "title": f"Fragmento {i+1}",
            "content": chunk,
            "metadata": json.dumps({"source": source_url})
        }
        docs.append(doc)
    search_client.upload_documents(docs)

    with open("data/chunks_guardados.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

@app.post("/scrap")
def scrapear_y_subir(data: URLRequest):
    try:
        crear_indice_vacio()
        texto = scrapear_texto(data.url)
        chunks = chunk_text(texto)
        subir_chunks(chunks, data.url)
        return {"resultado": f"Scrapeo completado ({len(chunks)} fragmentos subidos)."}
    except Exception as e:
        return {"resultado": f"Error: {str(e)}"}

@app.post("/chat")
def chat(pregunta: Pregunta):
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX,
        credential=AzureKeyCredential(AZURE_SEARCH_KEY)
    )
    resultados = list(search_client.search(pregunta.texto, top=3))
    contexto = "\n\n".join([r["content"] for r in resultados if "content" in r])

    intro = "Según el contexto..."

    user_prompt = f"""
Usa ÚNICAMENTE el siguiente contexto para responder la pregunta.
Si encuentras información relevante, empieza tu respuesta con:
- "{intro}"
Si NO, empieza con:
- "En la información dada, no hay nada sobre lo que preguntas pero..."

Adapta la respuesta a:
- Tono: {pregunta.tono}
- Tipo de respuesta: {pregunta.tipo_respuesta}

Contexto:
{contexto}

Pregunta:
{pregunta.texto}
"""

    system_message = (
        "Eres un asistente experto. "
        f"Adapta tu tono a '{pregunta.tono}'. "
        f"Redacta el contenido como una '{pregunta.tipo_respuesta}'. "
        "Responde solo con el contexto proporcionado y aclara si utilizas información externa."
    )

    respuesta = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=4000
    )

    return {"respuesta": respuesta.choices[0].message.content}
