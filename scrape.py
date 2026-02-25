import getpass
import io
import re
import pandas as pd
import math 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def clean_text(text):
    text = re.sub(r"<!--.*?-->", "", str(text))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_dualis_grades():
    print("--- DHBW Dualis Noten-Rechner ---")

    user = input("Benutzername: ") # or "your_email@gmx.de"
    pwd = getpass.getpass("Passwort: ") # or "your_password"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get("https://dualis.dhbw.de/")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "field_user"))
        )

        driver.find_element(By.ID, "field_user").send_keys(user)
        driver.find_element(By.ID, "field_pass").send_keys(pwd)
        driver.find_element(By.ID, "logIn_btn").click()

        try:
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Leistungsübersicht"))
            ).click()
        except:
            print("Login failed. Please check your username and password.")
            return

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        target_html = None

        if "Credits" in driver.page_source:
            target_html = driver.page_source
        else:
            frames = driver.find_elements(By.TAG_NAME, "frame")
            if not frames:
                frames = driver.find_elements(By.TAG_NAME, "iframe")

            for frame in frames:
                driver.switch_to.default_content()
                driver.switch_to.frame(frame)
                if "Credits" in driver.page_source:
                    target_html = driver.page_source
                    break

        if not target_html:
            print("Tabelle nicht gefunden.")
            return

    finally:
        driver.quit()

    dfs = pd.read_html(io.StringIO(target_html), decimal=",", thousands=".")

    target_df = None
    for df in dfs:
        df.columns = [str(c).strip() for c in df.columns]
        if len(df) > 10 and any("Note" in c for c in df.columns):
            target_df = df
            break

    if target_df is None:
        print("Keine passende Tabelle gefunden.")
        return

    grade_col = next(c for c in target_df.columns if "Note" in c or "Endnote" in c)
    ects_col = next(c for c in target_df.columns if "Credit" in c or "ECTS" in c)

    print(f"\n{'Modul':<50} | {'Note':<5} | {'ECTS':<5}")
    print("-" * 70)

    total_score = 0
    total_ects_graded = 0
    total_ects_all = 0

    for _, row in target_df.iterrows():
        try:
            name = clean_text(row.iloc[1])
            if not name:
                name = clean_text(row.iloc[0])
        except:
            continue

        if "Summe" in name or "GPA" in name:
            continue

        raw_grade = str(row[grade_col]).replace(",", ".").strip()
        raw_ects = str(row[ects_col]).replace(",", ".").strip()

        # ECTS in float konvertieren
        try:
            ects = float(raw_ects)
        except:
            continue

        # Module mit 0 oder NaN ECTS überspringen
        if ects == 0 or math.isnan(ects):
            continue

        # Nicht-bewertete / bestandene Module
        if raw_grade.lower() in ["b", "bestanden", "genehmigt"]:
            total_ects_all += ects
            print(f"{name[:50]:<50} | {'Pass':<5} | {ects:<5.1f}")
            continue

        if raw_grade in ["", "nan"]:
            continue

        # Note in float konvertieren
        try:
            grade = float(raw_grade)
        except:
            continue

        total_score += grade * ects
        total_ects_graded += ects
        total_ects_all += ects

        print(f"{name[:50]:<50} | {grade:<5.1f} | {ects:<5.1f}")

    print("-" * 70)

    if total_ects_graded > 0:
        avg = total_score / total_ects_graded
        print("\nSTATISTIK:")
        print(f"ECTS (Gesamt):     {total_ects_all}")
        print(f"ECTS (Benotet):    {total_ects_graded}")
        print(f"Durchschnitt:      {avg:.4f}")
    else:
        print("Keine benoteten Leistungen gefunden.")


if __name__ == "__main__":
    get_dualis_grades()