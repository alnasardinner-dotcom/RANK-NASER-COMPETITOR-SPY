import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
    'Cache-Control': 'no-cache',
}

def fetch_and_parse_url(url: str) -> dict:
    """
    Fetches HTML from a given URL.
    Uses Direct Scraping with automatic fallback to Jina Reader API (https://r.jina.ai/) for JS-heavy or protected pages.
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    html_content = ""
    is_jina_fallback = False
    
    # 1. Try Direct HTTP Request
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=12, verify=True)
        response.raise_for_status()
        html_content = response.text
    except Exception:
        try:
            # Retry with SSL verification disabled
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=12, verify=False)
            response.raise_for_status()
            html_content = response.text
        except Exception:
            pass

    direct_parsed = parse_html_content(html_content, url=url)
    
    # 2. Check if Direct Scraping returned anti-bot, empty, or low word count (< 50 words)
    if not direct_parsed.get('success') or direct_parsed.get('word_count', 0) < 50 or "Just a moment..." in html_content or "CAPTCHA" in html_content:
        # Fallback to Jina AI Reader API for live Markdown web fetching
        try:
            jina_url = f"https://r.jina.ai/{url}"
            jina_headers = {'User-Agent': 'Mozilla/5.0'}
            jina_res = requests.get(jina_url, headers=jina_headers, timeout=15)
            if jina_res.status_code == 200 and len(jina_res.text) > 200:
                jina_parsed = parse_jina_markdown(jina_res.text, url=url)
                if jina_parsed.get('word_count', 0) > direct_parsed.get('word_count', 0):
                    return jina_parsed
        except Exception:
            pass

    return direct_parsed

def parse_html_content(html_content: str, url: str = "") -> dict:
    """
    Parses raw HTML string and extracts accurate article components, word counts, headings, and images.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Parse URL slug for fallback keyword context
    url_slug_keywords = ""
    if url:
        parsed_url = urllib.parse.urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p and not p.endswith(('.html', '.php', '.aspx'))]
        # Ignore generic path parts like gadget, category, shop, product
        meaningful_parts = [p for p in path_parts if p.lower() not in ['gadget', 'category', 'shop', 'product', 'item', 'index']]
        if meaningful_parts:
            url_slug_keywords = meaningful_parts[-1].replace('-', ' ').replace('_', ' ').title()
        elif path_parts:
            url_slug_keywords = path_parts[-1].replace('-', ' ').replace('_', ' ').title()

    # Reject Cloudflare / Anti-bot Titles
    if any(b in page_title.lower() for b in ['just a moment', 'cloudflare', 'captcha', 'attention required', 'checking your browser', 'access denied']):
        page_title = url_slug_keywords or "Product Article"

    # Remove boilerplate & script elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe', 'noscript', 'svg']):
        element.decompose()
        
    # Remove widgets/sidebar containers
    for div in soup.find_all(['div', 'section'], class_=re.compile(r'(sidebar|comment|footer|header|widget|nav|menu|related|popup|modal)', re.I)):
        div.decompose()

    # Main Article Text Container Detection
    main_container = soup.find('article') or \
                     soup.find('main') or \
                     soup.find('div', class_=re.compile(r'(content|post-body|entry-content|article-body|product-description|description)', re.I)) or \
                     soup.body

    headings = []
    target_soup = main_container if main_container else soup
    for h in target_soup.find_all(['h1', 'h2', 'h3', 'h4']):
        text = h.get_text(strip=True)
        if text and len(text) > 1:
            headings.append({
                'tag': h.name.upper(),
                'text': text
            })

    images = []
    for img in target_soup.find_all('img'):
        src = img.get('src', '') or img.get('data-src', '')
        alt = img.get('alt', '').strip()
        if src:
            images.append({'src': src, 'alt': alt})

    text_elements = []
    for elem in target_soup.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'td', 'th', 'blockquote', 'span']):
        t = elem.get_text(strip=True)
        if t and len(t) > 2:
            text_elements.append(t)

    full_text = " ".join(text_elements) if text_elements else target_soup.get_text(separator=' ', strip=True)
    full_text = re.sub(r'\s+', ' ', full_text).strip()

    words = re.findall(r'[\w\u0980-\u09FF]+', full_text)
    word_count = len(words)
    reading_time_min = max(1, round(word_count / 200))

    domain = urllib.parse.urlparse(url).netloc if url else ""
    internal_links = 0
    external_links = 0
    for a in target_soup.find_all('a', href=True):
        href = a['href']
        if domain and domain in href:
            internal_links += 1
        elif href.startswith('http'):
            external_links += 1

    return {
        'success': True,
        'url': url,
        'title': page_title or url_slug_keywords,
        'meta_description': meta_description,
        'url_slug_keywords': url_slug_keywords,
        'full_text': full_text,
        'headings': headings,
        'h1_headings': [h['text'] for h in headings if h['tag'] == 'H1'],
        'h2_headings': [h['text'] for h in headings if h['tag'] == 'H2'],
        'h3_headings': [h['text'] for h in headings if h['tag'] == 'H3'],
        'word_count': word_count,
        'reading_time_min': reading_time_min,
        'image_count': len(images),
        'images': images,
        'internal_link_count': internal_links,
        'external_link_count': external_links,
        'source_engine': 'Direct Scraping'
    }

def parse_jina_markdown(markdown_text: str, url: str = "") -> dict:
    """
    Parses clean markdown output returned by Jina AI Reader API.
    """
    lines = markdown_text.split('\n')
    title = ""
    meta_desc = ""
    headings = []
    text_lines = []
    image_count = markdown_text.count('![')
    
    for line in lines:
        line_str = line.strip()
        if not title and line_str.startswith('Title:'):
            title = line_str.replace('Title:', '').strip()
        elif line_str.startswith('#'):
            level = min(line_str.count('#', 0, 4), 4)
            h_text = line_str.lstrip('#').strip()
            headings.append({'tag': f"H{level}", 'text': h_text})
        elif len(line_str) > 5 and not line_str.startswith(('URL Source:', 'Warning:', 'Markdown Content:')):
            text_lines.append(line_str)
            
    full_text = " ".join(text_lines)
    full_text = re.sub(r'\[.*?\]\(.*?\)', '', full_text) # Strip markdown links
    full_text = re.sub(r'\s+', ' ', full_text).strip()
    
    # Extract URL slug keywords for title fallback
    url_slug_keywords = ""
    if url:
        parsed_url = urllib.parse.urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p and not p.endswith(('.html', '.php', '.aspx'))]
        meaningful_parts = [p for p in path_parts if p.lower() not in ['gadget', 'category', 'shop', 'product', 'item', 'index']]
        if meaningful_parts:
            url_slug_keywords = meaningful_parts[-1].replace('-', ' ').replace('_', ' ').title()
        elif path_parts:
            url_slug_keywords = path_parts[-1].replace('-', ' ').replace('_', ' ').title()

    if any(b in title.lower() for b in ['just a moment', 'cloudflare', 'captcha', 'attention required', 'checking your browser', 'access denied']):
        title = url_slug_keywords or "Scraped Article"

    return {
        'success': True,
        'url': url,
        'title': title or (url_slug_keywords or "Scraped Article"),
        'meta_description': text_lines[0] if text_lines else "",
        'url_slug_keywords': url_slug_keywords,
        'full_text': full_text,
        'headings': headings,
        'h1_headings': [h['text'] for h in headings if h['tag'] == 'H1'],
        'h2_headings': [h['text'] for h in headings if h['tag'] == 'H2'],
        'h3_headings': [h['text'] for h in headings if h['tag'] == 'H3'],
        'word_count': word_count,
        'reading_time_min': max(1, round(word_count / 200)),
        'image_count': image_count,
        'images': [],
        'internal_link_count': 0,
        'external_link_count': 0,
        'source_engine': 'Jina AI Live Reader API'
    }

def process_raw_text(raw_text: str, title: str = "Pasted Article") -> dict:
    """
    Processes raw text directly.
    """
    cleaned_text = re.sub(r'\s+', ' ', raw_text).strip()
    words = re.findall(r'[\w\u0980-\u09FF]+', cleaned_text)
    word_count = len(words)
    
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    headings = []
    for line in lines:
        if line.startswith('#'):
            level = line.count('#', 0, 4)
            tag = f"H{min(level, 4)}"
            text = line.lstrip('#').strip()
            headings.append({'tag': tag, 'text': text})
        elif len(line) < 80 and not line.endswith(('.', '?', '!', ';')):
            headings.append({'tag': 'H2', 'text': line})
            
    return {
        'success': True,
        'url': 'Direct Text Input',
        'title': title or (lines[0] if lines else "Direct Text Article"),
        'meta_description': lines[1] if len(lines) > 1 else "",
        'url_slug_keywords': "",
        'full_text': cleaned_text,
        'headings': headings,
        'h1_headings': [h['text'] for h in headings if h['tag'] == 'H1'],
        'h2_headings': [h['text'] for h in headings if h['tag'] == 'H2'],
        'h3_headings': [h['text'] for h in headings if h['tag'] == 'H3'],
        'word_count': word_count,
        'reading_time_min': max(1, round(word_count / 200)),
        'image_count': 0,
        'images': [],
        'internal_link_count': 0,
        'external_link_count': 0,
        'source_engine': 'Direct Text'
    }
