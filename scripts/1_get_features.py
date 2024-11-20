from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

# Set up Selenium WebDriver (ensure the driver is installed and in PATH)
driver = webdriver.Chrome()  # Replace with your driver, e.g., webdriver.Firefox()

url = "https://wals.info/feature"
output_file = "wals_features.csv"

try:
    print("Fetching data from WALS Online with Selenium...")
    driver.get(url)

    # Wait for the table to load (adjust as needed)
    driver.implicitly_wait(10)

    # Locate the table (adjust the selector if needed)
    table = driver.find_element(By.TAG_NAME, "table")
    rows = table.find_elements(By.TAG_NAME, "tr")

    if not rows:
        raise ValueError("No rows found in the table.")

    # Open CSV file for writing
    with open(output_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        # Write the header row
        header = [th.text.strip() for th in rows[0].find_elements(By.TAG_NAME, "th")]
        writer.writerow(header)

        # Write data rows
        for row in rows[1:]:
            cols = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
            writer.writerow(cols)

    print(f"Data successfully saved to '{output_file}'.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
