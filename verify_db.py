import sqlite3

# 连接到数据库
conn = sqlite3.connect('./data/demo_indexer.db')
cursor = conn.cursor()

# 查询市场数据
print("=== 市场数据 ===")
cursor.execute('SELECT id, slug, condition_id, yes_token_id, no_token_id FROM markets LIMIT 10;')
for row in cursor.fetchall():
    print(f"ID: {row[0]}")
    print(f"Slug: {row[1]}")
    print(f"Condition ID: {row[2]}")
    print(f"YES Token ID: {row[3]}")
    print(f"NO Token ID: {row[4]}")
    print("---")

# 查询事件数据
print("\n=== 事件数据 ===")
cursor.execute('SELECT id, slug, title, status FROM events LIMIT 10;')
for row in cursor.fetchall():
    print(f"ID: {row[0]}")
    print(f"Slug: {row[1]}")
    print(f"Title: {row[2]}")
    print(f"Status: {row[3]}")
    print("---")

# 查询同步状态
print("\n=== 同步状态 ===")
cursor.execute('SELECT key, last_block, updated_at FROM sync_state;')
for row in cursor.fetchall():
    print(f"Key: {row[0]}")
    print(f"Last Block: {row[1]}")
    print(f"Updated At: {row[2]}")
    print("---")

# 关闭连接
conn.close()