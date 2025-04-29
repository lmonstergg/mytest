import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin
from fake_useragent import UserAgent

# 初始化工具
ua = UserAgent()
session = requests.Session()

# 配置参数
BASE_URL = "http://127.0.0.1:5000"
DELAY = random.uniform(1, 3)  # 随机延迟1-3秒
RETRY_TIMES = 3
TIMEOUT = 10

# 代理池示例 (实际使用时需要替换为有效代理)
PROXIES = [
    None,  # 直连
    # {"http": "http://proxy1.example.com:8080", "https": "http://proxy1.example.com:8080"},
    # {"http": "http://proxy2.example.com:8080", "https": "http://proxy2.example.com:8080"},
]

def get_random_proxy():
    return random.choice(PROXIES)

def get_random_headers():
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Referer': BASE_URL,
        'DNT': str(random.randint(0, 1))  # 随机发送Do Not Track
    }

def request_with_retry(url, method='GET', **kwargs):
    for attempt in range(RETRY_TIMES):
        try:
            # 随机选择代理和头部
            kwargs['proxies'] = get_random_proxy()
            if 'headers' not in kwargs:
                kwargs['headers'] = get_random_headers()
            
            # 设置超时
            kwargs['timeout'] = TIMEOUT
            
            # 随机延迟
            time.sleep(DELAY)
            
            if method.upper() == 'GET':
                response = session.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = session.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # 检查HTTP状态码
            response.raise_for_status()
            
            # 检查是否有反爬提示 (根据实际网站调整)
            if "检测到异常请求" in response.text:
                raise Exception("Anti-crawler detected")
                
            return response
            
        except Exception as e:
            print(f"请求失败 (尝试 {attempt + 1}/{RETRY_TIMES}): {e}")
            if attempt == RETRY_TIMES - 1:
                raise
            time.sleep(random.uniform(2, 5))  # 失败后等待更长时间

def simulate_human_behavior():
    """模拟人类行为模式"""
    # 随机鼠标移动模式
    mouse_movements = [
        {'x': random.randint(0, 100), 'y': random.randint(0, 100)},
        {'x': random.randint(100, 200), 'y': random.randint(100, 200)}
    ]
    
    # 随机滚动
    scroll_positions = [random.randint(0, 1000) for _ in range(2)]
    
    return {
        'mouse_movements': mouse_movements,
        'scroll_positions': scroll_positions,
        'click_delay': random.uniform(0.5, 1.5)
    }

def extract_with_bs4(html, selector, extract_func):
    """更健壮的提取函数"""
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.select(selector)
    if not elements:
        return None
    try:
        return extract_func(elements[0])
    except Exception as e:
        print(f"提取数据失败: {e}")
        return None

def crawl_website():
    print("=== 开始智能爬取测试网站数据 ===")
    
    # 1. 首先访问首页，获取cookies等
    print("\n[阶段1] 初始化会话...")
    try:
        home_response = request_with_retry(BASE_URL)
        print("成功建立初始会话")
    except Exception as e:
        print(f"初始化失败: {e}")
        return
    
    # 2. 爬取产品数据
    print("\n[阶段2] 爬取产品数据...")
    products = crawl_paginated_data("/products", "product", {
        "name": lambda div: extract_with_bs4(str(div), "h3", lambda x: x.get_text(strip=True)),
        "link": lambda div: extract_with_bs4(str(div), "a", lambda x: urljoin(BASE_URL, x["href"])),
        "category": lambda div: extract_field(str(div), "类别:"),
        "price": lambda div: extract_field(str(div), "价格:"),
        "specs": lambda div: {
            "CPU": extract_spec(str(div), "CPU"),
            "内存": extract_spec(str(div), "内存"),
            "存储": extract_spec(str(div), "存储")
        },
        "created_at": lambda div: extract_field(str(div), "上架时间:")
    })
    save_to_file(products, "products.json")
    
    # 3. 爬取新闻数据
    print("\n[阶段3] 爬取新闻数据...")
    news = crawl_paginated_data("/news", "news-item", {
        "title": lambda div: extract_with_bs4(str(div), "h3", lambda x: x.get_text(strip=True)),
        "link": lambda div: extract_with_bs4(str(div), "a", lambda x: urljoin(BASE_URL, x["href"])),
        "publish_date": lambda div: extract_field(str(div), "日期:"),
        "author": lambda div: extract_field(str(div), "作者:"),
        "views": lambda div: int(extract_field(str(div), "浏览量:")) if extract_field(str(div), "浏览量:").isdigit() else 0
    })
    save_to_file(news, "news.json")
    
    # 4. 爬取用户数据
    print("\n[阶段4] 爬取用户数据...")
    users = []
    try:
        response = request_with_retry(urljoin(BASE_URL, "/users"))
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.select("table tbody tr")
        for i, row in enumerate(rows):
            # 模拟人类浏览速度
            if i % 5 == 0:
                time.sleep(random.uniform(0.5, 2.0))
                
            cols = row.find_all("td")
            if len(cols) >= 6:
                user_id = cols[0].get_text(strip=True)
                users.append({
                    "id": int(user_id),
                    "username": cols[1].get_text(strip=True),
                    "name": cols[2].get_text(strip=True),
                    "role": cols[3].get_text(strip=True),
                    "department": cols[4].get_text(strip=True),
                    "register_date": cols[5].get_text(strip=True),
                    "detail_link": urljoin(BASE_URL, f"/user/{user_id}")
                })
        
        # 爬取用户详情 (随机爬取3-5个)
        detail_count = random.randint(3, min(5, len(users)))
        for user in random.sample(users, detail_count):
            user_detail = crawl_user_detail(user["detail_link"])
            user.update(user_detail)
            time.sleep(random.uniform(1, 3))  # 随机延迟
            
        save_to_file(users, "users.json")
    except Exception as e:
        print(f"爬取用户数据失败: {e}")
    
    print("\n=== 爬取完成 ===")

def crawl_paginated_data(base_path, item_class, field_extractors):
    print(f"开始爬取 {base_path} 数据...")
    data = []
    page = 1
    max_pages = 5  # 防止无限循环
    
    while page <= max_pages:
        url = urljoin(BASE_URL, f"{base_path}?page={page}")
        print(f"正在爬取: {url}")
        
        try:
            # 模拟人类行为
            behavior = simulate_human_behavior()
            
            response = request_with_retry(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = soup.select(f".{item_class}")
            for item in items:
                item_data = {}
                for field, extractor in field_extractors.items():
                    try:
                        item_data[field] = extractor(item)
                    except Exception as e:
                        print(f"提取字段 {field} 失败: {e}")
                        item_data[field] = None
                data.append(item_data)
            
            # 随机决定是否继续下一页 (模拟人类不一定点下一页)
            if random.random() < 0.7 and page < max_pages:  # 70%概率继续
                page += 1
                # 随机翻页延迟
                time.sleep(random.uniform(1, 4))
            else:
                break
                
        except Exception as e:
            print(f"爬取失败: {e}")
            break
    
    print(f"已获取 {len(data)} 条数据")
    return data

def crawl_user_detail(url):
    try:
        response = request_with_retry(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        detail = {
            "email": extract_field(str(soup), "邮箱:"),
            "phone": extract_field(str(soup), "电话:"),
            "last_login": extract_field(str(soup), "最后登录:")
        }
        return detail
    except Exception as e:
        print(f"爬取用户详情失败: {e}")
        return {}

def extract_field(html, label):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(strip=True)
        return text.split(label)[-1].split("|")[0].strip().split("\n")[0].strip()
    except:
        return ""

def extract_spec(html, spec_name):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(strip=True)
        return text.split(spec_name)[-1].split(",")[0].strip()
    except:
        return ""

def save_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到 {filename}")

if __name__ == '__main__':
    # 安装依赖: pip install fake-useragent
    crawl_website()
