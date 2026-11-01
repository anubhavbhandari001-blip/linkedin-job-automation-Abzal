from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("Starting Chrome...")

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

print("Chrome opened successfully!")

driver.get("https://www.google.com")

input("Press ENTER to close Chrome...")

driver.quit()