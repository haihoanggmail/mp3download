# Trích xuất link Audio / Video — deploy lên Render

Thư mục này gồm 3 file cần đưa lên GitHub: `Dockerfile`, `server.py`, `index.html`.

## Bước 1. Đưa code lên GitHub (không cần cài git)
1. Đăng nhập https://github.com → bấm dấu **+** (góc trên phải) → **New repository**.
2. Đặt tên (ví dụ `media-extractor`), chọn **Private** nếu muốn giữ riêng → **Create repository**.
3. Ở trang repo trống, bấm **uploading an existing file**.
4. Kéo thả cả 3 file `Dockerfile`, `server.py`, `index.html` vào (để ở thư mục gốc, không bỏ trong thư mục con).
5. Bấm **Commit changes**.

## Bước 2. Tạo Web Service trên Render
1. Vào https://render.com → **Get Started** → đăng nhập bằng GitHub.
2. Bấm **New +** → **Web Service**.
3. Chọn **Build and deploy from a Git repository** → **Next**.
4. Nếu Render chưa thấy repo: bấm **Configure account** và cấp quyền cho repo `media-extractor`.
5. Chọn repo → **Connect**.

## Bước 3. Cấu hình
- **Name**: tuỳ ý (sẽ thành địa chỉ `ten.onrender.com`)
- **Region**: Singapore (gần Việt Nam nhất)
- **Branch**: `main`
- **Runtime / Language**: **Docker** (Render tự nhận từ Dockerfile)
- **Instance Type**: Free (hoặc gói trả phí nếu muốn không bị "ngủ")
- Không cần điền Build Command, Start Command hay biến môi trường.

Bấm **Deploy Web Service**.

## Bước 4. Dùng
- Chờ build 2–5 phút, tới khi thấy "Your service is live".
- Mở địa chỉ `https://ten-app.onrender.com` ở đầu trang.

## Bảo trì
- **Gói Free ngủ** sau ~15 phút không dùng; lần mở sau chờ ~30–60 giây.
- **Cập nhật yt-dlp** (khi Zing/YouTube bắt đầu lỗi): Render → service → **Manual Deploy** → **Clear build cache & deploy**.
- Sửa code: upload file mới lên GitHub, Render tự build lại.
- Xem lỗi chi tiết ở tab **Logs** của Render.

## Lưu ý
- Ai biết địa chỉ đều dùng được; đừng chia sẻ công khai.
- Một số trang (YouTube, đôi khi Zing) chặn IP máy chủ đám mây nên có thể lỗi dù chạy local vẫn được.
- Chỉ tải nội dung bạn có quyền sử dụng.
