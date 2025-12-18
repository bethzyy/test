import time
import random
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

def setup_driver():
    """设置Selenium WebDriver"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        chrome_options.add_argument(f'--user-agent={user_agent}')
        
        # 禁用图片加载
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        print(f"❌ WebDriver设置失败: {e}")
        return None

def analyze_mismatched_job():
    """专门分析不匹配的职位"""
    url = "https://www.zhaopin.com/jobdetail/CCL1514719060J40910554815.htm?refcode=4019&srccode=401901&preactionid=4d684428-f439-475d-a897-9d5a10986e8c"
    
    print("🔍 专门分析不匹配的职位")
    print("=" * 60)
    print(f"📋 URL: {url}")
    print("=" * 60)
    
    driver = setup_driver()
    if not driver:
        return
    
    try:
        print("🔄 正在访问页面...")
        driver.get(url)
        
        # 等待页面加载
        time.sleep(8)  # 更长的等待时间
        
        print("📄 页面基本信息:")
        print(f"• 页面标题: {driver.title}")
        print(f"• 页面URL: {driver.current_url}")
        print(f"• 页面长度: {len(driver.page_source)}字符")
        print()
        
        # 尝试提取职位名称
        print("🔍 尝试提取职位名称...")
        
        # 方法1: 从页面标题
        page_title = driver.title
        print(f"📄 页面标题: {page_title}")
        
        job_title = "未知职位"
        if page_title and len(page_title) > 10:
            # 清理标题
            if '_' in page_title:
                job_title = page_title.split('_')[0].strip()
            elif '-' in page_title:
                job_title = page_title.split('-')[0].strip()
            else:
                job_title = page_title.replace('招聘', '').replace('智联招聘', '').strip()
        
        print(f"🎯 从标题提取: {job_title}")
        
        # 方法2: 查找H1标签
        try:
            h1_elements = driver.find_elements(By.TAG_NAME, "h1")
            for i, h1 in enumerate(h1_elements):
                print(f"  H1[{i}]: {h1.text.strip()}")
        except:
            print("  未找到H1标签")
        
        # 方法3: 查找常见的职位标题class
        title_selectors = [
            ".job-title", ".position-title", ".title", ".job-name",
            "[class*='job-title']", "[class*='position-title']",
            "[class*='job-name']", "h1", "h2", "h3"
        ]
        
        print("🔍 查找职位标题元素...")
        found_title = False
        for selector in title_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for i, elem in enumerate(elements[:3]):  # 只显示前3个
                        text = elem.text.strip()
                        if len(text) > 3 and len(text) < 100:
                            print(f"  {selector}[{i}]: {text}")
                            if not found_title and any(word in text for word in ['工程师', '开发', '程序员', '专员', '经理', '主管']):
                                job_title = text
                                found_title = True
            except:
                continue
        
        print()
        print(f"📝 最终提取的职位名称: {job_title}")
        
        # 尝试提取页面内容
        print()
        print("📄 尝试提取页面内容...")
        
        # 获取所有文本
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            all_text = body.text
            
            # 查找包含关键词的句子
            keywords = ['负责', '要求', '职责', '岗位', '工作', '技能', '开发', '技术', '系统', '软件']
            relevant_lines = []
            
            for line in all_text.split('\n'):
                line = line.strip()
                if (len(line) > 20 and len(line) < 200 and 
                    any(word in line for word in keywords) and
                    not any(word in line for word in ['登录', '注册', '首页', '广告', '推荐'])):
                    relevant_lines.append(line)
            
            if relevant_lines:
                print("📋 相关文本片段:")
                for i, line in enumerate(relevant_lines[:5]):
                    print(f"  {i+1}. {line}")
            else:
                print("⚠️ 未找到相关职位描述文本")
                
        except Exception as e:
            print(f"⚠️ 内容提取失败: {e}")
        
        # 分析为什么不匹配
        print()
        print("🔍 不匹配原因分析:")
        print("-" * 40)
        
        if job_title == "未知职位" or len(job_title) < 5:
            print("❌ 职位名称提取失败")
            print("  原因: 页面可能使用了特殊的动态加载或反爬虫技术")
            print("  表现: 无法从标题或常见元素中提取有效职位名称")
        else:
            print(f"✅ 职位名称提取成功: {job_title}")
            
            # 检查是否包含开发相关关键词
            dev_keywords = ['开发', '软件', '程序', '工程师', '技术', '系统', 'AI', '算法', '数据']
            has_dev_keyword = any(word in job_title for word in dev_keywords)
            
            if has_dev_keyword:
                print("✅ 职位名称包含开发相关关键词")
                print("  理论上应该匹配，可能是内容提取问题")
            else:
                print("❌ 职位名称不包含开发相关关键词")
                print(f"  职位'{job_title}'可能不是软件开发类职位")
        
        print()
        print("💡 总结:")
        print("=" * 60)
        print("这个URL的问题主要是：")
        print("1. 反爬虫机制导致页面内容不完整")
        print("2. 职位信息可能通过JavaScript动态加载失败")
        print("3. 网站对这个特定URL有更严格的访问限制")
        print()
        print("解决方案：")
        print("• 增加更长的等待时间")
        print("• 使用代理IP")
        print("• 模拟更真实的用户行为")
        print("• 手动验证该职位是否真的是软件开发类")
        
    finally:
        driver.quit()
        print("\n✅ 浏览器已关闭")

if __name__ == "__main__":
    analyze_mismatched_job()