import sys
import os

# Bulletproof path setup for Streamlit Cloud / Linux
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Add modules directory to sys.path if it exists
modules_path = os.path.join(BASE_DIR, 'modules')
if os.path.exists(modules_path) and modules_path not in sys.path:
    sys.path.insert(0, modules_path)

import streamlit as st
import pandas as pd
import json

# Bulletproof multi-environment imports
try:
    from modules.scraper import fetch_and_parse_url, process_raw_text
    from modules.competitor_analyzer import analyze_competitor_article
    from modules.gap_analyzer import analyze_content_gap
    from modules.recommendation_engine import generate_outrank_recommendations
    from modules.report_generator import generate_html_report, generate_json_report, generate_pdf_bytes
except ModuleNotFoundError:
    try:
        from Modules.scraper import fetch_and_parse_url, process_raw_text
        from Modules.competitor_analyzer import analyze_competitor_article
        from Modules.gap_analyzer import analyze_content_gap
        from Modules.recommendation_engine import generate_outrank_recommendations
        from Modules.report_generator import generate_html_report, generate_json_report, generate_pdf_bytes
    except ModuleNotFoundError:
        from scraper import fetch_and_parse_url, process_raw_text
        from competitor_analyzer import analyze_competitor_article
        from gap_analyzer import analyze_content_gap
        from recommendation_engine import generate_outrank_recommendations
        from report_generator import generate_html_report, generate_json_report, generate_pdf_bytes

# Streamlit Page Config
st.set_page_config(
    page_title="Rank Naser Competitor Spy ⚡",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Futuristic AI SaaS White Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Pure White Canvas */
    .stApp {
        background-color: #ffffff;
        color: #0f172a;
    }
    
    /* Modern AI Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* AI Badge Top Header */
    .ai-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        color: #0369a1;
        font-size: 12px;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 20px;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(2, 132, 199, 0.08);
    }
    
    .ai-status-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
    }

    /* Main Title Styling */
    .main-title {
        font-size: 34px;
        font-weight: 800;
        background: linear-gradient(135deg, #0284c7 0%, #4338ca 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
    }
    
    .sub-title {
        font-size: 15px;
        color: #64748b;
        margin-bottom: 30px;
        font-weight: 500;
    }
    
    /* High-Tech AI Metric Card */
    .ai-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.03);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .ai-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(2, 132, 199, 0.08);
    }
    .ai-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
    }
    .ai-card-title {
        font-size: 12px;
        color: #64748b;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .ai-card-value {
        font-size: 26px;
        font-weight: 800;
        color: #0f172a;
    }
    
    /* AI Action Recommendation Cards */
    .ai-action-high {
        background: #fff7ed;
        border: 1px solid #ffedd5;
        border-left: 5px solid #f97316;
        color: #7c2d12;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 14px;
        font-size: 14px;
        line-height: 1.6;
    }
    .ai-action-medium {
        background: #fefce8;
        border: 1px solid #fef9c3;
        border-left: 5px solid #eab308;
        color: #713f12;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 14px;
        font-size: 14px;
        line-height: 1.6;
    }
    .ai-action-low {
        background: #f0fdf4;
        border: 1px solid #dcfce7;
        border-left: 5px solid #22c55e;
        color: #14532d;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 14px;
        font-size: 14px;
        line-height: 1.6;
    }
    
    /* Ultra-Compact Concise Tab & Container Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 700;
        font-size: 12px;
        border-radius: 6px;
        padding: 6px 10px;
        white-space: nowrap;
    }
    h1 { font-size: 24px !important; }
    h2 { font-size: 20px !important; }
    h3 { font-size: 17px !important; }
    h4 { font-size: 15px !important; }
</style>
""", unsafe_allow_html=True)

# AI Header Element
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between;">
    <div>
        <div class="ai-pill">
            <span class="ai-status-dot"></span>
            🤖 RANK NASER NEURAL SEO ENGINE v2.6 • LIVE AI INTELLIGENCE
        </div>
        <div class="main-title">⚡ RANK NASER COMPETITOR SPY</div>
        <div class="sub-title">AI-Powered Competitive Article Inspector, Keyword Extraction, Content Gap Detection & Outrank Blueprint</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.markdown("## ⚙️ Input Settings")
input_mode = st.sidebar.radio("Input Source Method:", ["🌐 URL Scraping Mode", "📝 Direct Text Paste Mode"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Main Focus Keyword (ফোকাস কিওয়ার্ড)")
custom_fk_input = st.sidebar.text_input(
    "Target Main Keyword (optional):", 
    placeholder="e.g. Gimbal, Gaming Laptop",
    help="এখানে আপনার টার্গেটেড Main Keyword দিন। ফাঁকা রাখলে AI অটোমেটিক আর্টিকেলের কন্টেন্ট ও URL থেকে সেরা কিওয়ার্ড খুঁজে নেবে।"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🕵️ 1. Competitor Article")

if input_mode == "🌐 URL Scraping Mode":
    comp_url = st.sidebar.text_input("Competitor Article URL:", placeholder="https://competitor.com/article-slug")
    comp_text_input = ""
else:
    comp_url = ""
    comp_text_input = st.sidebar.text_area("Paste Competitor Article Text:", height=180, placeholder="Paste competitor full article text here...")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 2. Your Website Article (Same Product/Topic)")

if input_mode == "🌐 URL Scraping Mode":
    user_url = st.sidebar.text_input("Your Article URL:", placeholder="https://yourwebsite.com/your-article-slug")
    user_text_input = ""
else:
    user_url = ""
    user_text_input = st.sidebar.text_area("Paste Your Article Text:", height=180, placeholder="Paste your website article text here...")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔑 Google AI (Gemini) API Integration")
api_key_input = st.sidebar.text_input("Google Gemini API Key (Optional):", type="password", placeholder="AIzaSy...")
if api_key_input:
    st.sidebar.success("✨ Google Gemini AI Engine: Active")
else:
    st.sidebar.caption("💡 Leave blank to use built-in free Neural Engine.")

# Sample Demo Data Loader Button
if st.sidebar.button("⚡ Load Demo Sample Articles"):
    st.session_state['demo_loaded'] = True

if st.session_state.get('demo_loaded', False):
    comp_text_input = """
    # Best Gaming Laptops in Bangladesh 2026 - Price & Review
    Looking to buy the best gaming laptop in Bangladesh? In this comprehensive buying guide, we review top laptops from ASUS, HP, Dell, and Lenovo. Whether you need an RTX 4060 graphics card or Intel Core i7 processor, we break down prices, performance specs, and battery life.
    
    ## Why Choose RTX 4060 Gaming Laptops?
    RTX 4060 laptops offer high FPS for AAA gaming at 1080p and 1440p resolution. Ray tracing and DLSS 3.5 support make gaming ultra-smooth.
    
    ## Top Brands: ASUS ROG Strix vs Lenovo Legion
    ASUS ROG Strix G16 features liquid metal cooling, RGB keyboard, and 240Hz display. Lenovo Legion 5 Pro offers superior build quality and color-accurate display for video editing.
    
    ## Gaming Laptop Prices in BD
    - ASUS ROG Strix G16: BDT 185,000
    - Lenovo Legion 5 Pro: BDT 195,000
    - HP Victus 16: BDT 125,000
    
    ## Pros and Cons of Gaming Laptops
    Pros: High performance, portability, excellent cooling.
    Cons: Lower battery life compared to ultrabooks, heavier weight.
    
    ## Frequently Asked Questions (FAQ)
    Q: Which gaming laptop is best for video editing?
    A: Lenovo Legion 5 Pro with 100% sRGB screen display.
    """
    
    user_text_input = """
    # Best Gaming Laptops Buying Guide
    If you want to buy a gaming laptop, here are the best options available in Bangladesh market.
    
    ## Laptop Options
    We have laptops from Asus and HP. Asus laptop comes with fast processor and good graphics card. HP laptop is budget friendly.
    
    ## Price in BD
    Prices range from BDT 100,000 to 200,000 depending on specifications.
    """
    input_mode = "📝 Direct Text Paste Mode"
    st.sidebar.info("Demo Sample Articles Loaded! Click 'Run Competitor Spy Analysis' below.")

analyze_btn = st.sidebar.button("🚀 Run Competitor Spy Analysis", use_container_width=True)

# Main Processing Logic
if analyze_btn or st.session_state.get('analyzed', False):
    st.session_state['analyzed'] = True
    
    with st.spinner("🕵️ Scraping, Extracting Focus Keywords & Analyzing Content Gaps..."):
        # Process Competitor Data
        if input_mode == "🌐 URL Scraping Mode" and comp_url:
            comp_parsed = fetch_and_parse_url(comp_url)
        elif comp_text_input:
            comp_parsed = process_raw_text(comp_text_input, title="Competitor Article")
        else:
            st.error("Please provide Competitor Article URL or Paste Competitor Article Text!")
            st.stop()
            
        if not comp_parsed.get('success', False):
            st.error(comp_parsed.get('error', 'Failed to parse competitor article.'))
            st.stop()
            
        # Analyze Competitor
        comp_analysis = analyze_competitor_article(comp_parsed, api_key=api_key_input, custom_focus_keyword=custom_fk_input)
        
        # Process User Data
        if input_mode == "🌐 URL Scraping Mode" and user_url:
            user_parsed = fetch_and_parse_url(user_url)
        elif user_text_input:
            user_parsed = process_raw_text(user_text_input, title="Your Article")
        else:
            user_parsed = process_raw_text("", title="Your Article (Empty)")
            
        # Content Gap & Recommendations
        gap_analysis = analyze_content_gap(comp_parsed, comp_analysis, user_parsed)
        recommendations = generate_outrank_recommendations(gap_analysis, comp_analysis, comp_parsed, user_parsed)
        
    # Main Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🕵️ ১. কম্পিটিটর কী করেছে", 
        "⚔️ ২. কন্টেন্ট গ্যাপ", 
        "🏷️ ৩. আমাদের কী করা উচিত", 
        "🤖 ৪. AI স্ট্র্যাটেজি", 
        "📥 ৫. PDF রিপোর্ট"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: COMPETITOR ARTICLE ANALYSIS
    # -------------------------------------------------------------
    with tab1:
        st.markdown("### 📌 ১. কম্পিটিটর আর্টিকেলে কী কী করেছে (Focus Keyword, Sub-keywords & Outline)")
        
        # Metric Cards Row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="ai-card">
                <div class="ai-card-title">🤖 AI Focus Keyword</div>
                <div class="ai-card-value" style="font-size:20px; color:#0284c7;">{comp_analysis['focus_keyword']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m2:
            st.markdown(f"""
            <div class="ai-card">
                <div class="ai-card-title">📝 Article Word Count</div>
                <div class="ai-card-value">{comp_parsed['word_count']} <span style="font-size:14px; font-weight:normal; color:#64748b;">words</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        with m3:
            st.markdown(f"""
            <div class="ai-card">
                <div class="ai-card-title">🎯 AI Reader Intent</div>
                <div class="ai-card-value" style="font-size:15px; color:#4338ca;">{comp_analysis['intent_summary']['intent_type']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m4:
            st.markdown(f"""
            <div class="ai-card">
                <div class="ai-card-title">📑 Headings & Media</div>
                <div class="ai-card-value">{len(comp_parsed['headings'])} <span style="font-size:14px; font-weight:normal; color:#64748b;">H1-H4</span> / {comp_parsed['image_count']} <span style="font-size:14px; font-weight:normal; color:#64748b;">Img</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("#### 📝 মূল কথা (Executive Summary of Competitor Article)")
            st.info(comp_analysis['executive_summary']['overview_text'])
            
            st.markdown("##### 📌 আর্টিকেলে আলোচিত প্রধান বিষয়সমূহ:")
            for topic in comp_analysis['executive_summary']['key_topics_covered']:
                st.markdown(f"- 🔹 **{topic}**")
                
            st.markdown("---")
            st.markdown("#### 🎯 মানুষের জন্য কি বলতে চায় (Target Value & Purpose)")
            for val in comp_analysis['intent_summary']['core_value_for_users']:
                st.markdown(f"- 💡 {val}")
                
            st.markdown("#### 🏷️ কি ব্র্যান্ড ও প্রোডাক্ট হাইলাইট করা হয়েছে (Brands & Products)")
            st.markdown(f"**Detect Brands:** {', '.join(comp_analysis['brands_detected'])}")
            st.markdown(f"**Highlighted Products/Models:** {', '.join(comp_analysis['products_highlighted'])}")
            
        with col_right:
            st.markdown("#### 🔑 Sub-Keywords & LSI Phrases (সাব-কিওয়ার্ড)")
            sub_kw_df = pd.DataFrame(comp_analysis['sub_keywords'])
            if not sub_kw_df.empty:
                st.dataframe(sub_kw_df, use_container_width=True, hide_index=True)
            else:
                st.write("No secondary keywords detected.")
                
            st.markdown("#### 📑 Competitor Article Structure (Headings Outline)")
            with st.expander("Click to view full Heading Hierarchy", expanded=True):
                for h in comp_parsed['headings']:
                    indent = "&nbsp;&nbsp;&nbsp;&nbsp;" if h['tag'] in ['H2', 'H3'] else ""
                    st.markdown(f"{indent}**[{h['tag']}]** {h['text']}")

    # -------------------------------------------------------------
    # TAB 2: CONTENT GAP ANALYSIS & USER WEAKNESSES
    # -------------------------------------------------------------
    with tab2:
        st.markdown("### ⚔️ ২. কন্টেন্ট গ্যাপ ও আপনার দুর্বলতাসমূহ")
        
        # Overall Gap Metric Score
        gap_score = gap_analysis['gap_score']
        score_color = "#dc2626" if gap_score > 50 else ("#d97706" if gap_score > 25 else "#16a34a")
        
        g_col1, g_col2 = st.columns([1, 3])
        with g_col1:
            st.markdown(f"""
            <div class="ai-card" style="text-align:center;">
                <div class="ai-card-title" style="justify-content:center;">⚡ Overall Gap Score</div>
                <div class="ai-card-value" style="font-size:42px; color:{score_color};">{gap_score}%</div>
                <div style="font-size:12px; color:#64748b; margin-top:4px;">(Higher = More Gaps to Fix)</div>
            </div>
            """, unsafe_allow_html=True)
            
        with g_col2:
            st.markdown("#### 📊 Side-by-Side Metrics Comparison")
            metrics_df = pd.DataFrame([
                {
                    "Metric": "Total Word Count",
                    "Competitor Article": f"{gap_analysis['metrics_comparison']['competitor_word_count']} words",
                    "Your Article": f"{gap_analysis['metrics_comparison']['user_word_count']} words",
                    "Gap / Difference": f"{gap_analysis['metrics_comparison']['word_count_difference']} words missing"
                },
                {
                    "Metric": f"Focus Keyword Count ('{gap_analysis['focus_keyword']}')",
                    "Competitor Article": f"{gap_analysis['competitor_fk_count']} times",
                    "Your Article": f"{gap_analysis['user_fk_count']} times",
                    "Gap / Difference": gap_analysis['fk_gap_status']
                },
                {
                    "Metric": "Total Images",
                    "Competitor Article": f"{gap_analysis['metrics_comparison']['competitor_images']} images",
                    "Your Article": f"{gap_analysis['metrics_comparison']['user_images']} images",
                    "Gap / Difference": f"{gap_analysis['metrics_comparison']['competitor_images'] - gap_analysis['metrics_comparison']['user_images']} images missing"
                },
                {
                    "Metric": "Total Headings (Subtopics)",
                    "Competitor Article": f"{gap_analysis['metrics_comparison']['competitor_headings_count']} headings",
                    "Your Article": f"{gap_analysis['metrics_comparison']['user_headings_count']} headings",
                    "Gap / Difference": f"{gap_analysis['metrics_comparison']['competitor_headings_count'] - gap_analysis['metrics_comparison']['user_headings_count']} sections"
                }
            ])
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            
        st.markdown("---")
        st.markdown("#### 🚨 আপনার আর্টিকেলের চিহ্নিত দুর্বলতাসমূহ ও সমাধান (Weaknesses & Fixes)")
        
        for w in gap_analysis.get('user_weaknesses', []):
            st.markdown(f"""
            <div style="background:#fef2f2; border-left:4px solid #ef4444; padding:14px; border-radius:6px; margin-bottom:12px;">
                <div style="color:#991b1b; font-weight:bold;">❌ দুর্বলতা: {w['weakness']}</div>
                <div style="color:#166534; background:#f0fdf4; padding:8px 12px; border-radius:4px; margin-top:8px; font-weight:600;">
                    ✅ সমাধান: {w['solution']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        c_gap1, c_gap2 = st.columns(2)
        
        with c_gap1:
            st.markdown("#### 🔑 Sub-Keywords Gap Matrix")
            kw_gap_df = pd.DataFrame(gap_analysis['keyword_gaps'])
            if not kw_gap_df.empty:
                st.dataframe(kw_gap_df[['keyword', 'competitor_count', 'user_count', 'status']], use_container_width=True, hide_index=True)
                
        with c_gap2:
            st.markdown("#### 📌 Sub-Headings & Subtopic Gaps")
            heading_gap_df = pd.DataFrame(gap_analysis['heading_gaps'])
            if not heading_gap_df.empty:
                st.dataframe(heading_gap_df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 3: SUGGESTED META & SOLUTIONS
    # -------------------------------------------------------------
    with tab3:
        st.markdown("### 🎯 ৩. কম্পিটিটরকে টপকাতে আমাদের কী করা উচিত (Outrank Blueprint & Meta)")
        
        meta = comp_analysis.get('suggested_meta', {})
        
        st.markdown("#### 📌 আপনার আর্টিকেলের জন্য প্রস্তাবিত Meta Title (High CTR)")
        st.info(f"**{meta.get('suggested_title', '')}**")
        st.markdown("##### 🔄 বিকল্প Meta Title আইডিয়াসমূহ:")
        for alt_t in meta.get('alternative_titles', []):
            st.markdown(f"- 🔹 `{alt_t}`")
            
        st.markdown("---")
        st.markdown("#### 📝 আপনার আর্টিকেলের জন্য প্রস্তাবিত Meta Description")
        st.success(f"{meta.get('suggested_meta_description', '')}")
        st.caption(f"Character Count: {meta.get('meta_description_char_count', 0)} characters (Optimal SEO length: 150-160 chars)")
        
        st.markdown("---")
        st.markdown("### 🎯 Outrank Blueprint: আমার কি করা উচিত")
        
        st.markdown("#### 🔥 High Priority Fixes (জরুরী করণীয়)")
        for act in recommendations['high_priority']:
            st.markdown(f'<div class="ai-action-high">{act}</div>', unsafe_allow_html=True)
            
        if recommendations['medium_priority']:
            st.markdown("#### 💡 Medium Priority Enhancements (গুরুত্বপূর্ণ পদক্ষেপ)")
            for act in recommendations['medium_priority']:
                st.markdown(f'<div class="ai-action-medium">{act}</div>', unsafe_allow_html=True)
                
        if recommendations['low_priority']:
            st.markdown("#### ⚙️ Low Priority Optimization (অতিরিক্ত বোনাস টিপস)")
            for act in recommendations['low_priority']:
                st.markdown(f'<div class="ai-action-low">{act}</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 4: EEAT, AEO, GEO & AI OVERVIEW STRATEGY
    # -------------------------------------------------------------
    with tab4:
        st.markdown("### 🤖 ৪. E-E-A-T, AEO & AI Overview কৌশল")
        
        ai_seo = comp_analysis.get('ai_seo_strategy', {})
        
        ai_col1, ai_col2 = st.columns(2)
        
        with ai_col1:
            st.markdown("#### 👤 E-E-A-T (Experience, Expertise, Authoritativeness, Trust) Checklist")
            for item in ai_seo.get('eeat_checklist', []):
                st.markdown(f"- {item}")
                
            st.markdown("#### ⚡ AEO & GEO Strategy (Answer & Generative Engine Optimization)")
            for item in ai_seo.get('aeo_geo_strategy', []):
                st.markdown(f"- {item}")
                
        with ai_col2:
            st.markdown("#### 🔮 Google AI Overview (SGE) & Perplexity-তে আসার কৌশল")
            st.info("গুগল AI Overview এবং ChatGPT Search এ আপনার পোস্ট ডাইরেক্ট ফিচার্ড করাতে নিচের ব্লুপ্রিন্টটি অনুসরণ করুন:")
            for item in ai_seo.get('ai_overview_blueprint', []):
                st.markdown(f"- **{item}**")
                
        st.markdown("---")
        st.markdown("#### 📐 Recommended Ready-to-Use Article Outline Structure for AI Overviews")
        st.code("\n".join(recommendations['recommended_outline']), language="markdown")

    # -------------------------------------------------------------
    # TAB 5: EXPORT & PDF DOWNLOAD
    # -------------------------------------------------------------
    with tab5:
        st.markdown("### 📄 PDF ও রিপোর্ট ডাউনলোড (Export & Download Report)")
        
        html_report = generate_html_report(comp_parsed, comp_analysis, user_parsed, gap_analysis, recommendations)
        pdf_bytes = generate_pdf_bytes(comp_parsed, comp_analysis, user_parsed, gap_analysis, recommendations)
        json_report = generate_json_report(comp_parsed, comp_analysis, user_parsed, gap_analysis, recommendations)
        
        exp_c1, exp_c2, exp_c3 = st.columns(3)
        
        with exp_c1:
            st.download_button(
                label="📄 Download Official PDF Report",
                data=pdf_bytes,
                file_name=f"ranknaser_competitor_report_{comp_analysis['focus_keyword'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with exp_c2:
            st.download_button(
                label="🌐 Download HTML Report",
                data=html_report,
                file_name=f"ranknaser_competitor_report_{comp_analysis['focus_keyword'].replace(' ', '_')}.html",
                mime="text/html",
                use_container_width=True
            )
            
        with exp_c3:
            st.download_button(
                label="📊 Download JSON Raw Data",
                data=json_report,
                file_name=f"ranknaser_competitor_data_{comp_analysis['focus_keyword'].replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )
            
        st.markdown("---")
        st.markdown("##### 👁️ Live HTML Report Preview (Click Print button inside to Save PDF):")
        st.components.v1.html(html_report, height=600, scrolling=True)

else:
    st.info("👈 Please enter Competitor & Your Article inputs in the sidebar or click **'Load Demo Sample Articles'** to try!")

