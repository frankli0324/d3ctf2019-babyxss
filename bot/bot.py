from selenium import webdriver
import time, sys, json, selenium

def get_options():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--user-data-dir=./profile')
    chrome_options.add_argument('--no-proxy-server')
    return chrome_options


def add(url):
    try:
        url = url.decode() # rq_win gives binary
    except:
        pass
    chrome_options = get_options()
    client = webdriver.Chrome(options=chrome_options)
    client.get(url)
    i = 0
    while 1:
        try:
            client.switch_to.alert.accept()
            i += 1
            if i > 1000:
                break
        except selenium.common.exceptions.NoAlertPresentException:
            break
    time.sleep(10)
    client.close()


if __name__ == '__main__':
    add(sys.argv[1])