<div align="center">

# 🧰 Git Commands Cheatsheet

> **Tài liệu tham khảo nhanh** — Tổng hợp các lệnh Git thường dùng nhất

![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![Version](https://img.shields.io/badge/Version-2.x-blue?style=for-the-badge)
![Language](https://img.shields.io/badge/Ngôn_ngữ-Tiếng_Việt-red?style=for-the-badge)

</div>

---

## 📑 Mục lục

| # | Nhóm lệnh | Mô tả |
|:-:|-----------|-------|
| 1 | [🚀 Khởi tạo & Cấu hình](#-khởi-tạo--cấu-hình) | `init`, `clone`, `config` |
| 2 | [📁 File & Staging Area](#-file--staging-area) | `add`, `status`, `diff` |
| 3 | [💾 Commit](#-commit) | `commit`, `log` |
| 4 | [🌿 Branch](#-branch-nhánh) | Tạo, chuyển, xóa nhánh |
| 5 | [🔀 Merge & Rebase](#-merge--rebase) | Gộp nhánh |
| 6 | [🌐 Remote](#-remote) | `push`, `pull`, `fetch` |
| 7 | [🔄 Hoàn tác](#-hoàn-tác-undo) | `reset`, `revert`, `restore` |
| 8 | [📦 Stash](#-stash-lưu-tạm) | Lưu tạm thay đổi |
| 9 | [🏷️ Tag](#️-tag-phiên-bản) | Quản lý phiên bản |
| 10 | [🔍 Tìm kiếm](#-tìm-kiếm--kiểm-tra) | `grep`, `blame`, `bisect` |
| 11 | [🛠️ Tiện ích](#️-tiện-ích-khác) | `reflog`, `clean`, ... |
| 12 | [💡 Workflow thực tế](#-quy-trình-làm-việc-thực-tế) | Feature Branch Workflow |

---

## 🚀 Khởi tạo & Cấu hình

```bash
# ── Khởi tạo repository mới ──────────────────────────────────
git init

# ── Cấu hình thông tin cá nhân ───────────────────────────────
git config --global user.name  "Tên của bạn"
git config --global user.email "email@example.com"

# ── Xem toàn bộ cấu hình ─────────────────────────────────────
git config --list

# ── Clone repository về máy ──────────────────────────────────
git clone <url>
git clone <url> <tên-thư-mục>         # Clone vào thư mục tùy chỉnh
```

---

## 📁 File & Staging Area

```bash
# ── Xem trạng thái ───────────────────────────────────────────
git status
git status -s                          # Rút gọn (short)

# ── Thêm file vào staging ─────────────────────────────────────
git add <tên-file>                     # Thêm file cụ thể
git add .                              # Thêm tất cả thay đổi
git add *.py                           # Thêm theo pattern

# ── Xóa file khỏi staging (giữ file trên ổ đĩa) ──────────────
git restore --staged <tên-file>

# ── Xem sự khác biệt ─────────────────────────────────────────
git diff                               # Chưa staged
git diff --staged                      # Đã staged, chưa commit
git diff <branch1> <branch2>           # So sánh hai branch
```

---

## 💾 Commit

```bash
# ── Tạo commit ───────────────────────────────────────────────
git commit -m "feat: thêm tính năng đăng nhập"
git commit -am "fix: sửa lỗi validate"   # Add + commit luôn

# ── Chỉnh sửa commit gần nhất (chưa push) ────────────────────
git commit --amend -m "Message mới"
git commit --amend --no-edit             # Giữ nguyên message

# ── Xem lịch sử commit ───────────────────────────────────────
git log                                  # Chi tiết đầy đủ
git log --oneline                        # Rút gọn 1 dòng
git log --oneline --graph --all          # Sơ đồ nhánh
git log -n 5                             # 5 commit gần nhất
git log --author="Tên"                   # Lọc theo tác giả
git log --since="2024-01-01"             # Lọc theo ngày
```

---

## 🌿 Branch (Nhánh)

```bash
# ── Xem danh sách ────────────────────────────────────────────
git branch                             # Branch local
git branch -r                          # Branch remote
git branch -a                          # Tất cả branch

# ── Tạo branch ───────────────────────────────────────────────
git branch <tên-branch>
git checkout -b <tên-branch>           # Tạo và chuyển ngay
git switch -c <tên-branch>             # ✨ Cú pháp mới

# ── Chuyển branch ────────────────────────────────────────────
git checkout <tên-branch>
git switch <tên-branch>                # ✨ Cú pháp mới

# ── Đổi tên branch ───────────────────────────────────────────
git branch -m <tên-mới>               # Đổi tên branch hiện tại

# ── Xóa branch ───────────────────────────────────────────────
git branch -d <tên-branch>            # Chỉ xóa nếu đã merge
git branch -D <tên-branch>            # Xóa bất kể đã merge chưa
git push origin --delete <tên-branch> # Xóa branch trên remote
```

---

## 🔀 Merge & Rebase

```bash
# ── Merge ────────────────────────────────────────────────────
git merge <tên-branch>                 # Merge vào branch hiện tại
git merge --no-ff <tên-branch>         # Luôn tạo merge commit
git merge --ff-only <tên-branch>       # Chỉ fast-forward

# ── Rebase ───────────────────────────────────────────────────
git rebase <tên-branch>                # Rebase lên branch khác
git rebase -i HEAD~3                   # Interactive: chỉnh 3 commit cuối

# ── Hủy khi có conflict ──────────────────────────────────────
git merge --abort
git rebase --abort
```

---

## 🌐 Remote

```bash
# ── Quản lý remote ───────────────────────────────────────────
git remote -v                          # Xem danh sách remote
git remote add origin <url>            # Thêm remote mới
git remote set-url origin <url-mới>    # Đổi URL remote
git remote remove <tên>                # Xóa remote

# ── Fetch & Pull ─────────────────────────────────────────────
git fetch origin                       # Tải về, không merge
git fetch --all                        # Tải tất cả remote
git pull                               # Fetch + merge
git pull origin <tên-branch>           # Pull từ branch cụ thể
git pull --rebase                      # Pull với rebase thay vì merge

# ── Push ─────────────────────────────────────────────────────
git push                               # Push branch hiện tại
git push origin <tên-branch>           # Push branch cụ thể
git push -u origin <tên-branch>        # Push + thiết lập tracking
git push --tags                        # Push tất cả tags
```

> [!WARNING]
> `git push --force` sẽ ghi đè lịch sử remote. Chỉ dùng khi thực sự cần thiết và biết mình đang làm gì!

---

## 🔄 Hoàn tác (Undo)

```bash
# ── Hoàn tác thay đổi chưa staged ────────────────────────────
git restore <tên-file>                 # Khôi phục về commit cuối

# ── Bỏ staged, giữ thay đổi ──────────────────────────────────
git restore --staged <tên-file>

# ── Hoàn tác commit (giữ code) ───────────────────────────────
git reset --soft HEAD~1                # Giữ thay đổi ở staging
git reset --mixed HEAD~1               # Giữ thay đổi ở working dir
git reset HEAD~1                       # (mặc định = --mixed)

# ── Tạo commit đảo ngược (an toàn với remote) ────────────────
git revert <commit-hash>
git revert HEAD                        # Revert commit mới nhất
```

> [!CAUTION]
> `git reset --hard HEAD~1` sẽ **xóa vĩnh viễn** các thay đổi chưa commit. Không thể khôi phục!

---

## 📦 Stash (Lưu tạm)

```bash
# ── Lưu tạm thay đổi ─────────────────────────────────────────
git stash                              # Lưu nhanh
git stash push -m "Đang làm dở login" # Lưu có tên mô tả

# ── Xem danh sách stash ──────────────────────────────────────
git stash list

# ── Áp dụng stash ────────────────────────────────────────────
git stash pop                          # Lấy ra + xóa khỏi danh sách
git stash apply stash@{2}              # Lấy ra, giữ trong danh sách
git stash apply stash@{0}              # Áp dụng stash đầu tiên

# ── Xóa stash ────────────────────────────────────────────────
git stash drop stash@{0}              # Xóa một stash
git stash clear                        # Xóa toàn bộ stash
```

---

## 🏷️ Tag (Phiên bản)

```bash
# ── Tạo tag ──────────────────────────────────────────────────
git tag v1.0.0                         # Lightweight tag
git tag -a v1.0.0 -m "Release 1.0.0"  # Annotated tag (khuyên dùng)

# ── Xem tag ──────────────────────────────────────────────────
git tag                                # Danh sách tag
git show v1.0.0                        # Chi tiết một tag

# ── Push tag lên remote ───────────────────────────────────────
git push origin v1.0.0                 # Push một tag
git push origin --tags                 # Push tất cả tag

# ── Xóa tag ──────────────────────────────────────────────────
git tag -d v1.0.0                      # Xóa local
git push origin --delete v1.0.0        # Xóa remote
```

---

## 🔍 Tìm kiếm & Kiểm tra

```bash
# ── Tìm kiếm nội dung trong code ─────────────────────────────
git grep "từ-khóa"
git grep -n "từ-khóa"                  # Kèm số dòng

# ── Xem ai chỉnh sửa từng dòng ───────────────────────────────
git blame <tên-file>
git blame -L 10,20 <tên-file>          # Chỉ xem dòng 10-20

# ── Xem nội dung một commit ──────────────────────────────────
git show <commit-hash>
git show HEAD                          # Commit gần nhất

# ── Tìm commit gây ra bug ────────────────────────────────────
git bisect start
git bisect bad                         # Commit hiện tại là bad
git bisect good <commit-hash>          # Commit cũ còn tốt
git bisect reset                       # Kết thúc bisect
```

---

## 🛠️ Tiện ích Khác

```bash
# ── Xem lịch sử di chuyển HEAD ───────────────────────────────
git reflog                             # Cứu khi lỡ reset --hard

# ── Dọn dẹp file không được track ────────────────────────────
git clean -n                           # Preview trước (dry run)
git clean -fd                          # Xóa file + thư mục

# ── Sao chép commit từ branch khác ───────────────────────────
git cherry-pick <commit-hash>

# ── Tạm dừng tracking file (nhưng không xóa) ─────────────────
git update-index --assume-unchanged <file>
```

---

## 💡 Quy trình làm việc thực tế

### Feature Branch Workflow

```bash
# ① Luôn bắt đầu từ nhánh main mới nhất
git checkout main
git pull origin main

# ② Tạo nhánh tính năng mới
git checkout -b feature/user-authentication

# ③ Làm việc, commit thường xuyên
git add .
git commit -m "feat: thêm form đăng nhập"
git commit -m "feat: thêm JWT authentication"
git commit -m "test: thêm unit test cho auth"

# ④ Đẩy nhánh lên remote
git push -u origin feature/user-authentication

# ⑤ Tạo Pull Request trên GitHub/GitLab (làm trên web)

# ⑥ Sau khi PR được approve & merge, dọn dẹp
git checkout main
git pull origin main
git branch -d feature/user-authentication
```

---

## 📝 Chuẩn Commit Message (Conventional Commits)

| Prefix | Ý nghĩa | Ví dụ |
|--------|---------|-------|
| `feat:` | ✨ Thêm tính năng mới | `feat: thêm trang đăng ký` |
| `fix:` | 🐛 Sửa bug | `fix: sửa lỗi token hết hạn` |
| `docs:` | 📚 Cập nhật tài liệu | `docs: cập nhật README` |
| `style:` | 💅 Format, không đổi logic | `style: format lại code` |
| `refactor:` | ♻️ Tái cấu trúc code | `refactor: tách service layer` |
| `test:` | 🧪 Thêm/sửa test | `test: thêm test cho auth API` |
| `chore:` | 🔧 Cấu hình, dependencies | `chore: cập nhật requirements.txt` |
| `perf:` | ⚡ Tối ưu hiệu năng | `perf: cache kết quả query` |

---

<div align="center">

*Được tạo bởi Antigravity • Cập nhật: 2026*

</div>
