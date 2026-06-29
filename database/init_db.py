import os
import pymysql
from pymysql.constants import CLIENT

# Thêm flag MULTI_STATEMENTS để có thể chạy nhiều lệnh SQL cùng lúc
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "jvb_training"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "client_flag": CLIENT.MULTI_STATEMENTS
}

def init_db():
    print("Đang kiểm tra và khởi tạo Database...")
    sql_file_path = os.path.join(os.path.dirname(__file__), "init.sql")
    
    if not os.path.exists(sql_file_path):
        print("Lỗi: Không tìm thấy file init.sql")
        return

    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            # Kiểm tra xem bảng users đã tồn tại chưa
            cursor.execute("SHOW TABLES LIKE 'users'")
            if cursor.fetchone():
                print("Database đã được khởi tạo (bảng users đã tồn tại). Bỏ qua.")
                return

            print("Database trống. Đang chạy file init.sql để tạo bảng và seed data...")
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            # Thực thi toàn bộ file SQL
            cursor.execute(sql)
        conn.commit()
        print("Khởi tạo Database thành công!")
    except Exception as e:
        print(f"Lỗi khi khởi tạo Database: {e}")
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

if __name__ == "__main__":
    init_db()
