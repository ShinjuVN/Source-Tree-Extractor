"""
Source Tree Extractor
======================
Ứng dụng GUI quét một thư mục, xuất sơ đồ cây thư mục và/hoặc nội dung
các file văn bản bên trong, cho phép xuất ra file .txt.

Cấu trúc project:
    main.py              <- file này (giao diện + điều phối)
    core/scanner.py       <- logic quét thư mục / đọc file (không phụ thuộc GUI)
    core/settings_manager.py <- đọc/ghi settings.json
    core/i18n.py           <- đa ngôn ngữ, đọc file lang/*.json
    settings.json          <- cấu hình (bỏ qua đuôi file/folder nào, ngôn ngữ...)
    lang/vi.json, lang/en.json <- gói ngôn ngữ, có thể tự thêm file mới
    assets/icon.ico         <- icon ứng dụng

QUAN TRỌNG khi đóng gói bằng PyInstaller (--onedir):
    settings.json và thư mục lang/ được đọc/ghi từ THƯ MỤC CHỨA FILE .EXE
    (không phải từ bên trong gói nội bộ _internal), để người dùng có thể
    chỉnh sửa trực tiếp mà không cần build lại. Xem BUILD.md để biết chi tiết.
"""

import sys
import os

import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.scanner import build_output
from core.settings_manager import SettingsManager
from core.i18n import I18N


# ----------------------------------------------------------------------
# Xác định đường dẫn: nơi chứa file .exe (hoặc main.py khi chạy bằng Python)
# ----------------------------------------------------------------------

def get_base_dir():
    """Thư mục chứa .exe khi đã đóng gói, hoặc thư mục chứa main.py khi
    chạy bằng Python. settings.json và lang/ luôn nằm ở đây (BÊN NGOÀI
    gói nội bộ của PyInstaller) để người dùng dễ chỉnh sửa."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(*parts):
    """Đường dẫn tới tài nguyên có thể được PyInstaller nhúng vào gói
    (vd: icon.ico). Ưu tiên tìm trong gói nội bộ (_MEIPASS) khi đã build,
    nếu không có thì tìm cạnh main.py/exe."""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        p = os.path.join(base, *parts)
        if os.path.exists(p):
            return p
        return os.path.join(os.path.dirname(sys.executable), *parts)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)


BASE_DIR = get_base_dir()
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
LANG_DIR = os.path.join(BASE_DIR, "lang")
ICON_ICO_PATH = resource_path("assets", "icon.ico")
ICON_PNG_PATH = resource_path("assets", "icon.png")


def set_window_icon(window):
    """Đặt icon cho cửa sổ, thử lần lượt 2 cách để tương thích nhiều nền tảng:

    1) iconbitmap(.ico) — CHỈ thật sự hoạt động trên Windows (đây là hành vi
       đặc thù của Tk: trên Linux/macOS, đường dẫn .ico bị coi là bitmap X11
       không hợp lệ và luôn lỗi, bất kể nội dung file đúng định dạng gì).
    2) iconphoto(.png) — hoạt động trên mọi nền tảng có Tk 8.6+ trở lên,
       dùng làm phương án chính/dự phòng khi cách 1 thất bại.

    Giữ tham chiếu tới PhotoImage trên chính đối tượng window để tránh bị
    trình dọn rác (garbage collector) thu hồi làm icon biến mất."""
    try:
        window.iconbitmap(ICON_ICO_PATH)
        return
    except Exception:
        pass
    try:
        img = tk.PhotoImage(file=ICON_PNG_PATH)
        window.iconphoto(True, img)
        window._icon_photo_ref = img
    except Exception:
        pass  # Không tìm thấy icon hoặc nền tảng không hỗ trợ -> bỏ qua, không crash


# ----------------------------------------------------------------------
# Sửa lỗi giao diện bị mờ trên Windows màn hình HiDPI: cần khai báo
# process DPI-aware TRƯỚC khi tạo cửa sổ Tk đầu tiên. Đây là nguyên nhân
# gốc khiến hộp thoại chọn folder/tkinter bị mờ trên nhiều máy Windows.
# ----------------------------------------------------------------------
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# ----------------------------------------------------------------------
# Cửa sổ Cài đặt
# ----------------------------------------------------------------------

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.i18n = app.i18n
        self.settings = app.settings

        self.title(self.i18n.t("settings_title"))
        self.geometry("560x520")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()  # modal
        set_window_icon(self)

        pad = {"padx": 18, "pady": (14, 4)}

        # --- Ngôn ngữ ---
        ctk.CTkLabel(self, text=self.i18n.t("settings_language"), anchor="w").pack(fill="x", **pad)
        self.app.i18n.scan_languages()  # nhận diện file ngôn ngữ mới người dùng vừa thêm
        self.lang_map = dict(self.app.i18n.available_languages)  # code -> display name
        self.lang_display_to_code = {v: k for k, v in self.lang_map.items()}
        current_code = self.settings.get("language", "vi")
        current_display = self.lang_map.get(current_code, next(iter(self.lang_map.values()), current_code))
        self.lang_var = tk.StringVar(value=current_display)
        ctk.CTkOptionMenu(self, values=list(self.lang_map.values()) or [current_display],
                          variable=self.lang_var).pack(fill="x", padx=18)

        # --- Tên file xuất mặc định ---
        ctk.CTkLabel(self, text=self.i18n.t("settings_default_filename"), anchor="w").pack(fill="x", **pad)
        self.filename_var = tk.StringVar(value=self.settings.get("default_output_filename", "source.txt"))
        ctk.CTkEntry(self, textvariable=self.filename_var).pack(fill="x", padx=18)

        # --- Định dạng file bỏ qua ---
        ctk.CTkLabel(self, text=self.i18n.t("settings_ignored_ext"), anchor="w",
                     wraplength=520, justify="left").pack(fill="x", **pad)
        self.ext_text = ctk.CTkTextbox(self, height=90)
        self.ext_text.pack(fill="x", padx=18)
        self.ext_text.insert("1.0", ", ".join(self.settings.get("ignored_extensions", [])))

        # --- Thư mục bỏ qua ---
        ctk.CTkLabel(self, text=self.i18n.t("settings_ignored_folders"), anchor="w",
                     wraplength=520, justify="left").pack(fill="x", **pad)
        self.folder_text = ctk.CTkTextbox(self, height=60)
        self.folder_text.pack(fill="x", padx=18)
        self.folder_text.insert("1.0", ", ".join(self.settings.get("ignored_folders", [])))

        # --- Nút Lưu / Hủy ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=18, pady=18)
        ctk.CTkButton(btn_frame, text=self.i18n.t("btn_save"),
                      command=self.save).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_frame, text=self.i18n.t("btn_cancel"), fg_color="gray40",
                      hover_color="gray30", command=self.destroy).pack(side="right")

    def save(self):
        selected_display = self.lang_var.get()
        lang_code = self.lang_display_to_code.get(selected_display, "vi")

        ext_raw = self.ext_text.get("1.0", "end").strip()
        exts = [e.strip().lower() for e in ext_raw.split(",") if e.strip()]
        exts = [e if e.startswith(".") else f".{e}" for e in exts]

        folder_raw = self.folder_text.get("1.0", "end").strip()
        folders = [f.strip() for f in folder_raw.split(",") if f.strip()]

        self.settings.set("language", lang_code)
        self.settings.set("default_output_filename", self.filename_var.get().strip() or "source.txt")
        self.settings.set("ignored_extensions", exts)
        self.settings.set("ignored_folders", folders)
        self.settings.save()

        self.app.apply_language(lang_code)
        messagebox.showinfo(self.app.i18n.t("settings_title"), self.app.i18n.t("settings_saved"))
        self.destroy()


# ----------------------------------------------------------------------
# Cửa sổ chính
# ----------------------------------------------------------------------

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.settings = SettingsManager(SETTINGS_PATH)
        self.i18n = I18N(LANG_DIR)
        self.i18n.load(self.settings.get("language", "vi"))

        self.selected_folder = None

        self.geometry("760x520")
        self.minsize(760, 520)
        set_window_icon(self)

        self.export_tree_var = tk.BooleanVar(value=self.settings.get("export_tree", True))
        self.export_content_var = tk.BooleanVar(value=self.settings.get("export_content", True))

        self._build_ui()
        self.apply_language(self.i18n.current_lang)

    # ------------------------------------------------------------------
    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(16, 8))

        self.btn_choose = ctk.CTkButton(top, command=self.choose_folder, width=150)
        self.btn_choose.pack(side="left")

        self.lbl_folder = ctk.CTkLabel(top, text="", anchor="w")
        self.lbl_folder.pack(side="left", padx=12, fill="x", expand=True)

        self.btn_settings = ctk.CTkButton(top, command=self.open_settings, width=44, text="⚙")
        self.btn_settings.pack(side="right")

        opts = ctk.CTkFrame(self, fg_color="transparent")
        opts.pack(fill="x", padx=16, pady=(0, 8))

        self.chk_tree = ctk.CTkCheckBox(opts, variable=self.export_tree_var,
                                         command=self._persist_checkbox_state)
        self.chk_tree.pack(side="left", padx=(0, 24))

        self.chk_content = ctk.CTkCheckBox(opts, variable=self.export_content_var,
                                            command=self._persist_checkbox_state)
        self.chk_content.pack(side="left")

        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 12))
        self.textbox.pack(fill="both", expand=True, padx=16, pady=8)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=16, pady=(0, 16))

        self.btn_export = ctk.CTkButton(bottom, command=self.export_file, width=150)
        self.btn_export.pack(side="right")

    def _persist_checkbox_state(self):
        self.settings.set("export_tree", self.export_tree_var.get())
        self.settings.set("export_content", self.export_content_var.get())
        self.settings.save()

    # ------------------------------------------------------------------
    def apply_language(self, lang_code):
        self.i18n.load(lang_code)
        t = self.i18n.t
        self.title(t("app_title"))
        self.btn_choose.configure(text=t("btn_choose_folder"))
        self.btn_export.configure(text=t("btn_export"))
        self.chk_tree.configure(text=t("chk_export_tree"))
        self.chk_content.configure(text=t("chk_export_content"))
        if not self.selected_folder:
            self.lbl_folder.configure(text=t("lbl_no_folder"))

    # ------------------------------------------------------------------
    def choose_folder(self):
        if not self.export_tree_var.get() and not self.export_content_var.get():
            messagebox.showwarning(self.i18n.t("app_title"), self.i18n.t("msg_select_option_first"))
            return

        folder = filedialog.askdirectory(title=self.i18n.t("btn_choose_folder"))
        if not folder:
            return

        self.selected_folder = folder
        self.lbl_folder.configure(text=folder)
        self.configure(cursor="watch")
        self.update_idletasks()

        try:
            result = build_output(
                folder,
                ignored_folders=self.settings.get("ignored_folders", []),
                ignored_extensions=self.settings.get("ignored_extensions", []),
                export_tree=self.export_tree_var.get(),
                export_content=self.export_content_var.get(),
                tree_header=self.i18n.t("tree_header"),
                content_header=self.i18n.t("content_header"),
                binary_note=self.i18n.t("binary_skip_note"),
            )
        except Exception as e:
            messagebox.showerror(self.i18n.t("app_title"), self.i18n.t("msg_scan_error", error=e))
            result = ""
        finally:
            self.configure(cursor="")

        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", result)

    def export_file(self):
        content = self.textbox.get("1.0", "end")
        if not content.strip():
            messagebox.showwarning(self.i18n.t("app_title"), self.i18n.t("msg_no_content_to_export"))
            return

        default_name = self.settings.get("default_output_filename", "source.txt")
        save_path = filedialog.asksaveasfilename(
            title=self.i18n.t("btn_export"),
            initialfile=default_name,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo(self.i18n.t("app_title"), self.i18n.t("msg_export_success", path=save_path))
        except Exception as e:
            messagebox.showerror(self.i18n.t("app_title"), self.i18n.t("msg_export_error", error=e))

    def open_settings(self):
        SettingsWindow(self, self)


if __name__ == "__main__":
    app = App()
    app.mainloop()
