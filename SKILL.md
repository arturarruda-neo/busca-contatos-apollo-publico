---
name: busca-contatos-apollo
description: Use quando o usuario pedir para buscar emails e telefones de contatos via Apollo.io, enriquecer dados de contato em uma planilha Google Sheets, preencher colunas de email/telefone lendo LinkedIn URLs, ou qualquer variacao de "buscar contatos no Apollo", "enriquecer contatos", "pegar email pelo LinkedIn".
---

# Busca de Contatos — Apollo.io

Automatiza o enriquecimento de contatos via Apollo.io People Enrichment, lendo URLs de LinkedIn de uma coluna configuravel de uma planilha Google Sheets e escrevendo os resultados nas colunas de E-mail e/ou Telefone definidas pelo usuario.

**Nota sobre telefone:** A API Apollo retorna telefone de forma assincrona (requer webhook). Sem webhook configurado, o script ainda solicita o telefone e pode retornar dados publicos do perfil, mas a maioria dos casos vira vazio.

## Estrutura da planilha

A skill opera sobre tres colunas configuradas em `config/config.json`:

| Chave em config.json | Campo    | Papel nesta skill                            |
|----------------------|----------|----------------------------------------------|
| `linkedin`           | LinkedIn | **lido** — URL do perfil individual          |
| `email`              | E-mail   | **escrito** — email encontrado ou "N.A."     |
| `phone`              | Telefone | **escrito** — telefone encontrado ou "N.A."  |

As letras de coluna sao definidas pelo usuario em `config/config.json` antes de rodar (ex: `"linkedin": "C"`).

**Regra de skip:** Se as colunas de e-mail **ou** telefone ja tiverem qualquer conteudo (inclusive "N.A."), a linha e pulada. Para reprocessar, limpar as celulas primeiro.

---

## Passo 1 — Verificar configuracao

Verifique se existem no diretorio do projeto:
- `.env` com `APOLLO_API_KEY` preenchida
- `config/config.json` com as letras de coluna corretas para a planilha do usuario
- gspread OAuth2 configurado — requer `credentials.json` do Google Cloud Console
  (guia completo: https://docs.gspread.org/en/latest/oauth2.html e secao "Configuracao do Google Sheets" no README)

Se `.env` nao existir, criar a partir do exemplo:

Mac/Linux/PowerShell:
```bash
cp config/.env.example .env
```
Windows (Prompt de Comando):
```cmd
copy config\.env.example .env
```
Orientar o usuario a editar `.env` e preencher `APOLLO_API_KEY` com a chave de `app.apollo.io > Settings > Integrations > API`.

Se as dependencias nao estiverem instaladas:
```bash
pip install -r requirements.txt
```

---

## Passo 2 — Configurar colunas e modo de busca

Pergunte ao usuario:

1. **Qual e a letra da coluna que contem as URLs de LinkedIn?** (ex: `A`, `B`, `C`...)
2. **Qual e a letra da coluna onde deve ser gravado o E-mail?**
3. **Qual e a letra da coluna onde deve ser gravado o Telefone?**
4. **O que deseja buscar?**
   - `email_only` — apenas e-mail (padrao, funciona sem configuracao extra)
   - `phone_only` — apenas telefone (webhook recomendado para resultados completos)
   - `both` — e-mail e telefone (webhook recomendado para resultados completos)

Se o usuario escolher `phone_only` ou `both`, perguntar tambem:
- **Possui uma URL de webhook configurada?** Se sim, pedir a URL e incluir em `.env` como `APOLLO_WEBHOOK_URL`.
- Caso nao tenha webhook, avisar: *"Sem webhook, a Apollo pode retornar telefones publicos ja disponiveis no perfil, mas a maioria dos casos vira vazio."*

Com as respostas, edite `config/config.json`:

```json
{
  "columns": {
    "linkedin": "LETRA_LINKEDIN",
    "email": "LETRA_EMAIL",
    "phone": "LETRA_TELEFONE"
  },
  "mode": "MODO_ESCOLHIDO"
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

Antes de rodar, verificar qual comando Python esta disponivel no sistema do usuario:
```bash
python --version
python3 --version
```
Usar o que responder sem erro. Em caso de duvida, tentar `python` primeiro; se falhar, tentar `python3`.

```bash
python main.py --sheet-url "URL_DA_PLANILHA" --sheet-name "NOME_DA_ABA" --start-row LINHA --limit QUANTIDADE
```

**Atencao:** Se for a primeira execucao do gspread neste ambiente, o navegador abrira para autenticacao Google — informar o usuario antes de rodar.

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
| `python: command not found` | Usar `python3` no lugar de `python` (Mac/Linux) |
| Rate limit (429) | O script aguarda 60s automaticamente e retenta |
| Erro HTTP 422 | API key nao esta no header — verificar `modules/apollo.py` |
| Linhas ja preenchidas nao sao reprocessadas | A regra de skip bloqueia qualquer conteudo nas colunas de email ou telefone; para reprocessar, limpar as celulas antes de rodar |

---

## Nota sobre creditos Apollo

O consumo de creditos por chamada varia conforme o modo de busca:

- **`email_only`:** menor consumo por contato
- **`phone_only`:** consumo intermediario por contato
- **`both`:** maior consumo por contato

O plano Free tem 50 creditos de exportacao por mes. Consulte os valores exatos em `app.apollo.io > Settings > Credits` ou na pagina de precos da Apollo (https://www.apollo.io/pricing), pois as taxas podem variar por plano.
