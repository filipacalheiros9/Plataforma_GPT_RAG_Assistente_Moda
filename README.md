# Assistente Moda (Flask + ChromaDB + Ollama)

Projeto de assistente de moda com:
- scraper de produtos da MO (`modalfa.py`)
- indexacao vetorial em ChromaDB (`produtos/init_database.py`)
- API Flask para chat (`produtos/flask_app.py`)
- frontend simples em HTML/CSS/JS (`produtos/index.html`)
- execucao em Docker (`Dockerfile` e `docker-compose.yml`)

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
  Dockerfile
  docker-compose.yml
  requirements.txt
  modalfa.py
  dados.py
  README.md
  arquitetura.png
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
    db/                  # gerado localmente pelo ChromaDB
```

## Requisitos

- Docker Desktop
- Ollama instalado e em execucao
- Modelo Ollama: `qwen2.5:1.5b`

As bibliotecas Python estao no ficheiro `requirements.txt`:
- `flask`
- `flask-cors`
- `chromadb`
- `ollama`
- `pandas`
- `pypdf2`
- `requests`
- `beautifulsoup4`

## Preparar o projeto

No PowerShell, na raiz do projeto:

```powershell
docker compose build
```

Confirma tambem que o Ollama esta aberto no computador e que o modelo existe:

```powershell
ollama pull qwen2.5:1.5b
```

## Preparar dados

Se a pasta `produtos/db` ainda nao existir ou se mudares o CSV/PDFs:

```powershell
docker compose run --rm modabot python init_database.py
```

Isto cria a base vetorial local em `produtos/db`. Esta pasta e gerada e nao precisa de ser enviada no Git.

## Correr com Docker

```powershell
docker compose up
```

Depois abrir:

```text
http://localhost:5000
```

API em:

```text
http://localhost:5000/chat
```

O container usa o Ollama instalado no computador atraves de `host.docker.internal:11434`.

## Gravar video pelo Docker Desktop

Para mostrar ao professor a app a funcionar pelo Docker Desktop:

1. Garante que ja fizeste `docker compose build`.
2. Garante que ja fizeste `docker compose run --rm modabot python init_database.py`.
3. Abre o Docker Desktop.
4. Em `Containers`, procura o projeto `tp2_b`.
5. Clica no botao Play.
6. Quando o estado ficar `Running`, abre `http://localhost:5000`.
7. Testa uma pergunta, por exemplo `tops ate 20 euros` ou `como funciona a devolucao?`.

## Atualizar produtos

O CSV principal ja existe em `produtos/produtos_mo_final.csv`. Se for preciso voltar a gerar:

```powershell
cd produtos
python ..\modalfa.py
```

Isto cria/atualiza `produtos/produtos_mo_final.csv`.

## Exemplo de pedido API

```bash
curl -X POST http://localhost:5000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"tops ate 20 euros\"}"
```

## Ficheiros da entrega

Manter:
- `Dockerfile`, `docker-compose.yml`, `requirements.txt`
- `README.md`
- `modalfa.py`
- `produtos/flask_app.py`, `produtos/init_database.py`
- `produtos/index.html`, `produtos/style.css`, `produtos/script.js`
- `produtos/produtos_mo_final.csv`
- PDFs em `produtos/`
- `arquitetura.png`

Nao e preciso enviar/guardar no Git:
- `.venv/` ou `venv/`
- `__pycache__/`
- `produtos/db/`
- videos gravados para demonstracao, como `*.mp4`

## Notas

- Se mudares CSV/PDFs, volta a correr `docker compose run --rm modabot python init_database.py`.
- `dados.py` e `produtos.csv` sao auxiliares de outro scraper/dataset e nao entram no fluxo principal do ModaBot.
