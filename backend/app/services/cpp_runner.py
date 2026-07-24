"""
C++ 在线编译运行服务
在临时目录中编译并执行 C++ 代码，返回输出或错误信息
"""
import subprocess
import tempfile
import os
import shutil
from typing import Dict


def run_cpp_code(code: str, stdin: str = "") -> Dict:
    """
    编译并运行 C++ 代码
    Returns: {"success": bool, "output": str, "error": str}
    """
    # 检查 g++ 是否可用
    if not shutil.which("g++"):
        return {
            "success": False,
            "output": "",
            "error": "服务器未安装 g++ 编译器。请联系管理员安装 MinGW 或 GCC。"
        }

    tmp_dir = tempfile.mkdtemp(prefix="cpp_run_")
    src_file = os.path.join(tmp_dir, "main.cpp")
    exe_file = os.path.join(tmp_dir, "main.exe")

    try:
        # 写入源代码
        with open(src_file, "w", encoding="utf-8") as f:
            f.write(code)

        # 编译
        compile_result = subprocess.run(
            ["g++", "-std=c++17", "-O2", "-fexec-charset=UTF-8", "-finput-charset=UTF-8", "-o", exe_file, src_file],
            capture_output=True, text=True, timeout=15
        )

        if compile_result.returncode != 0:
            return {
                "success": False,
                "output": "",
                "error": "[编译错误]\n" + (compile_result.stderr or compile_result.stdout or "").strip()
            }

        # 运行
        run_result = subprocess.run(
            [exe_file],
            input=stdin,
            capture_output=True, encoding='utf-8', errors='replace', timeout=5
        )

        output = run_result.stdout or ""
        if run_result.stderr:
            output += "\n[stderr]\n" + run_result.stderr

        if run_result.returncode != 0:
            output += f"\n[程序退出码: {run_result.returncode}]"

        return {
            "success": True,
            "output": (output or "").strip() or "(程序无输出)",
            "error": ""
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "程序运行超时（超过 5 秒）。请检查是否有无限循环。"
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"运行异常: {str(e)}"
        }
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass


# 单例
cpp_runner = type('CppRunner', (), {'run': staticmethod(run_cpp_code)})()
