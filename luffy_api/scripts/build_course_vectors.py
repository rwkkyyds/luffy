"""
构建课程向量索引（文本分块版）

将每门课的概述 + 每个章节的每个课时分别向量化：
- 课程概述：课程名 + 简介
- 课时条目：课程名 → 章节名 → 课时名

这样 RAG 可以精确匹配到具体课时，而不是只能匹配整门课。

运行方式：
    cd luffy_api
    python scripts/build_course_vectors.py
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "luffy_api"))
sys.path.insert(0, os.path.join(BASE_DIR, "luffy_api", "apps"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luffy_api.setting.dev")

import django
django.setup()

from django.conf import settings
from course.models import Course
from libs.llm import ZhipuEmbedder
from libs.rag.faiss_store import FAISSVectorStore


def build_course_vectors():
    print("=" * 50)
    print("开始构建课程向量索引（分块模式 + FAISS）")
    print("=" * 50)

    api_key = getattr(settings, 'ZHIPU_API_KEY', '') or ''
    api_key = api_key.strip()
    if not api_key:
        print('错误：未配置 ZHIPU_API_KEY')
        return

    embedder = ZhipuEmbedder(api_key=api_key)
    store = FAISSVectorStore()
    courses = Course.objects.filter(status=0).select_related('teacher')

    overview_count = 0
    section_count = 0

    for course in courses:
        # ===== 块 1：课程概述 =====
        brief = (course.brief or '')[:300]
        overview_text = f"【课程】{course.name}（{course.get_level_display()}）\n简介：{brief}"

        vector = embedder.embed(overview_text)
        if vector:
            store.add(text=overview_text, vector=vector, metadata={
                "course_id": course.id,
                "course_name": course.name,
                "type": "course_overview",
            })
            overview_count += 1
            print(f"  [OK] 概述: {course.name}")

        # ===== 块 2：每个课时 =====
        for chapter in course.coursechapters.all():
            for section in chapter.coursesections.all():
                section_text = f"【课程】{course.name}\n【章节】{chapter.name}\n【课时】{section.name}"
                if section.duration:
                    section_text += f"\n时长：{section.duration}"

                vector = embedder.embed(section_text)
                if not vector:
                    continue

                store.add(text=section_text, vector=vector, metadata={
                    "course_id": course.id,
                    "course_name": course.name,
                    "chapter_name": chapter.name,
                    "section_name": section.name,
                    "type": "course_section",
                })
                section_count += 1
                print(f"  [OK] 课时: {course.name} / {chapter.name} / {section.name}")

    save_path = getattr(settings, 'COURSE_VECTOR_FILE', os.path.join(BASE_DIR, 'data', 'course_vectors.json'))
    data_dir = os.path.dirname(save_path)
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)

    # 向量全部添加完后，构建 FAISS 索引再保存
    store.build_index()
    store.save(save_path)

    print("\n" + "=" * 50)
    print(f"[OK] 构建完成！课程概述 {overview_count} 条，课时 {section_count} 条，共 {len(store)} 条")
    print(f"[OK] 保存位置: {save_path}")
    print("=" * 50)


if __name__ == "__main__":
    build_course_vectors()
