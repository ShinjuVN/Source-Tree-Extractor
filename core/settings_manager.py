"""
core.settings_manager
----------------------
Đọc/ghi file settings.json nằm CÙNG CẤP với main.py (khi chạy bằng Python)
hoặc CÙNG CẤP với file .exe (khi đã đóng gói bằng PyInstaller).

File này KHÔNG được nhúng vào bên trong file thực thi khi build --onedir,
để người dùng có thể mở và chỉnh sửa trực tiếp mà không cần build lại.
Xem BUILD.md để biết chi tiết.
"""

import json
import os

DEFAULT_SETTINGS = {
    "language": "vi",
    "default_output_filename": "source.txt",
    "export_tree": True,
    "export_content": True,
    "ignored_extensions": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".tiff",
        ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flac", ".wav", ".ogg", ".mkv",
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso",
        ".exe", ".dll", ".so", ".bin", ".dat", ".class", ".pyc", ".o", ".obj",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
        ".db", ".sqlite", ".sqlite3", ".jar", ".war", ".apk",
    ],
    "ignored_folders": [
        ".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode",
    ],
}


class SettingsManager:
    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.data = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.data.update(loaded)
            except Exception:
                # File lỗi/hỏng -> vẫn dùng giá trị mặc định, không crash app.
                pass
        else:
            # Chưa có file -> tạo mới với giá trị mặc định để người dùng
            # dễ tìm thấy và chỉnh sửa thủ công nếu muốn.
            self.save()

    def save(self):
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
