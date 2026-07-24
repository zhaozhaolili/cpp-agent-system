from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base, SessionLocal
from app.core.config import settings
from app.api.v1 import auth, chat, teacher, student, admin, dashboard, search
import os

app = FastAPI(title="C++ 课程智能体系统", version="0.1.0")

@app.on_event("startup")
def startup():
    # 确保所有需要的目录存在
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    # 建表
    Base.metadata.create_all(bind=engine)
    # 插入种子章节（如果不存在）
    from app.models.chapter import Chapter
    db = SessionLocal()
    try:
        if db.query(Chapter).count() == 0:
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
                db.add(Chapter(**ch))
            db.commit()
            print(f"[OK] Seed chapters inserted: {len(chapters)}")
    finally:
        db.close()

# CORS: 开发 + Docker 都允许
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(teacher.router, prefix="/api/v1")
app.include_router(student.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")

# 静态文件服务（上传的资料文件）
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/")
async def root():
    return {"message": "C++ Agent System API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}