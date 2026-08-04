import os
import shutil
import markdown

# ============================================================
# 🌐 Fluigel MD → SPA HTML Fragment Builder
#    (Markdown → SPA용 HTML fragment 변환)
#    (전역 줄바꿈: nl2br 적용)
# ============================================================

ROOT_DIR = "."
UPLOAD_DIR = "./_Upload"


# ------------------------------------------------------------
# 1) 안전한 open (MD 원본 보호)
# ------------------------------------------------------------
def safe_open(path, mode="r", *args, **kwargs):
    if path.lower().endswith(".md") and any(m in mode for m in ("w", "a", "+")):
        raise ValueError(f"🚫 MD 원본 보호 — MD 파일은 수정 불가: {path}")
    return open(path, mode, *args, **kwargs)


# ------------------------------------------------------------
# 2) 플래그 기반 페이지 타입 감지
# ------------------------------------------------------------
def detect_page_type(md_text):
    first_line = md_text.lstrip().splitlines()[0] if md_text.strip() else ""

    flags = {
        "<!-- page-list -->": "page-list",
        "<!-- poem -->": "poem",
        "<!-- page-list-small -->": "page-list-small",
        "<!-- page-list-middle -->": "page-list-middle",
    }

    for flag, typ in flags.items():
        if first_line.strip() == flag:
            cleaned = md_text.replace(first_line, "", 1).lstrip()
            return typ, cleaned

    return "normal", md_text


# ------------------------------------------------------------
# 3) 타입별 후처리 (HTML 줄바꿈 정리)
# ------------------------------------------------------------
def postprocess(area_type, html):
    lines = html.splitlines()

    h1_html = ""
    body_html = html

    # 맨 앞 h1 분리
    if lines and lines[0].strip().startswith("<h1"):
        h1_html = lines[0]
        body_html = "\n".join(lines[1:]).lstrip()

    # --- PAGE LIST ---
    if area_type == "page-list":
        return (
            f'<div class="page-list">\n'
            f'{h1_html}\n'
            f'<div class="page-list-body">\n'
            f'{body_html}\n'
            f'</div>\n'
            f'</div>\n'
        )

    # --- PAGE LIST SMALL ---
    elif area_type == "page-list-small":
        return (
            f'<div class="page-list-small">\n'
            f'{h1_html}\n'
            f'<div class="page-list-small-body">\n'
            f'{body_html}\n'
            f'</div>\n'
            f'</div>\n'
        )

    # --- PAGE LIST MIDDLE ---
    elif area_type == "page-list-middle":
        return (
            f'<div class="page-list-middle">\n'
            f'{h1_html}\n'
            f'<div class="page-list-middle-body">\n'
            f'{body_html}\n'
            f'</div>\n'
            f'</div>\n'
        )

    # --- POEM: 다시 div 래핑 추가 ---
    elif area_type == "poem":
        return (
            f'<div class="poem">\n'
            f'{h1_html}\n'
            f'<div class="poem-body">\n'
            f'{body_html}\n'
            f'</div>\n'
            f'</div>\n'
        )

    # --- NORMAL ---
    else:
        return html + "\n"


# ------------------------------------------------------------
# 4) MD → HTML 변환
# ------------------------------------------------------------
def convert_one_md(md_path):
    with safe_open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    page_type, md_body = detect_page_type(md_text)

    html = markdown.markdown(
        md_body,
        extensions=["fenced_code", "tables", "toc", "nl2br"],
        output_format="html5"
    )

    html = postprocess(page_type, html)

    rel_path = os.path.relpath(os.path.dirname(md_path), ROOT_DIR)
    output_dir = os.path.join(UPLOAD_DIR, rel_path)
    os.makedirs(output_dir, exist_ok=True)

    out_file = os.path.join(
        output_dir,
        os.path.splitext(os.path.basename(md_path))[0] + ".html"
    )

    # ------------------------------------------------------------
    # 직접 HTML 주소로 접속했을 때 SPA 껍데기(index.html)로 자동 복귀
    # 예: /PalJeongdo/example.html → /#/PalJeongdo/example.html
    # 단, index.html 안에서 fetch로 불러온 경우에는 실행되지 않음
    # ------------------------------------------------------------
    spa_redirect_script = """<script>
(function () {
  if (!document.getElementById("menu-panel")) {
    const path = location.pathname.replace(/^\\/+/, "");
    location.replace("/#/" + path);
  }
})();
</script>

"""

    html = spa_redirect_script + html

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ 변환: {md_path} → {out_file}")


# ------------------------------------------------------------
# 5) 전체 디렉터리 순회
# ------------------------------------------------------------
def walk_and_convert(start_path):
    for subdir, _, files in os.walk(start_path):
        abs_path = os.path.abspath(subdir)

        name = os.path.basename(subdir)

        # '_'로 시작하는 폴더와 Images 폴더는 변환 대상에서 제외
        if name.startswith("_") or name == "Images":
            continue

        if UPLOAD_DIR in abs_path:
            continue

        for filename in files:
            if filename.lower().endswith(".md"):
                convert_one_md(os.path.join(subdir, filename))


# ------------------------------------------------------------
# 6) 실행
# ------------------------------------------------------------
if __name__ == "__main__":
    print("🔒 Fluegel-Protect Mode — MD 원본 보호 활성화")
    print("📦 Markdown → SPA Fragment Builder 시작")

    walk_and_convert(ROOT_DIR)

    # Images 폴더를 _Upload로 복사
    images_src = os.path.join(ROOT_DIR, "Images")
    images_dst = os.path.join(UPLOAD_DIR, "Images")

    if os.path.isdir(images_src):
        shutil.copytree(images_src, images_dst, dirs_exist_ok=True)
        print(f"✓ 복사: {images_src} → {images_dst}")

    print("\n🎉 모든 변환 완료 — HTML fragment 생성 완료!")
