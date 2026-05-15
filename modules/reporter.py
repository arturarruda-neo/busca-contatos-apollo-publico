def print_report(results: list):
    total = len(results)
    found_both = sum(1 for r in results if r["status"] == "found_both")
    found_email = sum(1 for r in results if r["status"] == "found_email")
    found_phone = sum(1 for r in results if r["status"] == "found_phone")
    not_found = sum(1 for r in results if r["status"] == "not_found")
    found_any = found_both + found_email + found_phone
    aproveitamento = (found_any / total * 100) if total else 0

    def pct(n):
        return f"{n / total * 100:.1f}%" if total else "0.0%"

    sep = "=" * 44
    print(f"\n{sep}")
    print("         RELATORIO DA RODADA")
    print(sep)
    print(f"  Total processado:        {total}")
    print(f"  Email e telefone:        {found_both} ({pct(found_both)})")
    print(f"  So email:                {found_email} ({pct(found_email)})")
    print(f"  So telefone:             {found_phone} ({pct(found_phone)})")
    print(f"  Sem contato (N.A.):      {not_found} ({pct(not_found)})")
    print(f"  Taxa de aproveitamento:  {aproveitamento:.1f}%")
    print(f"{sep}\n")
