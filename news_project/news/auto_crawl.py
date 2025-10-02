from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://github.com/DE7-F1/HeadlineService')


with open('./testoutput.txt', 'w') as f:
    f.write(driver.find_element(By.XPATH, '//*[@id="repo-content-pjax-container"]/div/div/div/div[1]/react-partial/div/div/div[3]/div[2]/div/div[2]/article').text)
    
