import re

def analyze_content_gap(competitor_data: dict, competitor_analysis: dict, user_data: dict) -> dict:
    """
    Performs comprehensive side-by-side gap analysis between competitor's article and user's article.
    """
    comp_text = competitor_data.get('full_text', '').lower()
    user_text = user_data.get('full_text', '').lower()
    
    comp_word_count = competitor_data.get('word_count', 0)
    user_word_count = user_data.get('word_count', 0)
    
    focus_keyword = competitor_analysis.get('focus_keyword', '')
    sub_keywords = competitor_analysis.get('sub_keywords', [])
    
    # 1. Focus Keyword Presence in User Article
    fk_lower = focus_keyword.lower()
    user_fk_count = user_text.count(fk_lower) if fk_lower else 0
    comp_fk_count = comp_text.count(fk_lower) if fk_lower else 0
    
    fk_gap_status = "OK"
    if user_fk_count == 0:
        fk_gap_status = "CRITICAL: Focus keyword is missing from your article!"
    elif user_fk_count < comp_fk_count / 2:
        fk_gap_status = "WARNING: Focus keyword density is significantly lower than competitor."
        
    # 2. Sub-Keyword Gap Analysis
    keyword_gaps = []
    for sk in sub_keywords:
        kw = sk['keyword']
        kw_lower = kw.lower()
        comp_freq = sk['frequency']
        user_freq = user_text.count(kw_lower)
        
        if user_freq == 0:
            status = "MISSING"
        elif user_freq < comp_freq:
            status = "UNDERUSED"
        else:
            status = "WELL COVERED"
            
        keyword_gaps.append({
            'keyword': kw,
            'type': sk['type'],
            'competitor_count': comp_freq,
            'user_count': user_freq,
            'status': status
        })
        
    # 3. Topic & Heading Gap Analysis
    comp_h2 = competitor_data.get('h2_headings', [])
    user_h2 = user_data.get('h2_headings', [])
    user_headings_text = " ".join([h.lower() for h in user_h2] + [user_data.get('title', '').lower()])
    
    heading_gaps = []
    for h in comp_h2:
        h_words = [w for w in re.findall(r'\b\w+\b', h.lower()) if len(w) > 3]
        # Check if user covers this topic in headings or content
        is_in_headings = any(any(w in uh.lower() for w in h_words) for uh in user_h2)
        is_in_content = any(w in user_text for w in h_words) if h_words else False
        
        if not is_in_headings and not is_in_content:
            status = "MISSING SECTION"
        elif not is_in_headings:
            status = "IN CONTENT BUT MISSING HEADING"
        else:
            status = "COVERED IN HEADING"
            
        heading_gaps.append({
            'competitor_heading': h,
            'status': status
        })
        
    # 4. Depth & Metrics Comparison
    word_count_diff = comp_word_count - user_word_count
    media_diff = competitor_data.get('image_count', 0) - user_data.get('image_count', 0)
    
    # Calculate Overall Gap Score (0 to 100, higher means bigger gap/more room for improvement)
    missing_kws = sum(1 for k in keyword_gaps if k['status'] == 'MISSING')
    missing_sections = sum(1 for h in heading_gaps if h['status'] == 'MISSING SECTION')
    
    gap_score = min(100, round(
        (missing_kws / max(1, len(keyword_gaps)) * 40) +
        (missing_sections / max(1, len(heading_gaps)) * 40) +
        (max(0, word_count_diff) / max(1, comp_word_count) * 20)
    ))
    
    # 5. Extract Specific User Weaknesses & Solutions
    user_weaknesses = []
    weakness_solutions = []
    
    if user_word_count < comp_word_count * 0.7:
        user_weaknesses.append({
            'weakness': f"আর্টিকেলের দৈঘ্য অনেক কম ({user_word_count} শব্দ, যেখানে প্রতিযোগীর আছে {comp_word_count} শব্দ)।",
            'solution': f"কমপক্ষে আরও {comp_word_count - user_word_count + 150} শব্দ নতুন তথ্য ও সেকশন যোগ করে আর্টিকেলের গভীরতা বাড়ান।"
        })
        
    if user_fk_count == 0:
        user_weaknesses.append({
            'weakness': f"প্রধান ফোকাস কিওয়ার্ড '{focus_keyword}' আপনার আর্টিকেলে একবারও উল্লেখ করা হয়নি!",
            'solution': f"আর্টিকেলের টাইটেল, ১ম প্যারাগ্রাফ, H2 হেডিং এবং অন্তত ৪-৫ বার বডি টেক্সটে '{focus_keyword}' বসান।"
        })
        
    missing_kw_names = [k['keyword'] for k in keyword_gaps if k['status'] == 'MISSING']
    if missing_kw_names:
        user_weaknesses.append({
            'weakness': f"কম্পিটিটর যেসব সাব-কিওয়ার্ড র্যাংক করেছে তার কয়েকটি আপনার আর্টিকেলে অনুপস্থিত: {', '.join(missing_kw_names[:5])}।",
            'solution': f"সাব-হেডিং ও প্যারাগ্রাফের ভেতরে প্রাকৃতিক উপায়ে {', '.join(missing_kw_names[:5])} কিওয়ার্ডগুলো ব্যবহার করুন।"
        })
        
    missing_heading_names = [h['competitor_heading'] for h in heading_gaps if h['status'] == 'MISSING SECTION']
    if missing_heading_names:
        user_weaknesses.append({
            'weakness': f"কম্পিটিটরের আর্টিকেলে থাকা গুরুত্বপূর্ণ সাব-টপিক আপনার আর্টিকেলে মিসিং: {', '.join(missing_heading_names[:3])}।",
            'solution': f"আপনার আর্টিকেলে নতুন H2 হেডিং হিসেবে '{missing_heading_names[0]}' এবং FAQ সেকশন যুক্ত করুন।"
        })
        
    if competitor_data.get('image_count', 0) > user_data.get('image_count', 0):
        user_weaknesses.append({
            'weakness': f"ভিজ্যুয়াল মিডিয়া ও ইমেজের অভাব (কম্পিটিটর {competitor_data.get('image_count', 0)}টি ছবি ব্যবহার করেছে, আপনার আছে {user_data.get('image_count', 0)}টি)।",
            'solution': f"পণ্যের অরিজিনাল ইনফোগ্রাফিক, স্পেসিফিকেশন ইমেজ ও কাস্টম স্ক্রিনশট Alt text সহ যুক্ত করুন।"
        })
        
    if not user_weaknesses:
        user_weaknesses.append({
            'weakness': "আর্টিকেলে E-E-A-T (লেখক পরিচিতি ও টেস্ট প্রুফ) এবং FAQ Schema মিসিং রয়েছে।",
            'solution': "আর্টিকেলের শুরুতে লেখক পরিচিতি এবং শেষে ৩-৪টি FAQ সহ Schema markup যুক্ত করুন।"
        })

    return {
        'focus_keyword': focus_keyword,
        'user_fk_count': user_fk_count,
        'competitor_fk_count': comp_fk_count,
        'fk_gap_status': fk_gap_status,
        'keyword_gaps': keyword_gaps,
        'heading_gaps': heading_gaps,
        'user_weaknesses': user_weaknesses,
        'metrics_comparison': {
            'competitor_word_count': comp_word_count,
            'user_word_count': user_word_count,
            'word_count_difference': word_count_diff,
            'competitor_images': competitor_data.get('image_count', 0),
            'user_images': user_data.get('image_count', 0),
            'competitor_headings_count': len(competitor_data.get('headings', [])),
            'user_headings_count': len(user_data.get('headings', [])),
        },
        'gap_score': gap_score
    }
