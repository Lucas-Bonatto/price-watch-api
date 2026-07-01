# API de Monitoramento de Preços

![Tests](https://github.com/Lucas-Bonatto/price-watch-api/actions/workflows/tests.yml/badge.svg)

API desenvolvida em Python para cadastrar produtos, coletar preços via web scraping, salvar histórico de preços e verificar alertas quando o preço atual atingir ou ficar abaixo do preço desejado.

Este projeto simula um cenário real de backend, com organização em camadas, banco de dados, documentação automática, tratamento de erros e testes automatizados.

## Funcionalidades

- Cadastro de produtos para monitoramento
- Listagem de produtos cadastrados
- Busca de produto por ID
- Atualização parcial de produto
- Remoção de produto
- Coleta de dados via web scraping
- Salvamento de histórico de preços
- Consulta de histórico por produto
- Verificação de alerta de preço
- Documentação automática com Swagger
- Testes automatizados com Pytest

## Tecnologias utilizadas

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Requests
- BeautifulSoup4
- Pytest
- Uvicorn

## Estrutura do projeto

```text
price-watch-api/
├── app/
│   ├── models/
│   │   ├── price_history.py
│   │   └── product.py
│   ├── routers/
│   │   ├── alert_router.py
│   │   ├── history_router.py
│   │   ├── product_router.py
│   │   └── system_router.py
│   ├── schemas/
│   │   ├── alert.py
│   │   ├── price_history.py
│   │   ├── product.py
│   │   └── scraper.py
│   ├── scrapers/
│   │   └── product_scraper.py
│   ├── services/
│   │   └── alert_service.py
│   ├── database.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_alert_service.py
│   ├── test_product_routes.py
│   └── test_system_routes.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Como rodar o projeto

Clone o repositório:

```bash
git clone https://github.com/Lucas-Bonatto/price-watch-api.git
cd price-watch-api
```

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual.

No Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Rode a API:

```bash
uvicorn app.main:app --reload
```

Acesse a documentação automática:

```text
http://127.0.0.1:8000/docs
```

## Endpoints principais

### Sistema

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Página inicial da API |
| GET | `/health` | Verifica se a API está funcionando |

### Produtos

| Método | Rota | Descrição |
|---|---|---|
| POST | `/products` | Cadastra um novo produto |
| GET | `/products` | Lista todos os produtos |
| GET | `/products/{product_id}` | Busca um produto por ID |
| PATCH | `/products/{product_id}` | Atualiza parcialmente um produto |
| DELETE | `/products/{product_id}` | Remove um produto |
| POST | `/products/{product_id}/scrape` | Coleta dados atuais do produto |

### Histórico

| Método | Rota | Descrição |
|---|---|---|
| GET | `/products/{product_id}/history` | Lista o histórico de preços do produto |

### Alertas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/products/{product_id}/alert` | Verifica se o produto atingiu o preço desejado |

## Exemplo de cadastro de produto

```json
{
  "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "name": "Livro de teste",
  "target_price": 40
}
```

## Exemplo de resposta do scraper

```json
{
  "source_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "scraped_name": "A Light in the Attic",
  "current_price": 51.77,
  "available": true,
  "history_id": 1,
  "checked_at": "2026-07-01T18:30:00",
  "alert_triggered": false,
  "alert_message": "O produto ainda está acima do preço desejado."
}
```

## Exemplo de alerta

```json
{
  "alert_triggered": true,
  "alert_message": "O produto atingiu o preço desejado.",
  "product_id": 4,
  "product_name": "Livro de teste",
  "target_price": 60,
  "current_price": 51.77
}
```

## Como rodar os testes

Com o ambiente virtual ativado, execute:

```bash
pytest
```

Resultado esperado:

```text
11 passed
```

## Banco de dados

O projeto usa SQLite para facilitar a execução local.

O arquivo do banco é criado automaticamente ao rodar a aplicação:

```text
price_watch.db
```

Esse arquivo não é versionado no GitHub, pois está incluído no `.gitignore`.

## Boas práticas aplicadas

- Separação de responsabilidades em routers, schemas, models, services e scrapers
- Uso de ORM com SQLAlchemy
- Validação de dados com Pydantic
- Tratamento de erros com HTTPException
- Banco separado para testes
- Testes automatizados com Pytest
- Documentação automática da API
- Histórico de preços persistido em banco
- Serviço separado para regra de alerta
- Uso de `.gitignore` para evitar versionar ambiente virtual, cache e banco local

## Roadmap

- Adicionar envio de alertas por e-mail
- Adicionar integração com Telegram
- Criar autenticação de usuários
- Criar agendamento automático de scraping
- Adicionar Docker
- Adicionar GitHub Actions para rodar testes automaticamente
- Migrar de SQLite para PostgreSQL
- Melhorar suporte a diferentes sites com seletores configuráveis

## Status do projeto

Em desenvolvimento.

A versão atual já possui API funcional, scraping, histórico de preços, alertas, atualização de produtos, organização em routers e testes automatizados.

## Autor

Desenvolvido por Lucas Bonatto.

GitHub: [Lucas-Bonatto](https://github.com/Lucas-Bonatto)

Contato: lucas.jorchuabonatto@gmail.com