# UroBot Loja (Flask + ChromaDB + Ollama)

Projeto de assistente de moda com:
- scraper de produtos da MO (`modalfa.py`)
- indexacao vetorial em ChromaDB (`produtos/init_database.py`)
- API Flask para chat (`produtos/flask_app.py`)
- frontend simples em HTML/CSS/JS (`produtos/index.html`)

## O que faz

O sistema responde a perguntas como:
- "tops ate 20 euros"
- "quero vestidos azuis"
- "como funciona a devolucao?"

Fluxo:
1. Pesquisa produtos/documentos na base vetorial.
2. Aplica filtros (preco, cor, tipo).
3. Gera resposta curta com Ollama.
4. Mostra produtos sugeridos no frontend.

## Estrutura

```text
TP2_B/
  modalfa.py
  dados.py
  README.md
  produtos/
    index.html
    style.css
    script.js
    flask_app.py
    init_database.py
    produtos_mo_final.csv
    marca.pdf
    entregas.pdf
    devolucoes.pdf
    trocas.pdf
    db/
```

## Requisitos

- Python 3.10+
- Ollama instalado e em execucao
- Modelo Ollama: `qwen2.5:1.5b`

Bibliotecas Python:
- `flask`
- `flask-cors`
- `chromadb`
- `ollama`
- `pandas`
- `pypdf2`
- `requests`
- `beautifulsoup4`

## Instalacao

No PowerShell, na raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask flask-cors chromadb ollama pandas pypdf2 requests beautifulsoup4
```

## Preparar dados

### 1) Gerar CSV de produtos (opcional se ja existir)

Para garantir que o CSV sai na pasta `produtos`:

```powershell
cd produtos
python ..\modalfa.py
```

Isto cria/atualiza `produtos/produtos_mo_final.csv`.

### 2) Indexar CSV + PDFs no ChromaDB

Ainda dentro de `produtos`:

```powershell
python init_database.py
```

## Correr a aplicacao

### 1) Iniciar backend Flask

Dentro de `produtos`:

```powershell
python flask_app.py
```

API em: `http://127.0.0.1:5000/chat`

### 2) Abrir frontend

Abrir `produtos/index.html` no browser.

O frontend chama o backend em `http://127.0.0.1:5000/chat`.

## Exemplo de pedido API

```bash
curl -X POST http://127.0.0.1:5000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"tops ate 20 euros\"}"
```

## Notas

- Se mudar CSV/PDFs, volta a correr `init_database.py`.
- A pasta `produtos/db` guarda a base vetorial persistente.
- `dados.py` e `produtos.csv` sao de outro scraper/dataset auxiliar e nao entram no fluxo principal do UroBot.
