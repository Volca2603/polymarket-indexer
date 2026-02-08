"""市场发现服务"""
import requests
from datetime import datetime
from src.db.store import upsert_event, upsert_market


class MarketDiscoveryService:
    """市场发现服务类"""
    
    def __init__(self):
        """初始化市场发现服务"""
        self.gamma_api_base = "https://gamma-api.polymarket.com"
    
    def get_markets_by_event_slug(self, event_slug):
        """通过事件 slug 获取市场列表
        
        Args:
            event_slug: 事件 slug
            
        Returns:
            list: 市场列表
        """
        # 使用正确的 API 端点格式
        url = f"{self.gamma_api_base}/events?slug={event_slug}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            events = response.json()
            
            # 检查响应是否为空
            if not events:
                print(f"No events found for slug '{event_slug}'")
                return []
            
            # 获取第一个事件（通常只有一个）
            event = events[0]
            
            # 检查是否有 markets 字段
            if "markets" not in event or not event["markets"]:
                print(f"No markets found for event with slug '{event_slug}'")
                return []
            
            # 获取市场列表
            markets = event["markets"]
            print(f"成功从 {url} 获取 {len(markets)} 个市场")
            return markets
            
        except requests.RequestException as e:
            print(f"Failed to fetch markets for event {event_slug}: {str(e)}")
            return []
        except (IndexError, KeyError) as e:
            print(f"Invalid API response structure: {str(e)}")
            return []
    
    def get_all_markets(self):
        """获取所有市场
        
        Returns:
            list: 市场列表
        """
        url = f"{self.gamma_api_base}/markets"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            markets = response.json()
            
            return markets
            
        except requests.RequestException as e:
            print(f"Failed to fetch all markets: {str(e)}")
            return []
    
    def discover_markets(self, conn, event_slug=None):
        """发现市场并存储
        
        Args:
            conn: 数据库连接
            event_slug: 事件 slug，如果为 None 则获取所有市场
            
        Returns:
            int: 发现的市场数量
        """
        if event_slug:
            # 获取指定事件的市场
            markets = self.get_markets_by_event_slug(event_slug)
            
            # 获取事件信息
            event_info = self._get_event_info(event_slug)
            if event_info:
                upsert_event(conn, event_info)
        else:
            # 获取所有市场
            markets = self.get_all_markets()
        
        # 处理每个市场
        market_count = 0
        for market in markets:
            try:
                market_data = self._parse_market_data(market, event_slug)
                if market_data:
                    # 添加调试输出
                    print(f"发现市场: {market_data.get('slug')}")
                    print(f"Condition ID: {market_data.get('condition_id')}")
                    print(f"YES Token: {market_data.get('yes_token_id')}")
                    print(f"NO Token: {market_data.get('no_token_id')}")
                    print("---")
                    
                    upsert_market(conn, market_data)
                    market_count += 1
            except Exception as e:
                print(f"Error processing market {market.get('slug', 'unknown')}: {str(e)}")
                continue
        
        return market_count
    
    def _get_event_info(self, event_slug):
        """获取事件信息
        
        Args:
            event_slug: 事件 slug
            
        Returns:
            dict: 事件信息字典
        """
        url = f"{self.gamma_api_base}/events/{event_slug}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            event = response.json()
            
            return {
                'slug': event.get('slug'),
                'title': event.get('title'),
                'description': event.get('description'),
                'status': event.get('status', 'active'),
                'created_at': event.get('createdAt') or datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            print(f"Failed to fetch event info for {event_slug}: {str(e)}")
            return None
    
    def _parse_market_data(self, market, event_slug=None):
        """解析市场数据
        
        Args:
            market: 市场数据
            event_slug: 事件 slug
            
        Returns:
            dict: 解析后的市场数据字典
        """
        import json
        
        # 提取基本信息
        market_slug = market.get('slug')
        condition_id = market.get('conditionId')
        question_id = market.get('questionId') or market.get('questionID')
        oracle_address = market.get('oracleAddress') or market.get('oracle')
        collateral_token = market.get('collateralToken', '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')  # 默认 USDC 地址
        clob_token_ids = market.get('clobTokenIds')
        
        # 提取 YES/NO 代币 ID
        yes_token_id = None
        no_token_id = None
        
        if isinstance(clob_token_ids, str):
            # 处理字符串格式的 JSON 数组
            try:
                clob_token_ids = json.loads(clob_token_ids)
                print(f"成功解析 clobTokenIds: {clob_token_ids}")
            except json.JSONDecodeError as e:
                print(f"Failed to decode clobTokenIds: {str(e)}")
                clob_token_ids = None
        
        if isinstance(clob_token_ids, list) and len(clob_token_ids) >= 2:
            yes_token_id = clob_token_ids[0]
            no_token_id = clob_token_ids[1]
        
        # 提取市场状态
        status = market.get('status', 'active')
        
        # 构建市场数据字典
        market_data = {
            'slug': market_slug,
            'condition_id': condition_id,
            'question_id': question_id,
            'oracle': oracle_address,
            'collateral_token': collateral_token,
            'yes_token_id': yes_token_id,
            'no_token_id': no_token_id,
            'status': status,
            'event_slug': event_slug
        }
        
        return market_data