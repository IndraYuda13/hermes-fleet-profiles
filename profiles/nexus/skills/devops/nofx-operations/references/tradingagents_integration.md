# TradingAgents & 9router Integration Reference

## Overview
TradingAgents (`TauricResearch/TradingAgents`) is a multi-agent LLM financial trading framework (Fundamentals, Technical, Sentiment, News Analysts, Bull/Bear Researchers, Trader, Risk/Portfolio Managers).

## VPS Location & Virtual Environment
- Path: `/root/TradingAgents`
- Venv: `/root/TradingAgents/venv`
- Config: `/root/TradingAgents/.env`

## Integration with Local 9router
TradingAgents supports `openai_compatible` provider:

```python
import sys
sys.path.insert(0, "/root/TradingAgents")
from dotenv import load_dotenv
load_dotenv("/root/TradingAgents/.env")

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai_compatible"
config["backend_url"] = "http://localhost:20128/v1"
config["api_key"] = "sk-9router-local-key-2026"
config["model"] = "nofx"

ta = TradingAgentsGraph(config=config)
_, decision = ta.propagate("BTC-USD", "2026-08-10")
```

## Architectural Separation
- **TradingAgents:** Analysis & decision engine only (no direct live exchange order placement).
- **NOFX / Exchange REST:** Execution engine that takes TradingAgents output and places actual trades.
