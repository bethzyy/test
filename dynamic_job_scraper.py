#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium职位爬虫 - 处理JavaScript渲染页面
功能：爬取招聘网站，筛选软件开发职位
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from config import SOFTWARE_JOB_KEYWORDS as KEYWORDS

def setup_driver():
    """设置WebDriver"""
    try:
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        return driver
    except:
        return None

def extract_info(driver):
    """提取职位信息"""
    title = driver.title.split('_')[0].strip() if driver.title else "未知职位"
    content = driver.find_element(By.TAG_NAME, "body").text if driver.find_elements(By.TAG_NAME, "body") else ""
    return title, content

def match_keywords(text):
    """匹配关键词"""
    return [kw for kw in KEYWORDS if kw.lower() in text.lower()]

def main():
    """主函数"""
    try:
        with open('./joburl.txt', 'r', encoding='utf-8') as f:
            urls = [url.strip() for url in f if url.strip()]
    except:
        print("读取URL文件失败")
        return
    
    driver = setup_driver()
    if not driver:
        print("WebDriver设置失败")
        return
    
    matched = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        
        try:
            driver.get(url)
            time.sleep(4)
            title, content = extract_info(driver)
            
            title_matches = match_keywords(title)
            if title_matches:
                matched.append({
                    'url': url,
                    'title': title,
                    'reason': f"职位名称: {', '.join(title_matches)}"
                })
                print(f"✅ {title}")
            else:
                content_matches = match_keywords(content)
                if content_matches:
                    matched.append({
                        'url': url,
                        'title': title,
                        'reason': f"内容匹配: {', '.join(content_matches[:2])}"
                    })
                    print(f"✅ {title}")
                else:
                    print(f"❌ {title}")
        except:
            print("访问失败")
        
        print("-" * 40)
    
    driver.quit()
    
    print("\n结果:")
    if matched:
        for i, job in enumerate(matched, 1):
            print(f"{i}. {job['title']}")
            print(f"   URL: {job['url']}")
            print(f"   理由: {job['reason']}")
            print()
    else:
        print("未找到软件开发职位")

if __name__ == "__main__":
    main()