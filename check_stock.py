# check_stock.py (Final Version with SendGrid)

import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# New imports for our new email service
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# --- CONFIGURATION ---
# These will be loaded from your GitHub Secrets
PRODUCT_URL = os.environ.get('PRODUCT_URL')
# This MUST be the email you verified as a "Single Sender" in SendGrid
SENDER_EMAIL = os.environ.get('VERIFIED_SENDER_EMAIL') 
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
# For simplicity, we'll send the notification email to our verified sender address
RECEIVER_EMAIL = SENDER_EMAIL

# --- SET YOUR DESIRED SIZE HERE ---
DESIRED_SIZE = 'M' 

def check_stock():
    """Checks the Myntra product page for a specific, enabled size button."""
    
    # This XPath looks for a button for our desired size that is explicitly marked as disabled.
    DISABLED_BUTTON_XPATH = f"//p[text()='{DESIRED_SIZE}']/ancestor::button[contains(@class, 'size-buttons-size-button-disabled')]"

    print("Initializing Selenium WebDriver...")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print(f"Navigating to product page: {PRODUCT_URL}")
        driver.get(PRODUCT_URL)
        time.sleep(10) 

        print(f"Searching for a DISABLED button for size '{DESIRED_SIZE}'...")
        driver.find_element(By.XPATH, DISABLED_BUTTON_XPATH)
        
        print(f"Size '{DESIRED_SIZE}' is still OUT of stock.")
        return False

    except NoSuchElementException:
        # If the disabled button is NOT found, the size is IN STOCK.
        print(f">>> STOCK ALERT: Size '{DESIRED_SIZE}' is IN STOCK! <<<")
        return True
        
    except Exception as e:
        print(f"An unexpected error occurred during web check: {e}")
        return False

    finally:
        print("Closing WebDriver.")
        driver.quit()

def send_email_with_sendgrid(product_url, size):
    """Sends a notification email using the SendGrid API."""
    
    print("Preparing to send email notification via SendGrid...")
    
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=RECEIVER_EMAIL,
        subject=f"Myntra Stock Alert: Size {size} is Back!",
        plain_text_content=f"""
        Hello,

        Good news! Size '{size}' for the item you were watching is now back in stock on Myntra.

        Buy it now before it's gone again:
        {product_url}

        Regards,
        Your Python Stock Bot
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent! Status Code: {response.status_code}")
        print("Notification process complete.")
    except Exception as e:
        print(f"Failed to send email with SendGrid: {e}")


if __name__ == "__main__":
    # Check if all necessary environment variables are set
    if not all([PRODUCT_URL, SENDER_EMAIL, SENDGRID_API_KEY]):
        print("FATAL ERROR: One or more required environment variables are missing.")
        print("Please set PRODUCT_URL, VERIFIED_SENDER_EMAIL, and SENDGRID_API_KEY.")
    else:
        is_in_stock = check_stock()
        if is_in_stock:
            send_email_with_sendgrid(PRODUCT_URL, DESIRED_SIZE)
