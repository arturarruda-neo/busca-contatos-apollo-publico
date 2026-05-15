import time
import requests

APOLLO_URL = "https://api.apollo.io/api/v1/people/match"
DELAY_BETWEEN_REQUESTS = 1.5   # seconds between each API call
RATE_LIMIT_WAIT = 60           # seconds to wait on 429
MAX_RETRIES = 3


def enrich_by_linkedin(api_key: str, linkedin_url: str) -> dict:
    """
    Returns dict with keys: email, phone, status
    status: 'found_email' | 'found_phone' | 'not_found'
    """
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "linkedin_url": linkedin_url,
        "reveal_personal_emails": True,
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(APOLLO_URL, json=payload, headers=headers, timeout=30)

            if resp.status_code == 429:
                print(f"  [Rate limit] Aguardando {RATE_LIMIT_WAIT}s...")
                time.sleep(RATE_LIMIT_WAIT)
                continue

            if resp.status_code != 200:
                print(f"  [Erro HTTP {resp.status_code}]")
                break

            person = resp.json().get("person")
            if not person:
                break

            email = person.get("email") or ""
            phones = person.get("phone_numbers") or []
            phone = phones[0].get("sanitized_number", "") if phones else ""

            if email:
                return {"email": email, "phone": phone or "N.A.", "status": "found_email"}
            if phone:
                return {"email": "N.A.", "phone": phone, "status": "found_phone"}

            break

        except requests.exceptions.RequestException as e:
            print(f"  [Excecao] {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)

    return {"email": "N.A.", "phone": "N.A.", "status": "not_found"}


def wait():
    time.sleep(DELAY_BETWEEN_REQUESTS)
