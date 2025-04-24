from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_parking_prediction():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://flaskapplication-fagugzaxevb2cfgk.canadacentral-01.azurewebsites.net")  # Replace with your actual Azure-hosted app URL

    # Wait for the buttons to load
    time.sleep(2)

    # Find the first deck button
    button = driver.find_element(By.XPATH, "//button[contains(text(), 'North Level 3')]")
    button.click()

    # Wait for the fetch and DOM update
    time.sleep(2)

    # Get the result div
    result = driver.find_element(By.ID, "result")

    # Assertions
    assert "Prediction for North Level 3" in result.text
    assert "Day:" in result.text
    assert "Time Block:" in result.text
    assert "Availability:" in result.text
    assert "Estimated Spaces:" in result.text

    driver.quit()
