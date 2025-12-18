import requests
from bs4 import BeautifulSoup
import re

# 定义软件开发相关关键词 - 扩展更多相关关键词
KEYWORDS = [
    # 基础开发词汇
    '软件开发', '软件工程师', '程序员', '开发者', '开发工程师',
    
    # 前后端开发
    '前端开发', '后端开发', '全栈开发', 'Web开发', '网页开发',
    'Java开发', 'Python开发', 'C++开发', 'C#开发', 'PHP开发',
    'JavaScript开发', 'React开发', 'Vue开发', 'Node.js开发',
    
    # 移动开发
    'Android开发', 'iOS开发', '移动开发', 'APP开发', '小程序开发',
    
    # 数据库和运维
    '数据库开发', '运维开发', 'DevOps', '系统运维', '数据库管理员',
    
    # 人工智能和大数据
    'AI开发', '人工智能', '机器学习', '深度学习', '数据科学',
    '大数据开发', '数据分析', '算法工程师', '智能体开发',
    
    # 云计算和微服务
    '云计算', '微服务', '容器开发', 'Kubernetes', 'Docker开发',
    
    # 具体技术栈
    'Spring开发', 'Django开发', 'Flask开发', 'Laravel开发',
    '编程', '代码开发', '程序开发', '应用开发', '系统开发',
    
    # 架构和高级职位
    '架构师', '技术总监', 'CTO', '技术负责人', '首席技术官',
    
    # 测试和质量保证
    '测试开发', '自动化测试', 'QA工程师', '质量保障'
]

def read_job_urls(file_path):
    """读取职位URL文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [url.strip() for url in f if url.strip()]
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return []

def fetch_job_page(url):
    """获取职位页面内容，处理异常"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查HTTP错误
        return response.text
    except requests.exceptions.Timeout:
        print(f"⏱️  访问超时: {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP错误 {e.response.status_code}: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 访问失败: {url} - {e}")
        return None

def parse_job_info(html, url):
    """解析智联招聘页面的职位信息"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 添加调试信息
        print(f"📝 正在解析页面: {url}")
        
        # 提取职位名称（智联招聘的职位名称在不同页面结构可能不同）
        job_title = "未知职位"
        
        # 尝试不同的职位名称选择器 - 扩展更多选择器
        title_selectors = [
            'h1[class*="name"]',  # 常见的职位名称选择器
            'h1[class*="title"]',
            'div[class*="job-name"] h1',
            'div[class*="job-title"] h1',
            'h1[class="zp-job-name__company"]',  # 特定页面的选择器
            'div[class*="job-position"] h1',
            'h1[class*="position"]',
            'div[class*="position-name"]',
            'div[class*="jobName"]',
            'h1[class*="job"]',
            'title'  # 最后尝试从页面标题提取
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                if selector == 'title':
                    # 从页面标题提取，通常格式为 "职位名称_公司名称-智联招聘"
                    full_title = title_element.get_text(strip=True)
                    # 移除后缀
                    job_title = re.split(r'[_-]', full_title)[0].strip()
                else:
                    job_title = title_element.get_text(strip=True)
                break
        
        # 如果还是未知职位，尝试从URL或页面内容中提取更多信息
        if job_title == "未知职位":
            print(f"⚠️  未找到标准职位名称，尝试智能提取...")
            
            # 尝试从URL中提取职位信息
            url_parts = url.split('/')
            for part in reversed(url_parts):
                # 查找包含职位ID的部分，通常格式为 CCL... 或 CC...
                if re.match(r'^[A-Z]{2,3}\d+J\d+', part):
                    # 这部分通常是职位ID，不包含职位名称，跳过
                    continue
                elif len(part) > 5 and not part.startswith('http') and '.' not in part:
                    # 尝试从URL路径中提取职位信息，清理特殊字符
                    job_info = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', ' ', part)
                    job_info = re.sub(r'\s+', ' ', job_info).strip()
                    if len(job_info) > 5 and 'htm' not in job_info.lower():
                        job_title = job_info
                        print(f"📋 从URL路径提取职位: {job_title}")
                        break
            
            # 尝试从meta标签中获取
            if job_title == "未知职位":
                meta_title = soup.find('meta', {'property': 'og:title'}) or soup.find('meta', {'name': 'title'})
                if meta_title and meta_title.get('content'):
                    content = meta_title['content']
                    # 尝试从meta内容中提取职位名称
                    if '招聘' in content:
                        job_title = content.split('招聘')[0].strip()
                    elif '_' in content:
                        job_title = content.split('_')[0].strip()
                    elif '-' in content:
                        job_title = content.split('-')[0].strip()
                    else:
                        job_title = content.strip()
                    print(f"📋 从meta标签提取职位: {job_title}")
            
            # 如果还是未知，尝试从整个页面文本中智能提取
            if job_title == "未知职位":
                # 查找包含"招聘"或"职位"的文本
                text_content = soup.get_text()
                # 使用正则表达式查找可能的职位名称
                job_patterns = [
                    r'「([^」]*?)招聘」',
                    r'「([^」]*?)」',
                    r'([^，。！？\n]*?工程师[^，。！？\n]*)',
                    r'([^，。！？\n]*?开发[^，。！？\n]*)',
                    r'([^，。！？\n]*?程序员[^，。！？\n]*)',
                    r'([^，。！？\n]*?架构师[^，。！？\n]*)',
                    r'([^，。！？\n]*?技术[^，。！？\n]*)',
                    r'([^，。！？\n]*?软件[^，。！？\n]*)'
                ]
                
                for pattern in job_patterns:
                    match = re.search(pattern, text_content)
                    if match:
                        job_title = match.group(1) if match.groups() else match.group(0)
                        # 清理提取的职位名称
                        job_title = re.sub(r'[\s\n\r]+', ' ', job_title).strip()
                        if len(job_title) > 2 and len(job_title) < 50:  # 合理的职位名称长度
                            print(f"📋 从页面文本智能提取职位: {job_title}")
                            break
                        else:
                            job_title = "未知职位"
        
        print(f"📋 提取到的职位名称: {job_title}")
        
        # 提取职位描述和要求
        job_content = ""
        
        # 智联招聘的职位描述通常在以下位置 - 扩展更多选择器
        description_selectors = [
            'div[class*="describtion__detail-content"]',  # 新页面结构
            'div[class="describtion__detail-content"]',
            'div[class*="job-description"]',
            'div[class*="job-detail-content"]',
            'div[class*="pos-ul"]',
            'section[class*="job-intro"]',
            'div[class="pos-ul"]',
            'div[class="responsibility-req"]',  # 旧页面结构
            'div[class*="job-detail"]',
            'div[class*="position-desc"]',
            'div[class*="job-desc"]',
            'div[class*="detail-content"]',
            'div[class*="job-requirement"]',
            'div[class*="position-require"]',
            'div[class*="job-content"]',
            'div[class*="position-detail"]'
        ]
        
        for selector in description_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    # 获取文本但排除脚本和样式内容
                    for script in element(["script", "style"]):
                        script.decompose()
                    job_content += element.get_text(separator='\n', strip=True) + '\n'
                break
        
        # 如果没有找到，尝试更智能的内容提取
        if not job_content:
            print(f"⚠️  未找到标准职位描述，尝试智能提取...")
            # 尝试查找包含职位描述关键词的div
            desc_keywords = ['职位描述', '岗位职责', '任职要求', '工作要求', '工作内容', '职责描述']
            for keyword in desc_keywords:
                # 查找包含这些关键词的元素 - 使用string代替已弃用的text参数
                elements = soup.find_all(string=re.compile(keyword))
                for element in elements:
                    parent = element.find_parent(['div', 'section', 'p'])
                    if parent:
                        job_content += parent.get_text(separator='\n', strip=True) + '\n'
                        break
                if job_content:
                    print(f"📄 从关键词'{keyword}'提取到职位描述")
                    break
        
        # 如果还是没有找到，获取页面的主要内容区域
        if not job_content:
            print(f"⚠️  仍未找到职位描述，尝试提取主要内容区域...")
            # 尝试多种主要内容区域选择器
            main_selectors = [
                'main',
                'div[class*="main"]',
                'div[class*="content"]',
                'div[class*="body"]',
                'div[class*="wrapper"]',
                'div[class*="container"]',
                'div[id*="main"]',
                'div[id*="content"]',
                'section[class*="content"]',
                'article[class*="content"]'
            ]
            
            main_content = None
            for selector in main_selectors:
                if selector == 'main':
                    main_content = soup.find('main')
                else:
                    main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                # 移除脚本和样式
                for script in main_content(["script", "style"]):
                    script.decompose()
                job_content = main_content.get_text(separator='\n', strip=True)
                print(f"📄 从主要内容区域提取到{len(job_content)}字符的文本")
            else:
                # 最后手段：尝试更智能的内容提取
                print(f"⚠️  尝试智能内容提取...")
                
                # 尝试多种方法提取内容
                job_content = ""
                
                # 方法1: 查找所有可见文本内容
                try:
                    # 获取body内容或整个文档
                    body = soup.find('body') or soup
                    
                    # 移除脚本、样式、导航等无关内容
                    for element in body(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        element.decompose()
                    
                    # 提取文本
                    raw_text = body.get_text(separator='\n', strip=True)
                    
                    # 方法2: 如果内容太少，尝试查找特定的内容容器
                    if len(raw_text) < 100:
                        print(f"⚠️  内容太少，尝试查找隐藏内容...")
                        # 查找可能包含内容的元素，包括隐藏的元素
                        content_elements = soup.find_all(['div', 'section', 'article', 'main'], 
                                                      attrs={'style': re.compile(r'display:\s*block|visibility:\s*visible')})
                        
                        if not content_elements:
                            # 尝试查找所有div元素
                            content_elements = soup.find_all('div', limit=20)
                        
                        extracted_texts = []
                        for elem in content_elements:
                            text = elem.get_text(strip=True)
                            if len(text) > 50:  # 只保留有意义的文本
                                extracted_texts.append(text)
                        
                        if extracted_texts:
                            raw_text = '\n'.join(extracted_texts[:5])  # 限制数量
                    
                    # 方法3: 查找JSON数据或脚本中的内容
                    if len(raw_text) < 50:
                        print(f"⚠️  尝试从脚本中提取数据...")
                        scripts = soup.find_all('script')
                        for script in scripts:
                            if script.string and len(script.string) > 100:
                                # 查找可能包含职位信息的JSON数据
                                if 'job' in script.string.lower() or 'position' in script.string.lower():
                                    # 尝试提取中文文本
                                    chinese_text = re.findall(r'[\u4e00-\u9fa5]+', script.string)
                                    if chinese_text:
                                        raw_text += ' '.join(chinese_text[:20])  # 限制数量
                                        break
                    
                    # 清理和格式化文本
                    if raw_text:
                        # 移除多余的空白字符
                        raw_text = re.sub(r'\n{3,}', '\n\n', raw_text)
                        raw_text = re.sub(r'[ \t]+', ' ', raw_text)
                        raw_text = re.sub(r'\s*\n\s*\n\s*', '\n\n', raw_text)
                        
                        # 限制长度但保留足够信息
                        job_content = raw_text[:4000] if len(raw_text) > 4000 else raw_text
                        print(f"📄 智能提取成功，得到{len(job_content)}字符的文本")
                    else:
                        print(f"⚠️  智能提取失败，内容为空")
                        
                except Exception as e:
                    print(f"⚠️  智能提取出错: {e}")
                    # 最终备用方案
                    job_content = soup.get_text(separator='\n', strip=True)[:2000]
                    print(f"📄 使用备用方案提取到{len(job_content)}字符的文本")
        
        print(f"📄 提取到的职位描述长度: {len(job_content)}字符")
        
        return {
            'url': url,
            'title': job_title,
            'content': job_content
        }
        
    except Exception as e:
        print(f"🧩 解析失败: {url} - {e}")
        return None

def filter_software_jobs(job_info):
    """筛选软件开发相关职位"""
    if not job_info:
        return None
    
    print(f"🔍 正在筛选职位: {job_info['title']}")
    
    # 合并职位名称和内容进行匹配
    title_text = job_info['title'].lower()
    content_text = job_info['content'].lower()
    all_text = title_text + ' ' + content_text
    
    # 检查关键词匹配
    matched_keywords = []
    
    # 首先检查职位名称中的关键词（职位名称匹配权重更高）
    title_matched = []
    for keyword in KEYWORDS:
        if keyword.lower() in title_text:
            title_matched.append(keyword)
    
    print(f"📋 职位名称匹配到的关键词: {title_matched}")
    
    # 如果职位名称中有明确的技术关键词，直接认为匹配
    if title_matched:
        print(f"✅ 职位名称匹配成功！")
        return {
            'url': job_info['url'],
            'title': job_info['title'],
            'matched_reason': f"职位名称匹配关键词: {', '.join(title_matched)}"
        }
    
    # 如果职位名称没有明确匹配，检查内容中的关键词
    content_matched = []
    for keyword in KEYWORDS:
        if keyword.lower() in content_text:
            content_matched.append(keyword)
    
    print(f"📄 内容匹配到的关键词: {content_matched}")
    
    # 内容中需要至少匹配1个关键词就认为是相关的（放宽条件）
    if len(content_matched) >= 1:
        print(f"✅ 内容匹配成功！匹配到{len(content_matched)}个关键词")
        return {
            'url': job_info['url'],
            'title': job_info['title'],
            'matched_reason': f"内容匹配关键词: {', '.join(content_matched[:3])}"  # 只显示前3个匹配的关键词
        }
    
    # 特殊规则：如果内容中包含某些强相关的技术词汇，即使只匹配一个也认为相关
    strong_tech_keywords = ['编程', '代码', '算法', '数据结构', '软件架构', '系统设计']
    for strong_keyword in strong_tech_keywords:
        if strong_keyword in content_text and content_matched:
            print(f"✅ 强技术词汇匹配成功！")
            return {
                'url': job_info['url'],
                'title': job_info['title'],
                'matched_reason': f"技术内容匹配: {content_matched[0]}"
            }
    
    print(f"❎ 不匹配：职位名称未匹配，内容中匹配到{len(content_matched)}个关键词（需要≥1个）")
    return None

def main():
    """主函数"""
    file_path = './joburl.txt'
    
    print("🔍 开始筛选软件开发职位...")
    print("=" * 60)
    
    # 读取URL列表
    urls = read_job_urls(file_path)
    if not urls:
        print("📁 未找到职位URL")
        return
    
    print(f"📋 共读取到 {len(urls)} 个职位URL")
    print("=" * 60)
    
    # 处理每个URL
    matched_jobs = []
    for idx, url in enumerate(urls, 1):
        print(f"🔗 正在处理 ({idx}/{len(urls)}): {url}")
        
        html = fetch_job_page(url)
        if html:
            job_info = parse_job_info(html, url)
            if job_info:
                filtered_job = filter_software_jobs(job_info)
                if filtered_job:
                    matched_jobs.append(filtered_job)
                    print(f"✅ 找到匹配职位: {job_info['title']}")
                else:
                    print(f"❎ 不匹配: {job_info['title']}")
            else:
                print(f"❌ 解析失败")
        else:
            print(f"❌ 访问失败")
        print("-" * 60)
    
    # 输出结果
    print("\n" + "=" * 60)
    if matched_jobs:
        print("🎉 筛选结果:")
        print("=" * 60)
        for i, job in enumerate(matched_jobs, 1):
            print(f"职位 {i}:")
            print(f"📌 网址: {job['url']}")
            print(f"📝 名称: {job['title']}")
            print(f"💡 匹配理由: {job['matched_reason']}")
            print("-" * 60)
    else:
        print("⚠️  未找到招聘软件开发人员的职位")

if __name__ == "__main__":
    main()