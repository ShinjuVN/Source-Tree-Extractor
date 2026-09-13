"""
core.i18n
---------
Hệ thống đa ngôn ngữ đơn giản dựa trên các file JSON trong thư mục `lang/`.

Mỗi file lang/<code>.json cần có tối thiểu:
    {
      "language_code": "vi",
      "language_name": "Tiếng Việt (VN-vi)",
      ... các cặp key: chuỗi hiển thị ...
    }

Người dùng có thể tự thêm ngôn ngữ mới bằng cách thêm 1 file JSON mới vào
thư mục `lang/` (ví dụ lang/fr.json), sao chép toàn bộ key từ lang/en.json
rồi dịch giá trị sang ngôn ngữ mong muốn. Ứng dụng sẽ tự nhận diện file
mới này ở lần khởi động / mở Settings kế tiếp mà không cần sửa code.
"""

import json
import os


class I18N:
    def __init__(self, lang_dir):
        self.lang_dir = lang_dir
        self.current_lang = "vi"
        self.strings = {}
        self.available_languages = {}  # code -> display_name
        self.scan_languages()

    def scan_languages(self):
        """Quét thư mục lang/ để tìm mọi file .json hợp lệ, kể cả file
        do người dùng tự thêm vào."""
        self.available_languages = {}
        if not os.path.isdir(self.lang_dir):
            return
        for fname in sorted(os.listdir(self.lang_dir)):
            if not fname.lower().endswith(".json"):
                continue
            path = os.path.join(self.lang_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                code = data.get("language_code") or os.path.splitext(fname)[0]
                name = data.get("language_name", code)
                self.available_languages[code] = name
            except Exception:
                continue  # File lỗi -> bỏ qua, không crash app

    def load(self, lang_code):
        """Tải bộ chuỗi cho `lang_code`. Nếu không tìm thấy, fallback về
        tiếng Anh; nếu vẫn không có, fallback về ngôn ngữ đầu tiên tìm thấy."""
        path = os.path.join(self.lang_dir, f"{lang_code}.json")

        if not os.path.exists(path):
            fallback_path = os.path.join(self.lang_dir, "en.json")
            if os.path.exists(fallback_path):
                path = fallback_path
            elif self.available_languages:
                first_code = next(iter(self.available_languages))
                path = os.path.join(self.lang_dir, f"{first_code}.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.strings = json.load(f)
            self.current_lang = self.strings.get("language_code", lang_code)
        except Exception:
            self.strings = {}
            self.current_lang = lang_code

    def t(self, key, **kwargs):
        """Lấy chuỗi theo `key`; nếu thiếu key thì trả về chính key đó
        (giúp phát hiện thiếu bản dịch thay vì crash)."""
        text = self.strings.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text
