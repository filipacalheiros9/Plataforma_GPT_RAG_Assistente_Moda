import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
import ollama

app = Flask(__name__)
CORS(app)

client = chromadb.PersistentClient(path="db")
collection_produtos = client.get_or_create_collection(name="produtos")
collection_documentos = client.get_or_create_collection(name="documentos")


def extrair_preco_max(query):
    query = query.lower()

    match = re.search(r"(até|ate|menos de)\s*(\d+)", query)
    if match:
        return float(match.group(2))

    match = re.search(r"(\d+)\s*€", query)
    if match:
        return float(match.group(1))

    return None


def extrair_cor(query):
    query = query.lower()

    cores = [
        "preto", "preta", "branco", "branca",
        "azul", "azuis", "rosa",
        "vermelho", "vermelha",
        "verde", "verdes",
        "amarelo", "amarela",
        "cinzento", "cinza",
        "bege", "castanho"
    ]

    for cor in cores:
        if cor in query:
            return cor

    return None


def extrair_tipo(query, tipos_disponiveis):
    query = query.lower()

    for tipo in tipos_disponiveis:
        if tipo and tipo in query:
            return tipo

    return None


def pergunta_sobre_documentos(query):
    query = query.lower()

    palavras = [
        "marca", "modalfa", "quem é", "história",
        "entrega", "envio", "devolução",
        "troca", "reembolso", "prazo"
    ]

    return any(p in query for p in palavras)


def pergunta_sobre_produtos(query):
    query = query.lower()

    palavras = [
        "top", "t-shirt", "vestido", "calça",
        "saia", "casaco", "sapato", "roupa",
        "azul", "preto", "branco", "€"
    ]

    return any(p in query for p in palavras)


def aplicar_filtros(produtos, query):
    preco_max = extrair_preco_max(query)
    cor_query = extrair_cor(query)

    tipos = list(set([
        (p.get("categoria") or "").lower()
        for p in produtos
    ] + [
        (p.get("subcategoria") or "").lower()
        for p in produtos
    ]))

    tipo_query = extrair_tipo(query, tipos)

    filtrados = []

    for p in produtos:
        try:
            preco = float(str(p.get("preco", "")).replace(",", "."))
        except:
            preco = 999999

        cor = (p.get("cor") or "").lower()
        categoria = (p.get("categoria") or "").lower()
        subcategoria = (p.get("subcategoria") or "").lower()

        if preco_max and preco > preco_max:
            continue

        if cor_query and cor_query not in cor:
            continue

        if tipo_query and not (tipo_query in categoria or tipo_query in subcategoria):
            continue

        filtrados.append(p)

    return filtrados


def pesquisar_produtos(query):
    results = collection_produtos.query(query_texts=[query], n_results=20)

    produtos = []

    docs = results.get("documents", [[]])
    metas = results.get("metadatas", [[]])

    if not docs or not metas or not metas[0]:
        return []

    for i in range(len(docs[0])):
        m = metas[0][i]

        produtos.append({
            "nome": m.get("nome", ""),
            "preco": m.get("preco", ""),
            "cor": m.get("cor", ""),
            "categoria": m.get("categoria", ""),
            "subcategoria": m.get("subcategoria", ""),
            "link": m.get("link", ""),
            "imagem": m.get("imagem", "")
        })

    produtos = aplicar_filtros(produtos, query)

    return sorted(produtos, key=lambda x: float(str(x["preco"]).replace(",", ".")))[:5]


def pesquisar_documentos(query):
    results = collection_documentos.query(query_texts=[query], n_results=5)

    docs = results.get("documents", [[]])

    if not docs or not docs[0]:
        return []

    return docs[0]


def construir_contexto_produtos(produtos):
    contexto = ""
    for p in produtos:
        contexto += f"- {p['nome']} ({p['preco']}€)\n"
    return contexto


def construir_contexto_documentos(documentos):
    return "\n".join(documentos)


def process_query(query):
    usar_docs = pergunta_sobre_documentos(query)
    usar_produtos = pergunta_sobre_produtos(query)

    if usar_docs and not usar_produtos:
        documentos = pesquisar_documentos(query)

        if not documentos:
            return "Não encontrei informação sobre isso.", [], "documentos"

        contexto = construir_contexto_documentos(documentos)

        response = ollama.chat(
            model="qwen2.5:1.5b",
            messages=[{
                "role": "user",
                "content": f"{contexto}\n\nPergunta: {query}"
            }]
        )

        return response["message"]["content"].strip(), [], "documentos"

    produtos = pesquisar_produtos(query)

    if not produtos:
        return "Não encontrei produtos com essas características.", [], "produtos"

    contexto = construir_contexto_produtos(produtos)

    response = ollama.chat(
        model="qwen2.5:1.5b",
        messages=[{
            "role": "user",
            "content": f"{contexto}\n\nPergunta: {query}"
        }]
    )

    return response["message"]["content"].strip(), produtos, "produtos"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = str(data.get("message", "")).strip()

    resposta, produtos, tipo = process_query(query)

    return jsonify({
        "resposta": resposta,
        "produtos": produtos,
        "tipo_resposta": tipo
    })


if __name__ == "__main__":
    app.run(debug=True)