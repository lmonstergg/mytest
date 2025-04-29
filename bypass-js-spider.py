from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import time
import logging
import json
import undetected_chromedriver as uc  # 关键修改：使用 uc 的专属配置方式

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class AntiDetectCrawler:
    def __init__(self):
        self.driver = self._init_stealth_driver()
        self.wait = WebDriverWait(self.driver, 15)
        
    def _init_stealth_driver(self):
        """使用 undetected_chromedriver 的专属配置"""
        options = uc.ChromeOptions()  # 关键修改：使用 uc 提供的 ChromeOptions
        
        # 反检测配置（uc 已内置大部分优化，无需手动设置 excludeSwitches）
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # 随机用户代理
        user_agents = [
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 120)}.0.{random.randint(1000, 9999)}.{random.randint(100, 999)} Safari/537.36"
            for _ in range(5)
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # 初始化驱动（关键修改：直接使用 uc.Chrome，无需单独配置 Service）
        driver = uc.Chrome(
            options=options,
            version_main=114  # 与 ChromeDriver 主版本一致
        )
        return driver
    
    def _human_like_interaction(self):
        """模拟人类交互行为"""
        # 随机滚动
        for _ in range(random.randint(2, 5)):
            scroll_px = random.randint(200, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_px})")
            time.sleep(random.uniform(0.5, 1.5))
        
        # 随机鼠标移动
        actions = ActionChains(self.driver)
        for _ in range(random.randint(3, 7)):
            actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50)).perform()
            time.sleep(random.uniform(0.1, 0.3))
        
        # 随机键盘操作
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        for _ in range(random.randint(1, 3)):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.2, 0.5))
    
    def crawl_page(self, url):
        """爬取目标页面"""
        try:
            logger.info(f"正在访问: {url}")
            self.driver.get(url)
            self._human_like_interaction()
            
            # 确保内容加载
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
            time.sleep(random.uniform(1, 2))
            
            # 提取数据
            data = {
                "title": self.driver.title,
                "url": self.driver.current_url,
                "timestamp": int(time.time())
            }
            return data
            
        except Exception as e:
            logger.error(f"页面爬取失败: {str(e)}")
            return None
    
    def close(self):
        self.driver.quit()
        logger.info("浏览器已关闭")

if __name__ == "__main__":
    crawler = AntiDetectCrawler()
    try:
        result = crawler.crawl_page("http://cctest.weibeian.top")
        if result:
            logger.info(f"爬取结果:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
            with open("result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
    finally:
        crawler.close()
