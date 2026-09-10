import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_html_report(competitor_data: dict, competitor_analysis: dict, user_data: dict, gap_analysis: dict, recommendations: dict) -> str:
    """
    Generates a full HTML audit report of Competitor Intelligence, Content Gap Analysis, Weaknesses, Meta Suggestions, and AI Overview Strategies.
    """
    focus_kw = competitor_analysis.get('focus_keyword', 'N/A')
    suggested_meta = competitor_analysis.get('suggested_meta', {})
    ai_seo = competitor_analysis.get('ai_seo_strategy', {})
    weaknesses = gap_analysis.get('user_weaknesses', [])
    
    html = f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rank Naser Competitor Spy Report - {focus_kw}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #ffffff;
            color: #0f172a;
            margin: 0;
            padding: 25px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            background: #ffffff;
            padding: 35px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            border: 1px solid #e2e8f0;
        }}
        h1, h2, h3 {{
            color: #0284c7;
        }}
        h1 {{
            border-bottom: 2px solid #0284c7;
            padding-bottom: 10px;
            margin-top: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .badge {{
            background: #0284c7;
            color: #fff;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 25px;
        }}
        .card {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            color: #0f172a;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            border: 1px solid #e2e8f0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background: #f1f5f9;
            color: #0369a1;
            font-weight: 700;
        }}
        td {{
            color: #1e293b;
        }}
        .high-priority {{
            background: #fff7ed;
            border-left: 4px solid #ea580c;
            color: #9a3412;
            padding: 14px;
            margin: 10px 0;
            border-radius: 6px;
        }}
        .weakness-card {{
            background: #fef2f2;
            border-left: 4px solid #ef4444;
            color: #991b1b;
            padding: 14px;
            margin: 10px 0;
            border-radius: 6px;
        }}
        .solution-text {{
            color: #166534;
            background: #f0fdf4;
            padding: 8px 12px;
            border-radius: 4px;
            margin-top: 6px;
            font-weight: 600;
        }}
        .code-box {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            white-space: pre-wrap;
            color: #0369a1;
        }}
        .print-btn {{
            background: #0284c7;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
        }}
        @media print {{
            .print-btn {{ display: none; }}
            body {{ padding: 0; }}
            .container {{ border: none; box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>
            <span>⚡ Rank Naser Competitor Spy Report</span>
            <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
        </h1>
        <p><strong>Primary Focus Keyword:</strong> <span class="badge">{focus_kw}</span></p>
        <p><strong>Competitor URL:</strong> {competitor_data.get('url', 'N/A')}</p>
        <p><strong>Your Article URL:</strong> {user_data.get('url', 'Direct Text / Pasted Article')}</p>
        <p><strong>Content Gap Score:</strong> <span class="badge">{gap_analysis.get('gap_score', 0)}% Gap</span></p>
        
        <hr style="border-color: #e2e8f0; margin: 25px 0;">
        
        <h2>🕵️ 1. Competitor Article Analysis (কম্পিটিটর আর্টিকেলের মূল বিষয়)</h2>
        <div class="grid">
            <div class="card">
                <h3>📌 মূল কথা & সারসংক্ষেপ</h3>
                <p>{competitor_analysis.get('executive_summary', {}).get('overview_text', '')}</p>
                <ul>
                {"".join([f"<li>{t}</li>" for t in competitor_analysis.get('executive_summary', {}).get('key_topics_covered', [])])}
                </ul>
            </div>
            <div class="card">
                <h3>🎯 ইউজার ইন্টেন্ট & ব্র্যান্ড</h3>
                <p><strong>সার্চ ইন্টেন্ট:</strong> {competitor_analysis.get('intent_summary', {}).get('intent_type', '')}</p>
                <p><strong>ব্র্যান্ডসমূহ:</strong> {", ".join(competitor_analysis.get('brands_detected', []))}</p>
                <p><strong>শব্দ সংখ্যা:</strong> {competitor_data.get('word_count', 0)} words</p>
            </div>
        </div>
        
        <h2>⚔️ 2. Content Gap & Weaknesses Analysis (আপনার দুর্বলতাসমূহ ও গ্যাপ)</h2>
        <table>
            <thead>
                <tr>
                    <th>মেট্রিক</th>
                    <th>কম্পিটিটর আর্টিকেল</th>
                    <th>আপনার আর্টিকেল</th>
                    <th>পার্থক্য / গ্যাপ</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Word Count</td>
                    <td>{gap_analysis['metrics_comparison']['competitor_word_count']} words</td>
                    <td>{gap_analysis['metrics_comparison']['user_word_count']} words</td>
                    <td>{gap_analysis['metrics_comparison']['word_count_difference']} words</td>
                </tr>
                <tr>
                    <td>Focus Keyword Usage</td>
                    <td>{gap_analysis['competitor_fk_count']} times</td>
                    <td>{gap_analysis['user_fk_count']} times</td>
                    <td>{gap_analysis['fk_gap_status']}</td>
                </tr>
                <tr>
                    <td>Images</td>
                    <td>{gap_analysis['metrics_comparison']['competitor_images']} images</td>
                    <td>{gap_analysis['metrics_comparison']['user_images']} images</td>
                    <td>{gap_analysis['metrics_comparison']['competitor_images'] - gap_analysis['metrics_comparison']['user_images']} images</td>
                </tr>
            </tbody>
        </table>
        
        <h3>🚨 চিহ্নিত দুর্বলতাসমূহ & সমাধান (Weaknesses & Solutions)</h3>
        {"".join([f'<div class="weakness-card"><strong>❌ দুর্বলতা:</strong> {w["weakness"]}<div class="solution-text">✅ সমাধান: {w["solution"]}</div></div>' for w in weaknesses])}
        
        <h2>🏷️ 3. Proposed Meta Title & Meta Description Recommendations</h2>
        <div class="card">
            <p><strong>📌 প্রস্তাবিত Meta Title:</strong></p>
            <div class="code-box">{suggested_meta.get('suggested_title', '')}</div>
            
            <p style="margin-top:15px;"><strong>📝 প্রস্তাবিত Meta Description:</strong></p>
            <div class="code-box">{suggested_meta.get('suggested_meta_description', '')}</div>
        </div>

        <h2>🤖 4. E-E-A-T, AEO/GEO & AI Overview Strategy (গুগল AI র্যাঙ্কিং ব্লুপ্রিন্ট)</h2>
        <div class="grid">
            <div class="card">
                <h3>👤 E-E-A-T Checklist</h3>
                <ul>
                {"".join([f"<li>{item}</li>" for item in ai_seo.get('eeat_checklist', [])])}
                </ul>
            </div>
            <div class="card">
                <h3>⚡ AI Overview Feature Blueprint</h3>
                <ul>
                {"".join([f"<li>{item}</li>" for item in ai_seo.get('ai_overview_blueprint', [])])}
                </ul>
            </div>
        </div>
        
        <h2>🎯 5. Outrank Action Blueprint - আমার কি করা উচিত</h2>
        <h3>🔥 High Priority Action Items</h3>
        {"".join([f'<div class="high-priority">{act}</div>' for act in recommendations.get('high_priority', [])])}
        
        <h3>💡 Proposed Content Outline</h3>
        <div class="code-box">
{"\n".join(recommendations.get('recommended_outline', []))}
        </div>
    </div>
</body>
</html>
"""
    return html

def generate_pdf_bytes(competitor_data: dict, competitor_analysis: dict, user_data: dict, gap_analysis: dict, recommendations: dict) -> bytes:
    """
    Generates a clean, downloadable PDF report file.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('ReportTitle', parent=styles['Title'], fontSize=20, textColor=colors.HexColor('#0284c7'), spaceAfter=12)
    heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0369a1'), spaceBefore=12, spaceAfter=8)
    body_style = ParagraphStyle('ReportBody', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#1e293b'))
    bullet_style = ParagraphStyle('ReportBullet', parent=styles['Normal'], fontSize=10, leading=14, leftIndent=15, textColor=colors.HexColor('#334155'))
    
    story = []
    
    # Title & Metadata
    focus_kw = competitor_analysis.get('focus_keyword', 'N/A')
    story.append(Paragraph("Rank Naser Competitor Spy Report", title_style))
    story.append(Paragraph(f"<b>Focus Keyword:</b> {focus_kw}", body_style))
    story.append(Paragraph(f"<b>Competitor URL:</b> {competitor_data.get('url', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Content Gap Score:</b> {gap_analysis.get('gap_score', 0)}%", body_style))
    story.append(Spacer(1, 14))
    
    # 1. Executive Summary
    story.append(Paragraph("1. Competitor Article Analysis Summary", heading_style))
    summary_text = competitor_analysis.get('executive_summary', {}).get('overview_text', '')
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))
    
    # 2. Side-by-Side Metrics Table
    story.append(Paragraph("2. Content Metrics Comparison", heading_style))
    table_data = [
        ['Metric', 'Competitor Article', 'Your Article', 'Difference'],
        ['Word Count', f"{gap_analysis['metrics_comparison']['competitor_word_count']}", f"{gap_analysis['metrics_comparison']['user_word_count']}", f"{gap_analysis['metrics_comparison']['word_count_difference']}"],
        ['Focus Keyword Count', f"{gap_analysis['competitor_fk_count']}", f"{gap_analysis['user_fk_count']}", f"{gap_analysis['fk_gap_status']}"],
        ['Images Count', f"{gap_analysis['metrics_comparison']['competitor_images']}", f"{gap_analysis['metrics_comparison']['user_images']}", f"{gap_analysis['metrics_comparison']['competitor_images'] - gap_analysis['metrics_comparison']['user_images']}"]
    ]
    
    t = Table(table_data, colWidths=[130, 120, 120, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0369a1')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))
    
    # 3. Weaknesses & Solutions
    story.append(Paragraph("3. Identified Weaknesses & Fixes", heading_style))
    for w in gap_analysis.get('user_weaknesses', []):
        story.append(Paragraph(f"• <b>Weakness:</b> {w['weakness']}", bullet_style))
        story.append(Paragraph(f"  <b>Solution:</b> {w['solution']}", bullet_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 10))
    
    # 4. Suggested Metadata
    story.append(Paragraph("4. Suggested Title & Meta Description", heading_style))
    meta = competitor_analysis.get('suggested_meta', {})
    story.append(Paragraph(f"<b>Suggested Title:</b> {meta.get('suggested_title', '')}", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Suggested Meta Description:</b> {meta.get('suggested_meta_description', '')}", body_style))
    story.append(Spacer(1, 14))
    
    # 5. Outrank Actions
    story.append(Paragraph("5. Outrank Action Blueprint", heading_style))
    for act in recommendations.get('high_priority', []):
        clean_act = act.replace('**', '').replace('⚡', '').replace('🚨', '').replace('🔑', '').replace('📌', '')
        story.append(Paragraph(f"• {clean_act}", bullet_style))
        story.append(Spacer(1, 4))
        
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_json_report(competitor_data: dict, competitor_analysis: dict, user_data: dict, gap_analysis: dict, recommendations: dict) -> str:
    """
    Exports full analysis structured as JSON.
    """
    report = {
        'tool': 'Rank Naser Competitor Spy',
        'competitor': competitor_analysis,
        'gap_analysis': gap_analysis,
        'recommendations': recommendations
    }
    return json.dumps(report, indent=2, ensure_ascii=False)
