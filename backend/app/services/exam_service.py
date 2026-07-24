import json
from typing import List, Dict, Optional
from app.services.llm_service import llm_service

class ExamService:
    
    async def generate_questions(
        self, 
        chapter_title: str, 
        knowledge_points: List[str], 
        config: Dict
    ) -> List[Dict]:
        """根据知识点生成题目"""
        
        # 构建题型要求描述
        type_desc = []
        if config.get('choice', 0) > 0:
            type_desc.append(f"选择题{config.get('choice')}道")
        if config.get('judge', 0) > 0:
            type_desc.append(f"判断题{config.get('judge')}道")
        if config.get('short_answer', 0) > 0:
            type_desc.append(f"简答题{config.get('short_answer')}道")
        if config.get('programming', 0) > 0:
            type_desc.append(f"编程题{config.get('programming')}道")
        
        prompt = f"""请根据以下 C++ 课程章节生成考试题目。

        章节名称：{chapter_title}
        知识点：{', '.join(knowledge_points)}
        题型要求：{', '.join(type_desc)}

        要求：
        1. 题目要紧密结合 C++ 编程语言的实际应用
        2. 难度适中，适合大学生水平
        3. 选择题必须有 4 个选项（A、B、C、D）
        4. 判断题答案只能是"正确"或"错误"
        5. 简答题需要给出参考答案要点
        6. 编程题需要给出题目描述和参考代码

        请严格按照以下 JSON 格式输出，不要包含其他内容：
        {{
            "questions": [
                {{"type": "choice", "question": "题目内容", "options": ["A选项", "B选项", "C选项", "D选项"], "answer": "A"}},
                {{"type": "judge", "question": "题目内容", "answer": "正确"}},
                {{"type": "short_answer", "question": "题目内容", "answer": "参考答案"}},
                {{"type": "programming", "question": "题目描述", "answer": "参考代码"}}
            ]
        }}
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = await llm_service.chat(messages)
        
        try:
            # 尝试提取 JSON（处理可能的 Markdown 代码块）
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result)
            return data.get("questions", [])
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parse failed: {e}")
            print(f"Response: {result[:500]}...")
            return []
    
    async def grade_exam(
        self, 
        questions: List[Dict], 
        answers: List[str]
    ) -> Dict:
        """批改答卷并生成学习评价报告"""
        
        if not questions:
            return {
                "score": 0,
                "dimensions": {},
                "review_points": ["没有题目可供批改"],
                "overall_comment": "考试异常，请联系管理员"
            }
        
        # 构建题目-答案对照
        qa_pairs = []
        for i, q in enumerate(questions):
            q_type = q.get("type", "未知")
            q_text = q.get("question", "")
            correct = q.get("answer", "未提供")
            student_ans = answers[i] if i < len(answers) else "(未作答)"
            qa_pairs.append(f"题目{i+1} [{q_type}]：{q_text}\n正确答案：{correct}\n学生答案：{student_ans}")
        
        prompt = f"""请批改以下 C++ 课程考试答卷，并生成学习评价报告。

        {chr(10).join(qa_pairs)}

        评价维度：
        1. 知识掌握情况（对知识点的记忆和理解）
        2. 基础概念理解（对核心概念的掌握）
        3. 综合分析能力（对复杂问题的分析和解决）

        请严格按照以下 JSON 格式输出：
        {{
            "score": 85,
            "dimensions": {{
                "知识掌握情况": 80,
                "基础概念理解": 90,
                "综合分析能力": 75
            }},
            "review_points": ["建议复习虚函数的概念", "建议加强多态编程练习"],
            "overall_comment": "总体表现良好，对基础概念掌握较好，但综合分析能力有待加强。"
        }}
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = await llm_service.chat(messages)
        
        try:
            # 提取 JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            return json.loads(result)
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parse failed: {e}")
            print(f"Response: {result[:500]}...")
            return {
                "score": 0,
                "dimensions": {},
                "review_points": ["批改服务暂时不可用"],
                "overall_comment": "批改出现异常，请稍后重试"
            }

    def extract_wrong_answers(
        self,
        questions: List[Dict],
        student_answers: List[str]
    ) -> List[Dict]:
        """从答题中提取错题（简单判断：选择题和判断题直接比对答案）"""
        wrong_list = []
        for i, q in enumerate(questions):
            correct = q.get("answer", "").strip()
            student = student_answers[i].strip() if i < len(student_answers) else "(未作答)"

            if not student or student == "(未作答)":
                is_wrong = True
            elif q.get("type") in ("choice", "judge"):
                is_wrong = (correct != student)
            else:
                # 简答题/编程题：如果得分较低视为错题
                is_wrong = (len(student) < 10)  # 答案太短视为未认真作答

            if is_wrong:
                wrong_list.append({
                    "question_type": q.get("type", ""),
                    "question_text": q.get("question", ""),
                    "correct_answer": correct,
                    "student_answer": student,
                })

        return wrong_list


# 全局单例
exam_service = ExamService()