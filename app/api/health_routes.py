from fastapi import APIRouter
from app.schemas.schemas import HealthStatus

router = APIRouter()


@router.get("/", tags=["系统"])
async def root():
    """
    API根路径
    
    返回API的基本信息和可用端点
    """
    return {
        "message": "代码分析AI Agent API",
        "version": "1.0.0",
        "description": "接收代码和需求，分析代码功能并生成结构化报告的API服务",
        "endpoints": {
            "analyze": "/analyze - 分析代码并生成报告",
            "analyze_with_verification": "/analyze-with-verification - 分析代码并执行功能验证",
            "health": "/health - 健康检查"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@router.get("/health", response_model=HealthStatus, tags=["系统"])
async def health_check():
    """
    健康检查端点
    
    用于监控服务的运行状态
    """
    return HealthStatus(status="healthy")
