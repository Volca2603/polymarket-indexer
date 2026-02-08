"""数据库模式定义"""
import sqlite3


def init_db(db_path_or_conn):
    """初始化数据库表结构
    
    Args:
        db_path_or_conn: 数据库文件路径或已存在的数据库连接
        
    Returns:
        sqlite3.Connection: 数据库连接
    """
    # 检查是否是数据库连接对象
    if hasattr(db_path_or_conn, 'cursor'):
        conn = db_path_or_conn
    else:
        conn = sqlite3.connect(db_path_or_conn)
    cursor = conn.cursor()
    
    # 创建事件表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        slug TEXT UNIQUE,
        title TEXT,
        description TEXT,
        status TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')
    
    # 创建市场表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY,
        event_id INTEGER,
        slug TEXT,
        condition_id TEXT UNIQUE,
        question_id TEXT,
        oracle TEXT,
        collateral_token TEXT,
        yes_token_id TEXT,
        no_token_id TEXT,
        enable_neg_risk BOOLEAN,
        status TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    ''')
    
    # 创建交易表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY,
        market_id INTEGER,
        tx_hash TEXT,
        log_index INTEGER,
        maker TEXT,
        taker TEXT,
        side TEXT,
        outcome TEXT,
        price DECIMAL,
        size DECIMAL,
        block_number INTEGER,
        timestamp TIMESTAMP,
        created_at TIMESTAMP,
        FOREIGN KEY (market_id) REFERENCES markets (id),
        UNIQUE (tx_hash, log_index)
    )
    ''')
    
    # 创建同步状态表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sync_state (
        key TEXT PRIMARY KEY,
        last_block INTEGER,
        updated_at TIMESTAMP
    )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_markets_event_id ON markets (event_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_markets_slug ON markets (slug)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_market_id ON trades (market_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades (timestamp)')
    
    conn.commit()
    return conn