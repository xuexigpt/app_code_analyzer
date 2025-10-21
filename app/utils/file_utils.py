import os
import tempfile
import zipfile
import shutil
import logging
from typing import BinaryIO

logger = logging.getLogger(__name__)


def extract_zip_file(zip_file: BinaryIO, output_dir: str) -> None:
    """
    解压ZIP文件到指定目录
    
    Args:
        zip_file: ZIP文件的二进制流
        output_dir: 输出目录路径
    
    Raises:
        zipfile.BadZipFile: 如果ZIP文件无效
    """
    logger.info(f"正在解压ZIP文件到目录: {output_dir}")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 解压文件
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # 获取所有文件列表
            file_list = zip_ref.namelist()
            logger.info(f"ZIP文件包含 {len(file_list)} 个文件")
            
            # 解压所有文件
            zip_ref.extractall(output_dir)
            logger.info(f"ZIP文件解压完成，输出目录: {output_dir}")
    except zipfile.BadZipFile:
        logger.error("无效的ZIP文件格式")
        raise
    except Exception as e:
        logger.error(f"解压ZIP文件时出错: {e}")
        raise


def save_uploaded_file(file: BinaryIO, save_path: str) -> None:
    """
    保存上传的文件到指定路径
    
    Args:
        file: 上传的文件对象
        save_path: 保存路径
    """
    logger.info(f"正在保存上传的文件到: {save_path}")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file, buffer)
        logger.info(f"文件保存成功: {save_path}")
    except Exception as e:
        logger.error(f"保存文件时出错: {e}")
        raise


def create_temp_directory() -> str:
    """
    创建临时目录
    
    Returns:
        临时目录路径
    """
    temp_dir = tempfile.mkdtemp(prefix="code_analysis_")
    logger.info(f"创建临时目录: {temp_dir}")
    return temp_dir


def cleanup_temp_directory(temp_dir: str) -> None:
    """
    清理临时目录
    
    Args:
        temp_dir: 临时目录路径
    """
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            logger.info(f"清理临时目录: {temp_dir}")
        except Exception as e:
            logger.error(f"清理临时目录时出错: {e}")


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    验证文件扩展名是否允许
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表（不包含点号）
    
    Returns:
        是否允许的文件类型
    """
    extension = filename.split('.')[-1].lower()
    is_allowed = extension in allowed_extensions
    logger.debug(f"验证文件 '{filename}' 扩展名: {extension}, 是否允许: {is_allowed}")
    return is_allowed


def get_file_size(file_path: str) -> int:
    """
    获取文件大小（字节）
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件大小（字节）
    """
    return os.path.getsize(file_path)


def find_project_root(directory: str, marker_files: list = None) -> str:
    """
    查找项目根目录
    
    Args:
        directory: 起始目录
        marker_files: 标识根目录的文件列表，如 ['package.json', 'setup.py', 'requirements.txt']
    
    Returns:
        项目根目录路径，如果未找到则返回原始目录
    """
    if marker_files is None:
        marker_files = ['package.json', 'setup.py', 'requirements.txt', 'pom.xml', 'csproj']
    
    current_dir = directory
    while current_dir != os.path.dirname(current_dir):  # 直到到达文件系统根目录
        for marker in marker_files:
            if os.path.exists(os.path.join(current_dir, marker)):
                logger.info(f"找到项目根目录: {current_dir} (包含标记文件 {marker})")
                return current_dir
        current_dir = os.path.dirname(current_dir)
    
    logger.info(f"未找到项目根目录，使用原始目录: {directory}")
    return directory
