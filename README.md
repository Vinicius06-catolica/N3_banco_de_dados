# API de Interação com MongoDB usando FastAPI

Este projeto consiste em uma API desenvolvida em Python com o framework FastAPI, projetada para realizar interações simples de cadastro e consulta com um banco de dados MongoDB.

## Setup

Siga os passos abaixo para configurar e executar o ambiente de desenvolvimento.

### Clonar o repositório

Primeiro, clone o repositório do projeto para a sua máquina local:

```bash
git clone https://github.com/Vinicius06-catolica/N3_banco_de_dados.git
```

### 1\. Ativar o ambiente virtual

**Criando o ambiente virtual:**

```bash
python -m venv .venv
```

**Ativando o ambiente virtual:**

- No Windows:
  ```bash
  .venv\Scripts\activate
  ```
- No macOS ou Linux:
  ```bash
  source .venv/bin/activate
  ```

### 2\. Instalar as dependências

Com o ambiente virtual já ativado, instale todas as bibliotecas e pacotes necessários para o projeto com o seguinte comando:

```bash
pip install -r requirements.txt
```

## Rotas da API (Endpoints)

A API disponibiliza as seguintes rotas para interação com o banco de dados:

- **Cadastrar um novo registro:**

  - `POST /cadastrar`

- **Pesquisar por nome:**

  - `GET /pesquisar_nome?nome=valor_do_nome`

- **Pesquisar por rua:**

  - `GET /pesquisar_rua?rua=valor_da_rua`

- **Pesquisar por nome de filho:**

  - `GET /pesquisar_filhos?nome_filho=valor_do_nome_do_filho`

## Coleção do Postman

Para facilitar os testes e o uso da API, um arquivo de coleção do Postman com todas as rotas configuradas está anexado na atividade.
