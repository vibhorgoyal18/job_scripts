import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NAUKRI_LOGIN_URL   = "https://www.naukri.com/nlogin/login"
PROFILE_URL        = "https://www.naukri.com/mnjuser/profile"


def get_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--remote-debugging-port=9222")
    else:
        options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def login(driver: webdriver.Chrome, wait: WebDriverWait, email: str, password: str) -> None:
    print("[*] Opening login page …")
    driver.get(NAUKRI_LOGIN_URL)

    wait.until(EC.presence_of_element_located((By.ID, "usernameField"))).send_keys(email)
    driver.find_element(By.ID, "passwordField").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait until the home / dashboard page loads after login
    wait.until(EC.url_contains("naukri.com"))
    time.sleep(3)
    print("[+] Logged in successfully.")


def update_profile_summary(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    from selenium.webdriver.common.keys import Keys

    print("[*] Navigating to profile page …")
    driver.get(PROFILE_URL)
    time.sleep(4)

    # Click the Profile Summary nav link in the sidebar to scroll/load the section
    wait.until(EC.element_to_be_clickable((
        By.XPATH, "//li[normalize-space()='Profile summary']"
    ))).click()
    time.sleep(2)

    # Click the edit icon — inside .profileSummary > .card > div > .widgetHead > .edit
    print("[*] Opening profile summary editor …")
    summary_edit_btn = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, ".profileSummary .widgetHead .edit"
    )))
    driver.execute_script("arguments[0].click();", summary_edit_btn)
    time.sleep(2)

    # Wait for the drawer to open (it has class 'profileEditDrawer' without 'flipClose')
    modal = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, ".profileEditDrawer:not(.flipClose)"
    )))

    # Locate the textarea inside the open drawer
    textarea = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, ".profileEditDrawer:not(.flipClose) textarea"
    )))

    # Trigger a no-op edit so Naukri marks the field as dirty
    textarea.click()
    textarea.send_keys(" ")
    time.sleep(0.3)
    textarea.send_keys(Keys.BACK_SPACE)
    time.sleep(0.3)

    # Click Save
    print("[*] Saving profile summary …")
    save_btn = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, ".profileEditDrawer:not(.flipClose) button.btn-dark-ot, "
                         ".profileEditDrawer:not(.flipClose) button[type='submit']"
    )))
    driver.execute_script("arguments[0].click();", save_btn)
    time.sleep(3)
    print("[+] Profile summary saved successfully.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh Naukri profile summary.")
    parser.add_argument("--email",    required=True, help="Naukri account email")
    parser.add_argument("--password", required=True, help="Naukri account password")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")
    return parser.parse_args()


def main() -> None:
    args   = parse_args()
    driver = get_driver(headless=args.headless)
    wait   = WebDriverWait(driver, 20)

    try:
        login(driver, wait, args.email, args.password)
        update_profile_summary(driver, wait)
        print("[+] Done — profile has been refreshed.")
    except Exception as exc:
        print(f"[!] Error: {exc}")
        driver.save_screenshot("naukri_error.png")
        print("[!] Screenshot saved to naukri_error.png for debugging.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
