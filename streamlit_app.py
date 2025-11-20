# streamlit_app.py
import streamlit as st
import requests
from typing import List

# ----------------------------
# رابط API الذي أعطاه لك Colab (ngrok)
# تم التأكد من صحة الرابط: https://haematozoal-marquetta-unexceptional.ngrok-free.dev
API_BASE_URL = "https://haematozoal-marquetta-unexceptional.ngrok-free.dev"
# ----------------------------

SYMBOLS_MAP = {
    'C': '🌽', 'T': '🍅', 'P': '🌶️', 'R': '🥕',
    'S': '🍤', 'W': '🐄', 'F': '🐟', 'H': '🐔',
    'Z': '🍕', 'L': '🍇'
}
SYMBOL_KEYS = list(SYMBOLS_MAP.keys())

# الإعداد الافتراضي للصفحة
st.set_page_config(page_title="نظام التوقع الذكي", layout="wide")

# ---- CSS (لتحسين شكل الكروت والألوان) ----
st.markdown("""
<style>
/* CSS مُحسَّن للاستجابة على شاشات الجوال */
.smart-ensemble-container { font-family: "Segoe UI", Tahoma, Arial, sans-serif; color: #dfe7ff; background: #1a1f2e;
  border-radius: 12px; padding: 15px; margin: 10px 0; }
  
.card { 
  background: linear-gradient(180deg, rgba(29,36,49,0.9), rgba(17,23,33,0.9)); 
  border-radius:10px; 
  padding:10px; /* تقليل البادينج */
  min-width:70px; /* تقليل الحد الأدنى للعرض */
  flex:1; 
  box-sizing:border-box; 
  border:1px solid rgba(120,95,255,0.18); 
  box-shadow:0 4px 8px rgba(0,0,0,0.3); 
  display:flex;
  flex-direction:column; 
  align-items:center; 
  font-size:10px; /* تصغير الخط قليلاً */
  color: #dfe7ff; 
  margin: 5px; /* إضافة مسافة بين الكروت */
}
.stButton>button {
    width: 100%; /* جعل الأزرار تأخذ عرض العمود بالكامل */
    padding: 10px 5px; /* تقليل حجم الزر ليتناسب مع تخطيط 5 أعمدة */
    font-size: 14px; /* حجم خط الزر */
}
.current-display { background: #1e2433; padding: 10px; border-radius: 8px; margin: 10px 0; text-align:center; font-size:14px; color:#888;}
</style>
""", unsafe_allow_html=True)

# ---- Sidebar stats (لم يتغير) ----
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

# ----------------------------------------------------
# 1. لوحة المفاتيح: تم ترتيبها في 5 أعمدة لتكون أفقية
# ----------------------------------------------------
# تقسيم الرموز لصفوف من 5
num_cols = 5
cols = st.columns(num_cols)
buttons = {}

for i, k in enumerate(SYMBOL_KEYS):
    col = cols[i % num_cols] # يضمن تكرار الأعمدة (0, 1, 2, 3, 4, 0, 1, ...)
    # استخدم key فريد لتجنب أخطاء Streamlit
    if col.button(SYMBOLS_MAP[k] + f"  ({k})", key=f"btn_{k}"):
        buttons['pressed'] = k

# Keep session state for local accumulation before sending
if 'temp_results' not in st.session_state:
    st.session_state['temp_results'] = []
if 'temp_hot' not in st.session_state:
    st.session_state['temp_hot'] = None
if 'last_prediction' not in st.session_state:
    st.session_state['last_prediction'] = [] # تهيئة قائمة التوقعات

# handle button pressed
if 'pressed' in buttons:
    key = buttons['pressed']
    if mode == '🎮 إدخال النتائج':
        st.session_state['temp_results'].append(key)
    else:
        st.session_state['temp_hot'] = key

# ----------------------------------------------------
# 2. عرض النتائج المجمعة (تحت الكيبورد مباشرة)
# ----------------------------------------------------
if mode == '🎮 إدخال النتائج':
    if st.session_state['temp_results']:
        emojis = " ".join([SYMBOLS_MAP[s] for s in st.session_state['temp_results']])
        st.markdown(f"<div class='current-display'>📊 النتائج المضافة: {emojis}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='current-display'>لا توجد نتائج مضافة بعد</div>", unsafe_allow_html=True)
else:
    if st.session_state['temp_hot']:
        st.markdown(f"<div class='current-display'>🔥 HOT المختار: {SYMBOLS_MAP[st.session_state['temp_hot']]} ({st.session_state['temp_hot']})</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='current-display'>لم يتم اختيار HOT</div>", unsafe_allow_html=True)

st.markdown("---")


# ----------------------------------------------------
# 3. أزرار التحكم (مسح، إضافة، مسح الكل)
# ----------------------------------------------------
c1, c2, c3 = st.columns([1,1,1])
with c1:
    if st.button("🗑️ مسح الحالي", key="btn_clear_current"):
        st.session_state['temp_results'] = []
        st.session_state['temp_hot'] = None
        st.session_state['last_prediction'] = [] # مسح التوقع عند مسح النتائج
        st.rerun() # إعادة تشغيل الواجهة لرؤية التغيير
with c2:
    if st.button("🎯 إضافة وتوقع", key="btn_add_predict"):
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
                st.session_state['temp_results'] = [] # مسح النتائج المؤقتة بعد الإضافة الناجحة
                st.session_state['temp_hot'] = None
                st.rerun() # إعادة تشغيل الواجهة لرؤية التوقع الجديد
            else:
                st.error("خطأ في التوقع: " + str(resp.get("error")))
        except Exception as e:
            st.error("خطأ تواصل مع الـ API: تأكد أن خادم Colab يعمل. تفاصيل: " + str(e))
with c3:
    if st.button("🔄 مسح الكل", key="btn_clear_all"):
        try:
            requests.post(f"{API_BASE_URL}/clear_all", timeout=4)
            st.session_state['temp_results'] = []
            st.session_state['temp_hot'] = None
            st.session_state['last_prediction'] = [] # مسح التوقع
            st.success("✅ تم المسح الكامل للسجل")
            st.rerun()
        except Exception as e:
            st.error("خطأ مسح: تأكد أن خادم Colab يعمل. تفاصيل: " + str(e))

st.markdown("---")

# ----------------------------------------------------
# 4. عرض التوقعات الأربعة: تم وضعها في 4 أعمدة أفقية
# ----------------------------------------------------
st.markdown("## 📊 أفضل توقعات")
prediction_list = st.session_state.get('last_prediction')

# إذا لم يكن هناك توقع في الـ session، حاول جلب توقع افتراضي/آخر من API
if not prediction_list:
    try:
        resp = requests.get(f"{API_BASE_URL}/predict", timeout=4).json()
        if resp.get("ok"):
            prediction_list = resp.get("top", [])
        else:
            st.info("أدخل نتائج ثم اضغط إضافة وتوقع (API يعمل).")
    except Exception:
        st.warning("⚠️ API غير متوفر أو غير مستجيب. تأكد من تشغيل خادم Colab.")

# عرض التوقعات في 4 أعمدة (أفقياً)
if prediction_list:
    # استخدام 4 أعمدة لعرض الـ Top 4
    cols = st.columns(4) 
    for idx, pred in enumerate(prediction_list[:4]):
        c = cols[idx]
        # استخدام div لتنسيق البطاقة داخل العمود
        c.markdown(
            f"""
            <div class='card'>
                <div style='font-size:24px; margin-bottom: 2px;'>{pred['emoji']}</div>
                <div style='font-weight:600'>{pred['symbol']}</div>
                <div style='font-size:16px; font-weight: bold; color: #ff88d2;'>{pred['prob']*100:.2f}%</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
else:
    st.info("اضغط على الرموز أعلاه ثم '🎯 إضافة وتوقع' لرؤية أفضل 4 توقعات.")

st.markdown("---")
st.caption("واجهة Streamlit متصلة بخادم Google Colab. تأكد من أن الخادم يعمل لكي تستجيب الواجهة.")
