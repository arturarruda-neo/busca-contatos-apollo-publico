---
name: busca-contatos-apollo
description: Use quando o usuario pedir para buscar emails e telefones de contatos via Apollo.io, enriquecer dados de contato em uma planilha Google Sheets, preencher colunas de email/telefone lendo LinkedIn URLs, ou qualquer variacao de "buscar contatos no Apollo", "enriquecer contatos", "pegar email pelo LinkedIn".
---

# Busca de Contatos — Apollo.io

Automatiza o enriquecimento de contatos via Apollo.io People Enrichment, lendo URLs de LinkedIn de uma coluna configuravel de uma planilha Google Sheets e escrevendo os resultados nas colunas de E-mail e Telefone definidas pelo usuario.

**Nota:** A API Apollo nao retorna telefone de forma sincrona (exige webhook). Telefone sera sempre gravado como "N.A." — apenas email e retornado.

## Estrutura da planilha

A skill opera sobre tres colunas configuradas em `config/config.json`:

| Chave em config.json | Campo    | Papel nesta skill                            |
|----------------------|----------|----------------------------------------------|
| `linkedin`           | LinkedIn | **lido** — URL do perfil individual          |
| `email`              | E-mail   | **escrito** — email encontrado ou "N.A."     |
| `phone`              | Telefone | **escrito** — sempre "N.A." (ver nota acima) |

As letras de coluna sao definidas pelo usuario em `config/config.json` antes de rodar (ex: `"linkedin": "C"`).

**Regra de skip:** Se as colunas de e-mail **ou** telefone ja tiverem qualquer conteudo (inclusive "N.A."), a linha e pulada. Para reprocessar, limpar as celulas primeiro.

---

## Passo 1 — Verificar configuracao

Verifique se existem no diretorio do projeto:
- `.env` com `APOLLO_API_KEY` preenchida
- `config/config.json` com as letras de coluna corretas para a planilha do usuario
- gspread OAuth2 configurado (doc: https://docs.gspread.org/en/latest/oauth2.html)

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

## Passo 2 — Configurar colunas

Pergunte ao usuario:

1. **Qual e a letra da coluna que contem as URLs de LinkedIn?** (ex: `A`, `B`, `C`...)
2. **Qual e a letra da coluna onde deve ser gravado o E-mail?**
3. **Qual e a letra da coluna onde deve ser gravado o Telefone?**

Com as respostas, edite `config/config.json`:

```json
{
  "columns": {
    "linkedin": "LETRA_LINKEDIN",
    "email": "LETRA_EMAIL",
    "phone": "LETRA_TELEFONE"
  }
}
```

---

## Passo 3 — Coletar informacoes da planilha

Pergunte ao usuario:

1. **URL da planilha Google Sheets**
2. **Nome da aba** (case-sensitive)
3. **A partir de qual linha processar?** (primeira linha de dados, apos o cabecalho)
4. **Quantos contatos processar nessa rodada?**

Se o usuario informar "linha X ate linha Y", calcular limit = Y - start_row + 1.

---

## Passo 4 — Executar o script

```bash
python main.py --sheet-url "URL_DA_PLANILHA" --sheet-name "NOME_DA_ABA" --start-row LINHA --limit QUANTIDADE
```

**Atencao:** Se for a primeira execucao do gspread neste ambiente, o navegador abrira para autenticacao Google — informe o usuario antes de rodar.

---

## Passo 5 — Relatorio

O script exibe o relatorio automaticamente ao finalizar. Nao e necessaria nenhuma acao adicional apos a execucao.

---

## Problemas comuns

| Problema | Solucao |
|----------|---------|
| `APOLLO_API_KEY nao encontrada` | Preencher `.env` com a chave |
| `SpreadsheetNotFound` | Verificar URL da planilha e permissao de acesso |
| `WorksheetNotFound` | Nome da aba e case-sensitive — verificar exatamente |
| `ModuleNotFoundError` | Rodar `pip install -r requirements.txt` |
| Rate limit (429) | O script aguarda 60s automaticamente e retenta |
| Erro HTTP 422 | API key nao esta no header — verificar `modules/apollo.py` |
| Linhas ja preenchidas nao sao reprocessadas | A regra de skip bloqueia qualquer conteudo nas colunas de email ou telefone; para reprocessar, limpar as celulas antes de rodar |

---

## Nota sobre creditos Apollo

O plano Free tem 50 creditos de exportacao por mes. Cada chamada de People Match consome 1 credito.
Monitorar em: `app.apollo.io > Settings > Credits`
