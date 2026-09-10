import re
import requests
import json
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

STOPWORDS = set([
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'can\'t', 'cannot',
    'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each',
    'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d',
    'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i',
    'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s',
    'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or',
    'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll',
    'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs',
    'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve',
    'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll',
    'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which',
    'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d',
    'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves', 'best', 'top', 'review', 'guide',
    'how', 'com', 'http', 'https', 'www', 'get', 'use', 'using', 'also', 'one', 'two', 'new', 'buy', 'price',
    'amp', 'gt', 'lt', 'quot', 'nbsp', 'looking', 'comprehensive', 'buying', 'overall', 'overview', 'bd',
    'bangladesh', '2024', '2025', '2026', 'make', 'well', 'good', 'even', 'like', 'just', 'more', 'than',
    'such', 'only', 'select', 'options', 'view', 'read', 'click', 'here', 'more', 'details'
])

COMMON_BRANDS = [
    'Apple', 'Samsung', 'Xiaomi', 'Realme', 'Vivo', 'Oppo', 'OnePlus', 'Asus', 'Dell', 'HP', 'Lenovo', 'Acer',
    'Sony', 'LG', 'Google', 'Microsoft', 'Amazon', 'Nike', 'Adidas', 'Puma', 'Intel', 'AMD', 'Nvidia',
    'Walton', 'Symphony', 'Techland', 'Startech', 'Ryans', 'Daraz', 'Bikroy', 'Custom Brand'
]

def analyze_competitor_article(parsed_data: dict, api_key: str = "", custom_focus_keyword: str = "") -> dict:
    """
    Analyzes competitor article and extracts Focus Keyword, Sub-keywords,
    Article Summary, Intent, Brand/Product Mentions, Meta recommendations, EEAT, and AEO/GEO strategies.
    Supports optional Gemini API Key for deep AI semantic enrichment and optional custom user focus keyword input.
    """
    title = parsed_data.get('title', '')
    url_slug_kw = parsed_data.get('url_slug_keywords', '')
    meta_desc = parsed_data.get('meta_description', '')
    full_text = parsed_data.get('full_text', '')
    headings = parsed_data.get('headings', [])
    h1_h2_text = " ".join([h['text'] for h in headings if h['tag'] in ['H1', 'H2']])
    
    # 1. Extract or set Focus Keyword
    if custom_focus_keyword and custom_focus_keyword.strip():
        focus_keyword = custom_focus_keyword.strip().title()
    else:
        focus_keyword = _extract_focus_keyword(title, h1_h2_text, full_text, url_slug_kw)
    
    # 2. Extract Sub-Keywords (N-Grams & LSI Phrases)
    sub_keywords = _extract_sub_keywords(full_text, focus_keyword)
    
    # 3. Detect Brands & Products
    brand_info = _detect_brands_and_products(full_text, title)
    
    # 4. Determine User Intent & Purpose ("মানুষের জন্য কি বলতে চায়")
    intent_data = _analyze_reader_intent(title, meta_desc, full_text, headings)
    
    # 5. Core Executive Summary ("মূল কথা")
    summary = _generate_executive_summary(title, meta_desc, full_text, headings, brand_info)
    
    # 6. Generate Suggested Title & Meta Description for User's Article
    suggested_meta = _generate_suggested_metadata(focus_keyword, brand_info)
    
    # 7. Generate E-E-A-T & AEO/GEO Strategy for AI Overview Ranking
    ai_seo_strategy = _generate_ai_seo_strategy(focus_keyword, brand_info)
    
    # 8. Optional Gemini AI API Deep Enhancement
    ai_boost_results = None
    if api_key:
        ai_boost_results = _call_gemini_ai_analysis(full_text[:3000], focus_keyword, api_key)
        if ai_boost_results:
            if 'focus_keyword' in ai_boost_results and not (custom_focus_keyword and custom_focus_keyword.strip()):
                focus_keyword = ai_boost_results['focus_keyword']
            if 'suggested_title' in ai_boost_results:
                suggested_meta['suggested_title'] = ai_boost_results['suggested_title']
            if 'suggested_meta_description' in ai_boost_results:
                suggested_meta['suggested_meta_description'] = ai_boost_results['suggested_meta_description']
    
    return {
        'focus_keyword': focus_keyword,
        'sub_keywords': sub_keywords,
        'brands_detected': brand_info['brands'],
        'products_highlighted': brand_info['products'],
        'intent_summary': intent_data,
        'executive_summary': summary,
        'suggested_meta': suggested_meta,
        'ai_seo_strategy': ai_seo_strategy,
        'ai_boost_active': True if ai_boost_results else False,
        'stats': {
            'word_count': parsed_data.get('word_count', 0),
            'headings_count': len(headings),
            'reading_time': parsed_data.get('reading_time_min', 0),
            'image_count': parsed_data.get('image_count', 0),
            'internal_links': parsed_data.get('internal_link_count', 0),
            'external_links': parsed_data.get('external_link_count', 0),
            'engine': parsed_data.get('source_engine', 'Scraper Core')
        }
    }

def _call_gemini_ai_analysis(article_text: str, current_fk: str, api_key: str) -> dict:
    """
    Calls Google Gemini API for deep AI semantic analysis & Google AI Overview recommendations.
    """
    models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    prompt = (
        f"You are RankNaser AI SEO Intelligence. Analyze this competitor article:\n'{article_text[:2500]}'.\n"
        f"Return valid JSON ONLY with keys:\n"
        f"- 'focus_keyword': main focus keyword targeting\n"
        f"- 'suggested_title': high CTR Meta Title in Bangla/English\n"
        f"- 'suggested_meta_description': persuasive Meta Description under 160 chars\n"
        f"- 'ai_overview_tip': 1 key actionable tip to rank in Google AI Overviews\n"
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                data = res.json()
                raw_output = data['candidates'][0]['content']['parts'][0]['text']
                json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
        except Exception:
            continue
    return None

def _generate_suggested_metadata(focus_keyword: str, brand_info: dict) -> dict:
    """
    Generates optimized Title and Meta Description recommendations for high CTR.
    """
    fk = focus_keyword.title()
    brand_str = brand_info['brands'][0] if brand_info['brands'] else "Top Brand"
    
    suggested_titles = [
        f"{fk} Price in Bangladesh 2026 - Comprehensive Buyer's Guide & Review",
        f"Best {fk} ({brand_str}) - Price, Specification & Buying Advice in BD",
        f"{fk} Review & BD Price 2026: Everything You Need to Know Before Buying"
    ]
    
    suggested_meta_desc = (
        f"Looking for the best {fk} in Bangladesh? Compare prices, detailed specs, pros & cons, "
        f"and expert buying recommendations to get the best deal in 2026."
    )
    
    return {
        'suggested_title': suggested_titles[0],
        'alternative_titles': suggested_titles[1:],
        'suggested_meta_description': suggested_meta_desc,
        'meta_description_char_count': len(suggested_meta_desc),
        'title_char_count': len(suggested_titles[0])
    }

def _generate_ai_seo_strategy(focus_keyword: str, brand_info: dict) -> dict:
    """
    Generates E-E-A-T, AEO, GEO, and Google AI Overview inclusion strategies.
    """
    fk = focus_keyword.title()
    
    eeat_checklist = [
        "👤 **Author Bio & Credibility**: আর্টিকেলের শুরুতে লেখক/বিশেষজ্ঞের নাম, ছবি ও কাজের অভিজ্ঞতা যুক্ত করুন।",
        "🧪 **First-Hand Experience (অভিজ্ঞতা)**: পণ্যটি নিজে ব্যবহার বা টেস্ট করার নিজস্ব মতামত ও নিজস্ব তোলা আসল ছবি যুক্ত করুন।",
        "🔗 **Authority Citations (তথ্যসূত্র)**: অফিসিয়াল ব্র্যান্ড সাইট বা বিশ্বস্ত সূত্রে আউটবাউন্ড লিংক প্রদান করুন।",
        "🕒 **Last Updated Badge**: আর্টিকেলটি কত তারিখে আপডেট করা হয়েছে তার তারিখ স্পষ্টভাবে উল্লেখ করুন।"
    ]
    
    aeo_geo_strategy = [
        "🎯 **Direct Answer Box (৪০-৬০ শব্দের উত্তর)**: আর্টিকেলের প্রথম ১৫০ শব্দের মধ্যে মূল প্রশ্ন বা কিওয়ার্ডের একটি সংক্ষিপ্ত চূড়ান্ত উত্তর (Direct Summary) দিন।",
        "📊 **Tabular Data & Comparison**: তথ্যগুলোকে প্যারাগ্রাফের পাশাপাশি টেবিল আকারে সাজান (AEO/GEO বট ডাইরেক্ট টেবিল রিড করে)।",
        "❓ **FAQ Schema Markup**: আর্টিকেলের নিচে FAQ Schema সহ ৪-৫টি প্রশ্ন ও সঠিক উত্তর যুক্ত করুন।"
    ]
    
    ai_overview_blueprint = [
        f"1️⃣ **H2 Heading Question Format**: 'What is {fk}?' বা '{fk} Price in BD' টাইটেল দিন।",
        f"2️⃣ **Bullet List Summary**: পণ্যের ৫-৬টি প্রধান পয়েন্ট বুলেট লিস্ট আকারে দিন।",
        f"3️⃣ **Key Takeaways Box**: প্রতিটি সেকশনের শুরুতে ১ বাক্যের টেক-অ্যাওয়ে ডাব্বা যুক্ত করুন।",
        f"4️⃣ **Structured Specs Table**: মূল স্পেসিফিকেশন ও দামের স্বচ্ছ তুলনামূলক টেবিল যোগ করুন।"
    ]
    
    return {
        'eeat_checklist': eeat_checklist,
        'aeo_geo_strategy': aeo_geo_strategy,
        'ai_overview_blueprint': ai_overview_blueprint
    }

def _extract_focus_keyword(title: str, headings_text: str, full_text: str, url_slug_kw: str = "") -> str:
    """
    Determines the most likely Focus Keyword based on Title, H1/H2, URL Slug, TF-IDF and density.
    """
    # Strip common site titles like '| Star Tech', '- Daraz.com.bd', 'BD'
    cleaned_title = re.sub(r'(\||-)\s*(Star Tech|Daraz|Bikroy|Techland|Ryans).*', '', title, flags=re.I)
    clean_title = re.sub(r'[^\w\s]', '', cleaned_title.lower())
    
    # Exclude numeric words and digits
    title_words = [w for w in clean_title.split() if w not in STOPWORDS and len(w) > 2 and not w.isdigit()]
    
    if url_slug_kw:
        slug_clean = re.sub(r'[^\w\s]', '', url_slug_kw.lower())
        slug_words = [w for w in slug_clean.split() if w not in STOPWORDS and len(w) > 2 and not w.isdigit()]
        if len(slug_words) >= 2:
            return " ".join(slug_words).title()
    
    # Generate 2-gram and 3-gram candidates from title
    candidates = []
    for i in range(len(title_words)):
        if i + 1 < len(title_words):
            cand = f"{title_words[i]} {title_words[i+1]}"
            if not re.match(r'^\d+$', title_words[i]) and not re.match(r'^\d+$', title_words[i+1]):
                candidates.append(cand)
        if i + 2 < len(title_words):
            cand = f"{title_words[i]} {title_words[i+1]} {title_words[i+2]}"
            if not re.match(r'^\d+$', title_words[i+2]):
                candidates.append(cand)
            
    # Count candidate frequencies in full text
    full_text_lower = full_text.lower()
    candidate_scores = {}
    
    for candidate in candidates:
        count = full_text_lower.count(candidate)
        in_title_weight = 3 if candidate in clean_title else 1
        in_headings_weight = 2 if candidate in headings_text.lower() else 1
        candidate_scores[candidate] = count * in_title_weight * in_headings_weight
        
    if candidate_scores:
        best_candidate = max(candidate_scores, key=candidate_scores.get)
        if candidate_scores[best_candidate] > 0:
            return best_candidate.title()
            
    return title_words[0].title() if title_words else (url_slug_kw.title() if url_slug_kw else "Main Product Keyword")

def _extract_sub_keywords(full_text: str, focus_keyword: str, top_n: int = 15) -> list:
    """
    Extracts secondary / sub-keywords and LSI phrases from the body text.
    """
    full_text_clean = re.sub(r'[^\w\s]', ' ', full_text.lower())
    words = [w for w in full_text_clean.split() if w not in STOPWORDS and len(w) > 2 and not w.isdigit()]
    
    # Extract 2-gram and 3-grams
    bigrams = [" ".join(words[i:i+2]) for i in range(len(words)-1) if words[i] not in STOPWORDS and words[i+1] not in STOPWORDS]
    trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2) if words[i] not in STOPWORDS and words[i+2] not in STOPWORDS]
    
    fk_lower = focus_keyword.lower()
    
    # Filter out exact focus keyword
    bigram_counts = Counter([b for b in bigrams if b != fk_lower])
    trigram_counts = Counter([t for t in trigrams if t != fk_lower])
    single_counts = Counter([w for w in words if w not in fk_lower.split()])
    
    results = []
    
    # Top Trigrams (Long-tail)
    for phrase, count in trigram_counts.most_common(5):
        if count >= 2:
            results.append({'keyword': phrase.title(), 'type': 'Long-Tail / 3-Gram', 'frequency': count})
            
    # Top Bigrams (Sub-topics)
    for phrase, count in bigram_counts.most_common(8):
        if count >= 2 and not any(phrase in r['keyword'].lower() for r in results):
            results.append({'keyword': phrase.title(), 'type': 'Sub-Topic / 2-Gram', 'frequency': count})
            
    # Top Single Keywords (LSI)
    for word, count in single_counts.most_common(6):
        if count >= 3 and not any(word in r['keyword'].lower() for r in results):
            results.append({'keyword': word.title(), 'type': 'LSI Keyword', 'frequency': count})
            
    return results[:top_n]

def _detect_brands_and_products(full_text: str, title: str) -> dict:
    """
    Detects brand names, company names, and specific model/product highlights strictly present in the article.
    """
    text_to_search = title + " " + full_text
    found_brands = set()
    
    for brand in COMMON_BRANDS:
        if re.search(r'\b' + re.escape(brand) + r'\b', text_to_search, re.I):
            found_brands.add(brand)
            
    # Product Model Keywords (RTX 4060, Galaxy S24, Legion 5, iPhone 15, Core i7, etc.)
    product_keywords = [
        r'\b(iPhone\s+[0-9]{1,2}(?:\s+(?:Pro|Max|Plus|Mini))?)\b',
        r'\b(Galaxy\s+[S|A|M|Z][0-9]{1,2}(?:\s+(?:Ultra|Plus|FE))?)\b',
        r'\b(RTX\s+[0-9]{4}(?:\s+Ti)?)\b',
        r'\b(GTX\s+[0-9]{4}(?:\s+Ti)?)\b',
        r'\b(Radeon\s+RX\s+[0-9]{4})\b',
        r'\b(Core\s+i[3|5|7|9](?:\s+[0-9]{4,5}[A-Z]*)?)\b',
        r'\b(Ryzen\s+[3|5|7|9](?:\s+[0-9]{4,5}[A-Z]*)?)\b',
        r'\b(ROG\s+Strix(?:\s+[A-Z0-9]+)?)\b',
        r'\b(Legion\s+[0-9]{1,2}(?:\s+Pro)?)\b',
        r'\b(Victus\s+[0-9]{2})\b',
        r'\b(Redmi\s+Note\s+[0-9]{1,2})\b',
        r'\b(MacBook\s+(?:Air|Pro))\b',
        r'\b(iPad\s+(?:Air|Pro|Mini)?)\b'
    ]
    
    products = set()
    for pattern in product_keywords:
        matches = re.findall(pattern, text_to_search, re.I)
        for m in matches[:6]:
            prod_str = m.strip() if isinstance(m, str) else " ".join(m).strip()
            if len(prod_str) > 2:
                products.add(prod_str.title())
                
    return {
        'brands': list(found_brands) if found_brands else ["ব্র্যান্ডের নাম উল্লেখ নেই (Generic/Custom Brand)"],
        'products': list(products)[:8] if products else [title.title()[:35]]
    }

def _analyze_reader_intent(title: str, meta_desc: str, full_text: str, headings: list) -> dict:
    """
    Identifies intent, target audience, and primary consumer value ("মানুষের জন্য কি বলতে চায়").
    """
    combined = (title + " " + meta_desc + " " + " ".join([h['text'] for h in headings])).lower()
    
    intent_type = "Informational (তথ্যমূলক গাইড)"
    if any(k in combined for k in ['buy', 'price', 'cost', 'discount', 'deal', 'shop', 'order', 'কিনুন', 'দাম']):
        intent_type = "Transactional / Commercial (পণ্য কেনাকাটা বা বাণিজ্যিক)"
    elif any(k in combined for k in ['vs', 'versus', 'compare', 'difference', 'tuleana', 'তুলনা']):
        intent_type = "Commercial Comparison (তুলনামূলক রিভিউ ও গাইড)"
    elif any(k in combined for k in ['how to', 'guide', 'tips', 'tutorial', 'step by step', 'উপায়']):
        intent_type = "How-To / Educational (ব্যবহারিক টিউটোরিয়াল ও গাইড)"
        
    value_props = []
    if any(k in combined for k in ['price', 'budget', 'cheap', 'affordable', 'কম দাম']):
        value_props.append("বাজেট ও সাশ্রয়ী মূল্য সংক্রান্ত তথ্য (Budget & Pricing)")
    if any(k in combined for k in ['feature', 'spec', 'performance', 'quality', 'মান']):
        value_props.append("পারফরম্যান্স ও স্পেসিফিকেশন পরিচিতি (Performance & Specs)")
    if any(k in combined for k in ['pros', 'cons', 'advantage', 'disadvantage', 'সুবিধা', 'অসুবিধা']):
        value_props.append("সুবিধা ও অসুবিধা বিশ্লেষণ (Pros & Cons Analysis)")
    if any(k in combined for k in ['where to buy', 'store', 'shop', 'দোকান']):
        value_props.append("কোথা থেকে কিনবেন তার নির্দেশনা (Where to Buy Guide)")
        
    if not value_props:
        value_props.append("পণ্যের বিস্তারিত বৈশিষ্ট্য ও সঠিক ব্যবহার পদ্ধতি (Detailed Product Specs & Usage)")
        
    return {
        'intent_type': intent_type,
        'target_audience': "সাধারণ ক্রেতা, প্রযুক্তি ও পণ্য অনুসন্ধানী পাঠকরা",
        'core_value_for_users': value_props
    }

def _generate_executive_summary(title: str, meta_desc: str, full_text: str, headings: list, brand_info: dict) -> dict:
    """
    Generates structured executive summary ("মূল কথা: আর্টিকেলে কি কি আলোচনা করা হয়েছে").
    """
    top_topics = [h['text'] for h in headings if h['tag'] in ['H2', 'H3']][:6]
    
    summary_text = (
        f"প্রতিযোগীর এই আর্টিকেলে মূলত '{title}' সম্পর্কে বিষদ আলোচনা করা হয়েছে। "
        f"আর্টিকেলে প্রধানত {', '.join(brand_info['brands'])} ব্র্যান্ডের পণ্যসমূহ তুলে ধরা হয়েছে। "
        f"পাঠকদের জন্য আর্টিকেলের প্রধান আলোচ্য বিষয়গুলো নিচে উল্লেখ করা হলো:"
    )
    
    return {
        'overview_text': summary_text,
        'key_topics_covered': top_topics if top_topics else [
            "পণ্যের হাইলাইটস ও পরিচিতি",
            "প্রধান বৈশিষ্ট্য ও কারিগরি বিবরণ",
            "বাজার মূল্য ও অফারসমূহ",
            "ব্যবহারকারীদের জন্য গাইডলাইন"
        ]
    }
