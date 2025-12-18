import time
import random
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import json

# 定义软件开发相关关键词
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

def setup_driver():
    """设置Selenium WebDriver"""
    try:
        chrome_options = Options()
        
        # 添加更多伪装选项
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 浏览器参数
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # User-Agent
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        chrome_options.add_argument(f'--user-agent={user_agent}')
        
        # 禁用图片加载以加快速度
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 创建driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # 执行脚本隐藏webdriver属性
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
        
    except Exception as e:
        print(f"❌ WebDriver设置失败: {e}")
        return None

def fetch_page_with_selenium(driver, url, max_retries=3):
    """使用Selenium获取页面内容"""
    for attempt in range(max_retries):
        try:
            print(f"🔄 Selenium尝试 {attempt + 1}/{max_retries}: {url}")
            
            # 随机延迟
            if attempt > 0:
                delay = random.uniform(3, 8)
                print(f"⏱️  等待 {delay:.1f} 秒...")
                time.sleep(delay)
            
            # 导航到页面
            driver.get(url)
            
            # 等待页面加载
            wait = WebDriverWait(driver, 15)
            
            # 尝试等待不同的元素加载
            wait_conditions = [
                EC.presence_of_element_located((By.TAG_NAME, "body")),
                EC.presence_of_element_located((By.TAG_NAME, "title")),
                EC.presence_of_element_located((By.CLASS_NAME, "job-detail")),
                EC.presence_of_element_located((By.CLASS_NAME, "position-detail")),
            ]
            
            loaded = False
            for condition in wait_conditions:
                try:
                    wait.until(condition)
                    loaded = True
                    break
                except TimeoutException:
                    continue
            
            if not loaded:
                print("⚠️  页面加载超时，继续处理...")
            
            # 额外等待JavaScript渲染
            time.sleep(random.uniform(2, 5))
            
            # 获取页面源码
            page_source = driver.page_source
            
            if len(page_source) < 1000:
                print(f"⚠️  页面内容太少 ({len(page_source)}字符)")
                if attempt < max_retries - 1:
                    continue
                return None
            
            print(f"✅ 成功获取页面 ({len(page_source)}字符)")
            return page_source
            
        except TimeoutException:
            print(f"⏱️  页面加载超时 (尝试 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            return None
        except WebDriverException as e:
            print(f"❌ WebDriver错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return None
        except Exception as e:
            print(f"⚠️ 意外错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            return None
    
    return None

def extract_job_info_selenium(driver):
    """使用Selenium提取职位信息"""
    job_title = "未知职位"
    job_content = ""
    
    try:
        print("🔍 开始提取职位信息...")
        
        # 1. 从页面标题提取
        try:
            title_element = driver.find_element(By.TAG_NAME, "title")
            title_text = title_element.get_attribute("text")
            if title_text:
                print(f"📄 页面标题: {title_text}")
                if '_' in title_text:
                    job_title = title_text.split('_')[0].strip()
                elif '-' in title_text:
                    job_title = title_text.split('-')[0].strip()
                else:
                    job_title = title_text
        except:
            pass
        
        # 2. 从h1标签提取
        if job_title == "未知职位" or len(job_title) < 3:
            try:
                h1_elements = driver.find_elements(By.TAG_NAME, "h1")
                for h1 in h1_elements:
                    text = h1.text.strip()
                    if len(text) > 3 and any(word in text for word in ['工程师', '开发', '程序员', '架构师', '技术', 'AI', '算法']):
                        job_title = text
                        print(f"🎯 从H1提取: {job_title}")
                        break
            except:
                pass
        
        # 3. 从特定class提取
        if job_title == "未知职位" or len(job_title) < 3:
            title_selectors = [
                ".job-title", ".position-title", ".title", ".job-name",
                "[class*='job-title']", "[class*='position-title']",
                "h1[class*='title']", "h2[class*='title']"
            ]
            
            for selector in title_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if len(text) > 3 and any(word in text for word in ['工程师', '开发', '程序员', '架构师', '技术', 'AI', '算法']):
                            job_title = text
                            print(f"🎯 从CSS选择器提取: {job_title}")
                            break
                    if job_title != "未知职位" and len(job_title) > 3:
                        break
                except:
                    continue
        
        print(f"📋 提取到的职位名称: {job_title}")
        
        # 提取职位描述
        job_content = extract_job_content_selenium(driver)
        
        print(f"📄 提取到的职位描述长度: {len(job_content)}字符")
        if len(job_content) > 0:
            print(f"📝 内容预览: {job_content[:200]}...")
        
        return job_title, job_content
        
    except Exception as e:
        print(f"⚠️ 提取失败: {e}")
        return job_title, job_content

def extract_job_content_selenium(driver):
    """使用Selenium提取职位内容"""
    job_content = ""
    
    try:
        # 1. 常见的内容选择器
        content_selectors = [
            ".job-description",
            ".position-desc",
            ".job-detail",
            ".position-detail",
            ".job-content",
            ".job-intro",
            "[class*='job-description']",
            "[class*='position-desc']",
            "[class*='job-detail']",
            "div[class*='content']",
            "section[class*='job']"
        ]
        
        for selector in content_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if len(text) > 100:  # 最小长度要求
                        job_content = text
                        print(f"✅ 找到内容区域 ({len(text)}字符): {selector}")
                        break
                if job_content:
                    break
            except:
                continue
        
        # 2. 通过关键词查找
        if not job_content:
            print("🔍 尝试通过关键词查找内容...")
            keywords = ['岗位职责', '任职要求', '工作要求', '工作内容', '职责描述', 
                       '任职资格', '职位描述', '岗位描述', '职位要求']
            
            for keyword in keywords:
                try:
                    # 查找包含关键词的元素
                    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                    for elem in elements:
                        try:
                            # 获取父元素
                            parent = elem.find_element(By.XPATH, "..")
                            parent_text = parent.text.strip()
                            if len(parent_text) > 150:
                                job_content = parent_text
                                print(f"✅ 通过关键词 '{keyword}' 找到内容 ({len(parent_text)}字符)")
                                break
                        except:
                            continue
                        
                        if job_content:
                            break
                    if job_content:
                        break
                except:
                    continue
        
        # 3. 提取所有文本
        if not job_content:
            print("📝 尝试提取所有文本...")
            try:
                # 获取body文本
                body = driver.find_element(By.TAG_NAME, "body")
                all_text = body.text
                
                # 过滤有意义的行
                lines = []
                for line in all_text.split('\n'):
                    line = line.strip()
                    if (len(line) > 20 and 
                        any(word in line for word in ['负责', '要求', '职责', '岗位', '工作', '技能', '开发', '技术']) and
                        not any(word in line for word in ['登录', '注册', '首页', '推荐', '广告'])):
                        lines.append(line)
                
                if lines:
                    job_content = '\n'.join(lines[:20])  # 限制行数
                    print(f"✅ 通过文本提取获得内容 ({len(job_content)}字符)")
            except:
                pass
        
        return job_content
        
    except Exception as e:
        print(f"⚠️ 内容提取失败: {e}")
        return job_content

def filter_software_jobs(job_title, job_content, url):
    """筛选软件开发相关职位 - 保持原有逻辑"""
    if not job_title and not job_content:
        return None
    
    print(f"🔍 正在筛选职位: {job_title}")
    
    # 合并职位名称和内容进行匹配
    title_text = job_title.lower()
    content_text = job_content.lower()
    
    # 检查关键词匹配
    matched_keywords = []
    
    # 首先检查职位名称中的关键词
    title_matched = []
    for keyword in KEYWORDS:
        if keyword.lower() in title_text:
            title_matched.append(keyword)
    
    print(f"📋 职位名称匹配到的关键词: {title_matched}")
    
    # 如果职位名称中有明确的技术关键词，直接认为匹配
    if title_matched:
        print(f"✅ 职位名称匹配成功！")
        return {
            'url': url,
            'title': job_title,
            'matched_reason': f"职位名称匹配关键词: {', '.join(title_matched)}"
        }
    
    # 如果职位名称没有明确匹配，检查内容中的关键词
    content_matched = []
    for keyword in KEYWORDS:
        if keyword.lower() in content_text:
            content_matched.append(keyword)
    
    print(f"📄 内容匹配到的关键词: {content_matched}")
    
    # 内容中需要至少匹配1个关键词就认为是相关的
    if len(content_matched) >= 1:
        print(f"✅ 内容匹配成功！匹配到{len(content_matched)}个关键词")
        return {
            'url': url,
            'title': job_title,
            'matched_reason': f"内容匹配关键词: {', '.join(content_matched[:3])}"
        }
    
    print(f"❎ 不匹配：职位名称未匹配，内容中匹配到{len(content_matched)}个关键词（需要≥1个）")
    return None

def main():
    """主函数"""
    file_path = 'C:\\D\\work\\qianshi\\test\\joburl.txt'
    
    print("🌟 Selenium智联招聘软件开发职位筛选器")
    print("=" * 60)
    print("ℹ️  使用Selenium处理JavaScript渲染的页面")
    print("=" * 60)
    
    # 读取URL列表
    urls = read_job_urls(file_path)
    if not urls:
        print("📁 未找到职位URL")
        return
    
    print(f"📋 共读取到 {len(urls)} 个职位URL")
    print("=" * 60)
    
    # 设置WebDriver
    driver = setup_driver()
    if not driver:
        print("❌ WebDriver设置失败")
        return
    
    try:
        # 处理每个URL
        matched_jobs = []
        for idx, url in enumerate(urls, 1):
            print(f"\n🔗 正在处理 ({idx}/{len(urls)}): {url}")
            
            page_source = fetch_page_with_selenium(driver, url)
            if page_source:
                job_title, job_content = extract_job_info_selenium(driver)
                
                if job_title and job_content:
                    filtered_job = filter_software_jobs(job_title, job_content, url)
                    if filtered_job:
                        matched_jobs.append(filtered_job)
                        print(f"✅ 找到匹配职位: {job_title}")
                    else:
                        print(f"❎ 不匹配: {job_title}")
                else:
                    print(f"⚠️  提取信息不完整")
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
            print(f"\n📊 总计: 找到 {len(matched_jobs)} 个匹配的软件开发职位")
        else:
            print("⚠️  未找到招聘软件开发人员的职位")
    
    finally:
        # 确保关闭浏览器
        try:
            driver.quit()
            print("\n✅ 浏览器已关闭")
        except:
            pass

if __name__ == "__main__":
    main()