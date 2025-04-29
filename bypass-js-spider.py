from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import json
import os
from urllib.parse import urljoin

# 配置参数
BASE_URL = "http://127.0.0.1:5000"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 随机User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

def init_driver():
    """初始化Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 添加其他反检测参数
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 修改WebDriver属性以防检测
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def simulate_human_interaction(driver):
    """模拟人类交互行为"""
    # 随机滚动
    scroll_height = random.randint(200, 1000)
    driver.execute_script(f"window.scrollTo(0, {scroll_height})")
    time.sleep(random.uniform(0.5, 1.5))
    
    # 随机鼠标移动
    actions = webdriver.ActionChains(driver)
    actions.move_by_offset(random.randint(10, 50), random.randint(10, 50))
    actions.perform()

def wait_for_js_validation(driver, timeout=10):
    """等待JS验证完成"""
    try:
        # 等待可能出现的验证元素
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(random.uniform(2, 4))  # 额外等待时间
        
        # 检查是否有验证相关的元素
        if len(driver.find_elements(By.CSS_SELECTOR, ".js-validation")) > 0:
            print("检测到JS验证，等待验证完成...")
            time.sleep(5)  # 给验证留出时间
            
    except TimeoutException:
        print("等待JS验证超时，继续执行...")

def extract_product_data(driver):
    """提取产品数据"""
    products = []
    items = driver.find_elements(By.CSS_SELECTOR, ".product")
    for item in items:
        try:
            products.append({
                "name": item.find_element(By.CSS_SELECTOR, "h3").text,
                "category": item.find_element(By.CSS_SELECTOR, ".label:contains('类别') + span").text,
                "price": item.find_element(By.CSS_SELECTOR, ".label:contains('价格') + span").text,
                "specs": {
                    "CPU": item.find_element(By.CSS_SELECTOR, ".label:contains('CPU') + span").text,
                    "内存": item.find_element(By.CSS_SELECTOR, ".label:contains('内存') + span").text,
                    "存储": item.find_element(By.CSS_SELECTOR, ".label:contains('存储') + span").text
                },
                "link": item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            })
        except Exception as e:
            print(f"提取产品数据出错: {e}")
    return products

def crawl_with_selenium():
    """使用Selenium爬取数据"""
    driver = init_driver()
    try:
        # 1. 访问首页
        print("访问首页...")
        driver.get(BASE_URL)
        wait_for_js_validation(driver)
        simulate_human_interaction(driver)
        
        # 2. 爬取产品数据
        print("\n爬取产品数据...")
        products = []
        page = 1
        while True:
            driver.get(f"{BASE_URL}/products?page={page}")
            wait_for_js_validation(driver)
            simulate_human_interaction(driver)
            
            # 提取当前页数据
            page_products = extract_product_data(driver)
            products.extend(page_products)
            print(f"已获取第 {page} 页 {len(page_products)} 条产品数据")
            
            # 检查是否有下一页
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, ".pagination a:contains('下一页')")
                next_btn.click()
                page += 1
                time.sleep(random.uniform(2, 4))
            except:
                break
        
        # 保存产品数据
        with open(f"{OUTPUT_DIR}/products_selenium.json", 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        # 3. 爬取新闻数据 (类似实现)
        # ...
        
    finally:
        driver.quit()

if __name__ == '__main__':
    crawl_with_selenium()
    print("\n=== 爬取完成 ===")
