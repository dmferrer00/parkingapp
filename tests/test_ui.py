from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def test_prediction_display():
    driver = webdriver.Chrome()  # or use Firefox()
    driver.get("http://your-azure-hostname.com")  # replace with actual hosted URL

    # Click the button
    button = driver.find_element(By.XPATH, "//button[contains(text(), 'North Level 3')]")
    button.click()

    time.sleep(2)  # Wait for fetch and DOM update

    result_div = driver.find_element(By.ID, "result")
    assert "Prediction for North Level 3" in result_div.text
    assert "Day:" in result_div.text
    assert "Availability:" in result_div.text

    driver.quit()
