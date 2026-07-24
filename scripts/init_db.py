import sys
import os

# 将 backend 目录添加到 sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# 确保 data 目录存在（数据库和 Chroma 都需要）
data_dir = os.path.join(project_root, 'data')
os.makedirs(data_dir, exist_ok=True)
os.makedirs(os.path.join(data_dir, 'chroma_data'), exist_ok=True)

from app.core.database import Base, engine, SessionLocal

# 强制导入所有模型，确保它们注册到 Base.metadata
import app.models.user
import app.models.teacher_student
import app.models.chapter
import app.models.course_material
import app.models.exam_config
import app.models.exam_record
import app.models.chat_log
import app.models.wrong_answer

from app.models.chapter import Chapter

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    if db.query(Chapter).count() == 0:
        print("Inserting default chapters...")
        chapters = [
            {"title": "第一章 面向对象概述", "description": "面向对象基本概念、发展历程", "order": 1},
            {"title": "第二章 类与对象", "description": "类的定义、对象创建、封装", "order": 2},
            {"title": "第三章 继承与派生", "description": "继承、多态、虚函数", "order": 3},
            {"title": "第四章 运算符重载", "description": "运算符重载规则、友元", "order": 4},
            {"title": "第五章 模板与泛型编程", "description": "函数模板、类模板", "order": 5},
            {"title": "第六章 异常处理", "description": "try-throw-catch", "order": 6},
            {"title": "第七章 STL 初步", "description": "容器、迭代器、算法", "order": 7},
            {"title": "第八章 输入输出流", "description": "文件流、字符串流", "order": 8},
            {"title": "第九章 内存管理", "description": "new/delete，智能指针基础", "order": 9},
            {"title": "第十章 面向对象设计原则", "description": "SOLID原则", "order": 10},
        ]
        for ch in chapters:
            chapter = Chapter(**ch)
            db.add(chapter)
        db.commit()
        print(f"Inserted {len(chapters)} chapters.")
    else:
        print("Chapters already exist, skipping insert.")
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialization completed.")