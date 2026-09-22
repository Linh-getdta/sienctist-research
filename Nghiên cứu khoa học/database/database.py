"""
Module: database/database.py
Mục đích: Quản lý kết nối và thực thi câu lệnh SQL với cơ sở dữ liệu SQLite.
Tác giả: Senior Python Software Architect
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class DatabaseManager:
    """
    Quản lý kết nối và các thao tác cơ bản với CSDL SQLite.
    Đóng vai trò là Persistence Engine nền tảng cho hệ thống.
    """

    def __init__(self, db_path: Union[str, Path] = "data/learning.db") -> None:
        """
        Khởi tạo DatabaseManager với đường dẫn file CSDL.

        :param db_path: Đường dẫn tới file CSDL SQLite (Mặc định: data/learning.db)
        """
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None

    def _ensure_dir_exists(self) -> None:
        """Kiểm tra và tự động tạo thư mục chứa CSDL nếu chưa tồn tại."""
        try:
            if not self.db_path.parent.exists():
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[DATABASE ERROR] Không thể tạo thư mục CSDL '{self.db_path.parent}': {e}")
            raise e

    def connect(self) -> sqlite3.Connection:
        """
        Tạo hoặc trả về kết nối SQLite đang mở.
        Cấu hình sqlite3.Row để truy cập dữ liệu theo tên cột.

        :return: Đối tượng sqlite3.Connection
        """
        if self._connection is None:
            self._ensure_dir_exists()
            try:
                self._connection = sqlite3.connect(str(self.db_path))
                # Cho phép truy cập cột dữ liệu dạng dictionary: row['column_name']
                self._connection.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                print(f"[DATABASE ERROR] Lỗi kết nối tới CSDL '{self.db_path}': {e}")
                raise e

        return self._connection

    def close(self) -> None:
        """Đóng kết nối CSDL an toàn nếu đang mở."""
        if self._connection is not None:
            try:
                self._connection.close()
            except sqlite3.Error as e:
                print(f"[DATABASE ERROR] Lỗi khi đóng kết nối CSDL: {e}")
                raise e
            finally:
                self._connection = None

    def execute(
        self, query: str, params: Union[Tuple[Any, ...], Dict[str, Any]] = ()
    ) -> int:
        """
        Thực thi các câu lệnh SQL làm thay đổi dữ liệu (INSERT, UPDATE, DELETE, CREATE).
        Tự động commit khi thành công và rollback khi xảy ra lỗi.

        :param query: Chuỗi câu lệnh SQL (Sử dụng '?' hoặc ':key' làm parameter)
        :param params: Tham số đầu vào dạng tuple hoặc dict
        :return: ID dòng mới tạo (lastrowid) hoặc số dòng bị ảnh hưởng (rowcount)
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            # Trả về lastrowid nếu có (INSERT), ngược lại trả về rowcount (UPDATE/DELETE)
            return cursor.lastrowid if cursor.lastrowid and cursor.lastrowid > 0 else cursor.rowcount
        except sqlite3.Error as e:
            conn.rollback()
            print(f"[DATABASE ERROR] Thực thi SQL thất bại: {e}")
            print(f"[DATABASE QUERY] Query: {query} | Params: {params}")
            raise e
        finally:
            cursor.close()

    def fetch_one(
        self, query: str, params: Union[Tuple[Any, ...], Dict[str, Any]] = ()
    ) -> Optional[sqlite3.Row]:
        """
        Truy vấn và trả về 1 bản ghi duy nhất.

        :param query: Chuỗi câu lệnh SELECT SQL
        :param params: Tham số đầu vào dạng tuple hoặc dict
        :return: Bản ghi kiểu sqlite3.Row hoặc None nếu không tìm thấy
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Truyn vấn fetch_one thất bại: {e}")
            print(f"[DATABASE QUERY] Query: {query} | Params: {params}")
            raise e
        finally:
            cursor.close()

    def fetch_all(
        self, query: str, params: Union[Tuple[Any, ...], Dict[str, Any]] = ()
    ) -> List[sqlite3.Row]:
        """
        Truy vấn và trả về danh sách nhiều bản ghi.

        :param query: Chuỗi câu lệnh SELECT SQL
        :param params: Tham số đầu vào dạng tuple hoặc dict
        :return: Danh sách các bản ghi kiểu sqlite3.Row
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Truy vấn fetch_all thất bại: {e}")
            print(f"[DATABASE QUERY] Query: {query} | Params: {params}")
            raise e
        finally:
            cursor.close()

    def initialize(self) -> bool:
        """
        Kiểm tra khả năng tạo thư mục, mở kết nối và thực thi truy vấn kiểm thử thành công.
        KHÔNG khởi tạo cấu trúc bảng (schema) tại đây.

        :return: True nếu kết nối và kiểm tra hoạt động bình thường
        """
        try:
            self._ensure_dir_exists()
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.close()
            print(f"[DATABASE] Connected & Initialized: {self.db_path}")
            return True
        except Exception as e:
            print(f"[DATABASE ERROR] Khởi tạo CSDL thất bại: {e}")
            raise e


if __name__ == "__main__":
    print("=== KIỂM THỬ MODULE DATABASE MANAGER ===")
    
    # 1. Khởi tạo đối tượng quản lý database
    db = DatabaseManager(db_path="data/learning.db")
    
    try:
        # 2. Kiểm tra khả năng kết nối
        db.initialize()
        print("Database hoạt động bình thường.")
    except Exception as err:
        print(f"Xảy ra lỗi trong quá trình kiểm thử: {err}")
    finally:
        # 3. Đóng kết nối an toàn
        db.close()
        print("[DATABASE] Closed safely.")