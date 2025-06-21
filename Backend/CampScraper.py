from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Set up your Chrome driver
service = Service("C:\\Users\ethan\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")  # Replace with your actual path
driver = webdriver.Chrome(service=service)

# URL to load
url = "https://reservations.ontarioparks.ca/create-booking/results?mapId=-2147483377&searchTabGroupId=0&bookingCategoryId=0&startDate=2025-06-21&endDate=2025-06-22&nights=1&isReserving=true&equipmentId=-32768&subEquipmentId=-32768&peopleCapacityCategoryCounts=%5B%5B-32768,null,1,null%5D%5D&searchTime=2025-06-21T10:22:50.092&flexibleSearch=%5Bfalse,false,null,1%5D&filterData=%7B%22-32736%22:%22%5B%5B1%5D,0,0,0%5D%22,%22-32726%22:%22%5B%5B1%5D,0,0,0%5D%22%7D&resourceLocationId=-2147483585"

# Go to the page
driver.get(url)
time.sleep(10)  # Wait for JavaScript to fully render content

# Click on the first “Details” button found
try:
    detail_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Details')]")
    if detail_buttons:
        detail_buttons[0].click()
        time.sleep(5)

        # After clicking, extract data you need, e.g.:
        info = driver.find_element(By.CLASS_NAME, "mr-1")  # replace with actual class
        print(info.text)
    else:
        print("No details buttons found.")

except Exception as e:
    print("Error occurred:", e)

driver.quit()
