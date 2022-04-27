from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing.dummy import Pool
from loguru import logger
from sys import stderr, platform, version_info
from msvcrt import getch
from ctypes import windll
from urllib3 import disable_warnings
from os import system
from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
from time import sleep
from selenium.common.exceptions import NoSuchElementException        

if platform == "win32" and (3, 8, 0) <= version_info < (3, 9, 0):
	set_event_loop_policy(WindowsSelectorEventLoopPolicy())

disable_warnings()
def clear(): return system('cls')
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")
windll.kernel32.SetConsoleTitleW('UNFreeze Twitter Accounts | by NAZAVOD')
print('Telegram channel - https://t.me/n4z4v0d\n')

accounts_folder = str(input('Перетяните .txt с cookies: '))

with open(accounts_folder, 'r', encoding = 'utf-8') as file:
	all_cookies = [row.strip() for row in file]

threads = int(input('Threads: '))
use_proxies = str(input('Использовать Proxy? (y/N): ')).lower()

if use_proxies == 'y':
	proxy_type = str(input('Введите тип Proxy (http; https; socks4; socks5): '))

	proxies = []

def take_proxies():
	with open('proxies.txt') as file:
		proxies = [row.strip() for row in file]

	return(proxies)

class App():
	def __init__(self, data):
		self.cookies_str = data[0]
		self.proxy = data[1]

	def interceptor(self, request):
		del request.headers['cookie']  # Delete the header first
		request.headers['cookie'] = self.cookies_str

	def work(self):
		for _ in range(3):
			try:
				if self.proxy:
					options = {
					'proxy': {
							'http': f'{proxy_type}://{self.proxy}',
							'https': f'{proxy_type}://{self.proxy}',
							'no_proxy': 'localhost,127.0.0.1'
						}
					}

				else:
					options = {}

				co = webdriver.ChromeOptions()
				co.add_argument('--disable-gpu')
				co.add_argument('--disable-infobars')
				co.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
				co.add_argument("lang=en-US")
				co.page_load_strategy = 'eager'
				co.add_argument("--mute-audio")
				co.add_argument('log-level=3')
				co.add_argument("--headless")
				co.add_experimental_option('excludeSwitches', ['enable-logging'])

				driver = webdriver.Chrome(seleniumwire_options=options, options = co)
				driver.request_interceptor = self.interceptor
				wait = WebDriverWait(driver, 180)
				driver.get('https://twitter.com/account/access')
				wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'Button.EdgeButton.EdgeButton--primary'))).click()
				
				for i in range(181):
					try:
						driver.find_element(By.CLASS_NAME, "Button.EdgeButton.EdgeButton--primary")

						if 'twitter.com/?lang=' in driver.current_url:
							break

						elif i == 180:
							raise TimeoutError()

					except NoSuchElementException:
						pass

					finally:
						sleep(1)

			except TimeoutError as error:

				try:
					driver.quit()

				except:
					pass

				logger.error(f'{self.cookies_str} | Тайм-аут, пробую еще раз')

			except Exception as error:

				try:
					driver.quit()

				except:
					pass

				logger.error(f'{self.cookies_str} | Непредвиденная ошибка: {error}')

			else:

				try:
					driver.quit()

				except:
					pass

				with open('cookies.txt', 'a') as file:
					file.write(f'{self.cookies_str}\n')

				logger.success(f'{self.cookies_str} | Блокировка успешно снята')

				return

		try:
			driver.quit()

		except:
			pass

		with open('errors.txt', 'a') as file:
			file.write(f'{self.cookies_str}\n')

def start(data):
	app = App(data)
	app.work()

if __name__ == '__main__':
	clear()

	if use_proxies == 'y':
		while len(proxies) < len(all_cookies):
			proxies.append(list(current_proxy for current_proxy in take_proxies())[0])

	else:
		proxies = [None for _ in range(len(all_cookies))]

	logger.info(f'Loaded {len(all_cookies)} accounts | {len(proxies)} proxies\n')

	pool = Pool(threads)
	pool.map(start, list(zip(all_cookies, proxies)))

	logger.success('Работа успешно завершена')
	print('\nPress Any Key To Exit..')
	getch()
	exit()
