#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能：分析为什么某些职位未被识别为软件开发职位
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def main():
    """分析不匹配职位"""
    url = "https://www.zhaopin.com/jobdetail/CCL1514719060J40910554815.htm"
    
    print("分析不匹配职位")
    print(f"URL: {url}")
    print("-" * 30)
    
    try:
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(options=options)
        
        driver.get(url)
        time.sleep(3)
        
        title = driver.title.split('_')[0].strip() if driver.title else "未知"
        print(f"职位名称: {title}")
        
        # 检查是否包含开发关键词
        has_dev = any(word in title for word in ['开发', '软件', '程序', '工程师'])
        
        if has_dev:
            print("✅ 包含开发关键词，但未匹配")
            print("原因: 可能是内容提取不完整")
        else:
            print("❌ 不包含开发关键词")
            print("这不是软件开发职位")
        
        driver.quit()
        
    except Exception as e:
        print(f"分析失败: {e}")

if __name__ == "__main__":
    main()