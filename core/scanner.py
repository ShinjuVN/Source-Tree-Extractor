"""
core.scanner
------------
Logic thuần (không liên quan giao diện) để:
 - Quét cây thư mục (bỏ qua các folder trong `ignored_folders`).
 - Đọc nội dung file văn bản (bỏ qua các đuôi trong `ignored_extensions`
   và mọi file bị phát hiện là nhị phân qua việc dò byte NUL / lỗi decode).
 - Ghép thành chuỗi kết quả cuối cùng theo yêu cầu định dạng.

Được tách riêng khỏi main.py để có thể unit-test hoặc tái sử dụng mà
không cần khởi tạo giao diện.
"""

import os


def looks_binary(file_path, sample_size=2048):
    """Đọc thử vài KB đầu file; nếu có byte NUL (0x00) thì coi là nhị phân.
    Đây là cách dò nhanh, không phụ thuộc vào đuôi file."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sample_size)
        return b"\x00" in chunk
    except Exception:
        return True


def scan_directory(root_path, ignored_folders=None):
    """Quét đệ quy `root_path`, trả về (chuỗi sơ đồ cây, danh_sách_đường_dẫn_file).

    - `ignored_folders`: danh sách tên thư mục cần bỏ qua hoàn toàn
      (không hiện trong sơ đồ, không đọc nội dung bên trong).
    - Mọi mục con được sắp xếp A-Z (không phân biệt hoa/thường) ở mỗi cấp.
    """
    ignored_folders = {f.lower() for f in (ignored_folders or [])}
    tree_lines = [os.path.basename(os.path.normpath(root_path)) + "/"]
    file_paths = []

    def walk(dir_path, prefix):
        try:
            entries = sorted(os.listdir(dir_path), key=lambda x: x.lower())
        except Exception as e:
            tree_lines.append(prefix + f"[Không thể đọc thư mục: {e}]")
            return

        entries = [e for e in entries if e.lower() not in ignored_folders]

        for i, entry in enumerate(entries):
            full_path = os.path.join(dir_path, entry)
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            branch = "    " if is_last else "│   "

            if os.path.isdir(full_path):
                tree_lines.append(prefix + connector + entry + "/")
                walk(full_path, prefix + branch)
            else:
                tree_lines.append(prefix + connector + entry)
                file_paths.append(full_path)

    walk(root_path, "")
    return "\n".join(tree_lines), file_paths


def read_file_content(file_path, ignored_extensions=None):
    """Đọc nội dung nếu file là văn bản UTF-8 hợp lệ.

    Trả về None nếu:
      - Đuôi file nằm trong `ignored_extensions` (danh sách người dùng tự cấu hình), hoặc
      - File bị phát hiện là nhị phân (byte NUL), hoặc
      - Không giải mã được bằng UTF-8.
    Không bao giờ ném lỗi ra ngoài (luôn bắt exception khi đọc)."""
    ignored_extensions = {e.lower() for e in (ignored_extensions or [])}
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ignored_extensions:
        return None
    if looks_binary(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return None
    except Exception as e:
        return f"[Lỗi khi đọc file: {e}]"


def build_output(
    root_path,
    ignored_folders=None,
    ignored_extensions=None,
    export_tree=True,
    export_content=True,
    tree_header="DIRECTORY TREE",
    content_header="FILE CONTENTS",
    binary_note="[Binary/unsupported file - content skipped]",
):
    """Ghép sơ đồ thư mục và/hoặc nội dung file thành chuỗi kết quả cuối cùng.

    `export_tree` / `export_content` cho phép bật/tắt từng phần độc lập
    (tương ứng 2 checkbox trên giao diện)."""
    tree_str, file_paths = scan_directory(root_path, ignored_folders)

    parts = []

    if export_tree:
        parts += ["=" * 60, tree_header, "=" * 60, tree_str, ""]

    if export_content:
        parts += ["=" * 60, content_header, "=" * 60, ""]
        for fp in file_paths:
            content = read_file_content(fp, ignored_extensions)
            parts.append(f"-----{fp}-----")
            parts.append(binary_note if content is None else content)
            parts.append("")

    return "\n".join(parts)
