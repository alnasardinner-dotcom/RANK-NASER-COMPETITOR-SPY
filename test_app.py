from modules.scraper import process_raw_text
from modules.competitor_analyzer import analyze_competitor_article
from modules.gap_analyzer import analyze_content_gap
from modules.recommendation_engine import generate_outrank_recommendations
from modules.report_generator import generate_html_report

print("Testing Rank Naser Competitor Spy Modules...")

# Test Data
comp_text = """
# Best Smartphone in Bangladesh 2026 Price
Samsung Galaxy S24 Ultra is the top smartphone for camera performance and gaming in Bangladesh.
## Camera & Specs
With 200MP camera and Snapdragon 8 Gen 3, it offers supreme performance.
## Price in BD
The official price in BD is 185,000 BDT.
"""

user_text = """
# Best Smartphone Guide
Samsung phone is good for photos and apps.
## Prices
Price is high in BD market.
"""

comp_parsed = process_raw_text(comp_text, "Best Smartphone")
user_parsed = process_raw_text(user_text, "My Guide")

comp_analysis = analyze_competitor_article(comp_parsed)
print("Focus Keyword Detected:", comp_analysis['focus_keyword'])
print("Sub Keywords Count:", len(comp_analysis['sub_keywords']))
print("Brands Detected:", comp_analysis['brands_detected'])

gap_analysis = analyze_content_gap(comp_parsed, comp_analysis, user_parsed)
print("Gap Score:", gap_analysis['gap_score'])

recs = generate_outrank_recommendations(gap_analysis, comp_analysis, comp_parsed, user_parsed)
print("High Priority Recommendations Count:", len(recs['high_priority']))

html_report = generate_html_report(comp_parsed, comp_analysis, user_parsed, gap_analysis, recs)
print("HTML Report Generated Length:", len(html_report))

print("✅ ALL TESTS PASSED SUCCESSFULLY!")
