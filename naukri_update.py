import argparse
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

NAUKRI_LOGIN_URL = "https://www.naukri.com/nlogin/login"
PROFILE_URL      = "https://www.naukri.com/mnjuser/profile"


def run(email: str, password: str, headless: bool = True) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            # Use a realistic user-agent so Naukri doesn't serve a blocked page
            # to what it identifies as a headless bot.
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        # Hide the navigator.webdriver flag that headless Chromium exposes
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        try:
            # Login
            print("[*] Opening login page …")
            page.goto(NAUKRI_LOGIN_URL, wait_until="domcontentloaded")
            page.fill("#usernameField", email)
            page.fill("#passwordField", password)
            page.click("button[type='submit']")
            # Wait until the browser leaves the login page (SPA may do multiple navigations)
            page.wait_for_function("() => !window.location.href.includes('nlogin')", timeout=30_000)
            time.sleep(3)
            print("[+] Logged in successfully.")

            # Navigate to profile
            print("[*] Navigating to profile page …")
            page.goto(PROFILE_URL, wait_until="domcontentloaded")
            time.sleep(4)

            # Click the sidebar nav link to load the profile summary section
            page.locator("li", has_text="Profile summary").first.click()
            time.sleep(2)

            # Click the edit icon
            print("[*] Opening profile summary editor …")
            page.locator(".profileSummary .widgetHead .edit").click()
            time.sleep(2)

            # Wait for the drawer to open — profile summary drawer has the `profileSummaryEdit` class
            drawer = page.locator(".profileSummaryEdit")
            drawer.wait_for(state="visible", timeout=20_000)

            # No-op edit to mark the field dirty so Save becomes active
            textarea = drawer.locator("textarea").first
            textarea.click()
            textarea.type(" ")
            time.sleep(0.3)
            textarea.press("Backspace")
            time.sleep(0.3)

            # Save
            print("[*] Saving profile summary …")
            save_btn = drawer.locator("button.btn-dark-ot, button[type='submit']").first
            save_btn.click()
            time.sleep(3)
            print("[+] Profile summary saved successfully.")

        except Exception as exc:
            print(f"[!] Error: {exc}")
            try:
                page.screenshot(path="naukri_error.png")
                print("[!] Screenshot saved to naukri_error.png for debugging.")
            except Exception:
                pass
            browser.close()
            sys.exit(1)

        browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh Naukri profile summary.")
    parser.add_argument("--email",    default=None, help="Naukri account email (or set NAUKRI_EMAIL env var)")
    parser.add_argument("--password", default=None, help="Naukri account password (or set NAUKRI_PASSWORD env var)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    return parser.parse_args()


def main() -> None:
    import os
    args = parse_args()
    email    = args.email    or os.environ.get("NAUKRI_EMAIL")
    password = args.password or os.environ.get("NAUKRI_PASSWORD")
    if not email or not password:
        print("[!] Credentials required: pass --email/--password or set NAUKRI_EMAIL/NAUKRI_PASSWORD env vars.")
        sys.exit(1)
    run(email, password, headless=args.headless)
    print("[+] Done — profile has been refreshed.")


if __name__ == "__main__":
    main()
