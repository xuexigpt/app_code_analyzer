from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from app.core.code_analyzer import CodeAnalyzer
from app.schemas.schemas import AnalysisReport, FullReport
from app.utils.file_utils import (
    extract_zip_file, 
    save_uploaded_file, 
    create_temp_directory, 
    cleanup_temp_directory,
    validate_file_extension
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalysisReport, tags=["分析"])
async def analyze_code(
    background_tasks: BackgroundTasks,
    problem_description: str = Form(..., description="项目功能需求描述"),
    code_zip: UploadFile = File(..., description="包含完整源代码的ZIP文件")
):
    """
    分析代码并生成结构化报告
    
    - **problem_description**: 项目功能需求的自然语言描述
    - **code_zip**: 包含完整项目源代码的ZIP压缩文件
    """
    # 验证上传文件类型
    if not validate_file_extension(code_zip.filename, ['zip']):
        raise HTTPException(status_code=400, detail="只支持上传ZIP格式的文件")
    
    # 创建临时目录
    temp_dir = create_temp_directory()
    # 确保在请求完成后清理临时目录
    background_tasks.add_task(cleanup_temp_directory, temp_dir)
    
    # 保存上传的ZIP文件
    zip_path = f"{temp_dir}/{code_zip.filename}"
    save_uploaded_file(code_zip.file, zip_path)
    
    # 解压文件
    extract_dir = f"{temp_dir}/extracted"
    try:
        extract_zip_file(zip_path, extract_dir)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="无效的ZIP文件")
    except Exception as e:
        logger.error(f"解压文件时发生错误: {e}")
        raise HTTPException(status_code=500, detail="处理ZIP文件时发生错误")
    
    # 分析代码
    try:
        logger.info(f"开始分析代码，需求描述: {problem_description[:50]}...")
        analyzer = CodeAnalyzer(extract_dir, problem_description)
        feature_analysis = analyzer.analyze_features()
        execution_plan = analyzer.suggest_execution_plan()
        
        # 构建报告
        report = {
            "feature_analysis": feature_analysis,
            "execution_plan_suggestion": execution_plan
        }
        
        logger.info("代码分析完成，生成报告成功")
        return JSONResponse(content=report)
        
    except Exception as e:
        logger.error(f"分析代码时发生错误: {e}")
        raise HTTPException(status_code=500, detail="分析代码时发生错误")


@router.post("/analyze-with-verification", response_model=FullReport, tags=["分析"])
async def analyze_with_verification(
    background_tasks: BackgroundTasks,
    problem_description: str = Form(..., description="项目功能需求描述"),
    code_zip: UploadFile = File(..., description="包含完整源代码的ZIP文件")
):
    """
    分析代码并执行功能验证
    
    - **problem_description**: 项目功能需求的自然语言描述
    - **code_zip**: 包含完整项目源代码的ZIP压缩文件
    """
    # 首先执行基本分析
    # 注意：这里我们不能直接调用上面的函数，因为FastAPI不允许在路由处理函数中调用另一个路由处理函数
    # 我们需要重新实现相似的逻辑，但添加验证部分
    
    # 验证上传文件类型
    if not validate_file_extension(code_zip.filename, ['zip']):
        raise HTTPException(status_code=400, detail="只支持上传ZIP格式的文件")
    
    # 创建临时目录
    temp_dir = create_temp_directory()
    background_tasks.add_task(cleanup_temp_directory, temp_dir)
    
    # 保存上传的ZIP文件
    zip_path = f"{temp_dir}/{code_zip.filename}"
    save_uploaded_file(code_zip.file, zip_path)
    
    # 解压文件
    extract_dir = f"{temp_dir}/extracted"
    try:
        extract_zip_file(zip_path, extract_dir)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="无效的ZIP文件")
    except Exception as e:
        logger.error(f"解压文件时发生错误: {e}")
        raise HTTPException(status_code=500, detail="处理ZIP文件时发生错误")
    
    # 分析代码并生成验证结果
    try:
        logger.info(f"开始分析代码并进行功能验证，需求描述: {problem_description[:50]}...")
        analyzer = CodeAnalyzer(extract_dir, problem_description)
        
        # 基本分析
        feature_analysis = analyzer.analyze_features()
        execution_plan = analyzer.suggest_execution_plan()
        
        # 生成验证信息
        generated_test_code = analyzer.generate_test_code()
        execution_result = analyzer.verify_functionality()
        
        # 构建完整报告
        report = {
            "feature_analysis": feature_analysis,
            "execution_plan_suggestion": execution_plan,
            "functional_verification": {
                "generated_test_code": generated_test_code,
                "execution_result": execution_result
            }
        }
        
        logger.info("代码分析和功能验证完成，生成完整报告成功")
        return JSONResponse(content=report)
        
    except Exception as e:
        logger.error(f"分析代码或执行验证时发生错误: {e}")
        raise HTTPException(status_code=500, detail="分析代码或执行验证时发生错误")


# 导入zipfile模块，这里需要在函数内部使用，但需要在模块级别导入
import zipfile
