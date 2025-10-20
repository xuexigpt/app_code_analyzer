#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证脚本：用于测试重构后的项目结构是否正常工作
"""

import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_module_imports():
    """检查所有模块是否可以正常导入"""
    logger.info("开始检查模块导入...")
    
    # 检查核心模块
    modules_to_check = [
        'app.main',
        'app.api.analysis_routes',
        'app.api.health_routes',
        'app.core.code_analyzer',
        'app.schemas.schemas',
        'app.utils.file_utils'
    ]
    
    success_count = 0
    failure_count = 0
    
    for module_name in modules_to_check:
        try:
            # 尝试导入模块
            __import__(module_name)
            logger.info(f"✓ 成功导入模块: {module_name}")
            success_count += 1
        except ImportError as e:
            logger.error(f"✗ 导入模块失败: {module_name} - {str(e)}")
            failure_count += 1
        except Exception as e:
            logger.error(f"✗ 导入模块时发生错误: {module_name} - {str(e)}")
            failure_count += 1
    
    logger.info(f"模块导入检查完成: 成功 {success_count}, 失败 {failure_count}")
    return failure_count == 0

def check_directory_structure():
    """检查目录结构是否符合预期"""
    logger.info("开始检查目录结构...")
    
    expected_structure = [
        'app/',
        'app/__init__.py',
        'app/api/',
        'app/api/__init__.py',
        'app/api/analysis_routes.py',
        'app/api/health_routes.py',
        'app/core/',
        'app/core/__init__.py',
        'app/core/code_analyzer.py',
        'app/schemas/',
        'app/schemas/__init__.py',
        'app/schemas/schemas.py',
        'app/utils/',
        'app/utils/__init__.py',
        'app/utils/file_utils.py',
        'server.py',
        'requirements.txt',
        'Dockerfile',
        '.env',
        'README.md'
    ]
    
    success_count = 0
    missing_count = 0
    
    for path in expected_structure:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
        if os.path.exists(full_path):
            logger.info(f"✓ 存在: {path}")
            success_count += 1
        else:
            logger.warning(f"✗ 缺失: {path}")
            missing_count += 1
    
    logger.info(f"目录结构检查完成: 存在 {success_count}, 缺失 {missing_count}")
    return missing_count == 0

def check_entry_point():
    """检查入口文件是否存在且可执行"""
    logger.info("开始检查入口文件...")
    
    entry_point = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.py')
    if os.path.isfile(entry_point):
        # 检查文件是否有执行权限（Windows可能忽略此检查）
        if os.access(entry_point, os.X_OK) or os.name == 'nt':
            logger.info(f"✓ 入口文件检查通过: {entry_point}")
            return True
        else:
            logger.warning(f"⚠ 入口文件存在但可能没有执行权限: {entry_point}")
            return True  # Windows上允许继续
    else:
        logger.error(f"✗ 入口文件不存在: {entry_point}")
        return False

def main():
    """主验证函数"""
    logger.info("开始验证项目结构...")
    
    # 添加当前目录到Python路径，确保可以导入app模块
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    all_checks_passed = True
    
    # 运行各项检查
    checks = [
        ("目录结构", check_directory_structure),
        ("入口文件", check_entry_point),
        ("模块导入", check_module_imports)
    ]
    
    for check_name, check_func in checks:
        logger.info(f"\n=== 执行检查: {check_name} ===")
        if not check_func():
            all_checks_passed = False
    
    # 输出总体结果
    logger.info("\n" + "="*50)
    if all_checks_passed:
        logger.info("🎉 项目结构验证通过！所有检查项都已通过")
        logger.info("可以使用以下命令启动服务:")
        logger.info("  python server.py")
        logger.info("或使用Docker启动:")
        logger.info("  docker build -t code-analysis-agent .")
        logger.info("  docker run -p 8000:8000 code-analysis-agent")
        return 0
    else:
        logger.error("❌ 项目结构验证失败！请修复上述问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())