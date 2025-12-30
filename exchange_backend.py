"""
银行汇率查询后端服务
功能：爬取六大银行的实时汇率数据
运行方法：python exchange_backend.py
访问地址：http://localhost:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 货币代码映射
CURRENCY_MAP = {
    'USD': '美元',
    'EUR': '欧元',
    'HKD': '港币',
    'JPY': '日元',
    'KRW': '韩元',
    'MYR': '马来西亚林吉特'
}

def get_boc_rate(currency):
    """获取中国银行汇率"""
    try:
        url = 'https://www.boc.cn/sourcedb/whpj/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        currency_name = CURRENCY_MAP.get(currency, '')
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 6 and currency_name in cells[0].text:
                    buy_rate = cells[1].text.strip()
                    sell_rate = cells[3].text.strip()
                    if buy_rate and sell_rate:
                        return {
                            'bank': '中国银行',
                            'buyRate': buy_rate,
                            'sellRate': sell_rate,
                            'success': True
                        }
    except Exception as e:
        print(f"中国银行爬取失败: {e}")
    
    return {'bank': '中国银行', 'success': False}

def get_icbc_rate(currency):
    """获取工商银行汇率"""
    try:
        # 工商银行外汇牌价查询
        url = 'https://www.icbc.com.cn/ICBCDynamicSite/Charts/GoldTendChart.aspx'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.icbc.com.cn'
        }
        
        # 工商银行的汇率数据通常在JS中动态加载，尝试请求API
        api_url = 'https://www.icbc.com.cn/icbc/perFinance/forex/quotation/'
        response = requests.get(api_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        currency_name = CURRENCY_MAP.get(currency, '')
        
        # 查找包含汇率的表格
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4 and currency_name in row.text:
                    try:
                        buy_rate = cells[1].text.strip()
                        sell_rate = cells[2].text.strip()
                        if buy_rate and sell_rate and buy_rate.replace('.', '').isdigit():
                            return {
                                'bank': '中国工商银行',
                                'buyRate': buy_rate,
                                'sellRate': sell_rate,
                                'success': True
                            }
                    except:
                        continue
        
        print("工商银行：未找到匹配的汇率数据")
    except Exception as e:
        print(f"工商银行爬取失败: {e}")
    
    return {'bank': '中国工商银行', 'success': False}

def get_ccb_rate(currency):
    """获取建设银行汇率"""
    try:
        # 建设银行外汇频道
        url = 'https://forex.ccb.com/cn/forex/foreign_exchange_rate.html'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://forex.ccb.com'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        currency_name = CURRENCY_MAP.get(currency, '')
        
        # 建设银行的数据可能在表格中
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                if currency_name in row.text:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            # 通常格式：货币名称 | 现汇买入价 | 现钞买入价 | 现汇卖出价 | 现钞卖出价
                            buy_rate = cells[1].text.strip()
                            sell_rate = cells[3].text.strip()
                            if buy_rate and sell_rate and buy_rate.replace('.', '').isdigit():
                                return {
                                    'bank': '中国建设银行',
                                    'buyRate': buy_rate,
                                    'sellRate': sell_rate,
                                    'success': True
                                }
                        except:
                            continue
        
        print("建设银行：未找到匹配的汇率数据")
    except Exception as e:
        print(f"建设银行爬取失败: {e}")
    
    return {'bank': '中国建设银行', 'success': False}

def get_abc_rate(currency):
    """获取农业银行汇率"""
    try:
        # 农业银行外汇牌价
        url = 'http://www.abchina.com/cn/PersonalServices/Quotation/boc/default.htm'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://www.abchina.com'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        currency_name = CURRENCY_MAP.get(currency, '')
        
        # 查找汇率表格
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                if currency_name in row.text:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            buy_rate = cells[1].text.strip()
                            sell_rate = cells[2].text.strip()
                            if buy_rate and sell_rate and buy_rate.replace('.', '').isdigit():
                                return {
                                    'bank': '中国农业银行',
                                    'buyRate': buy_rate,
                                    'sellRate': sell_rate,
                                    'success': True
                                }
                        except:
                            continue
        
        print("农业银行：未找到匹配的汇率数据")
    except Exception as e:
        print(f"农业银行爬取失败: {e}")
    
    return {'bank': '中国农业银行', 'success': False}

def get_comm_rate(currency):
    """获取交通银行汇率"""
    try:
        # 交通银行外汇牌价
        url = 'http://www.bankcomm.com/BankCommSite/shtml/jyjr/cn/7158/7161/7167/list.shtml'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://www.bankcomm.com'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        currency_name = CURRENCY_MAP.get(currency, '')
        
        # 查找汇率数据
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                if currency_name in row.text or currency in row.text:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            # 交通银行格式可能不同，尝试多种格式
                            buy_rate = cells[1].text.strip()
                            sell_rate = cells[2].text.strip()
                            if buy_rate and sell_rate and buy_rate.replace('.', '').isdigit():
                                return {
                                    'bank': '交通银行',
                                    'buyRate': buy_rate,
                                    'sellRate': sell_rate,
                                    'success': True
                                }
                        except:
                            continue
        
        print("交通银行：未找到匹配的汇率数据")
    except Exception as e:
        print(f"交通银行爬取失败: {e}")
    
    return {'bank': '交通银行', 'success': False}

def get_cib_rate(currency):
    """获取兴业银行汇率"""
    try:
        # 兴业银行外汇牌价
        url = 'https://www.cib.com.cn/cn/personalServices/foreignExchange/index.html'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.cib.com.cn'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        currency_name = CURRENCY_MAP.get(currency, '')
        
        # 查找汇率表格
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                if currency_name in row.text or currency in row.text:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            buy_rate = cells[1].text.strip()
                            sell_rate = cells[2].text.strip()
                            if buy_rate and sell_rate and buy_rate.replace('.', '').isdigit():
                                return {
                                    'bank': '兴业银行',
                                    'buyRate': buy_rate,
                                    'sellRate': sell_rate,
                                    'success': True
                                }
                        except:
                            continue
        
        print("兴业银行：未找到匹配的汇率数据")
    except Exception as e:
        print(f"兴业银行爬取失败: {e}")
    
    return {'bank': '兴业银行', 'success': False}

def get_fallback_rate(currency):
    """备用方案：使用国际市场汇率API"""
    try:
        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{currency}', timeout=5)
        data = response.json()
        if data and data.get('rates', {}).get('CNY'):
            base_rate = data['rates']['CNY']
            return {
                'midRate': base_rate,
                'buyRate': round(base_rate * 0.992, 4),
                'sellRate': round(base_rate * 1.008, 4)
            }
    except Exception as e:
        print(f"备用API失败: {e}")
    
    return None

@app.route('/api/rates', methods=['GET'])
def get_rates():
    """API接口：获取所有银行汇率"""
    currency = request.args.get('currency', 'USD')
    trade_type = request.args.get('tradeType', 'buy')
    
    print(f"查询汇率: {currency} - {trade_type}")
    
    # 获取备用汇率
    fallback = get_fallback_rate(currency)
    
    if not fallback:
        return jsonify({'error': '无法获取汇率数据'}), 500
    
    # 尝试获取各银行汇率
    banks_data = []
    
    # 定义银行爬取函数和固定偏差
    banks_config = [
        {'func': get_boc_rate, 'name': '中国银行', 'icon': '中', 'offset': 0.002},
        {'func': get_icbc_rate, 'name': '中国工商银行', 'icon': '工', 'offset': -0.001},
        {'func': get_ccb_rate, 'name': '中国建设银行', 'icon': '建', 'offset': 0.003},
        {'func': get_abc_rate, 'name': '中国农业银行', 'icon': '农', 'offset': -0.002},
        {'func': get_comm_rate, 'name': '交通银行', 'icon': '交', 'offset': 0.001},
        {'func': get_cib_rate, 'name': '兴业银行', 'icon': '兴', 'offset': -0.003}
    ]
    
    for bank_config in banks_config:
        try:
            # 尝试获取真实银行数据
            print(f"\n正在爬取 {bank_config['name']} 的汇率...")
            bank_data = bank_config['func'](currency)
            
            if bank_data.get('success'):
                # 如果成功获取真实数据
                print(f"✓ {bank_config['name']} 爬取成功！")
                buy_rate = float(bank_data['buyRate'])
                sell_rate = float(bank_data['sellRate'])
            else:
                # 使用备用汇率加偏差
                print(f"✗ {bank_config['name']} 爬取失败，使用估算数据")
                base = fallback['midRate'] * (1 + bank_config['offset'])
                buy_rate = round(base * 0.992, 4)
                sell_rate = round(base * 1.008, 4)
            
            banks_data.append({
                'bank': bank_config['name'],
                'icon': bank_config['icon'],
                'buyRate': f"{buy_rate:.4f}",
                'sellRate': f"{sell_rate:.4f}",
                'spread': f"{((sell_rate - buy_rate) / buy_rate * 100):.2f}",
                'midRate': f"{((buy_rate + sell_rate) / 2):.4f}",
                'source': 'real' if bank_data.get('success') else 'estimated'
            })
        except Exception as e:
            print(f"{bank_config['name']} 处理失败: {e}")
            continue
    
    return jsonify({
        'success': True,
        'currency': currency,
        'tradeType': trade_type,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data': banks_data
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '服务运行正常'})

@app.route('/')
def index():
    """主页"""
    return '''
    <h1>银行汇率查询API服务</h1>
    <p>API接口：<code>GET /api/rates?currency=USD&tradeType=buy</code></p>
    <p>参数说明：</p>
    <ul>
        <li>currency: USD, EUR, HKD, JPY, KRW, MYR</li>
        <li>tradeType: buy(购汇), sell(结汇)</li>
    </ul>
    <p>示例：<a href="/api/rates?currency=USD&tradeType=buy">/api/rates?currency=USD&tradeType=buy</a></p>
    '''

if __name__ == '__main__':
    print('='*60)
    print('银行汇率查询后端服务启动中...')
    print('服务地址: http://localhost:5000')
    print('API接口: http://localhost:5000/api/rates?currency=USD&tradeType=buy')
    print('='*60)
    app.run(debug=True, host='0.0.0.0', port=5000)
