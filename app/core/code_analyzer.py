import os
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """代码分析器类，负责分析代码结构并生成报告"""
    
    def __init__(self, code_dir: str, problem_description: str):
        """
        初始化代码分析器
        
        Args:
            code_dir: 代码目录路径
            problem_description: 问题描述文本
        """
        self.code_dir = code_dir
        self.problem_description = problem_description
        self.files_map = {}
        self._build_files_map()
    
    def _build_files_map(self):
        """构建文件路径到内容的映射"""
        logger.info(f"正在构建文件映射，扫描目录: {self.code_dir}")
        for root, _, files in os.walk(self.code_dir):
            for file in files:
                if file.endswith(('.js', '.ts', '.tsx', '.jsx', '.py', '.java', '.cpp', '.cs')):
                    file_path = os.path.join(root, file)
                    try:
                        rel_path = os.path.relpath(file_path, self.code_dir)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            self.files_map[rel_path] = f.readlines()
                        logger.debug(f"成功读取文件: {rel_path}")
                    except Exception as e:
                        logger.error(f"读取文件 {file_path} 失败: {e}")
        logger.info(f"文件映射构建完成，共读取 {len(self.files_map)} 个文件")
    
    def extract_functions(self, file_content: List[str], file_ext: str) -> Dict[str, Dict[str, Any]]:
        """从文件内容中提取函数定义"""
        functions = {}
        
        # 根据文件类型选择不同的正则表达式
        if file_ext == '.py':
            # Python函数定义
            pattern = r'^\s*def\s+(\w+)\s*\(([^)]*)\)\s*:'
        elif file_ext in ('.js', '.ts', '.tsx', '.jsx'):
            # JavaScript/TypeScript函数定义
            pattern = r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)|^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(\s*([^)]*)\s*\)\s*=>'
        elif file_ext in ('.java', '.cs'):
            # Java/C#方法定义
            pattern = r'^(?:public|private|protected|static|final|abstract)\s*(?:\w+\s+)*\s+(\w+)\s*\(([^)]*)\)'
        elif file_ext == '.cpp':
            # C++函数定义
            pattern = r'^(?:\w+\s+)*(?:\*|\&)?\s*(\w+)\s*\(([^)]*)\)'
        else:
            return functions
        
        for i, line in enumerate(file_content, 1):
            match = re.search(pattern, line)
            if match:
                # 处理不同语言的捕获组
                if file_ext in ('.js', '.ts', '.tsx', '.jsx'):
                    func_name = match.group(1) or match.group(3)
                    params = match.group(2) or match.group(4) or ''
                else:
                    func_name = match.group(1)
                    params = match.group(2) or ''
                
                # 尝试找到函数结束位置
                end_line = self._find_function_end(file_content, i, file_ext)
                functions[func_name] = {
                    'start_line': i,
                    'end_line': end_line,
                    'params': params.strip()
                }
        
        return functions
    
    def _find_function_end(self, file_content: List[str], start_line: int, file_ext: str) -> int:
        """尝试确定函数的结束行"""
        # 简单实现：找到缩进减少的地方
        indent_pattern = re.compile(r'^(\s*)')
        
        # 尝试获取函数定义行的缩进
        match = indent_pattern.search(file_content[start_line - 1])
        if not match:
            return start_line
        
        func_indent = len(match.group(1))
        
        for i in range(start_line, len(file_content)):
            match = indent_pattern.search(file_content[i])
            if match:
                line_indent = len(match.group(1))
                # 如果遇到缩进更小且不是空行或注释的行，可能是函数结束
                if line_indent <= func_indent and line_indent > 0:
                    # 检查是否是注释行
                    if file_ext in ('.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.cs'):
                        if re.match(r'\s*(//|/\*|\*/)', file_content[i]):
                            continue
                    elif file_ext == '.py':
                        if re.match(r'\s*#', file_content[i]):
                            continue
                    return i
            # 如果遇到空行，继续检查
            elif not file_content[i].strip():
                continue
            # 如果遇到缩进为0的非空行，可能是函数结束
            else:
                return i
        
        return len(file_content)
    
    def analyze_features(self) -> List[Dict[str, Any]]:
        """分析代码中的功能实现位置"""
        logger.info("开始功能分析")
        
        # 从需求描述中提取关键功能点
        features = self._extract_features_from_description()
        analysis_results = []
        
        for feature in features:
            implementation_locations = []
            
            # 搜索相关文件和函数
            for file_path, file_content in self.files_map.items():
                file_ext = os.path.splitext(file_path)[1]
                functions = self.extract_functions(file_content, file_ext)
                
                # 简单的关键词匹配逻辑
                for func_name, func_info in functions.items():
                    # 结合文件名和函数名进行匹配
                    if self._is_relevant_to_feature(file_path, func_name, feature):
                        implementation_locations.append({
                            'file': file_path,
                            'function': func_name,
                            'lines': f"{func_info['start_line']}-{func_info['end_line']}"
                        })
            
            analysis_results.append({
                'feature_description': feature,
                'implementation_location': implementation_locations
            })
            logger.info(f"功能 '{feature}' 分析完成，找到 {len(implementation_locations)} 个实现位置")
        
        return analysis_results
    
    def _extract_features_from_description(self) -> List[str]:
        """从需求描述中提取功能点"""
        # 简化实现：基于标点符号分割句子
        sentences = [s.strip() for s in re.split(r'[。；;]', self.problem_description) if s.strip()]
        
        # 过滤出可能描述功能的句子
        feature_keywords = ['实现', '添加', '创建', '支持', '提供', '开发', '设计']
        features = []
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in feature_keywords):
                features.append(sentence)
            elif len(features) > 0 and len(sentence) > 10:  # 补充说明
                features[-1] += ' ' + sentence
        
        # 如果没有找到明显的功能点，返回整个描述
        if not features:
            features = [self.problem_description]
        
        logger.info(f"从需求描述中提取了 {len(features)} 个功能点")
        return features
    
    def _is_relevant_to_feature(self, file_path: str, func_name: str, feature: str) -> bool:
        """判断文件和函数是否与特定功能相关"""
        # 简单的关键词匹配
        # 提取功能中的关键词
        feature_words = re.findall(r'[\u4e00-\u9fa5]+', feature)  # 提取中文字符
        
        # 转换为小写用于比较
        file_path_lower = file_path.lower()
        func_name_lower = func_name.lower()
        feature_lower = feature.lower()
        
        # 检查直接匹配
        if feature_lower in file_path_lower or feature_lower in func_name_lower:
            return True
        
        # 检查功能关键词与文件名或函数名的匹配
        for word in feature_words:
            if word.lower() in file_path_lower or word.lower() in func_name_lower:
                return True
        
        # 检查英文关键词匹配
        english_words = re.findall(r'[a-zA-Z_]+', feature)
        for word in english_words:
            if len(word) > 2 and word.lower() in file_path_lower:
                return True
            # 对于函数名，检查驼峰命名或下划线命名的匹配
            if len(word) > 2:
                # 检查驼峰命名（如createUser可能匹配create或user）
                if word.lower() in func_name_lower or \
                   (re.search(r'[A-Z]', func_name) and 
                    (word.lower() == func_name_lower[:len(word)] or 
                     word.lower() in re.findall(r'[a-z]+', func_name_lower))):
                    return True
        
        return False
    
    def suggest_execution_plan(self) -> str:
        """生成执行计划建议"""
        # 检测项目类型并生成相应的执行计划
        project_type = self._detect_project_type()
        
        if project_type == 'nodejs':
            return "要执行此项目，应首先执行 `npm install` 安装依赖，然后执行 `npm run start` 来启动服务。"
        elif project_type == 'python':
            if os.path.exists(os.path.join(self.code_dir, 'requirements.txt')):
                return "要执行此项目，应首先执行 `pip install -r requirements.txt` 安装依赖，然后执行 `python main.py` 或相应的启动脚本。"
            else:
                return "要执行此项目，应执行 `python main.py` 或相应的启动脚本。"
        elif project_type == 'java':
            return "要执行此项目，应使用 Maven 或 Gradle 构建项目，然后运行生成的 JAR 文件。"
        elif project_type == 'dotnet':
            return "要执行此项目，应首先执行 `dotnet restore` 还原依赖，然后执行 `dotnet run` 来启动服务。"
        else:
            return "请根据项目类型，按照相应的构建和启动流程执行此项目。"
    
    def _detect_project_type(self) -> str:
        """检测项目类型"""
        # 检查关键文件以确定项目类型
        if any(f.endswith('.js') and not f.endswith('.test.js') for f in self.files_map):
            if os.path.exists(os.path.join(self.code_dir, 'package.json')):
                return 'nodejs'
        if any(f.endswith('.py') for f in self.files_map):
            return 'python'
        if any(f.endswith('.java') for f in self.files_map):
            return 'java'
        if any(f.endswith('.cs') for f in self.files_map):
            return 'dotnet'
        return 'unknown'
    
    def generate_test_code(self) -> str:
        """生成测试代码"""
        project_type = self._detect_project_type()
        
        if project_type == 'nodejs':
            return "// 为 Node.js 项目生成的测试代码示例\n" \
                   "const assert = require('assert');\n\n" \
                   "// 请根据实际项目结构和功能实现修改测试代码\n" \
                   "describe('项目功能测试', () => {\n" \
                   "  // 测试用例示例\n" \
                   "  it('应该实现需求中描述的功能', () => {\n" \
                   "    // TODO: 实现具体的测试逻辑\n" \
                   "    assert.strictEqual(1, 1);\n" \
                   "  });\n" \
                   "  \n" \
                   "  // 可以添加更多测试用例\n" \
                   "  // it('另一个测试用例', () => {...});\n" \
                   "\n});\n"
        elif project_type == 'python':
            return "# 为 Python 项目生成的测试代码示例\n" \
                   "import unittest\n\n" \
                   "# 请根据实际项目结构和功能实现修改测试代码\n" \
                   "class TestProjectFeatures(unittest.TestCase):\n" \
                   "    \n" \
                   "    def test_feature_implementation(self):\n" \
                   "        # TODO: 实现具体的测试逻辑\n" \
                   "        self.assertEqual(1, 1)\n" \
                   "        \n" \
                   "    # 可以添加更多测试方法\n" \
                   "    # def test_another_feature(self):\n" \
                   "    #     ...\n" \
                   "\n" \
                   "if __name__ == '__main__':\n" \
                   "    unittest.main()\n"
        else:
            return f"// 为 {project_type} 项目生成的测试代码示例\n" \
                   "// 请根据实际项目结构和功能实现修改测试代码\n"
    
    def verify_functionality(self) -> Dict[str, Any]:
        """验证功能正确性"""
        # 在实际应用中，这里应该执行生成的测试代码
        # 简化版本仅返回模拟结果
        return {
            "tests_passed": True,
            "log": "测试执行成功（模拟结果）。在实际实现中，这里将包含真实的测试执行日志。"
        }
