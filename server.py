#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码分析AI Agent 服务入口文件
负责启动FastAPI应用服务器
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加当前目录到Python路径，确保可以导入app模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger.info("正在启动代码分析AI Agent服务...")

# 导入FastAPI应用实例
from app.main import app

if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    reload = os.getenv("APP_RELOAD", "false").lower() == "true"
    
    logger.info(f"服务配置: host={host}, port={port}, reload={reload}")
    
    # 启动uvicorn服务器
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level.lower()
        )
    except Exception as e:
        logger.error(f"启动服务失败: {str(e)}")
        raise