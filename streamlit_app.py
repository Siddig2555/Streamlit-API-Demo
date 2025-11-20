# streamlit_app.py
import streamlit as st
import requests
from typing import List

# ----------------------------
# تم التعديل: وضع رابط API الجديد الذي أعطاه لك Colab (ngrok)
API_BASE_URL = "https://haematozoal-marquetta-unexceptional.ngrok-free.dev"
# ----------------------------

SYMBOLS_MAP = {
    'C': '🌽', 'T': '🍅', 'P': '🌶️', 'R': '🥕',
    'S': '🍤', 'W': '🐄', 'F': '🐟', 'H': '🐔',
    'Z': '🍕', 'L': '🍇'
}
SYMBOL_KEYS = list(SYMBOLS_MAP.keys())

st.set_page_config(page_title="نظام التوقع الذكي", layout="wide")

# ---- CSS (مقتبس من كودك الأصلي) ----
st.markdown("""
<style>
.smart-ensemble-container { font-family: "Segoe UI", Tahoma, Arial, sans-serif; color: #dfe7ff; background: #1a1f2e;
  border-radius: 12px; padding: 15px; margin: 10px 0; }
.card { background: linear-gradient(180deg, rgba(29,36,49,0.9), rgba(17,23,33,0.9)); border-radius:10px; padding:15px;
  min-width:140px; flex:1; box-sizing:border-box; border:1px solid rgba(120,95,255,0.18); box-shadow:0 4px 12px rgba(0,0,0,0.45); display:flex;
  flex-direction:column; align-items:center; font-size:11px; color: #dfe7ff; }
.progress-inner { height: 6px; border-radius: 6px; background: linear-gradient(90deg, #6b63ff, #ff5ec6); width:0%; }
.current-display { background: #1e2433; padding: 12px; border-radius: 8px; margin: 10px 0; text-align:center; font-size:16px; color:#888;}
</style>
""", unsafe_allow_html=True)

# ---- Sidebar stats ----
with st.sidebar:
    st.markdown("### 🎯 نظام التوقع الذكي")
    try:
        r = requests.get(f"{API_BASE_URL}/stats", timeout=5).json()
        if r.get("ok"):
            stats = r["stats"]
            st.write(f"**القائد:** {stats.get('leader')}")
            st.write(f"**الجولات:** {stats.get('total_predictions')}")
            st.write(f"**الدقة:** {stats.get('accuracy'):.2f}%")
            st.write(f"**أول 4:** {stats.get('top4_accuracy'):.2f}%")
        else:
            st.write("⚠️ لم يمكن جلب الإحصائيات")
    except Exception as e:
        st.write("⚠️ API غير متوفر")

# ---- Main UI ----
st.title("نظام التوقع الذكي — واجهة الويب")
mode = st.radio("الوضع:", ('🎮 إدخال النتائج', '🔥 إدخال HOT'))

# current display box
if mode == '🎮 إدخال النتائج':
    st.markdown('<div class="current-display">🎮 انقر على الرموز لإضافة النتائج</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="current-display">🔥 اختر HOT واحد</div>', unsafe_allow_html=True)

# keyboard grid
cols = st.columns(5)
buttons = {}
i = 0
for k in SYMBOL_KEYS:
    col = cols[i % 5]
    if col.button(SYMBOLS_MAP[k] + f"  ({k})"):
        buttons['pressed'] = k
    i += 1

# Keep session state for local accumulation before sending
if 'temp_results' not in st.session_state:
    st.session_state['temp_results'] = []
if 'temp_hot' not in st.session_state:
    st.session_state['temp_hot'] = None

# handle button pressed
if 'pressed' in buttons:
    key = buttons['pressed']
    if mode == '🎮 إدخال النتائج':
        st.session_state['temp_results'].append(key)
    else:
        st.session_state['temp_hot'] = key

# display current collected
if mode == '🎮 إدخال النتائج':
    if st.session_state['temp_results']:
        emojis = " ".join([SYMBOLS_MAP[s] for s in st.session_state['temp_results']])
        st.markdown(f"<div class='current-display'>📊 النتائج: {emojis}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='current-display'>لا توجد نتائج مضافة</div>", unsafe_allow_html=True)
else:
    if st.session_state['temp_hot']:
        st.markdown(f"<div class='current-display'>🔥 HOT: {SYMBOLS_MAP[st.session_state['temp_hot']]} ({st.session_state['temp_hot']})</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='current-display'>لم يتم اختيار HOT</div>", unsafe_allow_html=True)

# control buttons
c1, c2, c3 = st.columns([1,1,1])
with c1:
    if st.button("🗑️ مسح الحالي"):
        st.session_state['temp_results'] = []
        st.session_state['temp_hot'] = None
with c2:
    if st.button("🎯 إضافة وتوقع"):
        # إرسال النتائج المؤقتة إلى Colab API
        try:
            # أولاً إذا هناك نتائج نضيفها
            if st.session_state['temp_results']:
                requests.post(f"{API_BASE_URL}/add_results", json={"results": st.session_state['temp_results']}, timeout=6)
            # ضبط HOT إن وُجد
            if st.session_state['temp_hot']:
                requests.post(f"{API_BASE_URL}/set_hot", json={"hot": st.session_state['temp_hot']}, timeout=4)
            # اطلب توقع
            resp = requests.get(f"{API_BASE_URL}/predict", timeout=6).json()
            if resp.get("ok"):
                top = resp.get("top", [])
                st.session_state['last_prediction'] = top
            else:
                st.error("خطأ في التوقع: " + str(resp.get("error")))
        except Exception as e:
            st.error("خطأ تواصل مع الـ API: " + str(e))
with c3:
    if st.button("🔄 مسح الكل"):
        try:
            requests.post(f"{API_BASE_URL}/clear_all", timeout=4)
            st.session_state['temp_results'] = []
            st.session_state['temp_hot'] = None
            st.success("✅ تم المسح الكامل")
        except Exception as e:
            st.error("خطأ مسح: " + str(e))

# show prediction cards
st.markdown("## 📊 أفضل توقعات")
if 'last_prediction' in st.session_state and st.session_state['last_prediction']:
    cols = st.columns(4)
    for idx, pred in enumerate(st.session_state['last_prediction'][:4]):
        c = cols[idx]
        c.markdown(f"<div class='card'><div style='font-size:28px'>{pred['emoji']}</div><div style='font-weight:700'>{pred['symbol']}</div><div style='font-size:18px'>{pred['prob']*100:.2f}%</div></div>", unsafe_allow_html=True)
else:
    # حاول جلب توقع افتراضي
    try:
        resp = requests.get(f"{API_BASE_URL}/predict", timeout=4).json()
        if resp.get("ok"):
            top = resp.get("top", [])
            cols = st.columns(4)
            for idx, pred in enumerate(top[:4]):
                c = cols[idx]
                c.markdown(f"<div class='card'><div style='font-size:28px'>{pred['emoji']}</div><div style='font-weight:700'>{pred['symbol']}</div><div style='font-size:18px'>{pred['prob']*100:.2f}%</div></div>", unsafe_allow_html=True)
        else:
            st.info("أدخل نتائج ثم اضغط إضافة وتوقع")
    except Exception:
        st.info("API غير متوفر الآن")

st.markdown("---")
st.caption("واجهة Streamlit متصلة بخادم Google Colab. لتحديث رابط API استخدم متغير API_BASE_URL في أعلى الملف.")

