from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class FeatureLocation(BaseModel):
    """功能实现位置模型"""
    file: str
    function: str
    lines: str


class FeatureAnalysis(BaseModel):
    """功能分析结果模型"""
    feature_description: str
    implementation_location: List[FeatureLocation]


class AnalysisReport(BaseModel):
    """基础分析报告模型"""
    feature_analysis: List[FeatureAnalysis]
    execution_plan_suggestion: str


class VerificationResult(BaseModel):
    """功能验证结果模型"""
    generated_test_code: str
    execution_result: Dict[str, Any]


class FullReport(AnalysisReport):
    """包含功能验证的完整报告模型"""
    functional_verification: Optional[VerificationResult] = None


class CodeAnalysisRequest(BaseModel):
    """代码分析请求模型"""
    problem_description: str
    # code_zip 通过 multipart/form-data 上传，不在此处定义


class HealthStatus(BaseModel):
    """健康状态模型"""
    status: str
