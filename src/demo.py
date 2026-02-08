"""演示脚本"""
import argparse
import json
import sqlite3
from web3 import Web3
from dotenv import load_dotenv
import os
from src.db.schema import init_db
from src.indexer.run import run_indexer


def main():
    """主函数"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--tx-hash', help='交易哈希')
    parser.add_argument('--event-slug', help='事件 slug')
    parser.add_argument('--reset-db', action='store_true', help='重置数据库')
    parser.add_argument('--db', default='./data/demo_indexer.db', help='数据库路径')
    parser.add_argument('--output', default='./data/demo_output.json', help='输出文件路径')
    parser.add_argument('--from-block', type=int, default=66000000, help='起始区块')
    parser.add_argument('--to-block', type=int, default=66000000, help='结束区块')
    args = parser.parse_args()
    
    # 加载环境变量
    load_dotenv()
    
    # 连接到 Web3
    rpc_url = os.getenv('RPC_URL')
    if not rpc_url:
        raise ValueError('RPC_URL not set in .env file')
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # 初始化数据库
    if args.reset_db:
        if os.path.exists(args.db):
            os.remove(args.db)
    conn = init_db(args.db)
    
    # 运行索引器
    settings = {}
    results = run_indexer(
        w3=w3,
        conn=conn,
        settings=settings,
        from_block=args.from_block,
        to_block=args.to_block,
        event_slug=args.event_slug
    )
    
    # 构建输出结果
    output = {
        'stage2': {
            'from_block': args.from_block,
            'to_block': args.to_block,
            'inserted_trades': results['trades_indexer']['inserted_trades'],
            'market_slug': args.event_slug,
            'market_count': results['market_discovery']['market_count'],
            'db_path': args.db
        }
    }
    
    # 输出结果
    output_json = json.dumps(output, indent=2, ensure_ascii=False)
    
    if args.output:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        
        # 写入文件
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"演示结果已保存到: {args.output}")
    else:
        print(output_json)
    
    # 关闭数据库连接
    conn.close()


if __name__ == '__main__':
    main()