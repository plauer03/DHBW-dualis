# DHBW Dualis Grade Calculator

Python Selenium script that logs into the DHBW Dualis portal, extracts grades and ECTS credits, and calculates the weighted average grade.

## Setup

```bash
git clone https://github.com/plauer03/DHBW-dualis.git
cd DHBW-dualis

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
python3 scrape.py
```

Deactivate the virtual environment:

```bash
deactivate
```

## Optional: Hardcode Login

You can hardcode your credentials in `scrape.py`.

Edit the `get_dualis_grades()` function:

```python
def get_dualis_grades():
    print("--- DHBW Dualis Noten-Rechner ---")

    user = input("Benutzername: ") or "your_email@example.com"
    pwd = getpass.getpass("Passwort: ") or "your_password"
```

## License

MIT — Use it, modify it, share it.
