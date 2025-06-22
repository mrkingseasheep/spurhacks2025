import os
import time
import json
import re
import dotenv
import requests
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# --- Gemini setup ---
genai.configure(api_key=('AIzaSyA1nE9p0aD0I7wBy4hzE5JkDwRdF-X2T2Q'))
model = genai.GenerativeModel('gemini-2.0-flash')  # or 'gemini-2.0-flash' if you prefer

def extract_site_info_from_gemini(html_content):
    """
    Use Gemini to extract the Features and Specifications section as JSON.
    """
    prompt = """
    From the following Ontario Parks reservation HTML, extract the complete content found under the "Features and Specifications" section.
    Parse all text, bullet points, tables, and sub-sections into a well-structured, readable JSON object.
    Use keys that match the section headings and subheadings. For lists or tables, use arrays or nested objects as appropriate.
    Respond with ONLY the JSON, nothing else.
    """
    try:
        response = model.generate_content([prompt, html_content])
        # Try to parse the response as JSON, fallback to raw text if parsing fails
        try:
            return json.loads(response.text)
        except Exception:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini extraction error: {e}")
        return {}

def extract_campsite_info_from_gemini(html_content, data_resource, campground_name, provincial_park):
    """
    Use Gemini to extract campsite info as JSON for a single campsite.
    """
    prompt = f"""
    From the following Ontario Parks reservation HTML for a single campsite, extract the following fields:
    - "Campsite number": (use the value {data_resource})
    - "Service Type"
    - "Quality"
    - "Privacy"
    - "Adjacent to"
    - "Provincial Park": (use the value "{provincial_park}")
    - "Campground": (use the value "{campground_name}")
    - "Campsite Photo": (find something with the class "Campsite {data_resource} image", return the Link that end with .jpg)

    Output a JSON object with these keys. If a field is missing, leave its value as an empty string.

    Example output:
    {{
      "Provincial Park": "{provincial_park}",
      "Campground": "{campground_name}",
      "Campsite number": "{data_resource}",
      "Service Type": "",
      "Quality": "",
      "Privacy": "",
      "Adjacent to": "",
      "Campsite Photo": ""
    }}

    Respond with ONLY the JSON, nothing else. 
    Do NOT include any slashes, newline characters, or random characters in the output. 
    The output should be a single, clean JSON object as shown in the example.
    """
    try:
        response = model.generate_content([prompt, html_content])
        cleaned = response.text.replace("\\", "").replace("\n", "").replace("```", "").replace("json","")
        try:
            return json.loads(cleaned)
        except Exception:
            return cleaned.strip()
    except Exception as e:
        print(f"Gemini extraction error: {e}")
        return {}

def click_all_role_buttons(driver):
    """
    Clicks all elements with role="button" on the page.
    """
    buttons = driver.find_elements('xpath', '//*[@role="button"]')
    for btn in buttons:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            btn.click()
            time.sleep(0.5)  # Wait for UI to update
        except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
            continue

def click_list_view_and_all_buttons(driver):
    """
    Clicks the button with id="list-view-button-button" first,
    then clicks all elements with role="button" on the page.
    """
    try:
        # Click the list view button first
        list_view_btn = driver.find_element('id', 'list-view-button-button')
        driver.execute_script("arguments[0].scrollIntoView(true);", list_view_btn)
        list_view_btn.click()
        time.sleep(1)  # Wait for UI to update
    except Exception as e:
        print(f"Could not click list view button: {e}")

    # Now click all role="button" elements
    click_all_role_buttons(driver)

def get_maplink_buttons(driver):
    return driver.find_elements(By.CSS_SELECTOR, '[id^="mapLink-button-"]')

def get_maplink_button_texts(driver):
    return [btn.text for btn in get_maplink_buttons(driver)]

def click_maplink_by_text(driver, text):
    for btn in get_maplink_buttons(driver):
        if btn.text == text:
            safe_click(driver, btn)
            return True
    return False

def safe_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    element.click()
    time.sleep(2)

def append_to_json(data, output_path):
    # Remove or convert ObjectId before writing to JSON
    def clean(doc):
        if isinstance(doc, dict) and "_id" in doc:
            doc = dict(doc)  # Make a copy
            doc["_id"] = str(doc["_id"])
        return doc

    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except Exception:
                existing_data = []
    else:
        existing_data = []
    if isinstance(existing_data, list):
        existing_data.extend([clean(d) for d in data])
    else:
        existing_data = [clean(d) for d in data]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

def go_back_and_wait(driver, by, value, timeout=10):
    driver.back()
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    time.sleep(1)  # Small buffer

def click_view_previous_map(driver):
    try:
        btns = driver.find_elements(By.CSS_SELECTOR, '[aria-label="View previous map"]')
        if not btns:
            print("No 'View previous map' button found on this page.")
            return
        btn = btns[0]
        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        btn.click()
        time.sleep(2)
    except Exception as e:
        print(f"Could not click 'View previous map' button: {e}")

# --- Image download setup ---
os.makedirs("images", exist_ok=True)

def download_image(image_url, campsite_id):
    if not image_url or not image_url.startswith('http'):
        return image_url

    try:
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        filename = f"campsite_{campsite_id}_{url_hash}.jpg"
        local_path = os.path.join("images", filename)

        if os.path.exists(local_path):
            return f"./images/{filename}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://reservations.ontarioparks.ca/'
        }

        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        with open(local_path, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded image: {filename}")
        return f"./images/{filename}"

    except Exception as e:
        print(f"Failed to download image {image_url}: {e}")
        return image_url

if __name__ == '__main__':
    # --- Selenium setup ---
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless")  # Uncomment to run headless

    service = Service("C:\\Users\\ethan\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    # --- Load website ---
    url = "https://reservations.ontarioparks.ca/create-booking/results?mapId=-2147483464&searchTabGroupId=0&bookingCategoryId=0&startDate=2025-06-21&endDate=2025-06-22&nights=1&isReserving=true&equipmentId=-32768&subEquipmentId=-32768&peopleCapacityCategoryCounts=%5B%5B-32768,null,1,null%5D%5D&searchTime=2025-06-21T14:45:00.971&flexibleSearch=%5Bfalse,false,null,1%5D&filterData=%7B%22-32736%22:%22%5B%5B1%5D,0,0,0%5D%22,%22-32726%22:%22%5B%5B1%5D,0,0,0%5D%22%7D"
    driver.get(url)

    # --- Wait for page to load (adjust as needed) ---
    time.sleep(10)

    # --- Click list view and all role="button" elements ---
    click_list_view_and_all_buttons(driver)

    # --- Wait for UI to update ---
    time.sleep(2)

    output_path = "campsite_data.json"

    # --- MongoDB setup (before your main loops) ---
    uri = "mongodb+srv://ethanoly:nyCknT3J8fOPwLz0@judgejam.5bpp3ii.mongodb.net/?retryWrites=true&w=majority&appName=JudgeJam"
    client = MongoClient(uri,tls=True, server_api=ServerApi('1'))
    db = client["ontario_parks"]
    collection = db["campsites"]

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    # --- Loop through regions ---
    region_texts = get_maplink_button_texts(driver)[0:]  # Skip the first region button
    for region_text in region_texts:
        click_maplink_by_text(driver, region_text)
        time.sleep(2)

        # --- Loop through parks in region ---
        park_texts = get_maplink_button_texts(driver)
        for park_text in park_texts:
            click_maplink_by_text(driver, park_text)
            time.sleep(2)

            # --- Loop through campgrounds in park ---
            campground_texts = get_maplink_button_texts(driver)
            for campground_text in campground_texts:
                click_maplink_by_text(driver, campground_text)
                time.sleep(2)

                # --- Click all role="button" elements (open all campsite panels) ---
                click_all_role_buttons(driver)
                time.sleep(2)

                # --- Scrape campsites ---
                try:
                    campground_name = driver.find_element('id', 'pageTitle').text.strip()
                except Exception:
                    campground_name = ""
                try:
                    provincial_park = driver.find_element('id', 'sidebar-park-name').text.strip()
                except Exception:
                    provincial_park = ""

                campsite_panels = driver.find_elements('css selector', '.mat-expansion-panel.list-entry')
                campsite_data = []
                for panel in campsite_panels:
                    try:
                        data_resource = panel.get_attribute('data-resource')
                        panel_html = panel.get_attribute('outerHTML')
                        info = extract_campsite_info_from_gemini(
                            panel_html, data_resource, campground_name, provincial_park
                        )
                        # Add photo URL and page URL to the info dict
                        if isinstance(info, dict) and info.get("Campsite Photo"):
                            original_url = info["Campsite Photo"]
                            local_path = download_image(original_url, data_resource)
                            info["Campsite Photo"] = local_path
                            info["Original Photo URL"] = original_url
                            # --- Upload each campsite to MongoDB as soon as it's scraped ---
                            if isinstance(info, dict):
                                collection.insert_one(info)
                            else:
                                print("Skipped non-dict info for MongoDB insert.")

                    except Exception as e:
                        print(f"Error processing panel: {e}")

                append_to_json(campsite_data, output_path)
                print(f"Appended {len(campsite_data)} campsites from {campground_name}")

                # Go back to park level
                go_back_and_wait(driver, By.CSS_SELECTOR, '[id^="mapLink-button-"]')
                time.sleep(1)

            # After all campgrounds, go back to the region list by clicking the button
            click_view_previous_map(driver)
            time.sleep(1)

        # Go back to main region list
        go_back_and_wait(driver, By.CSS_SELECTOR, '[id^="mapLink-button-"]')
        time.sleep(1)

    driver.quit()
    print(f"All data appended to {output_path}")