import os
import pandas as pd
import chromadb
from PyPDF2 import PdfReader

CHROMA_DATA_PATH = "db"
CSV_FILE = "produtos_mo_final.csv"

PDFS = [
    ("marca.pdf", "marca"),
    ("entregas.pdf", "entregas"),
    ("devolucoes.pdf", "devolucoes"),
    ("trocas.pdf", "trocas")
]

client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

collection_produtos = client.get_or_create_collection(name="produtos")
collection_documentos = client.get_or_create_collection(name="documentos")


def limpar_colecao(collection):
    try:
        existing = collection.get()
        if existing and existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception:
        pass


def extrair_texto_pdf(path):
    reader = PdfReader(path)
    texto = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texto += page_text + "\n"

    return texto.strip()


def chunk_text(texto, tamanho=400, overlap=50):
    chunks = []
    start = 0

    while start < len(texto):
        end = start + tamanho
        chunk = texto[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += tamanho - overlap

    return chunks


def carregar_documentos_pdf():
    limpar_colecao(collection_documentos)

    all_docs = []
    all_meta = []
    all_ids = []

    for file_name, tipo in PDFS:
        if not os.path.exists(file_name):
            print(f"PDF não encontrado: {file_name}")
            continue

        texto = extrair_texto_pdf(file_name)
        chunks = chunk_text(texto)

        for i, chunk in enumerate(chunks):
            all_docs.append(chunk)
            all_meta.append({
                "source": os.path.basename(file_name),
                "tipo": tipo
            })
            all_ids.append(f"{tipo}_{i}")

    if all_docs:
        collection_documentos.add(
            documents=all_docs,
            metadatas=all_meta,
            ids=all_ids
        )
        print("Coleção 'documentos' criada com sucesso!")
    else:
        print("Não foram encontrados documentos PDF para indexar.")


def carregar_produtos_csv():
    limpar_colecao(collection_produtos)

    if not os.path.exists(CSV_FILE):
        print(f"CSV não encontrado: {CSV_FILE}")
        return

    df = pd.read_csv(CSV_FILE)

    documents = []
    metadatas = []
    ids = []

    for i, row in df.iterrows():
        base = str(row.get("Descricao", "")).strip()
        extra = f"{row.get('Cor', '')} {row.get('Categoria_Principal', '')} {row.get('Subcategoria', '')}".strip()
        texto = f"{base} {extra}".strip()

        documents.append(texto)

        metadatas.append({
            "nome": str(row.get("Nome", "")).strip(),
            "preco": str(row.get("Preço", "")).strip(),
            "cor": str(row.get("Cor", "")).strip(),
            "categoria": str(row.get("Categoria_Principal", "")).strip(),
            "subcategoria": str(row.get("Subcategoria", "")).strip(),
            "link": str(row.get("Link", "")).strip(),
            "imagem": str(row.get("Imagem", "")).strip()
        })

        ids.append(str(i))

    collection_produtos.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print("Coleção 'produtos' criada com sucesso!")


def main():
    carregar_produtos_csv()
    carregar_documentos_pdf()
    print("Base de dados inicializada com sucesso!")


if __name__ == "__main__":
    main()