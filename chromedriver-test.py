from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging
import time

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def init_driver():
    try:
        chrome_options = Options()
        
        # CentOS专用配置
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")  # CentOS必须
        chrome_options.add_argument("--disable-dev-shm-usage")  # Docker/小内存环境必须
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # 指定chromedriver路径
        service = Service('/usr/local/bin/chromedriver')
        
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        logger.info("ChromeDriver初始化成功")
        return driver
    except Exception as e:
        logger.error(f"浏览器初始化失败: {str(e)}")
        raise

def crawl_data():
    driver = None
    try:
        driver = init_driver()
        logger.info("正在访问测试页面...")
        
        driver.get("http://127.0.0.1:5000")
        time.sleep(2)  # 确保JS执行完成
        
        # 打印页面标题验证
        logger.info(f"当前页面标题: {driver.title}")
        logger.info(f"当前URL: {driver.current_url}")
        
        # 示例：打印产品数量
        products = driver.find_elements("css selector", ".product")
        logger.info(f"找到 {len(products)} 个产品")
        
    except Exception as e:
        logger.error(f"爬取过程中出错: {str(e)}")
    finally:
        if driver:
            driver.quit()
            logger.info("浏览器已关闭")

if __name__ == "__main__":
    crawl_data()
