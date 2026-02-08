"""API 服务器实现"""
import argparse
import json
from flask import Flask, request, jsonify, g
import sqlite3
from src.db.schema import init_db
from src.db.store import fetch_market_by_slug, fetch_market_by_token_id

app = Flask(__name__)
db_path = None


def get_db_connection():
    """获取数据库连接
    
    使用Flask的g对象为每个请求创建独立的数据库连接，避免线程安全问题
    """
    if 'db' not in g:
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db_connection(exception):
    """关闭数据库连接
    
    在请求结束时关闭数据库连接
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/markets/<slug>', methods=['GET'])
def get_market(slug):
    """获取市场信息
    
    Args:
        slug: 市场 slug
        
    Returns:
        JSON: 市场信息
    """
    db_conn = get_db_connection()
    market = fetch_market_by_slug(db_conn, slug)
    
    if not market:
        return jsonify({"error": "Market not found"}), 404
    
    # 构建响应
    response = {
        "market_id": market["id"],
        "slug": market["slug"],
        "condition_id": market["condition_id"],
        "question_id": market["question_id"],
        "oracle": market["oracle"],
        "collateral_token": market["collateral_token"],
        "yes_token_id": market["yes_token_id"],
        "no_token_id": market["no_token_id"],
        "status": market["status"]
    }
    
    return jsonify(response)


@app.route('/markets/<slug>/trades', methods=['GET'])
def get_market_trades(slug):
    """获取市场交易记录
    
    Args:
        slug: 市场 slug
        
    Returns:
        JSON: 交易记录列表
    """
    db_conn = get_db_connection()
    
    # 获取市场信息
    market = fetch_market_by_slug(db_conn, slug)
    if not market:
        return jsonify({"error": "Market not found"}), 404
    
    # 获取查询参数
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    cursor = request.args.get('cursor', 0, type=int)
    
    # 计算实际偏移量
    actual_offset = max(offset, cursor)
    
    # 查询交易记录
    cursor = db_conn.cursor()
    cursor.execute('''
    SELECT 
        id, tx_hash, log_index, maker, taker, side, outcome, 
        price, size, block_number, timestamp 
    FROM trades 
    WHERE market_id = ? 
    ORDER BY timestamp DESC 
    LIMIT ? OFFSET ?
    ''', (market["id"], limit, actual_offset))
    
    trades = []
    for row in cursor.fetchall():
        trade = {
            "trade_id": row[0],
            "tx_hash": row[1],
            "log_index": row[2],
            "maker": row[3],
            "taker": row[4],
            "side": row[5],
            "outcome": row[6],
            "price": row[7],
            "size": row[8],
            "block_number": row[9],
            "timestamp": row[10]
        }
        trades.append(trade)
    
    return jsonify(trades)


@app.route('/tokens/<token_id>/trades', methods=['GET'])
def get_token_trades(token_id):
    """按 TokenId 获取交易记录
    
    Args:
        token_id: 代币 ID
        
    Returns:
        JSON: 交易记录列表
    """
    db_conn = get_db_connection()
    
    # 通过 token_id 找到所属市场
    market = fetch_market_by_token_id(db_conn, token_id)
    if not market:
        return jsonify({"error": "Token not found in any market"}), 404
    
    # 获取查询参数
    limit = request.args.get('limit', 100, type=int)
    
    # 查询交易记录
    cursor = db_conn.cursor()
    cursor.execute('''
    SELECT 
        id, tx_hash, log_index, maker, taker, side, outcome, 
        price, size, block_number, timestamp 
    FROM trades 
    WHERE market_id = ? 
    ORDER BY timestamp DESC 
    LIMIT ?
    ''', (market["id"], limit))
    
    trades = []
    for row in cursor.fetchall():
        trade = {
            "trade_id": row[0],
            "tx_hash": row[1],
            "log_index": row[2],
            "maker": row[3],
            "taker": row[4],
            "side": row[5],
            "outcome": row[6],
            "price": row[7],
            "size": row[8],
            "block_number": row[9],
            "timestamp": row[10]
        }
        trades.append(trade)
    
    return jsonify(trades)


@app.route('/events/<slug>', methods=['GET'])
def get_event(slug):
    """获取事件信息
    
    Args:
        slug: 事件 slug
        
    Returns:
        JSON: 事件信息
    """
    db_conn = get_db_connection()
    
    # 查询事件信息
    cursor = db_conn.cursor()
    cursor.execute('SELECT id, slug, title, description, status, created_at FROM events WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    
    if not row:
        return jsonify({"error": "Event not found"}), 404
    
    # 构建响应
    response = {
        "id": row[0],
        "slug": row[1],
        "title": row[2],
        "description": row[3],
        "status": row[4],
        "created_at": row[5]
    }
    
    return jsonify(response)


@app.route('/events/<slug>/markets', methods=['GET'])
def get_event_markets(slug):
    """获取事件下的所有市场
    
    Args:
        slug: 事件 slug
        
    Returns:
        JSON: 市场列表
    """
    db_conn = get_db_connection()
    
    # 查询事件 ID
    cursor = db_conn.cursor()
    cursor.execute('SELECT id FROM events WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    
    if not row:
        return jsonify({"error": "Event not found"}), 404
    
    event_id = row[0]
    
    # 查询市场列表
    cursor.execute('''
    SELECT id, slug, condition_id, question_id, oracle, collateral_token, 
           yes_token_id, no_token_id, status, created_at 
    FROM markets 
    WHERE event_id = ?
    ''', (event_id,))
    
    markets = []
    for row in cursor.fetchall():
        market = {
            "id": row[0],
            "slug": row[1],
            "condition_id": row[2],
            "question_id": row[3],
            "oracle": row[4],
            "collateral_token": row[5],
            "yes_token_id": row[6],
            "no_token_id": row[7],
            "status": row[8],
            "created_at": row[9]
        }
        markets.append(market)
    
    return jsonify(markets)


def main():
    """主函数"""
    global db_path
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='./data/demo_indexer.db', help='数据库路径')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口')
    args = parser.parse_args()
    
    # 设置数据库路径
    db_path = args.db
    
    # 初始化数据库（创建表结构）
    temp_conn = sqlite3.connect(db_path)
    init_db(temp_conn)
    temp_conn.close()
    
    # 启动服务器
    app.run(debug=True, host='0.0.0.0', port=args.port)


if __name__ == '__main__':
    main()
