"""索引器核心实现"""
from web3 import Web3
from src.indexer.market_discovery import MarketDiscoveryService
from src.indexer.trades_indexer import TradesIndexer


def run_market_discovery(conn, event_slug=None):
    """运行市场发现服务
    
    Args:
        conn: 数据库连接
        event_slug: 事件 slug，如果为 None 则获取所有市场
        
    Returns:
        dict: 运行结果
    """
    discovery_service = MarketDiscoveryService()
    
    # 发现市场
    market_count = discovery_service.discover_markets(conn, event_slug)
    
    return {
        'market_count': market_count,
        'event_slug': event_slug
    }


def run_indexer(
    w3,
    conn,
    settings,
    from_block,
    to_block,
    exchange_address=None,
    neg_risk_exchange=None,
    ctf_address=None,
    exchange_abi=None,
    ctf_abi=None,
    include_ctf=False,
    include_exchange=True,
    include_neg_risk=True,
    event_slug=None
):
    """运行完整索引器
    
    Args:
        w3: Web3 实例
        conn: 数据库连接
        settings: 设置字典
        from_block: 起始区块
        to_block: 结束区块
        exchange_address: 交易所合约地址
        neg_risk_exchange: 负风险交易所合约地址
        ctf_address: CTF 合约地址
        exchange_abi: 交易所合约 ABI
        ctf_abi: CTF 合约 ABI
        include_ctf: 是否包含 CTF 合约
        include_exchange: 是否包含交易所合约
        include_neg_risk: 是否包含负风险交易所合约
        event_slug: 事件 slug
        
    Returns:
        dict: 运行结果
    """
    # 首先运行市场发现
    market_results = run_market_discovery(conn, event_slug)
    
    # 运行交易索引器
    trades_indexer = TradesIndexer(w3)
    trade_results = trades_indexer.run_indexer(conn, from_block, to_block)
    
    # 合并结果
    results = {
        'market_discovery': market_results,
        'trades_indexer': trade_results,
        'event_slug': event_slug
    }
    
    return results
