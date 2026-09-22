"""
Module: database/schema.py
Mục đích: Định nghĩa và khởi tạo cấu trúc các bảng (Schema) và chỉ mục (Index)
          cho hệ thống AI Personalized Learning.
Tác giả: Senior Python Software Architect & AI/ML Engineer
"""

import sys
from pathlib import Path

# Đảm bảo đường dẫn gốc của dự án có trong sys.path để import chuẩn module
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.database import DatabaseManager


def create_tables(db: DatabaseManager) -> None:
    """
    Tạo tất cả các bảng trong cơ sở dữ liệu nếu chưa tồn tại.
    """
    # Bật tính năng kiểm tra Ràng buộc Khóa ngoại (Foreign Keys) trong SQLite
    db.execute("PRAGMA foreign_keys = ON;")

    # 1. Bảng learners
    db.execute("""
    CREATE TABLE IF NOT EXISTS learners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER CHECK(age > 0),
        email TEXT UNIQUE NOT NULL,
        learning_goal TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    );
    """)

    # 2. Bảng subjects
    db.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    );
    """)

    # 3. Bảng concepts
    db.execute("""
    CREATE TABLE IF NOT EXISTS concepts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        difficulty REAL CHECK(difficulty >= 0.0 AND difficulty <= 1.0) DEFAULT 0.5,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
    );
    """)

    # 4. Bảng concept_relationships
    db.execute("""
    CREATE TABLE IF NOT EXISTS concept_relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_concept_id INTEGER NOT NULL,
        target_concept_id INTEGER NOT NULL,
        relationship_type TEXT CHECK(relationship_type IN ('prerequisite', 'related', 'depends_on')) NOT NULL,
        weight REAL CHECK(weight >= 0.0 AND weight <= 1.0) DEFAULT 1.0,
        FOREIGN KEY (source_concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
        FOREIGN KEY (target_concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
        UNIQUE(source_concept_id, target_concept_id, relationship_type)
    );
    """)

    # 5. Bảng questions
    db.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concept_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        explanation TEXT,
        difficulty REAL CHECK(difficulty >= 0.0 AND difficulty <= 1.0) DEFAULT 0.5,
        question_type TEXT CHECK(question_type IN ('multiple_choice', 'true_false', 'short_answer')) NOT NULL,
        points REAL CHECK(points > 0.0) DEFAULT 1.0,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );
    """)

    # 6. Bảng question_options
    db.execute("""
    CREATE TABLE IF NOT EXISTS question_options (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        option_text TEXT NOT NULL,
        option_label TEXT NOT NULL,
        is_correct INTEGER CHECK(is_correct IN (0, 1)) NOT NULL DEFAULT 0,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    );
    """)

    # 7. Bảng test_sessions
    db.execute("""
    CREATE TABLE IF NOT EXISTS test_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learner_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        test_type TEXT CHECK(test_type IN ('standard', 'adaptive', 'diagnostic')) NOT NULL,
        started_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        completed_at TEXT,
        total_questions INTEGER CHECK(total_questions >= 0) DEFAULT 0,
        correct_answers INTEGER CHECK(correct_answers >= 0) DEFAULT 0,
        score REAL CHECK(score >= 0.0) DEFAULT 0.0,
        FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE RESTRICT,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE RESTRICT
    );
    """)

    # 8. Bảng answers (Lịch sử làm bài - KHÔNG xóa khi cascade)
    db.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        selected_option_id INTEGER,
        answer_text TEXT,
        is_correct INTEGER CHECK(is_correct IN (0, 1)) NOT NULL,
        response_time REAL CHECK(response_time >= 0.0) DEFAULT 0.0,
        answered_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (session_id) REFERENCES test_sessions(id) ON DELETE RESTRICT,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE RESTRICT,
        FOREIGN KEY (selected_option_id) REFERENCES question_options(id) ON DELETE SET NULL
    );
    """)

    # 9. Bảng error_records
    db.execute("""
    CREATE TABLE IF NOT EXISTS error_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        answer_id INTEGER NOT NULL,
        error_type TEXT CHECK(error_type IN ('concept_error', 'formula_error', 'calculation_error', 'careless_error', 'prerequisite_error', 'unknown')) NOT NULL DEFAULT 'unknown',
        confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0) DEFAULT 1.0,
        description TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (answer_id) REFERENCES answers(id) ON DELETE CASCADE
    );
    """)

    # 10. Bảng knowledge_states (Dynamic Ability Profile)
    db.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learner_id INTEGER NOT NULL,
        concept_id INTEGER NOT NULL,
        mastery REAL CHECK(mastery >= 0.0 AND mastery <= 1.0) DEFAULT 0.0,
        confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0) DEFAULT 0.0,
        attempts INTEGER CHECK(attempts >= 0) DEFAULT 0,
        correct_count INTEGER CHECK(correct_count >= 0) DEFAULT 0,
        incorrect_count INTEGER CHECK(incorrect_count >= 0) DEFAULT 0,
        last_updated TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
        UNIQUE(learner_id, concept_id)
    );
    """)

    # 11. Bảng recommendations
    db.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learner_id INTEGER NOT NULL,
        concept_id INTEGER NOT NULL,
        recommendation_type TEXT CHECK(recommendation_type IN ('review', 'practice', 'advance', 'prerequisite')) NOT NULL,
        priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')) NOT NULL DEFAULT 'medium',
        reason TEXT,
        confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0) DEFAULT 1.0,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        status TEXT CHECK(status IN ('pending', 'accepted', 'completed', 'dismissed')) NOT NULL DEFAULT 'pending',
        FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );
    """)

    # 12. Bảng learning_paths
    db.execute("""
    CREATE TABLE IF NOT EXISTS learning_paths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learner_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        status TEXT CHECK(status IN ('active', 'completed', 'paused')) NOT NULL DEFAULT 'active',
        FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE
    );
    """)

    # 13. Bảng learning_path_steps
    db.execute("""
    CREATE TABLE IF NOT EXISTS learning_path_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learning_path_id INTEGER NOT NULL,
        concept_id INTEGER NOT NULL,
        step_order INTEGER CHECK(step_order > 0) NOT NULL,
        activity_type TEXT CHECK(activity_type IN ('learn', 'practice', 'test', 'review')) NOT NULL,
        target_mastery REAL CHECK(target_mastery >= 0.0 AND target_mastery <= 1.0) DEFAULT 0.8,
        status TEXT CHECK(status IN ('pending', 'active', 'completed', 'skipped')) NOT NULL DEFAULT 'pending',
        started_at TEXT,
        completed_at TEXT,
        FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
        UNIQUE(learning_path_id, step_order)
    );
    """)


def create_indexes(db: DatabaseManager) -> None:
    """
    Tạo các chỉ mục (Index) tối ưu tốc độ truy vấn cho các trường dữ liệu tần suất cao.
    """
    db.execute("CREATE INDEX IF NOT EXISTS idx_learners_email ON learners(email);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_concepts_subject_id ON concepts(subject_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_questions_concept_id ON questions(concept_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_test_sessions_learner_id ON test_sessions(learner_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_answers_session_id ON answers(session_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_answers_question_id ON answers(question_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_error_records_answer_id ON error_records(answer_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_states_learner_concept ON knowledge_states(learner_id, concept_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_learner_id ON recommendations(learner_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_learning_path_steps_path_id ON learning_path_steps(learning_path_id);")


def initialize_schema(db_path: str = "data/learning.db") -> None:
    """
    Thực thi tạo toàn bộ cấu trúc cơ sở dữ liệu và chỉ mục.
    """
    db = DatabaseManager(db_path=db_path)
    try:
        print("[DATABASE] Connected")
        print("[SCHEMA] Creating tables...")
        create_tables(db)
        
        print("[SCHEMA] Creating indexes...")
        create_indexes(db)
        
        print("[SCHEMA] Database schema initialized successfully.")
    except Exception as e:
        print(f"[SCHEMA ERROR] Thất bại khi khởi tạo schema: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    initialize_schema()