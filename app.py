import streamlit as st
import requests
import streamlit.components.v1 as components
import os
import re
import urllib.parse

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

# Google Fonts 載入
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# ==================== 全局自訂 CSS ====================
st.markdown("""
<style>
/* ===== Reset & Base ===== */
.stApp {
    background-color: #000;
    color: #cbd5e1;
    font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    overflow-x: hidden;
}
header[data-testid="stHeader"], .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ===== Scrollbar ===== */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #b91c1c; }

/* ===== Script Card Grid (Mobile-first: 1 col) ===== */
.script-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
}

/* ===== Script Card ===== */
.script-card {
    background: #111;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    text-decoration: none !important;
    display: block;
    color: inherit;
}
.script-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 35px rgba(0,0,0,0.7), 0 0 15px rgba(220,38,38,0.1);
}

/* Card Image */
.sc-img-wrap {
    position: relative;
    aspect-ratio: 4/3;
    overflow: hidden;
    background: #0a0a0a;
}
.sc-img-wrap img {
    width: 100%; height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
    display: block;
}
.script-card:hover .sc-img-wrap img { transform: scale(1.06); }
.sc-img-grad {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 40%;
    background: linear-gradient(to top, rgba(17,17,17,0.7), transparent);
    pointer-events: none;
}

/* Difficulty Badge */
.sc-badge-diff {
    position: absolute;
    bottom: 10px; right: 10px;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(6px);
    color: #e4e4e7;
    font-size: 0.65rem;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid rgba(255,255,255,0.1);
    z-index: 2;
}

/* Card Body */
.sc-body { padding: 12px 14px 16px; }
.sc-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.sc-tag {
    font-size: 0.6rem;
    color: #a1a1aa;
    border: 1px solid rgba(255,255,255,0.12);
    padding: 2px 7px;
    border-radius: 3px;
    letter-spacing: 0.03em;
    white-space: nowrap;
}
.sc-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f0f0f0;
    letter-spacing: 0.08em;
    margin: 0 0 12px 0;
    font-family: 'Noto Serif TC', serif;
}
.sc-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
    color: #71717a;
}
.sc-players { display: flex; align-items: center; gap: 5px; }
.sc-price { color: #a1a1aa; font-size: 0.7rem; text-align: right; }
.sc-price .amt { font-size: 1.3rem; font-weight: 800; color: #f0f0f0; margin: 0 2px; }

/* ===== Dialog ===== */
section[data-testid="stDialog"] > div {
    background-color: #09090b !important;
    border: 1px solid #dc2626 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 50px rgba(220, 38, 38, 0.1) !important;
}
section[data-testid="stDialog"] [data-testid="stDialogTitle"] { display: none !important; }

/* ===== Filters ===== */
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.05) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 4px;
}

/* ===== Show More Button ===== */
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

/* ===== Responsive: Tablet (2 cols) ===== */
@media (min-width: 640px) {
    .script-grid { grid-template-columns: repeat(2, 1fr); gap: 18px; }
}
/* ===== Responsive: Desktop (4 cols) ===== */
@media (min-width: 1024px) {
    .script-grid { grid-template-columns: repeat(4, 1fr); gap: 22px; }
}
/* ===== Responsive: Wide (5 cols) ===== */
@media (min-width: 1280px) {
    .script-grid { grid-template-columns: repeat(5, 1fr); gap: 24px; }
}

/* ===== Responsive: Mobile tweaks ===== */
@media (max-width: 768px) {
    .sc-title { font-size: 0.85rem; }
    .sc-tag { font-size: 0.5rem; padding: 2px 5px; }
    .sc-price .amt { font-size: 1.1rem; }
    .sc-footer { font-size: 0.65rem; }
    .sc-body { padding: 10px 12px 14px; }
    .sc-players svg { width: 14px !important; height: 14px !important; }
    .sc-badge-diff { font-size: 0.55rem; padding: 3px 7px; }

    button[data-testid="stBaseButton-secondary"][kind="secondary"] {
        padding: 0.5rem 1rem !important;
        font-size: 0.85rem !important;
    }
}
@media (max-width: 380px) {
    .sc-title { font-size: 0.75rem; }
    .sc-tags { gap: 4px; margin-bottom: 6px; }
    .sc-tag { font-size: 0.45rem; }
    .sc-price .amt { font-size: 0.95rem; }
    .sc-body { padding: 8px 10px 12px; }
}
</style>
""", unsafe_allow_html=True)

# ==================== Helpers ====================
def format_player_range(players):
    """['5人', '6人', '7人'] → '5~7人'"""
    nums = []
    for p in players:
        m = re.search(r'(\d+)', p)
        if m:
            nums.append(int(m.group(1)))
    if not nums:
        return "未知"
    nums.sort()
    if len(nums) == 1:
        return f"{nums[0]}人"
    return f"{nums[0]}~{nums[-1]}人"

# ==================== Fetch Notion Data ====================
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

# ==================== Modal Dialog ====================
@st.dialog(" ", width="large")
def show_script_modal(card):
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
.char-avatar-grid { padding-top: 12px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px 16px; }
.char-avatar-item { display: flex; flex-direction: column; align-items: center; text-align: center; }
.char-avatar-img { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #27272a; margin-bottom: 10px; transition: border-color 0.3s, transform 0.3s; background: #18181b; }
.char-avatar-item:hover .char-avatar-img { border-color: #dc2626; transform: scale(1.08); }
.char-avatar-name { font-size: 0.85rem; font-weight: 600; letter-spacing: 0.08em; color: #e4e4e7; margin-bottom: 2px; }
.char-avatar-desc { font-size: 0.7rem; color: #71717a; line-height: 1.5; font-weight: 300; max-width: 120px; }
div[data-testid="stTabs"] button[data-baseweb="tab"] {font-size: 0.85rem !important; letter-spacing: 0.15em !important; color: #71717a !important; padding-bottom: 12px !important;}
div[data-testid="stTabs"] button[aria-selected="true"] {color: white !important; border-bottom-color: #dc2626 !important;}
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

    fallback_img = "https://images.unsplash.com/photo-1505635552518-3448ff116af3?q=80&w=800&auto=format&fit=crop"
    st.markdown(f"""<div class="modal-poster-wrap">
<div class="modal-poster-bg" style="background-image: url('{card['image']}'), url('{fallback_img}');"></div>
<div class="modal-poster-grad"></div>
<div class="modal-poster-title">
<h1>{card['name']}</h1>
</div>
</div>""", unsafe_allow_html=True)

    genre_text = card.get('genre', '') or ''
    genre_tags = [g.strip() for g in genre_text.replace('/', ',').replace('、', ',').split(',') if g.strip()]
    all_tags = card['players'] + genre_tags
    tags_html = "".join([f'<span class="modal-tag">{t}</span>' for t in all_tags])
    st.markdown(f'<div style="margin-bottom: 16px;">{tags_html}</div>', unsafe_allow_html=True)

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
            silhouette_svg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%231a1a2e' rx='50'/%3E%3Ccircle cx='50' cy='38' r='18' fill='%2327272a'/%3E%3Cellipse cx='50' cy='82' rx='26' ry='18' fill='%2327272a'/%3E%3C/svg%3E"
            chars_html = ""
            for idx, line in enumerate(lines):
                char_name = line
                char_desc = ""
                for sep in ['：', ':', '－', ' - ']:
                    if sep in line:
                        parts = line.split(sep, 1)
                        char_name = parts[0].strip()
                        char_desc = parts[1].strip()
                        break
                desc_html = f'<div class="char-avatar-desc">{char_desc}</div>' if char_desc else ''
                chars_html += f'''<div class="char-avatar-item">
<img src="{silhouette_svg}" class="char-avatar-img" alt="{char_name}">
<div class="char-avatar-name">{char_name}</div>
{desc_html}
</div>'''
            st.markdown(f'<div class="char-avatar-grid">{chars_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: #71717a; padding-top: 12px; letter-spacing: 0.05em;">（尚無角色資料）</p>', unsafe_allow_html=True)

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    st.markdown("""<div style="text-align: center;"><a href="https://www.facebook.com/bglarp.studio/" target="_blank" style="display: inline-block; padding: 12px 40px; background: #dc2626; color: white; font-weight: 700; font-size: 0.9rem; letter-spacing: 0.25em; text-decoration: none; border-radius: 4px; transition: all 0.3s;">馬上預約 →</a></div>""", unsafe_allow_html=True)


# ==================== Scripts Section ====================
st.markdown('<div id="scripts" style="padding-top: 1.5rem; background: #000;"></div>', unsafe_allow_html=True)

with st.spinner("影片載入中..."):
    pages = fetch_notion_data(NOTION_TOKEN, DATABASE_ID)

_, main_col, _ = st.columns([1, 10, 1])

with main_col:
    st.markdown("""
    <div style="margin-bottom: 3rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1.5rem;">
        <span style="color: #dc2626; font-weight: bold; letter-spacing: 0.2em; font-size: 0.8rem; display: block; margin-bottom: 0.5rem;">NOW SHOWING</span>
        <h2 style="font-size: 2.5rem; font-family: serif; font-weight: bold; color: white; letter-spacing: 0.1em; margin: 0;">現正熱映</h2>
    </div>
    """, unsafe_allow_html=True)

    # 篩選 UI
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        player_filter = st.selectbox("人數", ["全部", "5人", "6人", "7人", "8人", "9人以上"], label_visibility="collapsed")
    with f2:
        genre_filter = st.selectbox("類型", ["全部", "推理", "硬核", "沉浸", "恐怖", "機制"], label_visibility="collapsed")

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

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

            if genre_filter != "全部":
                if not genre or genre_filter not in genre:
                    continue
            if player_filter != "全部":
                is_match = False
                for p_tag in players:
                    if player_filter == p_tag:
                        is_match = True
                        break
                    elif player_filter == "9人以上":
                        match = re.search(r'(\d+)', p_tag)
                        if match and int(match.group(1)) >= 9:
                            is_match = True
                            break
                if not is_match:
                    continue

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
        INITIAL_COUNT = 10
        if "script_display_limit" not in st.session_state:
            st.session_state.script_display_limit = INITIAL_COUNT

        visible_data = display_data[:st.session_state.script_display_limit]

        # SVG icon for players (small)
        svg_p = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'

        # Build CSS Grid HTML
        cards_html = '<div class="script-grid">'
        for card in visible_data:
            player_range = format_player_range(card['players'])
            genre_text = card.get('genre', '') or ''
            genre_parts = [g.strip() for g in genre_text.replace('/', ',').replace('、', ',').split(',') if g.strip()]
            tags_html = ''.join([f'<span class="sc-tag">#{t}</span>' for t in genre_parts])
            price_html = f'NT$ <span class="amt">{card["price"]}</span> /人' if card['price'] else '<span style="color:#71717a;">價格未定</span>'
            url_name = urllib.parse.quote(card['name'])

            cards_html += f'''
<a href="?script={url_name}" target="_self" class="script-card">
    <div class="sc-img-wrap">
        <img src="{card['image']}" alt="{card['name']}" loading="lazy"
             onerror="this.src='{placeholder_img}'">
        <div class="sc-img-grad"></div>
    </div>
    <div class="sc-body">
        <div class="sc-tags">{tags_html}</div>
        <h3 class="sc-title">{card['name']}</h3>
        <div class="sc-footer">
            <div class="sc-players">{svg_p} {player_range}</div>
            <div class="sc-price">{price_html}</div>
        </div>
    </div>
</a>'''

        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

        # 展示更多
        if len(display_data) > st.session_state.script_display_limit:
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
            with btn_col2:
                if st.button("顯示更多", key="show_more_scripts", use_container_width=True):
                    st.session_state.script_display_limit += 10
                    st.rerun()


# ==================== URL Params (Modal trigger) ====================
if "script" in st.query_params:
    target_script_name = st.query_params["script"]
    target_script = next((s for s in display_data if s["name"] == target_script_name), None)
    if target_script:
        st.query_params.clear()
        show_script_modal(target_script)

# ==================== Booking / Footer ====================
booking_html = """<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0; padding:0; background:#000; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
<section id="booking" style="padding: 6rem 0; background-color: #09090b; border-top: 1px solid rgba(255,255,255,0.05);">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem; display: flex; flex-wrap: wrap; gap: 4rem;">
        <div style="flex: 1; min-width: 280px;">
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
                        <a href="https://www.google.com/maps/search/?api=1&query=台中市北區太平路19巷1號3樓" target="_blank" style="color: #6b7280; text-decoration: none;">
                            台中市北區太平路19巷1號3樓<br>(一中街麥當勞正對面三樓)
                        </a>
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1.5rem;">
                <div style="width: 48px; height: 48px; background: #18181b; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #dc2626;">📞</div>
                <div>
                    <h4 style="color: white; margin: 0 0 0.4rem 0; letter-spacing: 0.1em; font-size: 0.95rem;">連絡電話</h4>
                    <p style="color: #6b7280; margin: 0; font-size: 0.85rem; letter-spacing: 0.05em;">
                        <a href="tel:0422250020" style="color: #6b7280; text-decoration: none;">(04) 2225-0020</a>
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1.5rem;">
                <div style="width: 48px; height: 48px; background: #18181b; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #dc2626;">📘</div>
                <div>
                    <h4 style="color: white; margin: 0 0 0.4rem 0; letter-spacing: 0.1em; font-size: 0.95rem;">臉書專頁</h4>
                    <p style="color: #6b7280; margin: 0; font-size: 0.85rem; letter-spacing: 0.05em;">
                        <a href="https://www.facebook.com/bglarp.studio/" target="_blank" style="color: #6b7280; text-decoration: none;">BGLARP實境推理館</a>
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 3rem;">
                <div style="width: 48px; height: 48px; background: #18181b; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #dc2626;">📷</div>
                <div>
                    <h4 style="color: white; margin: 0 0 0.4rem 0; letter-spacing: 0.1em; font-size: 0.95rem;">IG帳號</h4>
                    <p style="color: #6b7280; margin: 0; font-size: 0.85rem; letter-spacing: 0.05em;">
                        <a href="https://www.instagram.com/bglarp.studio/" target="_blank" style="color: #6b7280; text-decoration: none;">bglarp.studio</a>
                    </p>
                </div>
            </div>

            <a href="https://www.facebook.com/bglarp.studio" target="_blank" style="display: inline-flex; align-items: center; gap: 10px; padding: 1rem 2rem; background-color: white; color: black; font-weight: bold; letter-spacing: 0.1em; text-decoration: none; border-radius: 2px; transition: background 0.3s;">
                📩 私訊預約
            </a>
        </div>

        <div style="flex: 1; min-width: 280px; min-height: 400px; position: relative; padding: 1rem;">
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
