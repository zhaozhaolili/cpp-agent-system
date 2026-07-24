from app.core.database import Base
from .user import User
from .teacher_student import TeacherStudent
from .chapter import Chapter
from .course_material import CourseMaterial
from .exam_config import ExamConfig
from .exam_record import ExamRecord
from .chat_log import ChatLog
from .wrong_answer import WrongAnswer

__all__ = [
    'Base',
    'User',
    'TeacherStudent',
    'Chapter',
    'CourseMaterial',
    'ExamConfig',
    'ExamRecord',
    'ChatLog',
    'WrongAnswer',
]