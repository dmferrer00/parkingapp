import time # Keep time only if absolutely needed for specific non-Selenium waits
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def test_parking_prediction():
    """
    Tests the parking predictor web application UI based on the original HTML.
    1. Navigates to the page.
    2. Clicks a specific parking deck button ('North Level 3').
    3. Waits for the result div to be updated with the prediction text.
    4. Asserts that the expected information is present in the result.
    """
    driver = None # Initialize driver to None for the finally block
    try:
        # --- Setup ---
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless') # Optional: Run in headless mode
        # options.add_argument('--disable-gpu') # Often needed for headless mode
        # options.add_argument('--window-size=1920,1080') # Optional: Set window size
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # !!! IMPORTANT: Replace with your actual Azure-hosted app URL !!!
        driver.get("https://flaskapplication-fagugzaxevb2cfgk.canadacentral-01.azurewebsites.net")

        # Define a maximum wait time (in seconds)
        wait = WebDriverWait(driver, 10) # Wait up to 10 seconds

        # --- Test Steps ---

        # 1. Wait for buttons to be generated and find the target button
        #    Locator strategy: Find a button within the deck-buttons div based on its exact text.
        #    Waits for the button to be clickable.
        #    Using normalize-space() is robust against leading/trailing whitespace in the button text.
        button_locator = (By.XPATH, "//div[@id='deck-buttons']//button[normalize-space()='North Level 3']")
        print("Waiting for 'North Level 3' button...")
        target_button = wait.until(EC.element_to_be_clickable(button_locator))
        print("Button found and clickable.")

        # 2. Click the button
        target_button.click()
        print("Clicked 'North Level 3' button.")

        # 3. Wait for the result div to be updated
        #    Locator strategy: Find the div with id="result".
        #    Wait condition: Wait until the div's text contains the expected prediction header.
        #    This implicitly waits for the fetch call to complete and the DOM to update.
        result_locator = (By.ID, "result")
        expected_text_in_result = "Prediction for North Level 3"
        print(f"Waiting for result div to contain text: '{expected_text_in_result}'...")
        wait.until(EC.text_to_be_present_in_element(result_locator, expected_text_in_result))
        print("Result div updated.")

        # 4. Get the result div text *after* waiting for the update
        result_div = driver.find_element(*result_locator) # Find element using the defined locator tuple
        result_text = result_div.text # Get all text within the #result div

        # --- Assertions ---
        print(f"\n--- Result Text Found ---\n{result_text}\n------------------------")
        # Check if the key pieces of information are present in the result text
        assert "Prediction for North Level 3" in result_text, "Assertion Failed: 'Prediction for North Level 3' not found."
        assert "Day:" in result_text, "Assertion Failed: 'Day:' not found."
        assert "Time Block:" in result_text, "Assertion Failed: 'Time Block:' not found."
        assert "Availability:" in result_text, "Assertion Failed: 'Availability:' not found."
        assert "Estimated Spaces:" in result_text, "Assertion Failed: 'Estimated Spaces:' not found."
        # Note: Confidence percentage check might be brittle if the format changes
        # assert "% confident)" in result_text, "Assertion Failed: Confidence percentage not found."

        print("\n✅ All assertions passed!")

    except TimeoutException as e:
        print(f"\n❌ Test Failed: A timeout occurred while waiting for an element or condition: {e}")
        if driver:
            # Attempt to capture page source and screenshot for debugging timeouts
            try:
                print("\nPage Source at Timeout:")
                print(driver.page_source)
                driver.save_screenshot("error_screenshot_timeout.png")
                print("Screenshot saved as error_screenshot_timeout.png")
            except Exception as screenshot_err:
                print(f"Could not save screenshot or get page source: {screenshot_err}")
        assert False, f"Test failed due to TimeoutException: {e}"
    except NoSuchElementException as e:
        print(f"\n❌ Test Failed: An element was not found on the page: {e}")
        if driver:
            driver.save_screenshot("error_screenshot_no_element.png")
            print("Screenshot saved as error_screenshot_no_element.png")
        assert False, f"Test failed due to NoSuchElementException: {e}"
    except AssertionError as e:
        print(f"\n❌ Test Failed: An assertion failed: {e}")
        if driver:
            driver.save_screenshot("error_screenshot_assertion.png")
            print("Screenshot saved as error_screenshot_assertion.png")
        # Re-raise the assertion error to ensure test frameworks like pytest mark it as failed
        raise
    except Exception as e:
        # Catch any other unexpected exceptions during the test
        print(f"\n❌ Test Failed: An unexpected error occurred: {e}")
        if driver:
            driver.save_screenshot("error_screenshot_unexpected.png")
            print("Screenshot saved as error_screenshot_unexpected.png")
        assert False, f"Test failed with an unexpected exception: {e}"

    finally:
        # --- Cleanup ---
        # Ensure the browser is closed even if errors occurred
        if driver:
            print("\nClosing the browser...")
            driver.quit()
            print("Browser closed.")

# --- Run the test ---
if __name__ == "__main__":
    print("Starting parking prediction UI test (based on original HTML)...")
    test_parking_prediction()
    print("\nTest finished.")
