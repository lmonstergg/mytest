import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

def crawl_website():
    print("=== 开始爬取测试网站数据 ===")
    
    # 1. 爬取产品数据
    products = crawl_paginated_data("/products", "product", {
        "name": lambda div: div.find("h3").get_text(strip=True),
        "link": lambda div: urljoin(BASE_URL, div.find("a")["href"]),
        "category": lambda div: extract_field(div, "类别:"),
        "price": lambda div: extract_field(div, "价格:"),
        "specs": lambda div: {
            "CPU": extract_spec(div, "CPU"),
            "内存": extract_spec(div, "内存"),
            "存储": extract_spec(div, "存储")
        },
        "created_at": lambda div: extract_field(div, "上架时间:")
    })
    save_to_file(products, "products.json")
    
    # 2. 爬取新闻数据
    news = crawl_paginated_data("/news", "news-item", {
        "title": lambda div: div.find("h3").get_text(strip=True),
        "link": lambda div: urljoin(BASE_URL, div.find("a")["href"]),
        "publish_date": lambda div: extract_field(div, "日期:"),
        "author": lambda div: extract_field(div, "作者:"),
        "views": lambda div: int(extract_field(div, "浏览量:"))
    })
    save_to_file(news, "news.json")
    
    # 3. 爬取用户数据
    users = []
    print("\n=== 爬取用户数据 ===")
    try:
        response = requests.get(urljoin(BASE_URL, "/users"))
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.select("table tbody tr")
        for row in rows:
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
        
        # 爬取用户详情
        for user in users[:3]:  # 只爬取前3个用户详情作为示例
            user_detail = crawl_user_detail(user["detail_link"])
            user.update(user_detail)
            time.sleep(1)
        
        save_to_file(users, "users.json")
    except Exception as e:
        print(f"爬取用户数据失败: {e}")
    
    print("\n=== 爬取完成 ===")

def crawl_paginated_data(base_path, item_class, field_extractors):
    print(f"\n=== 开始爬取 {base_path} ===")
    data = []
    page = 1
    
    while True:
        url = urljoin(BASE_URL, f"{base_path}?page={page}")
        print(f"正在爬取: {url}")
        
        try:
            response = requests.get(url)
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
            
            # 检查是否有下一页
            next_page = soup.select_one('.pagination a[href*="page="]:contains("下一页")')
            if not next_page:
                break
            page += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"爬取失败: {e}")
            break
    
    print(f"已获取 {len(data)} 条数据")
    return data

def crawl_user_detail(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        detail = {
            "email": extract_field(soup, "邮箱:"),
            "phone": extract_field(soup, "电话:"),
            "last_login": extract_field(soup, "最后登录:")
        }
        return detail
    except Exception as e:
        print(f"爬取用户详情失败: {e}")
        return {}

def extract_field(container, label):
    try:
        return container.get_text(strip=True).split(label)[-1].split("|")[0].strip()
    except:
        return ""

def extract_spec(container, spec_name):
    try:
        return container.get_text(strip=True).split(spec_name)[-1].split(",")[0].strip()
    except:
        return ""

def save_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到 {filename}")

if __name__ == '__main__':
    crawl_website()
