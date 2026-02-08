# Polymarket 索引器
<img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python"/> <img src="https://img.shields.io/badge/Flask-2.0+-green.svg" alt="Flask"/> <img src="https://img.shields.io/badge/SQLite-3.0+-lightgrey.svg" alt="SQLite"/> <img src="https://img.shields.io/badge/Web3.py-6.0+-yellow.svg" alt="Web3.py"/> <img src="https://img.shields.io/badge/Polygon-Mainnet-orange.svg" alt="Polygonscan"/>

Polymarket 索引器是一个用于索引和查询 Polymarket 交易数据的系统，支持从 Gamma API 获取市场信息，扫描区块链上的交易事件，并提供 RESTful API 接口进行数据查询。

## 功能特性
- 市场发现 ：从 Gamma API 获取市场信息并存储到数据库
- 交易索引 ：扫描指定区块范围的 OrderFilled 事件并解析交易数据
- 数据存储 ：使用 SQLite 数据库持久化存储市场和交易数据
- API 服务 ：提供 RESTful API 接口，支持市场和交易数据查询
- 分页支持 ：API 支持分页查询，提高数据获取效率
- 幂等性 ：重复插入相同交易不会产生重复数据
- 同步状态 ：记录最后处理的区块高度，支持断点续扫

```
polymarketIndexer/
├── src/
│   ├── api/
│   │   └── server.py          # API 服务器实现
│   ├── db/
│   │   ├── schema.py          # 数据库模式定义
│   │   └── store.py           # 数据访问层函数
│   ├── indexer/
│   │   ├── market_discovery.py # 市场发现服务
│   │   ├── trades_indexer.py   # 交易索引器
│   │   └── run.py              # 索引器核心实现
│   ├── demo.py                 # 演示脚本
│   └── __init__.py
├── data/                       # 数据存储目录
├── .env                        # 环境变量配置
├── requirements.txt            # 依赖包列表
└── README.md                   # 项目说明文档
```

## 技术栈
- Python 3.8+ ：主要开发语言
- Flask ：API 服务器框架
- SQLite ：轻量级数据库
- Web3.py ：以太坊区块链交互
- Requests ：HTTP 请求库
- python-dotenv ：环境变量管理

## 安装步骤
1. 克隆项目
   
   ```
   git clone <repository-url>
   cd polymarketIndexer
   ```
2. 创建虚拟环境
   
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   # 或
   source venv/bin/activate  # Linux/
   Mac
   ```
3. 安装依赖
   
   ```
   pip install -r requirements.txt
   ```
4. 配置环境变量
   
   在 .env 文件中添加以下内容：
   
   ```
   RPC_URL=https://polygon-mainnet.g.
   alchemy.com/v2/YOUR_ALCHEMY_API_KEY
   ```
## 使用方法
### 1. 运行市场发现服务
使用 demo.py 脚本运行市场发现服务，从 Gamma API 获取市场信息并存储到数据库：

```
python -m src.demo --event-slug 
will-there-be-another-us-government-sh
utdown-by-january-31 --db ./data/test.
db --from-block 66000000 --to-block 
66000000
```
### 2. 启动 API 服务器
```
python -m src.api.server --db ./data/
test.db --port 8000
```


## API 文档
### 市场信息端点
- 端点 ： GET /markets/{slug}
- 描述 ：获取指定市场的详细信息
- 参数 ：
  - slug ：市场的唯一标识符（路径参数）
- 响应 ：市场信息 JSON 对象
### 市场交易记录端点
- 端点 ： GET /markets/{slug}/trades
- 描述 ：获取指定市场的交易记录
- 参数 ：
  - slug ：市场的唯一标识符（路径参数）
  - limit ：返回的交易记录数量限制（查询参数，默认 100）
  - offset ：分页偏移量（查询参数，默认 0）
  - cursor ：游标（查询参数，默认 0）
- 响应 ：交易记录 JSON 数组
### 代币交易记录端点
- 端点 ： GET /tokens/{token_id}/trades
- 描述 ：获取指定代币的交易记录
- 参数 ：
  - token_id ：代币的唯一标识符（路径参数）
  - limit ：返回的交易记录数量限制（查询参数，默认 100）
- 响应 ：交易记录 JSON 数组
### 事件信息端点
- 端点 ： GET /events/{slug}
- 描述 ：获取指定事件的详细信息
- 参数 ：
  - slug ：事件的唯一标识符（路径参数）
- 响应 ：事件信息 JSON 对象
### 事件市场列表端点
- 端点 ： GET /events/{slug}/markets
- 描述 ：获取指定事件下的所有市场
- 参数 ：
  - slug ：事件的唯一标识符（路径参数）
- 响应 ：市场列表 JSON 数组
## 数据库结构
### 1. events 表
- id ：事件 ID（主键）
- slug ：事件 slug（唯一）
- title ：事件标题
- description ：事件描述
- status ：事件状态
- created_at ：创建时间
- updated_at ：更新时间
### 2. markets 表
- id ：市场 ID（主键）
- event_id ：事件 ID（外键）
- slug ：市场 slug
- condition_id ：条件 ID（唯一）
- question_id ：问题 ID
- oracle ：预言机地址
- collateral_token ：抵押代币地址
- yes_token_id ：YES 代币 ID
- no_token_id ：NO 代币 ID
- enable_neg_risk ：是否启用负风险
- status ：市场状态
- created_at ：创建时间
- updated_at ：更新时间
### 3. trades 表
- id ：交易 ID（主键）
- market_id ：市场 ID（外键）
- tx_hash ：交易哈希
- log_index ：日志索引
- maker ：做市商地址
- taker ：交易对手地址
- side ：交易方向
- outcome ：结果（YES/NO）
- price ：价格
- size ：数量
- block_number ：区块高度
- timestamp ：时间戳
- created_at ：创建时间
- UNIQUE (tx_hash, log_index) ：确保交易唯一性
### 4. sync_state 表
- key ：状态键（主键）
- last_block ：最后处理的区块高度
- updated_at ：更新时间

## 许可证
MIT License