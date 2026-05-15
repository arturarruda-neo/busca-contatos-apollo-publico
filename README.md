# busca-contatos-apollo-publico

Enriquece contatos via [Apollo.io People Enrichment](https://apolloio.github.io/apollo-api-docs/?shell#people-enrichment): lê URLs de LinkedIn de uma coluna configurável de uma planilha Google Sheets e preenche automaticamente as colunas de e-mail e telefone.

Desenvolvido como skill do [Claude Code](https://claude.ai/code) — pode ser usado tanto via linha de comando quanto acionado pelo Claude diretamente.

## O que faz

- Lê a coluna de LinkedIn URLs configurada na sua planilha Google Sheets
- Chama a API Apollo.io para buscar o e-mail de cada perfil
- Escreve o resultado nas colunas de e-mail e telefone que você definir
- Pula linhas que já têm conteúdo nas colunas de saída (evita reprocessar)

> **Limitação:** A API Apollo não retorna telefone de forma síncrona (exige webhook). O campo Telefone é sempre gravado como `N.A.`.

## Pré-requisitos

- Python 3.8+
- Conta no [Apollo.io](https://app.apollo.io) (plano Free tem 50 créditos/mês)
- Google Sheets com autenticação OAuth2 via [gspread](https://gspread.readthedocs.io)

## Instalação

```bash
git clone https://github.com/arturarruda-neo/busca-contatos-apollo-publico.git
cd busca-contatos-apollo-publico
pip install -r requirements.txt
cp config/.env.example .env
```

Edite `.env` e preencha sua chave Apollo:

```
APOLLO_API_KEY=sua_api_key_aqui
```

A API key está em `app.apollo.io > Settings > Integrations > API`.

## Configuração do Google Sheets

Autenticação via OAuth2 com gspread. Na primeira execução o navegador abre para você autorizar o acesso. Siga a [documentação do gspread](https://docs.gspread.org/en/latest/oauth2.html) para configurar as credenciais.

## Configuração das colunas

Edite `config/config.json` para indicar quais colunas da sua planilha correspondem a cada campo:

```json
{
  "columns": {
    "linkedin": "A",
    "email": "B",
    "phone": "C"
  }
}
```

| Chave       | Descrição                                              |
|-------------|--------------------------------------------------------|
| `linkedin`  | Coluna que contém as URLs de LinkedIn (lida pelo script) |
| `email`     | Coluna onde o e-mail encontrado será gravado           |
| `phone`     | Coluna onde o telefone será gravado (sempre `N.A.`)    |

Use a letra da coluna correspondente na sua planilha (ex: `A`, `B`, `C`, `AA`...).

## Como rodar

```bash
python main.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/SEU_ID/edit" \
  --sheet-name "NOME_DA_ABA" \
  --start-row LINHA_INICIAL \
  --limit QUANTIDADE
```

| Parâmetro | Descrição |
|---|---|
| `--sheet-url` | URL completa da planilha Google Sheets |
| `--sheet-name` | Nome da aba (case-sensitive) |
| `--start-row` | Primeira linha de dados (logo após o cabeçalho) |
| `--limit` | Número máximo de contatos a processar nessa rodada |

## Uso como skill do Claude Code

1. Copie o arquivo `SKILL.md` para a pasta de skills do seu projeto Claude Code (geralmente `.claude/skills/` ou o diretório raiz do projeto)
2. No Claude Code, acione com `/busca-contatos-apollo`
3. O Claude vai guiar você pela configuração das colunas, coletar as informações da planilha, montar o comando e executar

## Créditos Apollo

O plano Free tem 50 créditos de exportação por mês. Cada chamada consome 1 crédito. Monitore em `app.apollo.io > Settings > Credits`.
