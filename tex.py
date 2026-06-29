import os
import signal
import sys
import time
import logging
from datetime import datetime

import pycron
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("tex")


class AttendanceBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self._setup_driver()

    def _setup_driver(self):
        chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

        if not chrome_bin:
            raise EnvironmentError("GOOGLE_CHROME_BIN tidak di-set.")
        if not chromedriver_path:
            raise EnvironmentError("CHROMEDRIVER_PATH tidak di-set.")

        options = webdriver.ChromeOptions()
        options.binary_location = chrome_bin
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,800")

        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)
        log.info("Driver Chrome berhasil diinisialisasi.")

    def submit_attendance(self):
        today_date = datetime.today().strftime("%Y-%m-%d")
        log.info("Menjalankan absen untuk tanggal: %s", today_date)

        url = "https://forms.gle/VUwbshGuXxDb7NRbA"
        self.driver.get(url)

        date_input = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input.quantumWizTextinputPaperinputInput")
            )
        )
        self.driver.execute_script(
            "arguments[0].setAttribute('value', arguments[1]);", date_input, today_date
        )
        log.info("Tanggal diisi: %s", today_date)

        self._retry_click(By.XPATH, "//span[text()='Next']", label="Next (step 1)")
        log.info("Menekan tombol Next (langkah 1).")

        self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Next']")))
        webdriver.ActionChains(self.driver).key_down(Keys.ARROW_RIGHT).send_keys("a").perform()
        log.info("Memilih opsi 'a' via Arrow Right + a.")

        self._retry_click(By.XPATH, "//span[text()='Next']", label="Next (step 2)")
        log.info("Menekan tombol Next (langkah 2).")

        self._retry_click(By.XPATH, "//span[text()='e']", label="Nama 'e'")
        log.info("Memilih nama 'e'.")

        submit_selector = (
            "div.freebirdFormviewerViewNavigationLeftButtons "
            "div.appsMaterialWizButtonEl.freebirdFormviewerViewNavigationSubmitButton "
            "span"
        )
        self._retry_click(By.CSS_SELECTOR, submit_selector, label="Submit")
        log.info("Absen berhasil dikirim.")

    def _retry_click(self, by, locator, label="element", max_attempts=3, delay=2):
        for attempt in range(1, max_attempts + 1):
            try:
                el = self.wait.until(EC.element_to_be_clickable((by, locator)))
                el.click()
                return
            except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as exc:
                log.warning(
                    "Gagal menekan %s (percobaan %d/%d): %s", label, attempt, max_attempts, exc
                )
                if attempt == max_attempts:
                    raise
                time.sleep(delay)

    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
                log.info("Driver ditutup.")
            except Exception as exc:
                log.warning("Error saat menutup driver: %s", exc)


_running = True


def _handle_signal(signum, frame):
    global _running
    log.info("Menerima sinyal %s, menghentikan bot...", signum)
    _running = False


def main():
    global _running

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    bot = AttendanceBot()
    try:
        while _running:
            if pycron.is_now("30 7 * * 1-5"):
                try:
                    bot.submit_attendance()
                except (WebDriverException, TimeoutException, NoSuchElementException) as exc:
                    log.error("Absen gagal: %s", exc)
            time.sleep(60)
    finally:
        bot.quit()
        log.info("Bot dihentikan.")


if __name__ == "__main__":
    main()
