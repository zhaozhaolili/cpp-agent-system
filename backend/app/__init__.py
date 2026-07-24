import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.chapter import Chapter
from app.core.database import Base

def init_database():
    # 创建表（如果不存在）
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. 检查是否已有管理员
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="系统管理员",
            email="admin@example.com",
            role="admin"
        )
        db.add(admin_user)

    # 2. 创建教师
    teacher = db.query(User).filter(User.username == "teacher01").first()
    if not teacher:
        teacher_user = User(
            username="teacher01",
            hashed_password=get_password_hash("teacher123"),
            full_name="王老师",
            email="teacher@example.com",
            role="teacher"
        )
        db.add(teacher_user)
        db.flush()  # 获取 teacher.id

        # 3. 创建学生（关联该教师）
        student = db.query(User).filter(User.username == "student01").first()
        if not student:
            student_user = User(
                username="student01",
                hashed_password=get_password_hash("student123"),
                full_name="张三",
                email="student@example.com",
                role="student",
                teacher_id=teacher_user.id
            )
            db.add(student_user)

    # 4. 插入章节种子数据
    chapters_seed = [
        {"title": "第一章", "knowledge_points": ["面向对象基本概念", "类与对象", "封装与继承"], "order": 1},
        {"title": "第二章", "knowledge_points": ["多态", "虚函数", "抽象类"], "order": 2},
        {"title": "第三章", "knowledge_points": ["模板", "STL容器", "迭代器"], "order": 3},
        {"title": "第四章", "knowledge_points": ["异常处理", "I/O流"], "order": 4},
        {"title": "第五章", "knowledge_points": ["AVL树定义", "平衡调整", "旋转操作"], "order": 5},
    ]
    for chapter_data in chapters_seed:
        existing = db.query(Chapter).filter(Chapter.title == chapter_data["title"]).first()
        if not existing:
            db.add(Chapter(**chapter_data))

    db.commit()
    db.close()
    print("[OK] Database initialization complete!")
    print("默认账号：")
    print("  - 管理员: admin / admin123")
    print("  - 教师: teacher01 / teacher123")
    print("  - 学生: student01 / student123")

if __name__ == "__main__":
    init_database()