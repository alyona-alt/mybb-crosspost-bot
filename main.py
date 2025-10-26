# === Custom login handler with fallback for modals and JS popups ===

def login(domain, login, password):
    try:
        driver.get(f"https://{domain}/login.php?action=in")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, "req_username")))
        driver.find_element(By.NAME, "req_username").send_keys(login)
        password_field = driver.find_element(By.NAME, "req_password")
        password_field.send_keys(password)
        from selenium.webdriver.common.keys import Keys
        password_field.send_keys(Keys.ENTER)
        time.sleep(1)
        print(f"✅ Вход через login.php на {domain}")
    except Exception as e:
        # check if already logged in
        if driver.find_elements(By.CSS_SELECTOR, "li#navlogout") or driver.find_elements(By.CSS_SELECTOR, "li#navprofile"): 
            print(f"✅ Уже залогинены на {domain}")
            return
        print(f"⚠️ Прямой вход не удался на {domain}, пробуем через navlogin — {e}")
        try:
            driver.get(f"https://{domain}/")
            driver.execute_script("document.getElementById('OnBottom')?.style?.setProperty('display', 'none', 'important')")
            driver.execute_script("document.querySelector('.site-attention-modal')?.style?.setProperty('display', 'none', 'important')")
            nav_login = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li#navlogin a")))
            driver.execute_script("arguments[0].scrollIntoView(true);", nav_login)
            nav_login.click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "req_username")))
            driver.find_element(By.NAME, "req_username").send_keys(login)
            password_field = driver.find_element(By.NAME, "req_password")
            password_field.send_keys(password)
            from selenium.webdriver.common.keys import Keys
            password_field.send_keys(Keys.ENTER)
            time.sleep(1)
            print(f"✅ Вход через navlogin на {domain}")
        except Exception as err:
            if driver.find_elements(By.CSS_SELECTOR, "li#navlogout") or driver.find_elements(By.CSS_SELECTOR, "li#navprofile"): 
                print(f"✅ Уже залогинены на {domain}")
                return
            print(f"⚠️ Вход через navlogin не удался на {domain}, пробуем PR.set() — {err}")

            # === ⏳ Пытаемся войти через PR.set() с принудительным показом формы ===
            try:
                driver.get(f"https://{domain}/")
                driver.execute_script("PR.set();")

                # Явно показать скрытую форму
                driver.execute_script("""
                    const splash = document.querySelector('#resplash');
                    if (splash) splash.style.setProperty('display', 'block', 'important');
                """)

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "req_username"))
                )

                # Заполнить поля
                driver.find_element(By.NAME, "req_username").send_keys(login)
                driver.find_element(By.NAME, "req_password").send_keys(password)

                # Попытка кликнуть
                try:
                    WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.NAME, "login"))
                    )
                    driver.find_element(By.NAME, "login").click()
                except:
                    # Если клик не сработал — пробуем submit
                    form = driver.find_element(By.CSS_SELECTOR, "form[action*='login']")
                    driver.execute_script("arguments[0].submit()", form)

                time.sleep(1)
                if driver.find_elements(By.CSS_SELECTOR, "li#navlogout") or driver.find_elements(By.CSS_SELECTOR, "li#navprofile"):
                    print(f"✅ Вход через PR.set() на {domain}")
                    return
                else:
                    raise Exception("Форма PR входа не сработала")
            except Exception as final_err:
                print(f"❌ Полный провал входа на {domain}: {final_err}")
                raise

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import re
import random
from configparser import ConfigParser
from datetime import datetime

#для доступа к гугл докам
import requests
import csv
import os
from io import StringIO

# selenium setup
chrome_options = Options()
#chrome_options.add_argument("--headless=new") #невидимка
chrome_options.add_argument("--start-maximized") #видимка
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

log_lines = []
summary_lines = []
summary_results = []
success_count = 0

def log(msg):
    print(msg)
    log_lines.append(msg)


def get_target_url_for_domain(domain):
    url = "https://docs.google.com/spreadsheets/..."
    response = requests.get(url)
    response.encoding = "utf-8"

    reader = csv.reader(StringIO(response.text))
    next(reader)  # skip header

    # Возможные варианты написания
    domain_variants = {domain.strip(), f"[{domain.strip()}]"}
    for row in reader:
        print(repr(row[0])) 
        print(repr(row[1])) 
        if not row or len(row) < 2:
            continue
        dom = row[0].strip()
        if dom in domain_variants:
            return row[1].strip()
    return None


# === Load your forum config (login credentials, target URL, reply text, and limit) ===
config = ConfigParser()
config.read("forum_config.txt")
self_forum = list(config.sections())[0]
login_user = config[self_forum].get("login")
password = config[self_forum].get("password")
#target_url = config[self_forum].get("foreign_ad_target")

target_url = get_target_url_for_domain(self_forum)
print(target_url)
if not target_url:
    raise RuntimeError(f"❌ Не найден foreign_ad_target для {self_forum} в Google Sheet")

#говорим что хотим рандом аки взрослые
import_ads = config[self_forum].get("reply_text", "").replace("\\n", "\n")
reply_options = [opt.strip() for opt in import_ads.split("|||") if opt.strip()]
if not reply_options:
    raise ValueError(f"❌ reply_text пуст или невалиден для {self_forum}")
reply_text = random.choice(reply_options)

#глядим на лимит
LIMIT = int(config[self_forum].get("limit", fallback="0"))

# === Read partner forums from forums.txt ===
#with open("forums.txt", "r", encoding="utf-8") as f:
#    forums = [line.strip() for line in f if line.strip()]

# ____________________________
# === Read files and collect the links for our forum ===

def get_forums():
    # Сначала пробуем прочитать из файла
    if os.path.exists("forums.txt"):
        with open("forums.txt", "r", encoding="utf-8") as f:
            forums = [line.strip() for line in f if line.strip()]
        if forums:
            print(f"[INFO] Найдено {len(forums)} форумов в forums.txt")
            return forums
        else:
            print("[INFO] forums.txt пуст — переключаемся на Google Sheet")

    # Если файл пустой — берём из Google Таблицы
    return get_forum_links_from_sheet()

def get_forum_links_from_sheet():
#    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
#             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
#    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
#    client = gspread.authorize(creds)

#    sheet = client.open_by_key("15RsB4McEz4T3CE21SO_0OD1yZEv-gkUsGe1SWhQAhdQ").worksheet("Список для рекламы")
#    data = sheet.get_all_values()
    url = "https://docs.google.com/spreadsheets/..."
    response = requests.get(url)
    response.encoding = "utf-8"

    reader = csv.reader(StringIO(response.text))
    next(reader)  # пропустить заголовок
    
    links = []
    for row in reader:
        if row and row[0].strip().startswith("http"):
            links.append(row[0].strip())
#    for row in data[1:]:  # Пропустить заголовки
#        cell = row[0].strip() if row else ""
#        if cell.startswith("http"):
#            links.append(cell)
    print(f"[INFO] Найдено {len(links)} форумов в Google Таблице")
    return links

forums = get_forums()

# ____________________________

# === Loop through each forum in forums.txt ===
for url in forums:
    if LIMIT and success_count >= LIMIT:
        log(f"⏹️ Достигнут лимит {LIMIT}. Останавливаемся.")
        break

    domain = re.search(r"https?://([^/]+)/", url).group(1)
    try:
        print(f"🔎 Ищем рекламу на: {url}")
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.post")))
        first_post = driver.find_element(By.CSS_SELECTOR, "div.post")
        code_block = first_post.find_element(By.CSS_SELECTOR, "div.code-box pre")
        foreign_ad = code_block.text.strip()
    except Exception as e:
        summary_results.append(f"❌ Реклама не найдена на {url} -- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log(f"❌ Не найдена реклама на {url} — {str(e)}")
        continue

    last_link_tag = driver.find_elements(By.CSS_SELECTOR, "link[rel='last']")
    foreign_last_page = last_link_tag[0].get_attribute("href") if last_link_tag else url


    # === Проверка: уже ли опубликована наша реклама ===
    try:
        driver.get(foreign_last_page)
        time.sleep(1)
        post_contents = driver.find_elements(By.CSS_SELECTOR, "div.post-content")

        already_present = False
        for post in post_contents:
            if self_forum in post.get_attribute("innerHTML"):
                already_present = True
                break

        if already_present:
            log(f"❌ Реклама уже опубликована на этой странице: {foreign_last_page}")
            summary_results.append(f"❌ Реклама уже размещена на {foreign_last_page} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            continue
    except Exception as e:
        log(f"⚠️ Не удалось проверить наличие рекламы на последней странице — {str(e)}")

    
    try:
        login(self_forum, login_user, password)
        driver.get(target_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "req_message")))
        driver.find_element(By.NAME, "req_message").send_keys(
            f"{foreign_ad}\n"
            f"[url={foreign_last_page}]ваша реклама[/url]\n"
            f"[align=right][size=10][i]снегуркино[/i][/size][/align]"
        )
        #driver.find_element(By.NAME, "req_message").send_keys(f"{foreign_ad}\n{foreign_last_page}")
        driver.find_element(By.NAME, "submit").click()

# Проверка: если <link rel="last"> есть — переходим на последнюю страницу
        last_link = driver.find_elements(By.CSS_SELECTOR, "link[rel='last']")
        if last_link:
            last_page_url = last_link[0].get_attribute("href")
            driver.get(last_page_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.permalink"))
            )

        # Получаем последний permalink (уже на нужной странице)
        permalinks = driver.find_elements(By.CSS_SELECTOR, "a.permalink")
        last_permalink = permalinks[-1].get_attribute("href")
        log(f"🔗 Получен permalink нового поста: {last_permalink}")
        log(f"✅ Опубликована реклама партнёра на нашем форуме: {last_permalink}")
    except Exception as e:
        summary_results.append(f"❌ Не удалось опубликовать на своём форуме -- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log(f"❌ Ошибка при публикации на своём форуме — {str(e)}")
        continue

    # Try to log in to partner forum with PR.nick or PiarNik
    try:
        driver.get(url)
        html = driver.page_source
        pr_script_match = re.search(r"PR\.nick\s*=\s*['\"](.*?)['\"]", html)
        pr_pass_match = re.search(r"PR\.pass\s*=\s*['\"](.*?)['\"]", html)
        alt_nick_match = re.search(r"PiarNik\s*=\s*['\"](.*?)['\"]", html)
        alt_pass_match = re.search(r"PiarPas\s*=\s*['\"](.*?)['\"]", html)

        if pr_script_match and pr_pass_match:
            pr_nick = pr_script_match.group(1)
            pr_pass = pr_pass_match.group(1)
        elif alt_nick_match and alt_pass_match:
            pr_nick = alt_nick_match.group(1)
            pr_pass = alt_pass_match.group(1)
        else:
            raise Exception("Не удалось найти PR.nick / PiarNik")

        login(domain, pr_nick, pr_pass)
    except Exception as e:
        summary_results.append(f"❌ Не удалось войти на {domain} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log(f"❌ Не удалось войти на форум {domain} — {str(e)}")
        continue

    try:
           driver.get(url)
           WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "req_message")))
           full_reply = f"{reply_text}\n{last_permalink}"
           driver.find_element(By.NAME, "req_message").send_keys(full_reply)
           driver.find_element(By.NAME, "submit").click()
           time.sleep(2)
   
           success_count += 1

           # === Step 4: Log success into visited_today.csv ===
           with open(f"visited_today_{datetime.now().strftime('%Y-%m-%d')}.csv", "a", encoding="utf-8") as vfile:
               vfile.write(f"{self_forum},{last_permalink},{foreign_last_page},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
           summary_results.append(f"✅ Реклама опубликована на {foreign_last_page} -- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
           log(f"✅ Ответ опубликован на {url}")
    except Exception as e:
           error_message = f"❌ Ошибка при публикации ответа на {url} — {str(e)}"
           summary_results.append(f"❌ Не удалось опубликовать ответ на {url} -- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
           log(error_message)
           # === Step 4b: Log failure into visited_today.csv ===
           with open(f"visited_today_{datetime.now().strftime('%Y-%m-%d')}.csv", "a", encoding="utf-8") as vfile:
               vfile.write(f"{self_forum},{last_permalink},{foreign_last_page},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{error_message}\n")

# === Write final summary and detailed log to log.txt ===
summary_lines.append(f"[{self_forum}]\n\n📊 Успешно: {success_count} из {LIMIT if LIMIT else '∞'}\n")
summary_lines.extend(summary_results)
summary_lines.append('\n------ Подробный лог ------\n')
log_lines = summary_lines + log_lines

with open(f"log_{datetime.now().strftime('%Y-%m-%d')}.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

driver.quit()
