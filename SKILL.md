---
name: busca-contatos-apollo
description: Use quando o usuario pedir para buscar emails e telefones de contatos via Apollo.io, enriquecer dados de contato em uma planilha Google Sheets, preencher colunas de email/telefone lendo LinkedIn URLs, ou qualquer variacao de "buscar contatos no Apollo", "enriquecer contatos", "pegar email pelo LinkedIn".
---

# Busca de Contatos — Apollo.io

Automatiza o enriquecimento de contatos via Apollo.io People Enrichment, lendo URLs de LinkedIn da coluna O de uma planilha Google Sheets e escrevendo os resultados nas colunas M (Telefone) e N (E-mail).

**Nota:** A API Apollo nao retorna telefone de forma sincrona (exige webhook). Telefone sera sempre gravado como "N.A." — apenas email e retornado.

## Estrutura fixa da planilha

| Col | Campo     | Papel nesta skill                          |
|-----|-----------|--------------------------------------------|
| M   | Telefone  | **escrito** — sempre "N.A." (ver nota acima) |
| N   | E-mail    | **escrito** — email encontrado ou "N.A."    |
| O   | LinkedIn  | **lido** — URL do perfil individual         |

Linhas 1-4 sao cabecalho. Dados a partir da linha 5.

**Regra de skip (Opcao A):** Se a coluna M **ou** a coluna N ja tiver qualquer conteudo (inclusive "N.A."), a linha e pulada.

---

## Passo 1 — Verificar configuracao

Verifique se existem no diretorio do projeto:
- `.env` com `APOLLO_API_KEY` preenchida
- `config.json` presente (ja configurado para as colunas M, N, O)
- gspread OAuth2 ja configurado (mesmo setup do busca-linkedin)

Se `.env` nao existir:
```bash
cp config/.env.example .env
```
Orientar o usuario a editar `.env` e preencher `APOLLO_API_KEY` com a chave de `app.apollo.io > Settings > Integrations > API`.

Se as dependencias nao estiverem instaladas:
```bash
pip install -r requirements.txt
```

---

## Passo 2 — Coletar informacoes do usuario

Pergunte ao usuario:

1. **URL da planilha Google Sheets**
2. **Nome da aba** (ex: `Mapeamento`)
3. **A partir de qual linha processar?** (padrao: 5)
4. **Quantos contatos processar nessa rodada?**

Se o usuario informar "linha X ate linha Y", calcular limit = Y - start_row + 1.

---

## Passo 3 — Executar o script

```bash
python main.py --sheet-url "URL_DA_PLANILHA" --sheet-name "NOME_DA_ABA" --start-row LINHA --limit QUANTIDADE
```

**Atencao:** Se for a primeira execucao do gspread neste ambiente, o navegador abrira para autenticacao Google — informe o usuario antes de rodar.

---

## Passo 4 — Relatorio

O script exibe o relatorio automaticamente ao finalizar. Nao e necessaria nenhuma acao adicional apos a execucao.

---

## Problemas comuns

| Problema | Solucao |
|----------|---------|
| `APOLLO_API_KEY nao encontrada` | Preencher `.env` com a chave |
| `SpreadsheetNotFound` | Verificar URL da planilha e permissao de acesso |
| `WorksheetNotFound` | Nome da aba e case-sensitive — verificar exatamente |
| `ModuleNotFoundError` | Rodar o pip install acima |
| Rate limit (429) | O script aguarda 60s automaticamente e retenta |
| Erro HTTP 422 | API key nao esta no header — verificar modules/apollo.py |
| Linhas com "N.A." nao sao reprocessadas | A regra de skip bloqueia qualquer conteudo em M ou N; para reprocessar, limpar as celulas manualmente ou via script antes de rodar |

---

## Nota sobre creditos Apollo

O plano Free tem 50 creditos de exportacao por mes. Cada chamada de People Match consome 1 credito.
Monitorar em: `app.apollo.io > Settings > Credits`
