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
from urllib.parse import urljoin
import undetected_chromedriver as uc  # 需要安装：pip install undetected-chromedriver

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
        """初始化防检测浏览器驱动"""
        options = Options()
        
        # 反检测核心配置
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 常规无头模式配置
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # 随机用户代理
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Safari/537.36".format(
                random.randint(90, 120), random.randint(1000, 9999), random.randint(100, 999)
            for _ in range(5)
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # 使用undetected-chromedriver增强隐蔽性
        driver = uc.Chrome(
            service=Service('/usr/local/bin/chromedriver'),
            options=options,
            version_main=114  # 与安装的ChromeDriver主版本一致
        )
        
        # 修改navigator属性
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
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
            x_offset = random.randint(-50, 50)
            y_offset = random.randint(-50, 50)
            actions.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(0.1, 0.3))
        
        # 随机键盘操作
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        for _ in range(random.randint(1, 3)):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.2, 0.5))
    
    def _wait_for_js_validation(self):
        """处理JS验证"""
        try:
            # 等待可能出现的验证元素
            self.wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(random.uniform(1, 3))
            
            # 检查是否有验证框架
            if len(self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='captcha'], .geetest_holder")) > 0:
                logger.warning("检测到验证码框架，尝试绕过...")
                time.sleep(5)
                self.driver.execute_script("window.scrollBy(0, 500)")
                time.sleep(2)
                
        except Exception as e:
            logger.warning(f"JS验证等待异常: {str(e)}")
    
    def crawl_page(self, url):
        """爬取目标页面"""
        try:
            logger.info(f"正在访问: {url}")
            self.driver.get(url)
            
            # 处理验证和模拟行为
            self._wait_for_js_validation()
            self._human_like_interaction()
            
            # 确保内容加载
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            time.sleep(random.uniform(1, 2))
            
            # 获取动态渲染后的页面源码
            rendered_html = self.driver.page_source
            
            # 提取数据示例
            data = {
                "title": self.driver.title,
                "url": self.driver.current_url,
                "products": self._extract_products(),
                "timestamp": int(time.time())
            }
            
            return data
            
        except Exception as e:
            logger.error(f"页面爬取失败: {str(e)}")
            return None
    
    def _extract_products(self):
        """提取产品数据"""
        products = []
        try:
            items = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product"))
            
            for item in items:
                try:
                    product_data = {
                        "name": item.find_element(By.CSS_SELECTOR, "h3").text,
                        "price": item.find_element(By.CSS_SELECTOR, ".price").text,
                        "link": item.find_element(By.CSS_SELECTOR, "a").get_attribute("href"),
                        # 添加更多字段...
                    }
                    products.append(product_data)
                except Exception as e:
                    logger.warning(f"产品提取失败: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.warning(f"产品列表提取失败: {str(e)}")
        
        return products
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit()
        logger.info("浏览器已关闭")

if __name__ == "__main__":
    crawler = AntiDetectCrawler()
    try:
        # 示例爬取
        target_url = "http://127.0.0.1"
        result = crawler.crawl_page(target_url)
        
        if result:
            logger.info(f"成功爬取数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            with open("crawler_results.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            logger.error("爬取失败，未获取有效数据")
            
    finally:
        crawler.close()
