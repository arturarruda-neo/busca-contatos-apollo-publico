# busca-contatos-apollo-publico

Enriquece contatos via [Apollo.io People Enrichment](https://apolloio.github.io/apollo-api-docs/?shell#people-enrichment): lê URLs de LinkedIn de uma coluna configurável de uma planilha Google Sheets e preenche automaticamente as colunas de e-mail e/ou telefone.

Desenvolvido como skill do [Claude Code](https://claude.ai/code) — pode ser usado tanto via linha de comando quanto acionado pelo Claude diretamente.

## O que faz

- Lê a coluna de LinkedIn URLs configurada na sua planilha Google Sheets
- Chama a API Apollo.io para buscar e-mail e/ou telefone de cada perfil
- Escreve o resultado nas colunas que você definir
- Pula linhas que já têm conteúdo nas colunas de saída (evita reprocessar)

## Pré-requisitos

- Python 3.8+
- Conta no [Apollo.io](https://app.apollo.io) (plano Free tem 50 créditos/mês)
- Google Sheets com autenticação OAuth2 via [gspread](https://gspread.readthedocs.io)

## Instalação

```bash
git clone https://github.com/arturarruda-neo/busca-contatos-apollo-publico.git
cd busca-contatos-apollo-publico
pip install -r requirements.txt
```

**Mac/Linux/PowerShell:**
```bash
cp config/.env.example .env
```

**Windows (Prompt de Comando):**
```cmd
copy config\.env.example .env
```

Edite `.env` e preencha sua chave Apollo:

```
APOLLO_API_KEY=sua_api_key_aqui
```

A API key está em `app.apollo.io > Settings > Integrations > API`.

## Configuração do Google Sheets

Este projeto usa autenticação OAuth2 via [gspread](https://gspread.readthedocs.io). O processo exige criar credenciais no Google Cloud Console antes da primeira execução:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com) e crie um projeto (ou use um existente)
2. Ative a **Google Sheets API** e a **Google Drive API** no projeto
3. Em **APIs e serviços > Credenciais**, crie uma credencial do tipo **ID do cliente OAuth 2.0** (tipo: aplicativo de área de trabalho)
4. Baixe o arquivo `credentials.json` gerado e salve em:
   - **Linux/Mac:** `~/.config/gspread/credentials.json`
   - **Windows:** `C:\Users\SEU_USUARIO\AppData\Roaming\gspread\credentials.json`
5. Na primeira execução do script, o navegador abrirá automaticamente para você autorizar o acesso à sua conta Google

Para mais detalhes, consulte a [documentação oficial do gspread](https://docs.gspread.org/en/latest/oauth2.html).

## Configuração das colunas e modo de busca

**Antes de rodar**, edite `config/config.json`:

```json
{
  "columns": {
    "linkedin": "A",
    "email": "B",
    "phone": "C"
  },
  "mode": "email_only"
}
```

> Os valores `A`, `B`, `C` são apenas exemplos. Você **deve** trocá-los pelas letras correspondentes na sua planilha antes de executar o script.

### Colunas

| Chave       | Descrição                                                |
|-------------|----------------------------------------------------------|
| `linkedin`  | Coluna que contém as URLs de LinkedIn (lida pelo script) |
| `email`     | Coluna onde o e-mail encontrado será gravado             |
| `phone`     | Coluna onde o telefone encontrado será gravado           |

Use a letra da coluna da sua planilha (ex: `D`, `E`, `F`, `AA`...).

### Modos de busca

| Modo          | O que busca             | Requisito extra          |
|---------------|-------------------------|--------------------------|
| `email_only`  | Apenas e-mail           | Nenhum                   |
| `phone_only`  | Apenas telefone         | Webhook recomendado¹     |
| `both`        | E-mail e telefone       | Webhook recomendado¹     |

> ¹ **Sobre o webhook:** A API Apollo retorna telefone de forma assíncrona — ela envia o resultado para uma URL de webhook que você precisa configurar. Sem webhook, o script ainda solicita o telefone e pode retornar dados públicos já presentes no perfil, mas a maioria dos casos virá vazio. Para configurar, adicione `APOLLO_WEBHOOK_URL=sua_url` no `.env`.

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
3. O Claude vai guiar você pela configuração das colunas e modo, coletar as informações da planilha, montar o comando e executar

## Créditos Apollo

O consumo de créditos por chamada varia conforme o modo de busca:

- **`email_only`:** menor consumo por contato
- **`phone_only`:** consumo intermediário por contato
- **`both`:** maior consumo por contato

O plano Free tem 50 créditos de exportação por mês. Consulte os valores exatos em `app.apollo.io > Settings > Credits` ou na [página de preços da Apollo](https://www.apollo.io/pricing), pois as taxas podem variar por plano.
