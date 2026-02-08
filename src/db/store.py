"""数据访问层函数"""
import sqlite3
from datetime import datetime


def upsert_event(conn, event_data):
    """插入或更新事件信息
    
    Args:
        conn: 数据库连接
        event_data: 事件数据字典
    """
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute('''
    INSERT INTO events (slug, title, description, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT (slug) DO UPDATE SET
        title = excluded.title,
        description = excluded.description,
        status = excluded.status,
        updated_at = ?
    ''', (
        event_data.get('slug'),
        event_data.get('title'),
        event_data.get('description'),
        event_data.get('status', 'active'),
        now,
        now,
        now
    ))
    
    conn.commit()


def upsert_market(conn, market_data):
    """插入或更新市场信息
    
    Args:
        conn: 数据库连接
        market_data: 市场数据字典
    """
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    # 先获取事件 ID
    event_slug = market_data.get('event_slug')
    event_id = None
    if event_slug:
        cursor.execute('SELECT id FROM events WHERE slug = ?', (event_slug,))
        result = cursor.fetchone()
        if result:
            event_id = result[0]
    
    cursor.execute('''
    INSERT INTO markets (
        event_id, slug, condition_id, question_id, oracle, collateral_token,
        yes_token_id, no_token_id, enable_neg_risk, status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT (condition_id) DO UPDATE SET
        event_id = excluded.event_id,
        slug = excluded.slug,
        question_id = excluded.question_id,
        oracle = excluded.oracle,
        collateral_token = excluded.collateral_token,
        yes_token_id = excluded.yes_token_id,
        no_token_id = excluded.no_token_id,
        enable_neg_risk = excluded.enable_neg_risk,
        status = excluded.status,
        updated_at = ?
    ''', (
        event_id,
        market_data.get('slug'),
        market_data.get('condition_id'),
        market_data.get('question_id'),
        market_data.get('oracle'),
        market_data.get('collateral_token'),
        market_data.get('yes_token_id'),
        market_data.get('no_token_id'),
        market_data.get('enable_neg_risk', False),
        market_data.get('status', 'active'),
        now,
        now,
        now
    ))
    
    conn.commit()


def fetch_market_by_slug(conn, slug):
    """通过 slug 获取市场信息
    
    Args:
        conn: 数据库连接
        slug: 市场 slug
        
    Returns:
        dict: 市场信息字典
    """
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM markets WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    
    if not row:
        return None
    
    return {
        'id': row[0],
        'event_id': row[1],
        'slug': row[2],
        'condition_id': row[3],
        'question_id': row[4],
        'oracle': row[5],
        'collateral_token': row[6],
        'yes_token_id': row[7],
        'no_token_id': row[8],
        'enable_neg_risk': row[9],
        'status': row[10],
        'created_at': row[11],
        'updated_at': row[12]
    }


def fetch_market_by_condition_id(conn, condition_id):
    """通过 condition_id 获取市场信息
    
    Args:
        conn: 数据库连接
        condition_id: 条件 ID
        
    Returns:
        dict: 市场信息字典
    """
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM markets WHERE condition_id = ?', (condition_id,))
    row = cursor.fetchone()
    
    if not row:
        return None
    
    return {
        'id': row[0],
        'event_id': row[1],
        'slug': row[2],
        'condition_id': row[3],
        'question_id': row[4],
        'oracle': row[5],
        'collateral_token': row[6],
        'yes_token_id': row[7],
        'no_token_id': row[8],
        'enable_neg_risk': row[9],
        'status': row[10],
        'created_at': row[11],
        'updated_at': row[12]
    }


def fetch_market_by_token_id(conn, token_id):
    """通过 token_id 获取市场信息
    
    Args:
        conn: 数据库连接
        token_id: 代币 ID
        
    Returns:
        dict: 市场信息字典
    """
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM markets WHERE yes_token_id = ? OR no_token_id = ?
    ''', (token_id, token_id))
    row = cursor.fetchone()
    
    if not row:
        return None
    
    return {
        'id': row[0],
        'event_id': row[1],
        'slug': row[2],
        'condition_id': row[3],
        'question_id': row[4],
        'oracle': row[5],
        'collateral_token': row[6],
        'yes_token_id': row[7],
        'no_token_id': row[8],
        'enable_neg_risk': row[9],
        'status': row[10],
        'created_at': row[11],
        'updated_at': row[12]
    }


def get_sync_state(conn, key='global_indexer'):
    """获取同步状态
    
    Args:
        conn: 数据库连接
        key: 状态键名
        
    Returns:
        dict: 同步状态字典
    """
    cursor = conn.cursor()
    cursor.execute('SELECT last_block, updated_at FROM sync_state WHERE key = ?', (key,))
    row = cursor.fetchone()
    
    if not row:
        return {'last_block': 0, 'updated_at': None}
    
    return {
        'last_block': row[0],
        'updated_at': row[1]
    }


def update_sync_state(conn, last_block, key='global_indexer'):
    """更新同步状态
    
    Args:
        conn: 数据库连接
        last_block: 最后处理的区块高度
        key: 状态键名
    """
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute('''
    INSERT INTO sync_state (key, last_block, updated_at)
    VALUES (?, ?, ?)
    ON CONFLICT (key) DO UPDATE SET
        last_block = excluded.last_block,
        updated_at = ?
    ''', (key, last_block, now, now))
    
    conn.commit()