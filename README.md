# Source Tree Extractor

Ứng dụng GUI (Python + [customtkinter](https://github.com/TomSchimansky/CustomTkinter))
giúp quét một thư mục, xuất ra:

1. **Sơ đồ cây thư mục** (file & folder, sắp xếp A-Z, có ký tự cây `├──`, `└──`).
2. **Nội dung các file văn bản** bên trong (tự động nhận diện UTF-8/text
   thuần, bỏ qua file nhị phân — ảnh, media, file nén...).

Có thể bật/tắt riêng từng phần (chỉ xuất sơ đồ, chỉ xuất nội dung, hoặc cả
hai), tuỳ chỉnh danh sách đuôi file / thư mục muốn bỏ qua, và hỗ trợ đa
ngôn ngữ (Tiếng Việt / English, có thể tự thêm ngôn ngữ khác).

## Tính năng

- Chọn 1 thư mục bất kỳ, quét đệ quy toàn bộ file/folder bên trong.
- 2 checkbox độc lập: **Xuất sơ đồ thư mục** và **Trích xuất nội dung file**.
- Tự động nhận diện file văn bản: đọc nội dung mọi file giải mã được UTF-8
  (kể cả file config không đuôi như `.env`, `.gitignore`, `Dockerfile`...),
  bỏ qua file nhị phân mà không cần khai báo thủ công từng đuôi.
- Cửa sổ **Cài đặt** riêng, gồm:
  - Chọn ngôn ngữ giao diện.
  - Đổi tên file xuất mặc định (mặc định `source.txt`).
  - Ô nhập **định dạng file bỏ qua** (ví dụ `.log, .csv`) — buộc bỏ qua
    nội dung dù đó là file text, chỉ liệt kê tên trong sơ đồ.
  - Ô nhập **thư mục bỏ qua** (ví dụ `.git, node_modules`) — loại hẳn
    khỏi sơ đồ, không quét bên trong.
- Nút **Xuất File**: lưu toàn bộ nội dung khung hiển thị ra file `.txt`
  (mở hộp thoại Lưu, tên mặc định lấy từ Cài đặt, có thể đổi tên/vị trí
  tuỳ ý mỗi lần xuất).
- Đa ngôn ngữ: sẵn có Tiếng Việt (`VN-vi`) và English (`EN-en`); người
  dùng tự thêm ngôn ngữ khác bằng cách thêm file JSON vào thư mục `lang/`
  (xem mục [Thêm ngôn ngữ mới](#thêm-ngôn-ngữ-mới)).
- Bắt lỗi toàn diện khi đọc file/quét thư mục — ứng dụng không bao giờ
  bị crash vì 1 file/folder lỗi.

## Cấu trúc project

```
SourceTreeExtractor/
├── main.py                    # Giao diện chính + điều phối
├── core/
│   ├── scanner.py              # Logic quét thư mục / đọc file (thuần, không phụ thuộc GUI)
│   ├── settings_manager.py     # Đọc/ghi settings.json
│   └── i18n.py                 # Hệ thống đa ngôn ngữ
├── lang/
│   ├── vi.json                 # Gói ngôn ngữ Tiếng Việt
│   └── en.json                 # Gói ngôn ngữ English
├── assets/
│   └── icon.ico                 # Icon ứng dụng
├── settings.json                 # Cấu hình (ngôn ngữ, đuôi/thư mục bỏ qua...)
├── requirements.txt
├── BUILD.md                      # Hướng dẫn đóng gói .exe (--onedir)
└── README.md                     # File này
```

---

## Cách 1: Cài đặt & chạy bằng file thực thi (.exe) — dành cho người dùng thường

1. Truy cập vào mục **[Releases](../../releases#release-Source-Tree-Extractor-Install)** của dự án trên GitHub.
2. Tải về file cài đặt mới nhất: **[Setup-Source-Tree-Extractor.exe](https://github.com/ShinjuVN/Picture-Lite/releases/download/Source-Tree-Extractor-Install/Setup-Source-Tree-Extractor.exe)** (hoặc bản Portable **[Source-Tree-Extractor-Portable.exe](https://github.com/ShinjuVN/Picture-Lite/releases/download/Source-Tree-Extractor-Install/Source-Tree-Extractor-Portable.exe)** nếu không muốn cài đặt).
3. Mở file **setup-Picture-Lite.exe** vừa tải về, làm theo các bước hướng dẫn trên màn hình cài đặt (chọn đường dẫn cài đặt, bấm *Next*).
4. Sau khi hoàn tất, bạn có thể khởi chạy ứng dụng trực tiếp từ **Shortcut ngoài Desktop** hoặc trong Menu Start.

---

## Cách 2: Chạy từ mã nguồn Python — dành cho lập trình viên / muốn tùy biến

### Yêu cầu

- Python 3.9 trở lên.
- Hệ điều hành có sẵn Tkinter (mặc định có trên Windows/macOS; trên một
  số bản Linux cần cài thêm gói `python3-tk`, ví dụ Ubuntu/Debian:
  `sudo apt install python3-tk`).

### Cài đặt thư viện

```bash
git clone <repo-url> SourceTreeExtractor
cd SourceTreeExtractor
pip install -r requirements.txt
```

### Chạy ứng dụng

```bash
python main.py
```

Ứng dụng sẽ tự tạo `settings.json` (nếu chưa có) ngay cạnh `main.py` với
giá trị mặc định.

### Đóng gói thành file `.exe`

Xem hướng dẫn đầy đủ, từng bước trong [BUILD.md](BUILD.md) — bao gồm cách
build ở chế độ `--onedir` và giữ `settings.json` / `lang/` nằm ngoài,
cùng cấp với file `.exe` để người dùng chỉnh sửa được mà không cần build
lại.

---

## Thêm ngôn ngữ mới

1. Mở thư mục `lang/`, sao chép file `en.json` thành file mới, ví dụ
   `lang/fr.json`.
2. Sửa 2 trường đầu tiên cho ngôn ngữ mới:
   ```json
   {
     "language_code": "fr",
     "language_name": "Français (FR-fr)",
     ...
   }
   ```
3. Dịch toàn bộ giá trị (giữ nguyên key) sang ngôn ngữ mong muốn.
4. Mở lại ứng dụng (hoặc mở cửa sổ **Cài đặt**) — ngôn ngữ mới sẽ tự xuất
   hiện trong danh sách chọn, không cần sửa code hay build lại.

## Quy tắc nhận diện file văn bản / nhị phân

- Ứng dụng **không** dựa vào một danh sách đuôi file cố định để quyết
  định file nào là "văn bản". Thay vào đó, nó thử đọc mọi file bằng
  UTF-8; nếu đọc thành công và không có dấu hiệu nhị phân (byte `NUL`),
  nội dung sẽ được đưa vào kết quả.
- Điều này đảm bảo các file config không có đuôi chuẩn (`.env`,
  `.gitignore`, `Dockerfile`, `Makefile`...) vẫn được đọc nội dung bình
  thường, thay vì bị bỏ sót như khi dùng whitelist đuôi file cứng.
- Mục **Định dạng file bỏ qua** trong Cài đặt dùng để **ép** bỏ qua nội
  dung của một số đuôi cụ thể (ví dụ `.log`, `.csv` quá dài dòng) dù bản
  thân chúng vẫn là file text — file đó vẫn hiện tên trong sơ đồ, chỉ
  không in nội dung.

## Giấy phép

Phát hành theo giấy phép [MIT](LICENSE).
