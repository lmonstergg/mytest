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
        news_topics = ["云计算", "人工智能", "大数据", "物联网", "区块链"]
        news = []
        for i in range(1, 21):
            news.append({
                "id": i,
                "title": f"{random.choice(news_types)}：关于{random.choice(news_topics)}的{random.choice(['重磅', '最新', '独家'])}消息",
                "content": f"这里是新闻{i}的详细内容。本次新闻主要关于{random.choice(news_topics)}领域的发展，详细介绍了{random.choice(['技术突破', '市场趋势', '应用案例'])}。\n\n更多详情请关注我们的官方公告。",
                "publish_date": (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                "author": random.choice(["华为云官方", "技术专家", "市场部", "行业分析师"]),
                "views": random.randint(100, 5000)
            })
        return news
    
    def _generate_users(self):
        first_names = ["张", "王", "李", "赵", "刘"]
        last_names = ["伟", "芳", "娜", "秀英", "强", "洋"]
        roles = ["管理员", "普通用户", "VIP用户", "测试用户"]
        departments = ["技术部", "市场部", "销售部", "产品部", "客服部"]
        users = []
        for i in range(1, 16):
            users.append({
                "id": i,
                "username": f"user{i}",
                "name": f"{random.choice(first_names)}{random.choice(last_names)}",
                "email": f"user{i}@example.com",
                "phone": f"138{random.randint(1000,9999)}{random.randint(1000,9999)}",
                "role": random.choice(roles),
                "department": random.choice(departments),
                "register_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
                "last_login": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
            })
        return users

db = Database()

# 基础模板
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>云计算服务测试平台</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { display: flex; }
        .sidebar { width: 200px; padding: 10px; background: #f5f5f5; }
        .content { flex: 1; padding: 10px 20px; }
        .product, .news-item, .user-card { 
            border: 1px solid #ddd; 
            padding: 15px; 
            margin-bottom: 10px; 
            border-radius: 5px;
        }
        .pagination { margin-top: 20px; }
        a { color: #0066cc; text-decoration: none; margin: 0 5px; }
        a:hover { text-decoration: underline; }
        .label { font-weight: bold; color: #555; }
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

def render_page(content, **context):
    """渲染页面辅助函数"""
    return render_template_string(BASE_TEMPLATE + content, **context)

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
            <p><span class="label">类别:</span> {{ p.category }} | <span class="label">价格:</span> ¥{{ p.price }}</p>
        </div>
        {% endfor %}
        <p><a href="/products">查看所有产品 →</a></p>
    </div>
    
    <div>
        <h3>最新新闻</h3>
        {% for n in news[:3] %}
        <div class="news-item">
            <h4><a href="/news/{{ n.id }}">{{ n.title }}</a></h4>
            <p><span class="label">日期:</span> {{ n.publish_date }} | <span class="label">作者:</span> {{ n.author }}</p>
        </div>
        {% endfor %}
        <p><a href="/news">查看所有新闻 →</a></p>
    </div>
    '''
    return render_page(content, products=db.products, news=db.news)

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
        <p><span class="label">类别:</span> {{ p.category }} | <span class="label">价格:</span> ¥{{ p.price }}</p>
        <p><span class="label">规格:</span> CPU {{ p.specs.CPU }}, 内存 {{ p.specs.内存 }}, 存储 {{ p.specs.存储 }}</p>
        <p><span class="label">上架时间:</span> {{ p.created_at }}</p>
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
    return render_page(content, 
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
        <p><span class="label">类别:</span> {{ product.category }}</p>
        <p><span class="label">价格:</span> ¥{{ product.price }}</p>
        <p><span class="label">规格:</span> 
            CPU {{ product.specs.CPU }}, 
            内存 {{ product.specs.内存 }}, 
            存储 {{ product.specs.存储 }}
        </p>
        <p><span class="label">描述:</span> {{ product.description }}</p>
        <p><span class="label">上架时间:</span> {{ product.created_at }}</p>
    </div>
    <a href="/products">返回产品列表</a>
    '''
    return render_page(content, product=product)

@app.route('/news')
def news_list():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    total_pages = (len(db.news) + per_page - 1) // per_page
    paginated_news = db.news[(page-1)*per_page : page*per_page]
    
    content = '''
    <h2>新闻中心</h2>
    {% for n in news %}
    <div class="news-item">
        <h3><a href="/news/{{ n.id }}">{{ n.title }}</a></h3>
        <p><span class="label">日期:</span> {{ n.publish_date }} | 
           <span class="label">作者:</span> {{ n.author }} | 
           <span class="label">浏览量:</span> {{ n.views }}</p>
        <p>{{ n.content[:100] }}...</p>
    </div>
    {% endfor %}
    
    <div class="pagination">
        {% if page > 1 %}
            <a href="/news?page={{ page-1 }}">上一页</a>
        {% endif %}
        第 {{ page }} 页/共 {{ total_pages }} 页
        {% if page < total_pages %}
            <a href="/news?page={{ page+1 }}">下一页</a>
        {% endif %}
    </div>
    '''
    return render_page(content, 
                     news=paginated_news, 
                     page=page, 
                     total_pages=total_pages)

@app.route('/news/<int:id>')
def news_detail(id):
    news_item = next((n for n in db.news if n['id'] == id), None)
    if not news_item:
        return "新闻不存在", 404
    
    content = '''
    <h2>{{ news_item.title }}</h2>
    <div class="news-item">
        <p><span class="label">发布日期:</span> {{ news_item.publish_date }}</p>
        <p><span class="label">作者:</span> {{ news_item.author }}</p>
        <p><span class="label">浏览量:</span> {{ news_item.views }}</p>
        <div style="margin-top: 20px; line-height: 1.6;">
            {{ news_item.content | replace('\n', '<br>') }}
        </div>
    </div>
    <a href="/news">返回新闻列表</a>
    '''
    return render_page(content, news_item=news_item)

@app.route('/users')
def user_list():
    content = '''
    <h2>用户管理</h2>
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background: #f5f5f5;">
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">ID</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">用户名</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">姓名</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">角色</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">部门</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">注册日期</th>
            </tr>
        </thead>
        <tbody>
            {% for u in users %}
            <tr style="border: 1px solid #ddd;">
                <td style="padding: 10px;">{{ u.id }}</td>
                <td style="padding: 10px;">{{ u.username }}</td>
                <td style="padding: 10px;">{{ u.name }}</td>
                <td style="padding: 10px;">{{ u.role }}</td>
                <td style="padding: 10px;">{{ u.department }}</td>
                <td style="padding: 10px;">{{ u.register_date }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    '''
    return render_page(content, users=db.users)

@app.route('/user/<int:id>')
def user_detail(id):
    user = next((u for u in db.users if u['id'] == id), None)
    if not user:
        return "用户不存在", 404
    
    content = '''
    <h2>用户详情</h2>
    <div class="user-card">
        <p><span class="label">ID:</span> {{ user.id }}</p>
        <p><span class="label">用户名:</span> {{ user.username }}</p>
        <p><span class="label">姓名:</span> {{ user.name }}</p>
        <p><span class="label">邮箱:</span> {{ user.email }}</p>
        <p><span class="label">电话:</span> {{ user.phone }}</p>
        <p><span class="label">角色:</span> {{ user.role }}</p>
        <p><span class="label">部门:</span> {{ user.department }}</p>
        <p><span class="label">注册日期:</span> {{ user.register_date }}</p>
        <p><span class="label">最后登录:</span> {{ user.last_login }}</p>
    </div>
    <a href="/users">返回用户列表</a>
    '''
    return render_page(content, user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
