import streamlit as st
import requests
import streamlit.components.v1 as components

import os

# =====================================================================
# ★ Notion 設定（從環境變數或 Streamlit Secrets 讀取）★
NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or st.secrets.get("NOTION_TOKEN", "")
DATABASE_ID = os.environ.get("DATABASE_ID") or st.secrets.get("DATABASE_ID", "")
# =====================================================================

st.set_page_config(
    page_title="BGLARP 實境推理館",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 全局自訂 CSS 注入，重現 React 版面風格
st.markdown("""
<style>
/* Reset and base */
.stApp {
    background-color: #000;
    color: #cbd5e1;
    font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    overflow-x: hidden;
}

/* 隱藏預設 header / padding */
header[data-testid="stHeader"], .stDeployButton {
    display: none !important;
}
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* 自訂捲軸 */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #b91c1c; }

/* Notion 匯入區塊專用 Hover Card */
.react-card {
    position: relative;
    aspect-ratio: 2/3;
    overflow: hidden;
    background-color: #111;
    border-radius: 4px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
    cursor: pointer;
    margin-bottom: 0px; 
    isolation: isolate;
}

/* 確保容器可以讓 absolute 的按鈕正確定位 */
div[data-testid="stVerticalBlock"] > div {
    position: relative;
}

/* 圖片預設 */
.react-card-img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    opacity: 0.95;
    transition: opacity 0.5s ease-in-out, transform 0.5s ease-in-out;
    z-index: 1;
}
/* 由卡片自身控制 Hover */
.react-card:hover .react-card-img {
    opacity: 0.15;
    transform: scale(1.05);
}

/* 漸色遮罩預設 */
.react-card-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.6) 25%, transparent 60%);
    pointer-events: none;
    z-index: 2;
    transition: background 0.4s ease-in-out, backdrop-filter 0.4s ease-in-out;
}
.react-card:hover .react-card-overlay {
    background: rgba(10, 10, 10, 0.95);
    backdrop-filter: blur(4px);
}

/* 預設狀態資訊 (置底) */
.react-card-default {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    padding: 20px;
    opacity: 1;
    transform: translateY(0);
    transition: opacity 0.4s ease-in-out, transform 0.4s ease-in-out;
    z-index: 3;
    pointer-events: none;
}
.react-card:hover .react-card-default {
    opacity: 0;
    transform: translateY(20px);
}

/* Hover 狀態資訊 (置中) */
.react-card-hover {
    position: absolute;
    inset: 0;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.4s ease-in-out, transform 0.4s ease-in-out;
    pointer-events: none;
    z-index: 4;
}
.react-card:hover .react-card-hover {
    opacity: 1;
    transform: translateY(0);
}



/* st.dialog 彈出視窗樣式 */
section[data-testid="stDialog"] > div {
    background-color: #09090b !important;
    border: 1px solid #dc2626 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 50px rgba(220, 38, 38, 0.1) !important;
}

/* 篩選器樣式 */
div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.05) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 4px;
}

/* 隱藏 dialog 空白標題 */
section[data-testid="stDialog"] [data-testid="stDialogTitle"] {
    display: none !important;
}

/* 「展示更多」按鈕樣式 */
button[data-testid="stBaseButton-secondary"][kind="secondary"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: rgba(255,255,255,0.8) !important;
    letter-spacing: 0.1em !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s !important;
}
button[data-testid="stBaseButton-secondary"][kind="secondary"]:hover {
    background: #b91c1c !important;
    border-color: #dc2626 !important;
    color: white !important;
}
/* ===== 手機版響應式設計 ===== */
@media (max-width: 768px) {
    /* 導覽列：縮小字體與間距 */
    nav div[style*="gap: 2rem"] {
        gap: 1rem !important;
        font-size: 0.75rem !important;
    }
    nav div[style*="font-size: 1.5rem"] {
        font-size: 1.1rem !important;
    }
    
    /* 卡片：手機上兩欄為主 */
    .react-card {
        aspect-ratio: 2/3;
        margin-bottom: 0 !important;
    }
    .react-card-default h3 {
        font-size: 0.85rem !important;
    }
    .react-card-hover {
        padding: 12px !important;
    }
    .react-card-hover h3 {
        font-size: 0.9rem !important;
    }
    .react-card-hover p {
        font-size: 0.7rem !important;
    }
    
    /* 「展示更多」按鈕 */
    button[data-testid="stBaseButton-secondary"][kind="secondary"] {
        padding: 0.5rem 1rem !important;
        font-size: 0.85rem !important;
    }
}

@media (max-width: 480px) {
    .react-card-default h3 {
        font-size: 0.75rem !important;
    }
    .react-card-hover h3 {
        font-size: 0.8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ================= 頂部導覽列與 Hero Section =================
hero_html = """<nav style="position: fixed; width: 100%; z-index: 50; top: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); padding: 1.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
<div style="display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 0 auto; padding: 0 2rem;">
<div style="color: white; font-size: 1.2rem; font-weight: bold; letter-spacing: 0.15em; font-family: serif; display: flex; align-items: center; gap: 8px;">
<span style="color: #dc2626;">🎬</span> BGLARP實境推理館
</div>
<div style="display: flex; gap: 2rem; font-size: 0.875rem; letter-spacing: 0.1em; text-transform: uppercase;">
<a href="#about" style="color: white; text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='white'">關於本館</a>
<a href="#scripts" style="color: white; text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='white'">上映劇本</a>
<a href="#booking" style="color: white; text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='white'">預約入戲</a>
</div>
</div>
</nav>

<section style="position: relative; height: 60vh; min-height: 400px; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #000;">
<div style="position: absolute; inset: 0; z-index: 0;">
<div style="position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.4) 50%, #000 100%); z-index: 10;"></div>
<img src="https://images.unsplash.com/photo-1519074069444-1ba4fff66d16?q=80&w=2000&auto=format&fit=crop" style="width: 100%; height: 100%; object-fit: cover;">
</div>

<div style="position: relative; z-index: 20; text-align: center; padding: 0 1rem; margin-top: 4rem;">
<div style="color: #dc2626; font-weight: bold; letter-spacing: 0.4em; margin-bottom: 1.5rem; font-size: 0.85rem;">CINEMATIC LARP EXPERIENCE</div>
<p style="font-size: 1.05rem; color: #e5e7eb; letter-spacing: 0.15em; line-height: 2; margin-bottom: 2.5rem; max-width: 650px; margin-inline: auto; text-shadow: 0 2px 10px rgba(0,0,0,0.8); font-weight: 300;">
打破現實與虛構的邊界。<br>穿上戲服，走進專屬場景，在 BGLARP 演繹你的第二人生。
</p>
<a href="#scripts" style="display: inline-block; padding: 0.8rem 2.5rem; border: 1px solid rgba(220, 38, 38, 0.5); background-color: rgba(185, 28, 28, 0.15); backdrop-filter: blur(4px); color: white; font-size: 0.9rem; letter-spacing: 0.15em; text-decoration: none; transition: all 0.3s; border-radius: 2px;" onmouseover="this.style.backgroundColor='rgba(220, 38, 38, 0.8)'; this.style.borderColor='#dc2626';" onmouseout="this.style.backgroundColor='rgba(185, 28, 28, 0.15)'; this.style.borderColor='rgba(220, 38, 38, 0.5)';">
查看熱映劇本
</a>
</div>
</section>"""
st.markdown(hero_html, unsafe_allow_html=True)


# ================= Fetch Notion Data & Setup Modal =================
@st.cache_data(ttl=600)
def fetch_notion_data(token, db_id):
    if not token or not db_id or token == "YOUR_NOTION_API_KEY": return []
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    pages = []
    has_more = True
    next_cursor = None
    while has_more:
        payload = {"page_size": 100}
        if next_cursor: payload["start_cursor"] = next_cursor
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=15)
            r.raise_for_status()
            d = r.json()
            pages.extend(d.get("results", []))
            has_more = d.get("has_more", False)
            next_cursor = d.get("next_cursor")
        except:
            break
    return pages

def get_text(props, key, is_title=False):
    t_type = "title" if is_title else "rich_text"
    arr = props.get(key, {}).get(t_type, [])
    return "".join(x.get("plain_text", "") for x in arr)

@st.dialog(" ", width="large")
def show_script_modal(card):
    # ===== 內頁專屬 CSS =====
    st.markdown("""<style>
.modal-poster-wrap {position: relative; border-radius: 12px; overflow: hidden; border: 1px solid #27272a; box-shadow: 0 25px 50px rgba(0,0,0,0.8); margin-bottom: 24px;}
.modal-poster-wrap .modal-poster-bg {width: 100%; min-height: 400px; display: block; background-size: contain; background-position: center; background-repeat: no-repeat; transition: transform 0.7s ease;}
.modal-poster-wrap:hover .modal-poster-bg {transform: scale(1.03);}
.modal-poster-grad {position: absolute; inset: 0; background: linear-gradient(to top, #000 0%, transparent 60%, rgba(0,0,0,0.15) 100%); pointer-events: none;}
.modal-poster-title {position: absolute; bottom: 24px; left: 28px; right: 28px;}
.modal-poster-title h1 {font-size: 2.4rem; font-family: serif; font-weight: bold; letter-spacing: 0.02em; margin: 0 0 4px 0; color: white; text-shadow: 0 4px 20px rgba(0,0,0,0.8);}
.modal-tag {display: inline-block; padding: 3px 10px; font-size: 9px; letter-spacing: 0.15em; border: 1px solid #3f3f46; background: rgba(24,24,27,0.5); color: #a1a1aa; margin-right: 6px; margin-bottom: 6px;}
.info-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: 3px; padding: 3px; background: rgba(39,39,42,0.3); border-radius: 10px; border: 1px solid #27272a; margin-bottom: 20px;}
.info-card {display: flex; align-items: center; gap: 14px; padding: 16px 20px; background: #111112; border-radius: 8px;}
.info-card .info-icon {flex-shrink: 0;}
.info-card .info-label {font-size: 9px; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;}
.info-card .info-value {font-size: 1.05rem; font-weight: 500; color: #e4e4e7;}
.synopsis-para {color: #a1a1aa; line-height: 1.8; letter-spacing: 0.04em; font-weight: 300; border-left: 2px solid transparent; padding-left: 16px; margin-bottom: 16px; transition: border-color 0.3s;}
.synopsis-para:hover {border-left-color: rgba(220,38,38,0.5);}
/* 角色頭像卡片 */
.char-avatar-grid { padding-top: 12px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px 16px; }
.char-avatar-item { display: flex; flex-direction: column; align-items: center; text-align: center; }
.char-avatar-img { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #27272a; margin-bottom: 10px; transition: border-color 0.3s, transform 0.3s; background: #18181b; }
.char-avatar-item:hover .char-avatar-img { border-color: #dc2626; transform: scale(1.08); }
.char-avatar-name { font-size: 0.85rem; font-weight: 600; letter-spacing: 0.08em; color: #e4e4e7; margin-bottom: 2px; }
.char-avatar-desc { font-size: 0.7rem; color: #71717a; line-height: 1.5; font-weight: 300; max-width: 120px; }
div[data-testid="stTabs"] button[data-baseweb="tab"] {font-size: 0.85rem !important; letter-spacing: 0.15em !important; color: #71717a !important; padding-bottom: 12px !important;}
div[data-testid="stTabs"] button[aria-selected="true"] {color: white !important; border-bottom-color: #dc2626 !important;}
/* === Modal 手機版響應式 === */
@media (max-width: 768px) {
    .modal-poster-wrap .modal-poster-bg { min-height: 250px; }
    .modal-poster-title h1 { font-size: 1.5rem !important; }
    .modal-poster-title { bottom: 16px; left: 16px; right: 16px; }
    .info-grid { grid-template-columns: 1fr !important; gap: 2px; }
    .info-card { padding: 12px 16px; gap: 10px; }
    .info-card .info-value { font-size: 0.9rem; }
    .char-avatar-grid { grid-template-columns: repeat(3, 1fr) !important; gap: 16px 12px; }
    .char-avatar-img { width: 64px; height: 64px; }
    .char-avatar-name { font-size: 0.75rem; }
    .char-avatar-desc { font-size: 0.65rem; max-width: 90px; }
    .synopsis-para { padding-left: 12px; font-size: 0.85rem; }
}
@media (max-width: 480px) {
    .modal-poster-wrap .modal-poster-bg { min-height: 200px; }
    .modal-poster-title h1 { font-size: 1.3rem !important; }
    .char-avatar-grid { grid-template-columns: repeat(2, 1fr) !important; }
}
</style>""", unsafe_allow_html=True)

    # ===== 海報展示區（頂部全寬，帶漸層遮罩與浮動標題）=====
    fallback_img = "https://images.unsplash.com/photo-1505635552518-3448ff116af3?q=80&w=800&auto=format&fit=crop"
    st.markdown(f"""<div class="modal-poster-wrap">
<div class="modal-poster-bg" style="background-image: url('{card['image']}'), url('{fallback_img}');"></div>
<div class="modal-poster-grad"></div>
<div class="modal-poster-title">
<h1>{card['name']}</h1>
</div>
</div>""", unsafe_allow_html=True)

    # ===== 標籤列 =====
    genre_text = card.get('genre', '') or ''
    genre_tags = [g.strip() for g in genre_text.replace('/', ',').replace('、', ',').split(',') if g.strip()]
    all_tags = card['players'] + genre_tags
    tags_html = "".join([f'<span class="modal-tag">{t}</span>' for t in all_tags])
    st.markdown(f'<div style="margin-bottom: 16px;">{tags_html}</div>', unsafe_allow_html=True)

    # 資訊網格（人數 / 時長 / 價格）
    dur = card['duration'] or '未標示'
    price = f"NT$ {card['price']}/人" if card['price'] else '價格未定'
    players_str = ", ".join(card['players'])

    svg_users = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
    svg_clock = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#eab308" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
    svg_dollar = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 18V6"/></svg>'

    st.markdown(f"""<div class="info-grid">
<div class="info-card"><div class="info-icon">{svg_users}</div><div><div class="info-label">人數限制</div><div class="info-value">{players_str}</div></div></div>
<div class="info-card"><div class="info-icon">{svg_clock}</div><div><div class="info-label">預估時長</div><div class="info-value">{dur}</div></div></div>
<div class="info-card"><div class="info-icon">{svg_dollar}</div><div><div class="info-label">收費標準</div><div class="info-value">{price}</div></div></div>
</div>""", unsafe_allow_html=True)

    # ===== 分頁切換：劇情指引 / 角色檔案 =====
    tab_synopsis, tab_chars = st.tabs(["劇情指引 (Synopsis)", "角色檔案 (Characters)"])

    with tab_synopsis:
        synopsis = card.get('synopsis', '') or '（資料未建立或遭受損毀）'
        paragraphs = [p.strip() for p in synopsis.split('\n') if p.strip()]
        para_html = "".join([f'<p class="synopsis-para">{p}</p>' for p in paragraphs])
        st.markdown(f'<div style="padding-top: 12px;">{para_html}</div>', unsafe_allow_html=True)

    with tab_chars:
        chars = card.get('characters', '')
        if chars:
            lines = [l.strip() for l in chars.split('\n') if l.strip()]
            # 頭像風格列表 (DiceBear avatars)
            avatar_styles = ['adventurer', 'avataaars', 'big-ears', 'lorelei', 'micah', 'miniavs', 'personas', 'bottts']
            chars_html = ""
            for idx, line in enumerate(lines):
                # 解析名字與介紹（支援 ： 或 - 分隔）
                char_name = line
                char_desc = ""
                for sep in ['：', ':', '－', ' - ']:
                    if sep in line:
                        parts = line.split(sep, 1)
                        char_name = parts[0].strip()
                        char_desc = parts[1].strip()
                        break
                
                # 每個角色用不同的 DiceBear 風格
                style = avatar_styles[idx % len(avatar_styles)]
                seed = f"{card['name']}_{char_name}_{idx}"
                avatar_url = f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}&backgroundColor=1a1a2e,16213e,0f3460,1b1b2f&radius=50"
                
                desc_html = f'<div class="char-avatar-desc">{char_desc}</div>' if char_desc else ''
                chars_html += f'''<div class="char-avatar-item">
<img src="{avatar_url}" class="char-avatar-img" alt="{char_name}">
<div class="char-avatar-name">{char_name}</div>
{desc_html}
</div>'''
            st.markdown(f'<div class="char-avatar-grid">{chars_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: #71717a; padding-top: 12px; letter-spacing: 0.05em;">（尚無角色資料）</p>', unsafe_allow_html=True)

    # ===== 馬上預約按鈕 =====
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    st.markdown("""<div style="text-align: center;"><a href="https://www.facebook.com/bglarp.studio/" target="_blank" style="display: inline-block; padding: 12px 40px; background: #dc2626; color: white; font-weight: 700; font-size: 0.9rem; letter-spacing: 0.25em; text-decoration: none; border-radius: 4px; transition: all 0.3s;" onmouseover="this.style.background='#b91c1c';" onmouseout="this.style.background='#dc2626';">馬上預約 →</a></div>""", unsafe_allow_html=True)


# ================= Scripts Section =================
st.markdown('<div id="scripts" style="padding-top: 6rem; background: #000;"></div>', unsafe_allow_html=True)

with st.spinner("影片載入中..."):
    pages = fetch_notion_data(NOTION_TOKEN, DATABASE_ID)

# 為了控制寬度，使用列切分 (左右留白，中間主內容)
_, main_col, _ = st.columns([1, 10, 1])

with main_col:
    # 標題區
    st.markdown("""
    <div style="margin-bottom: 3rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 1rem;">
        <div>
            <span style="color: #dc2626; font-weight: bold; letter-spacing: 0.2em; font-size: 0.8rem; display: block; margin-bottom: 0.5rem;">NOW SHOWING</span>
            <h2 style="font-size: 2.5rem; font-family: serif; font-weight: bold; color: white; letter-spacing: 0.1em; margin: 0;">現正熱映</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 搜尋過濾 UI (改為雙下拉選單)
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        player_filter = st.selectbox("人數", ["全部", "5人", "6人", "7人", "8人", "9人以上"], label_visibility="collapsed")
    with f2:
        genre_filter = st.selectbox("類型", ["全部", "推理", "硬核", "沉浸", "恐怖", "機制"], label_visibility="collapsed")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # 當篩選條件變更時，重置分頁
    filter_key = f"{player_filter}_{genre_filter}"
    if st.session_state.get("_last_filter_key") != filter_key:
        st.session_state.show_all_scripts = False
        st.session_state["_last_filter_key"] = filter_key
    
    display_data = []
    placeholder_img = "https://images.unsplash.com/photo-1505635552518-3448ff116af3?q=80&w=800&auto=format&fit=crop"
    
    if pages:
        for p in pages:
            props = p.get("properties", {})
            name = get_text(props, "劇本名稱", True) or "未命名"
            synopsis = get_text(props, "劇情簡介")
            characters = get_text(props, "角色")
            genre = get_text(props, "類型標籤")
            duration = get_text(props, "時長")
            price = props.get("價格", {}).get("number")
            players = [o.get("name") for o in props.get("人數", {}).get("multi_select", [])]
            
            # 類型篩選 (關鍵字比對)
            if genre_filter != "全部":
                if not genre or genre_filter not in genre:
                    continue
            
            # 人數篩選
            if player_filter != "全部":
                is_match = False
                for p_tag in players:
                    if player_filter == p_tag:
                        is_match = True
                        break
                    elif player_filter == "9人以上":
                        # 如果標籤是如 "9人", "10人" 等，或者標籤字串中包含這些數字
                        import re
                        match = re.search(r'(\d+)', p_tag)
                        if match and int(match.group(1)) >= 9:
                            is_match = True
                            break
                            
                if not is_match: 
                    continue
                
            # 優先抓取 Notion 的封面照片，若無則使用預設圖
            cover_obj = p.get("cover") or {}
            image_url = placeholder_img
            if cover_obj:
                ctype = cover_obj.get("type", "")
                if ctype == "external":
                    url = (cover_obj.get("external") or {}).get("url", "")
                    if url and url.startswith("http"):
                        image_url = url
                elif ctype == "file":
                    url = (cover_obj.get("file") or {}).get("url", "")
                    if url and url.startswith("http"):
                        image_url = url
                    
            display_data.append({
                "name": name, "synopsis": synopsis, "genre": genre,
                "duration": duration, "price": price, "players": players,
                "image": image_url, "characters": characters
            })
            
    if not display_data:
        st.info("無符合條件之劇本。")
    else:
        # 預設顯示 10 個，每次展開追加 10 個
        INITIAL_COUNT = 10
        if "script_display_limit" not in st.session_state:
            st.session_state.script_display_limit = INITIAL_COUNT
            
        visible_data = display_data[:st.session_state.script_display_limit]
        
        # 5 欄式網格（桌面 5 欄，手機自動堆疊為 1 欄）
        cols_per_row = 5
        for i in range(0, len(visible_data), cols_per_row):
            cols = st.columns(cols_per_row)
            row_items = visible_data[i : i+cols_per_row]
            
            for j, card in enumerate(row_items):
                with cols[j]:
                    # 處理卡片顯示的標籤 (人數 + 類型)
                    player_tags = card['players'][:1]
                    genre_text = card.get('genre', '') or ''
                    genre_parts = [g.strip() for g in genre_text.replace('/', ',').replace('、', ',').split(',') if g.strip()]
                    genre_label = ' X '.join(genre_parts) if genre_parts else ''
                    
                    tag_style = 'font-size: 11px; font-weight: bold; letter-spacing: 0.05em; border: 1px solid rgba(255,255,255,0.4); padding: 5px 8px; color: rgba(255,255,255,0.9); backdrop-filter: blur(4px); margin-right: 5px; margin-bottom: 5px; display: inline-block;'
                    tags_html = ''.join([f'<span style="{tag_style}">{t}</span>' for t in player_tags])
                    if genre_label:
                        tags_html += f'<span style="{tag_style}">{genre_label}</span>'
                    
                    dur_str = card['duration'] if card['duration'] else "未知"
                    price_str = str(card['price']) if card['price'] else "未定"
                    players_str = ", ".join(card['players'])
                    
                    # 定義紅線框 SVG icon
                    svg_users = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
                    svg_clock = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
                    svg_ticket = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2"/><path d="M13 17v2"/><path d="M13 11v2"/></svg>'

                    import urllib.parse
                    url_script_name = urllib.parse.quote(card['name'])
                    
                    # 生成 Hover Card (用 <a> 標籤包裝，點擊後會在網址加上 ?script=劇本名稱)
                    card_html = f"""
<a href="?script={url_script_name}" target="_self" style="text-decoration: none; display: block; width: 100%; height: 100%;">
<div class="react-card">
<div class="react-card-img" style="background-image: url('{card['image']}'), url('{placeholder_img}');"></div>
<div class="react-card-overlay"></div>

<!-- 預設顯示 (底部) -->
<div class="react-card-default">
<div style="display: flex; flex-wrap: wrap; margin-bottom: 12px;">{tags_html}</div>
<h3 style="font-size: 1.35rem; font-family: serif; font-weight: bold; color: white; letter-spacing: 0.05em; margin: 0 0 8px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">{card['name']}</h3>
</div>

<!-- Hover 顯示 (滿版資訊與簡介預覽) -->
<div class="react-card-hover" style="background: rgba(10,10,10,0.95); backdrop-filter: blur(8px);">
<h3 style="font-size: 1.7rem; font-family: serif; font-weight: bold; color: white; letter-spacing: 0.05em; margin: 0 0 16px 0; border-bottom: 1px solid rgba(220, 38, 38, 0.5); padding-bottom: 12px;">{card['name']}</h3>
<div style="font-size: 1.05rem; color: #d1d5db; letter-spacing: 0.05em; margin-bottom: 16px; line-height: 1.6;">
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">{svg_users} {players_str}</div>
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">{svg_clock} {dur_str}</div>
<div style="display: flex; align-items: center; gap: 10px;">{svg_ticket} NT$ {price_str}</div>
</div>
<div style="font-size: 1rem; color: #9ca3af; line-height: 1.7; max-height: calc(1.7em * 6); overflow: hidden; display: -webkit-box; -webkit-line-clamp: 6; -webkit-box-orient: vertical; margin-bottom: 0; text-overflow: ellipsis; white-space: pre-wrap;">
{card['synopsis'] or "無簡介..."}
</div>
</div>
</div>
</a>"""
                    
                    st.markdown(card_html, unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
        
        # 「展示更多」按鈕
        if len(display_data) > st.session_state.script_display_limit:
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
            with btn_col2:
                if st.button("顯示更多", key="show_more_scripts", use_container_width=True):
                    st.session_state.script_display_limit += 10
                    st.rerun()


# ================= 網址參數解析 (獨立連結支援) =================
# 如果使用者透過點擊劇本封面的 <a> 連結進入 (網址後帶有 ?script=劇本名稱)
if "script" in st.query_params:
    target_script_name = st.query_params["script"]
    # 找到對應的劇本資料
    target_script = next((s for s in safe_display_data if s["name"] == target_script_name), None)
    if target_script:
        # 清除參數避免重新整理一直開著
        st.query_params.clear()
        # 觸發顯示 Modal
        show_script_modal(target_script)

# ================= Booking / Footer Section =================
booking_html = """
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0; padding:0; background:#000; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
<section id="booking" style="padding: 6rem 0; background-color: #09090b; border-top: 1px solid rgba(255,255,255,0.05);">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem; display: flex; flex-wrap: wrap; gap: 4rem;">
        <div style="flex: 1; min-width: 300px;">
            <span style="color: #dc2626; font-weight: bold; letter-spacing: 0.2em; font-size: 0.875rem; display: block; margin-bottom: 0.5rem;">BOX OFFICE</span>
            <h2 style="font-size: 2.5rem; font-family: serif; font-weight: bold; color: white; letter-spacing: 0.1em; margin-bottom: 2rem; margin-top: 0;">預約入戲</h2>
            <p style="color: #9ca3af; line-height: 1.8; letter-spacing: 0.05em; margin-bottom: 1rem; font-size: 0.95rem;">
                BGLARP實境推理館採全預約制。為確保最佳的遊戲體驗，請提前至少 3 天透過臉書專頁私訊或致電進行預約。
            </p>
            <p style="color: #9ca3af; line-height: 1.8; letter-spacing: 0.05em; margin-bottom: 3rem; font-size: 0.95rem;">
                新手玩家無須擔心，預約時告知我們，客服將為您推薦最適合的入門劇本。每場次皆提供相應時代風格之服裝，為求完美沉浸，建議提早 15 分鐘到場換裝。
            </p>
            
            <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem; align-items: flex-start;">
                <div style="width: 48px; height: 48px; background: #18181b; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #dc2626;">📍</div>
                <div>
                    <h4 style="color: white; margin: 0 0 0.4rem 0; letter-spacing: 0.1em; font-size: 0.95rem;">劇院地址</h4>
                    <p style="color: #6b7280; margin: 0; font-size: 0.85rem; letter-spacing: 0.05em; line-height: 1.6;">
                        <a href="https://www.google.com/maps/search/?api=1&query=台中市北區太平路19巷1號3樓" target="_blank" style="color: #6b7280; text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#6b7280'">
                            台中市北區太平路19巷1號3樓<br>
                            (一中街麥當勞正對面三樓)
                        </a>
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1.5rem;">
                <div style="width: 48px; height: 48px; background: #18181b; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #dc2626;">📞</div>
                <div>
                    <h4 style="color: white; margin: 0 0 0.4rem 0; letter-spacing: 0.1em; font-size: 0.95rem;">連絡電話</h4>
                    <p style="color: #6b7280; margin: 0; font-size: 0.85rem; letter-spacing: 0.05em;">
                        <a href="tel:0422250020" style="color: #6b7280; text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#6b7280'">
                            (04) 2225-0020
                        </a>
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1.5rem;">
                <div style="width: 48px; height: 48px; background: #18181b; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #dc2626;">📘</div>
                <div>
                    <h4 style="color: white; margin: 0 0 0.4rem 0; letter-spacing: 0.1em; font-size: 0.95rem;">臉書專頁</h4>
                    <p style="color: #6b7280; margin: 0; font-size: 0.85rem; letter-spacing: 0.05em;">
                        <a href="https://www.facebook.com/bglarp.studio/" target="_blank" style="color: #6b7280; text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#6b7280'">
                            BGLARP實境推理館
                        </a>
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 3rem;">
                <div style="width: 48px; height: 48px; background: #18181b; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #dc2626;">📷</div>
                <div>
                    <h4 style="color: white; margin: 0 0 0.4rem 0; letter-spacing: 0.1em; font-size: 0.95rem;">IG帳號</h4>
                    <p style="color: #6b7280; margin: 0; font-size: 0.85rem; letter-spacing: 0.05em;">
                        <a href="https://www.instagram.com/bglarp.studio/" target="_blank" style="color: #6b7280; text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#6b7280'">
                            bglarp.studio
                        </a>
                    </p>
                </div>
            </div>
            
            <a href="https://www.facebook.com/bglarp.studio" target="_blank" style="display: inline-flex; align-items: center; gap: 10px; padding: 1rem 2rem; background-color: white; color: black; font-weight: bold; letter-spacing: 0.1em; text-decoration: none; border-radius: 2px; transition: background 0.3s;" onmouseover="this.style.backgroundColor='#e5e7eb'" onmouseout="this.style.backgroundColor='white'">
                📩 私訊預約
            </a>
        </div>
        
        <div style="flex: 1; min-width: 300px; min-height: 400px; position: relative; padding: 1rem;">
            <div style="position: absolute; inset: 0; background: rgba(185, 28, 28, 0.2); transform: translate(1.5rem, 1.5rem); border-radius: 4px;"></div>
            <iframe src="https://maps.google.com/maps?q=台中市北區太平路19巷1號&t=&z=16&ie=UTF8&iwloc=&output=embed" style="width: 100%; height: 100%; min-height: 400px; border: 0; position: relative; z-index: 10; border-radius: 4px;" allowfullscreen="" loading="lazy"></iframe>
        </div>
    </div>
</section>

<footer style="background: #000; padding: 4rem 0; border-top: 1px solid rgba(255,255,255,0.05); text-align: center;">
    <div style="color: white; font-size: 1.5rem; font-weight: bold; letter-spacing: 0.2em; font-family: serif; margin-bottom: 1rem; display: flex; justify-content: center; align-items: center; gap: 8px;">
        <span style="color: #dc2626;">🎬</span> BGLARP
    </div>
    <div style="color: #6b7280; font-size: 0.85rem; letter-spacing: 0.1em;">&copy; 2026 BGLARP 實境推理館. All Rights Reserved.</div>
</footer>
</body></html>
"""
components.html(booking_html, height=850, scrolling=False)
