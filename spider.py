import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

def crawl_products():
    """爬取产品列表"""
    print("=== 开始爬取产品数据 ===")
    products = []
    page = 1
    
    while True:
        url = f"{BASE_URL}/products?page={page}"
        print(f"正在爬取: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取当前页产品
            for product_div in soup.select('.product'):
                product = {
                    'name': product_div.find('h3').get_text(strip=True),
                    'link': urljoin(BASE_URL, product_div.find('a')['href']),
                    'category': product_div.find('p').get_text(strip=True).split('|')[0].replace('类别:', '').strip(),
                    'price': product_div.find('p').get_text(strip=True).split('|')[1].replace('价格:', '').strip(),
                    'specs': {
                        'CPU': product_div.find_all('p')[1].get_text(strip=True).split('CPU')[-1].split(',')[0].strip(),
                        '内存': product_div.find_all('p')[1].get_text(strip=True).split('内存')[-1].split(',')[0].strip(),
                        '存储': product_div.find_all('p')[1].get_text(strip=True).split('存储')[-1].strip()
                    }
                }
                products.append(product)
                print(f"已获取产品: {product['name']}")
            
            # 检查是否有下一页
            next_page = soup.select_one('.pagination a[href*="page="]:contains("下一页")')
            if not next_page:
                break
            page += 1
            time.sleep(1)  # 礼貌性延迟
            
        except Exception as e:
            print(f"爬取失败: {e}")
            break
    
    # 保存数据
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(products)} 条产品数据到 products.json")

def crawl_news():
    """爬取新闻数据"""
    print("\n=== 开始爬取新闻数据 ===")
    url = f"{BASE_URL}/news"
    news = []
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for news_div in soup.select('.news-item'):
            news_item = {
                'title': news_div.find('h3').get_text(strip=True),
                'link': urljoin(BASE_URL, news_div.find('a')['href']),
                'date': news_div.find('p').get_text(strip=True).split('|')[0].strip(),
                'author': news_div.find('p').get_text(strip=True).split('|')[-1].replace('作者:', '').strip()
            }
            news.append(news_item)
            print(f"已获取新闻: {news_item['title']}")
        
        # 保存数据
        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump(news, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(news)} 条新闻数据到 news.json")
        
    except Exception as e:
        print(f"爬取失败: {e}")

def crawl_product_details():
    """爬取产品详情"""
    print("\n=== 开始爬取产品详情 ===")
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    for product in products[:5]:  # 只爬取前5个作为示例
        try:
            print(f"正在爬取产品详情: {product['name']}")
            response = requests.get(product['link'])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            detail = {
                'name': soup.select_one('h2').get_text(strip=True),
                'description': soup.select_one('.product p:nth-of-type(4)').get_text(strip=True).replace('描述:', '').strip(),
                'specs': {
                    'CPU': soup.select_one('.product p:nth-of-type(3)').get_text(strip=True).split('CPU')[-1].split(',')[0].strip(),
                    '内存': soup.select_one('.product p:nth-of-type(3)').get_text(strip=True).split('内存')[-1].split(',')[0].strip(),
                    '存储': soup.select_one('.product p:nth-of-type(3)').get_text(strip=True).split('存储')[-1].strip()
                },
                'created_at': soup.select_one('.product p:nth-of-type(5)').get_text(strip=True).replace('上架时间:', '').strip()
            }
            
            # 更新产品数据
            product.update(detail)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"爬取产品详情失败: {e}")
    
    # 保存更新后的数据
    with open('products_with_details.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print("产品详情已保存到 products_with_details.json")

if __name__ == '__main__':
    crawl_products()
    crawl_news()
    crawl_product_details()
    print("\n=== 爬取任务完成 ===")
