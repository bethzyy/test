#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件开发职位筛选工具 - GUI版本
功能：从界面输入文件名，筛选软件开发相关职位
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
from bs4 import BeautifulSoup
from config import SOFTWARE_JOB_KEYWORDS as KEYWORDS

class JobFilterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("软件开发职位筛选")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件名输入区域
        file_frame = ttk.LabelFrame(main_frame, text="文件名输入", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="职位链接列表文件名:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_entry = ttk.Entry(file_frame, width=50)
        self.file_entry.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10))
        self.file_entry.insert(0, "joburl.txt")  # 默认值
        
        self.filter_btn = ttk.Button(file_frame, text="开始筛选", command=self.start_filter)
        self.filter_btn.grid(row=0, column=2)
        
        file_frame.columnconfigure(1, weight=1)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="筛选结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=90, height=25)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.config(state=tk.DISABLED)
        
    def match_keywords(self, text):
        """匹配关键词"""
        return [kw for kw in KEYWORDS if kw.lower() in text.lower()]
    
    def start_filter(self):
        """开始筛选职位"""
        filename = self.file_entry.get().strip()
        if not filename:
            self.show_result("请输入文件名！\n", error=True)
            return
            
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"正在读取文件: {filename}\n")
        self.result_text.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                urls = [url.strip() for url in f if url.strip()]
            
            if not urls:
                self.show_result("文件中没有找到有效链接！\n", error=True)
                return
                
            self.show_result(f"找到 {len(urls)} 个职位链接，开始筛选...\n\n")
            
            matched = []
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            for i, url in enumerate(urls, 1):
                self.show_result(f"处理第 {i} 个链接: {url}\n")
                self.root.update()
                
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    html = response.text
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    title = soup.title.text.split('_')[0].strip() if soup.title else "未知职位"
                    content = soup.get_text(separator=' ', strip=True)[:1000]
                    
                    # 匹配关键词
                    title_matches = self.match_keywords(title)
                    if title_matches:
                        matched.append({
                            'url': url,
                            'title': title,
                            'reason': f"职位名称匹配: {', '.join(title_matches)}"
                        })
                        self.show_result(f"✅ 匹配: {title}\n")
                    else:
                        content_matches = self.match_keywords(content)
                        if content_matches:
                            matched.append({
                                'url': url,
                                'title': title,
                                'reason': f"内容匹配: {', '.join(content_matches[:2])}"
                            })
                            self.show_result(f"✅ 匹配: {title}\n")
                        else:
                            self.show_result(f"❌ 不匹配: {title}\n")
                            
                except Exception as e:
                    self.show_result(f"❌ 处理失败: {str(e)}\n")
                    
                self.show_result("-" * 60 + "\n")
            
            # 显示最终结果
            self.show_result("\n" + "=" * 60 + "\n")
            self.show_result("筛选结果总结:\n")
            if matched:
                self.show_result(f"共找到 {len(matched)} 个软件开发相关职位:\n\n")
                for i, job in enumerate(matched, 1):
                    self.show_result(f"{i}. {job['title']}\n")
                    self.show_result(f"   URL: {job['url']}\n")
                    self.show_result(f"   匹配理由: {job['reason']}\n\n")
            else:
                self.show_result("未找到招聘软件开发人员的职位\n")
                
        except FileNotFoundError:
            self.show_result(f"错误：未找到文件 '{filename}'！\n", error=True)
        except Exception as e:
            self.show_result(f"错误：{str(e)}\n", error=True)
            
    def show_result(self, text, error=False):
        """显示结果到文本框"""
        self.result_text.config(state=tk.NORMAL)
        if error:
            self.result_text.insert(tk.END, "❌ " + text)
        else:
            self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = JobFilterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()