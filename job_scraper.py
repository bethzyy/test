#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础职位爬虫 - 使用requests+BeautifulSoup, 适合静态页面
功能：爬取招聘网站，筛选软件开发职位
"""

import requests
from bs4 import BeautifulSoup
from config import SOFTWARE_JOB_KEYWORDS as KEYWORDS

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
    
    matched = []
    for url in urls:
        print(f"处理: {url}")
        
        # 获取页面
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            html = response.text
        except:
            print("访问失败")
            print("-" * 40)
            continue
        
        # 解析
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.text.split('_')[0].strip() if soup.title else "未知职位"
            content = soup.get_text(separator=' ', strip=True)[:1000]
        except:
            print("解析失败")
            print("-" * 40)
            continue
        
        # 匹配
        title_matches = match_keywords(title)
        if title_matches:
            matched.append({
                'url': url,
                'title': title,
                'reason': f"职位名称: {', '.join(title_matches)}"
            })
            print(f"✅ 匹配: {title}")
        else:
            content_matches = match_keywords(content)
            if content_matches:
                matched.append({
                    'url': url,
                    'title': title,
                    'reason': f"内容匹配: {', '.join(content_matches[:2])}"
                })
                print(f"✅ 匹配: {title}")
            else:
                print(f"❌ 不匹配: {title}")
        
        print("-" * 40)
    
    # 输出结果
    print("\n筛选结果:")
    if matched:
        for i, job in enumerate(matched, 1):
            print(f"{i}. {job['title']}")
            print(f"   URL: {job['url']}")
            print(f"   匹配理由: {job['reason']}")
            print()
    else:
        print("未找到招聘软件开发人员的职位")

if __name__ == "__main__":
    main()