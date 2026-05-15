import gspread


def col_letter_to_index(letter: str) -> int:
    """Convert column letter (A, B, ... Z, AA, ...) to 0-based index."""
    letter = letter.upper()
    result = 0
    for char in letter:
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result - 1


def get_sheet(sheet_url: str, tab_name: str):
    gc = gspread.oauth()
    spreadsheet = gc.open_by_url(sheet_url)
    return spreadsheet.worksheet(tab_name)


def get_pending_rows(sheet, start_row: int, limit: int,
                     col_linkedin: str, col_phone: str, col_email: str) -> list:
    """
    Returns list of (row_number, linkedin_url) for rows pending enrichment.
    Skips rows where phone OR email already has content (Option A).
    """
    li_idx = col_letter_to_index(col_linkedin)
    ph_idx = col_letter_to_index(col_phone)
    em_idx = col_letter_to_index(col_email)

    all_rows = sheet.get_all_values()
    pending = []
    max_col = max(li_idx, ph_idx, em_idx)

    for i, row in enumerate(all_rows):
        row_num = i + 1
        if row_num < start_row:
            continue

        while len(row) <= max_col:
            row.append('')

        linkedin = row[li_idx].strip()
        phone = row[ph_idx].strip()
        email = row[em_idx].strip()

        if not linkedin:
            continue

        # Option A: skip if either phone OR email is already filled
        if phone or email:
            continue

        pending.append((row_num, linkedin))

        if len(pending) >= limit:
            break

    return pending


def update_contact(sheet, row_num: int, col_phone: str, col_email: str,
                   phone_val: str, email_val: str):
    sheet.batch_update([
        {"range": f"{col_phone}{row_num}", "values": [[phone_val]]},
        {"range": f"{col_email}{row_num}", "values": [[email_val]]},
    ])
