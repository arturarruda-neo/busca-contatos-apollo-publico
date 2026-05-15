# busca-contatos-apollo

Enriquece contatos via [Apollo.io People Enrichment](https://apolloio.github.io/apollo-api-docs/?shell#people-enrichment): lê URLs de LinkedIn de uma planilha Google Sheets e preenche automaticamente as colunas de e-mail e telefone.

Desenvolvido como skill do [Claude Code](https://claude.ai/code) — pode ser usado tanto via linha de comando quanto acionado pelo Claude diretamente.

## O que faz

- Lê a coluna O (LinkedIn URL) de uma planilha Google Sheets
- Chama a API Apollo.io para buscar o e-mail corporativo de cada perfil
- Escreve o resultado nas colunas M (Telefone) e N (E-mail)
- Pula linhas que já têm conteúdo em M ou N (regra de skip)

> **Limitação:** A API Apollo não retorna telefone de forma síncrona (exige webhook). O campo Telefone é sempre gravado como `N.A.`.

## Pré-requisitos

- Python 3.8+
- Conta no [Apollo.io](https://app.apollo.io) (plano Free tem 50 créditos/mês)
- Google Sheets com autenticação OAuth2 via [gspread](https://gspread.readthedocs.io)

## Instalação

```bash
git clone https://github.com/arturarruda-neo/busca-contatos-apollo.git
cd busca-contatos-apollo
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

## Estrutura esperada da planilha

| Coluna | Campo    | Papel                                        |
|--------|----------|----------------------------------------------|
| M      | Telefone | **escrito** — sempre `N.A.` (ver limitação)  |
| N      | E-mail   | **escrito** — e-mail encontrado ou `N.A.`    |
| O      | LinkedIn | **lido** — URL do perfil individual          |

Linhas 1–4 são cabeçalho. Dados a partir da linha 5.

## Como rodar

```bash
python main.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/SEU_ID/edit" \
  --sheet-name "Mapeamento" \
  --start-row 5 \
  --limit 50
```

| Parâmetro | Descrição |
|---|---|
| `--sheet-url` | URL completa da planilha Google Sheets |
| `--sheet-name` | Nome da aba (case-sensitive) |
| `--start-row` | Linha inicial dos dados (padrão: 5) |
| `--limit` | Número máximo de linhas a processar |

## Uso como skill do Claude Code

Se você usa Claude Code, copie `SKILL.md` para o diretório de skills do seu projeto e acione com `/busca-contatos-apollo`. O Claude vai perguntar a linha inicial e a quantidade, montar o comando e executar.

## Créditos Apollo

O plano Free tem 50 créditos de exportação por mês. Cada chamada consome 1 crédito. Monitore em `app.apollo.io > Settings > Credits`.
