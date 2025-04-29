from flask import Flask, render_template_string, request
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# 模拟数据库
class Database:
    def __init__(self):
        self.products = self._generate_products()
        self.news = self._generate_news()
        self.users = self._generate_users()
    
    def _generate_products(self):
        categories = ["云计算", "服务器", "数据库", "存储", "网络", "安全"]
        products = []
        for i in range(1, 31):
            products.append({
                "id": i,
                "name": f"{random.choice(categories)}服务{i}",
                "category": random.choice(categories),
                "price": round(random.uniform(100, 5000), 2),
                "specs": {
                    "CPU": f"{random.choice([2,4,8,16])}核",
                    "内存": f"{random.choice([8,16,32,64])}GB",
                    "存储": f"{random.choice([100,200,500,1000])}GB SSD"
                },
                "description": f"这是{random.choice(categories)}类产品的详细描述，适用于各种企业场景",
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
            })
        return products
    
    def _generate_news(self):
        news_types = ["产品发布", "优惠活动", "技术分享", "行业动态"]
        news = []
        for i in range(1, 21):
            news.append({
                "id": i,
                "title": f"{random.choice(news_types)}：{random.choice(['重磅', '最新', '独家'])}消息",
                "content": f"这里是新闻的详细内容，包含各种技术术语和产品介绍。本次新闻主要关于{random.choice(['云计算', '大数据', '人工智能'])}领域的发展。",
                "publish_date": (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                "author": random.choice(["华为云官方", "技术专家", "市场部"])
            })
        return news
    
    def _generate_users(self):
        roles = ["管理员", "普通用户", "VIP用户", "测试用户"]
        users = []
        for i in range(1, 11):
            users.append({
                "id": i,
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "role": random.choice(roles),
                "register_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
            })
        return users

db = Database()

# 基础模板字符串
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>云计算服务测试平台</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { display: flex; }
        .sidebar { width: 200px; padding: 10px; }
        .content { flex: 1; padding: 10px; }
        .product, .news-item, .user { border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; }
        .pagination { margin-top: 20px; }
        a { margin: 0 5px; }
    </style>
</head>
<body>
    <h1>云计算服务测试平台</h1>
    <div class="container">
        <div class="sidebar">
            <h3>导航</h3>
            <ul>
                <li><a href="/">首页</a></li>
                <li><a href="/products">产品列表</a></li>
                <li><a href="/news">新闻中心</a></li>
                <li><a href="/users">用户管理</a></li>
            </ul>
        </div>
        <div class="content">
            {% block content %}{% endblock %}
        </div>
    </div>
</body>
</html>
'''

def render_with_base(content):
    """辅助函数：将内容插入基础模板"""
    return BASE_TEMPLATE + content

@app.route('/')
def index():
    content = '''
    <h2>欢迎来到测试平台</h2>
    <p>这是一个用于爬虫练习的模拟云计算服务平台</p>
    <div>
        <h3>最新产品</h3>
        {% for p in products[:3] %}
        <div class="product">
            <h4><a href="/product/{{ p.id }}">{{ p.name }}</a></h4>
            <p>类别: {{ p.category }} | 价格: ¥{{ p.price }}</p>
        </div>
        {% endfor %}
    </div>
    <div>
        <h3>最新新闻</h3>
        {% for n in news[:3] %}
        <div class="news-item">
            <h4><a href="/news/{{ n.id }}">{{ n.title }}</a></h4>
            <p>{{ n.publish_date }} | 作者: {{ n.author }}</p>
        </div>
        {% endfor %}
    </div>
    '''
    return render_template_string(render_with_base(content), 
                               products=db.products, 
                               news=db.news)

@app.route('/products')
def product_list():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    total_pages = (len(db.products) + per_page - 1) // per_page
    paginated_products = db.products[(page-1)*per_page : page*per_page]
    
    content = '''
    <h2>产品列表</h2>
    {% for p in products %}
    <div class="product">
        <h3><a href="/product/{{ p.id }}">{{ p.name }}</a></h3>
        <p>类别: {{ p.category }} | 价格: ¥{{ p.price }} | 发布日期: {{ p.created_at }}</p>
        <p>规格: CPU {{ p.specs.CPU }}, 内存 {{ p.specs.内存 }}, 存储 {{ p.specs.存储 }}</p>
    </div>
    {% endfor %}
    <div class="pagination">
        {% if page > 1 %}
            <a href="/products?page={{ page-1 }}">上一页</a>
        {% endif %}
        第 {{ page }} 页/共 {{ total_pages }} 页
        {% if page < total_pages %}
            <a href="/products?page={{ page+1 }}">下一页</a>
        {% endif %}
    </div>
    '''
    return render_template_string(render_with_base(content),
                               products=paginated_products,
                               page=page,
                               total_pages=total_pages)

@app.route('/product/<int:id>')
def product_detail(id):
    product = next((p for p in db.products if p['id'] == id), None)
    if not product:
        return "产品不存在", 404
    
    content = '''
    <h2>{{ product.name }}</h2>
    <div class="product">
        <p><strong>类别:</strong> {{ product.category }}</p>
        <p><strong>价格:</strong> ¥{{ product.price }}</p>
        <p><strong>规格:</strong> 
            CPU {{ product.specs.CPU }}, 
            内存 {{ product.specs.内存 }}, 
            存储 {{ product.specs.存储 }}
        </p>
        <p><strong>描述:</strong> {{ product.description }}</p>
        <p><strong>上架时间:</strong> {{ product.created_at }}</p>
    </div>
    <a href="/products">返回产品列表</a>
    '''
    return render_template_string(render_with_base(content),
                               product=product)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
