import argparse
import json
import os
import sys

from dotenv import load_dotenv

from modules.sheets import get_sheet, get_pending_rows, update_contact
from modules.apollo import enrich_by_linkedin, wait
from modules.reporter import print_report

load_dotenv()

VALID_MODES = ("email_only", "phone_only", "both")
REQUIRED_COLUMN_KEYS = ("linkedin", "email", "phone")


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] config/config.json nao encontrado. Verifique se o arquivo existe.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERRO] config/config.json tem JSON invalido: {e}")
        sys.exit(1)


def validate_config(config):
    columns = config.get("columns")
    if not isinstance(columns, dict):
        print("[ERRO] config.json: campo 'columns' ausente ou invalido.")
        sys.exit(1)
    for key in REQUIRED_COLUMN_KEYS:
        if key not in columns or not str(columns[key]).strip():
            print(f"[ERRO] config.json: coluna '{key}' ausente ou vazia em 'columns'.")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Enriquecimento de contatos via Apollo.io")
    parser.add_argument("--sheet-url", required=True, help="URL da planilha Google Sheets")
    parser.add_argument("--sheet-name", required=True, help="Nome da aba")
    parser.add_argument("--start-row", type=int, required=True, help="Linha inicial (1-indexed)")
    parser.add_argument("--limit", type=int, required=True, help="Maximo de contatos a processar")
    args = parser.parse_args()

    if args.start_row < 1:
        print("[ERRO] --start-row deve ser >= 1.")
        sys.exit(1)
    if args.limit < 1:
        print("[ERRO] --limit deve ser >= 1.")
        sys.exit(1)

    api_key = os.getenv("APOLLO_API_KEY")
    if not api_key:
        print("[ERRO] APOLLO_API_KEY nao encontrada. Copie config/.env.example para .env e preencha a chave.")
        sys.exit(1)

    webhook_url = os.getenv("APOLLO_WEBHOOK_URL", "")

    config = load_config()
    validate_config(config)

    col_linkedin = config["columns"]["linkedin"]
    col_phone = config["columns"]["phone"]
    col_email = config["columns"]["email"]
    mode = config.get("mode", "email_only")

    if mode not in VALID_MODES:
        print(f"[ERRO] Modo invalido em config.json: '{mode}'. Use: {', '.join(VALID_MODES)}")
        sys.exit(1)

    if mode in ("phone_only", "both") and not webhook_url:
        print(f"[AVISO] Modo '{mode}' selecionado sem APOLLO_WEBHOOK_URL configurado.")
        print("        Telefones so serao retornados se ja estiverem publicos no perfil Apollo.")

    print(f"Modo: {mode}")
    print(f"Conectando a planilha '{args.sheet_name}'...")
    sheet = get_sheet(args.sheet_url, args.sheet_name)

    print(f"Buscando linhas a partir da linha {args.start_row} (limite: {args.limit})...")
    pending = get_pending_rows(
        sheet, args.start_row, args.limit, col_linkedin, col_phone, col_email
    )

    if not pending:
        print("Nenhuma linha elegivel encontrada para processar.")
        return

    print(f"{len(pending)} contato(s) encontrado(s) para processar.\n")

    results = []

    for i, (row_num, linkedin_url) in enumerate(pending, 1):
        display_url = linkedin_url[:70] + ("..." if len(linkedin_url) > 70 else "")
        print(f"[{i}/{len(pending)}] Linha {row_num}: {display_url}")

        result = enrich_by_linkedin(api_key, linkedin_url, mode, webhook_url)
        update_contact(sheet, row_num, col_phone, col_email, result["phone"], result["email"])

        label = {
            "found_both":  "Email e telefone encontrados",
            "found_email": "Email encontrado",
            "found_phone": "Telefone encontrado",
            "not_found":   "Nao encontrado",
        }.get(result["status"], "?")

        print(f"  -> {label}: email={result['email']}, tel={result['phone']}")
        results.append(result)

        if i < len(pending):
            wait()

    print_report(results)


if __name__ == "__main__":
    main()
