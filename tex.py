import pycron
from selenium import webdriver
import time
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os

today_date = datetime.today().strftime('%Y-%m-%d')
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=Options)

wait = WebDriverWait(driver, 30)

def absen():
    


    driver.get("https://forms.gle/VUwbshGuXxDb7NRbA")
    time.sleep(1)
    date = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.quantumWizTextinputPaperinputInput")))
    driver.execute_script(f"arguments[0].setAttribute('value', '{today_date}')", date)
    element =driver.find_element_by_xpath("//span[text()='Next']")

    element.click()
    time.sleep(1)
    webdriver.ActionChains(driver).key_down(Keys.ARROW_RIGHT).send_keys("a").perform()
    time.sleep(1)
    element.click()

    time.sleep(1)
    driver.find_element_by_css_selector("#i5 > div.appsMaterialWizToggleRadiogroupRadioButtonContainer > div").click()
    time.sleep(0.5)
    driver.find_element_by_css_selector("#mG61Hd > div.freebirdFormviewerViewFormCard.exportFormCard > div > div.freebirdFormviewerViewNavigationNavControls > div > div.freebirdFormviewerViewNavigationLeftButtons > div.appsMaterialWizButtonEl.appsMaterialWizButtonPaperbuttonEl.appsMaterialWizButtonPaperbuttonFilled.freebirdFormviewerViewNavigationSubmitButton.freebirdThemedFilledButtonM2 > span").click()

absen()
# while True:
# #                     v----------------- on minute 0, so every full hour
# #                       v--------------- on hours 9 till 16
# #                            v v-------- every day in month and every month
# #                                v------ on weekdays monday till friday
#     if pycron.is_now('30 7 * * mon-fri'):
#         absen()
#     time.sleep(60)
