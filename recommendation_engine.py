def generate_outrank_recommendations(gap_analysis: dict, competitor_analysis: dict, competitor_data: dict, user_data: dict) -> dict:
    """
    Generates actionable outrank recommendations ('আমার কি করা উচিত') based on content gap analysis.
    """
    focus_kw = gap_analysis.get('focus_keyword', 'Main Keyword')
    gap_score = gap_analysis.get('gap_score', 50)
    metrics = gap_analysis.get('metrics_comparison', {})
    
    high_priority_actions = []
    medium_priority_actions = []
    low_priority_actions = []
    
    # 1. Word Count & Content Depth Check
    word_diff = metrics.get('word_count_difference', 0)
    if word_diff > 300:
        high_priority_actions.append(
            f"⚡ **আর্টিকেলের দৈর্ঘ্য বাড়ান (Word Count Expansion):** "
            f"আপনার আর্টিকেলে বর্তমানে {metrics['user_word_count']} শব্দ আছে, যা প্রতিযোগীর চেয়ে {word_diff} শব্দ কম। "
            f"কমপক্ষে আরও {word_diff + 150} শব্দ নতুন তথ্য যোগ করে আর্টিকেলটি সমৃদ্ধ করুন।"
        )
    elif word_diff > 0:
        medium_priority_actions.append(
            f"📝 **সামান্য শব্দের পরিমাণ বাড়ান:** "
            f"প্রতিযোগীর সমকক্ষ হতে আরও অন্তত {word_diff + 100} শব্দ যুক্ত করুন।"
        )
        
    # 2. Focus Keyword Fixes
    if gap_analysis.get('user_fk_count', 0) == 0:
        high_priority_actions.append(
            f"🚨 **প্রধান কিওয়ার্ড যোগ করুন (Focus Keyword Insertion):** "
            f"আপনার আর্টিকেলে মূল কিওয়ার্ড **'{focus_kw}'** একবারও ব্যবহার করা হয়নি! "
            f"আর্টিকেলের প্রথম ১০০ শব্দের মধ্যে (Intro), H1/H2 হেডিং এবং অন্তত ৪-৫ বার বডি টেক্সটে এই কিওয়ার্ড যুক্ত করুন।"
        )
    elif gap_analysis.get('user_fk_count', 0) < gap_analysis.get('competitor_fk_count', 0) / 2:
        medium_priority_actions.append(
            f"🎯 **প্রধান কিওয়ার্ডের ব্যবহার বাড়ান:** "
            f"প্রতিযোগী **'{focus_kw}'** {gap_analysis['competitor_fk_count']} বার ব্যবহার করেছে, আপনার আর্টিকেলে আছে {gap_analysis['user_fk_count']} বার। "
            f"প্রাকৃতিকভাবে আরও {gap_analysis['competitor_fk_count'] - gap_analysis['user_fk_count']} বার কিওয়ার্ডটি যুক্ত করুন।"
        )
        
    # 3. Missing Keywords Fixes
    missing_kws = [k for k in gap_analysis.get('keyword_gaps', []) if k['status'] == 'MISSING']
    if missing_kws:
        top_missing = [k['keyword'] for k in missing_kws[:6]]
        high_priority_actions.append(
            f"🔑 **অনুপস্থিত সাব-কিওয়ার্ডসমূহ যুক্ত করুন (Missing Sub-Keywords):** "
            f"প্রতিযোগী আর্টিকেলে নিম্নলিখিত সাব-কিওয়ার্ডগুলো ব্যবহার করেছে যা আপনার আর্টিকেলে অনুপস্থিত: "
            f"**{', '.join(top_missing)}**। এগুলো আপনার আর্টিকেলের সাব-সেকশনে যুক্ত করুন।"
        )
        
    # 4. Missing Headings / Topics
    missing_headings = [h['competitor_heading'] for h in gap_analysis.get('heading_gaps', []) if h['status'] == 'MISSING SECTION']
    if missing_headings:
        suggested_h2 = missing_headings[:4]
        high_priority_actions.append(
            f"📌 **নতুন সাব-হেডিং যোগ করুন (Add Missing Sections/Headings):** "
            f"প্রতিযোগীর আর্টিকেলে থাকা নিচের টপিকগুলো আপনার আর্টিকেলে মিসিং রয়েছে। আপনার আর্টিকেলে এগুলো হেডিং হিসেবে যোগ করুন:\n" +
            "\n".join([f"  - 🔹 H2: **{h}**" for h in suggested_h2])
        )
        
    # 5. Media & Visual Enhancement
    img_diff = metrics.get('competitor_images', 0) - metrics.get('user_images', 0)
    if img_diff > 0:
        medium_priority_actions.append(
            f"🖼️ **ছবি ও ভিজ্যুয়াল কন্টেন্ট যোগ করুন (Add Images & Media):** "
            f"প্রতিযোগী {metrics['competitor_images']}টি ছবি ব্যবহার করেছে, আর আপনার আছে {metrics['user_images']}টি। "
            f"পণ্যের অন্তত {img_diff + 1}টি ইনফোগ্রাফিক, স্ক্রিনশট বা হাই-কোয়ালিটি ছবি Alt Text সহ যুক্ত করুন।"
        )
        
    # 6. FAQ & Schema Suggestions
    low_priority_actions.append(
        f"❓ **FAQ (প্রশ্নোত্তর সেকশন) ও Schema markup যোগ করুন:** "
        f"আর্টিকেলের শেষে অন্তত ৩-৪টি সচরাচর জিজ্ঞাসিত প্রশ্ন (FAQ) এবং FAQ Schema যুক্ত করুন। "
        f"এটি গুগলের Rich Snippet বা People Also Ask (PAA) তে র‍্যাংক পেতে সাহায্য করবে।"
    )
    
    # 7. Comparison Table Suggestion
    low_priority_actions.append(
        f"📊 **একটি বৈশিষ্ট্য/মূল্য তুলনা টেবিল (Comparison Table) যুক্ত করুন:** "
        f"পাঠকদের দ্রুত সিদ্ধান্ত নিতে সাহায্য করার জন্য একটি সুন্দর Table যোগ করুন।"
    )
    
    # Proposed Ready-to-Use Outline
    recommended_outline = [
        f"H1: {user_data.get('title', 'আপনার পণ্যের শিরোনাম (Optimized Title)')}",
        f"  ├── Intro: প্রথম অনুচ্ছেদে '{focus_kw}' কিওয়ার্ডের সহজ ব্যবহার",
        f"  ├── H2: {focus_kw} এর মূল বৈশিষ্ট্য ও পরিচিতি",
    ]
    for h in missing_headings[:3]:
        recommended_outline.append(f"  ├── H2: {h}")
    recommended_outline.extend([
        f"  ├── H2: সুবিধা ও অসুবিধা (Pros & Cons)",
        f"  ├── H2: সচরাচর জিজ্ঞাসিত প্রশ্নাবলী (FAQ Section)",
        f"  └── Conclusion: চূড়ান্ত সিদ্ধান্ত ও কেনার গাইডলাইন (Call to Action)"
    ])
    
    return {
        'gap_score': gap_score,
        'summary_verdict': (
            f"আপনার কন্টেন্ট প্রতিযোগীর চেয়ে পিছিয়ে রয়েছে ({gap_score}% গ্যাপ স্কোর)। "
            f"উপরে উল্লেখিত হাই-প্রাইওরিটি অ্যাকশনগুলো সম্পন্ন করলে আপনার আর্টিকেলের র্যাঙ্কিং সম্ভাবনা ৯+ গুণ বৃদ্ধি পাবে।"
            if gap_score > 40 else
            f"আপনার আর্টিকেল যথেষ্ট ভালো অবস্থানে আছে ({gap_score}% গ্যাপ)। "
            f"কেবল কয়েকটি সাব-কিওয়ার্ড ও মিডিয়া অপটিমাইজ করলেই প্রতিযোগীকে সহজেই পেছনে ফেলা সম্ভব।"
        ),
        'high_priority': high_priority_actions,
        'medium_priority': medium_priority_actions,
        'low_priority': low_priority_actions,
        'recommended_outline': recommended_outline
    }
