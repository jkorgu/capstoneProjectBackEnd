import time
import pandas as pd
from io import StringIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

#The last time this web scraper was used was before the end of the 25/26 football season, data may vary depending on when you're using this web scraper.

#statshub covers lower leagues too
#rerun this everytime depending on which league you want to do
#url = "https://www.statshub.com/league/premier-league/1?tab=player-statistics" #premier league (england)
#url = "https://www.statshub.com/league/laliga/24?tab=player-statistics" #laliga (spain)
#url = "https://www.statshub.com/league/bundesliga/30?tab=player-statistics" #bundesliga (germany)
#url = "https://www.statshub.com/league/ligue-1/4?tab=player-statistics" #ligue 1 (france)
#url = "https://www.statshub.com/league/serie-a/21?tab=player-statistics" #serie a (italy)
#### top 5 second-tier leagues
#url = "https://www.statshub.com/league/laliga-2/25?tab=player-statistics" #laliga2 (spain)
#url = "https://www.statshub.com/league/championship/2?tab=player-statistics" #championship (england)
#url = "https://www.statshub.com/league/2-bundesliga/29?tab=player-statistics" #2buundesliga (germany)
#url = "https://www.statshub.com/league/serie-b/22?tab=player-statistics" #serie b (italy)
#url = "https://www.statshub.com/league/ligue-2/13?tab=player-statistics" #ligue 2 (france)
#### non-top 5 leagues 
#url = "https://www.statshub.com/league/liga-portugal-betclic/37?tab=player-statistics" #liga portugal (top)
#url = "https://www.statshub.com/league/liga-portugal-2/94?tab=player-statistics" #liga portugal 2 (second tier)
#url = "https://www.statshub.com/league/eredivisie/27?tab=player-statistics" #eredivisie (netherlands)
url = "https://www.statshub.com/league/premiership/39?tab=player-statistics" #premiership (scotland)

driver.get(url)

#wait for the tablee
wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

#this selects the page to show "last season" (24/25) stats, statshub also only provides last and current season stats, unfortunate raelly
driver.execute_script("arguments[0].click();", wait.until(EC.element_to_be_clickable((By.ID, "game-range"))))
driver.execute_script("arguments[0].click();", wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Last Season')]"))))

time.sleep(4)

#filters for seperate csv files, add them together later, with other data sources
positions = ["Forward", "Midfielder", "Defender", "Goalkeeper"]
presets = ["Default", "Attacking", "Defending", "Passing", "Goalkeeping"]

#finds the position dropdown to let us filteer through positions
positionSelect = Select(
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select")))
)

#scraping loops
for position in positions:

    #chooses position value to change to the current position we're looping (forward, midfielder etc.)
    positionSelect.select_by_visible_text(position)
    time.sleep(4)

    for preset in presets:

        #finds preset button (for default, attacking etc.)
        driver.execute_script("arguments[0].click();", wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(),'{preset}')]"))))
        time.sleep(4)

        #list for pagination 
        pages = []

        #this loops thedata table back to 1, to keep consistency through the csvs and to not miss anyone out
        try:
            driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//button[text()='1']"))
            time.sleep(4)
        except:
            pass

        #now we continue to scrape until the final page
        while True:
            #relocate the table everytime
            table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

            #take the html into a df to store
            pages.append(pd.read_html(StringIO(table.get_attribute("outerHTML")))[0])

            try:
                #finds the current page number
                currentPage = driver.find_element(By.CSS_SELECTOR,"button.bg-secondary").text
                #finds the next page arrow
                nextButton = driver.find_element(By.CSS_SELECTOR,"button svg.lucide-chevron-right").find_element(By.XPATH, "..")
                #next page doesnt exist, meeaning we reached the final page
                if nextButton.get_attribute("disabled"):
                    break

                driver.execute_script("arguments[0].click();", nextButton)

                # wait until page number changes
                time.sleep(8)

            except:
                break

        #merges dataframes and make the downloaded files follow the naming scheme
        pd.concat(pages, ignore_index=True).to_csv(f"{position.lower()}{preset.upper()}.csv", index=False)
driver.quit()