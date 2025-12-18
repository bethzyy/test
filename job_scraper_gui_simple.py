#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件开发职位筛选工具 - GUI版本
功能：通过图形界面输入文件名，筛选软件开发职位
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import requests
from bs4 import BeautifulSoup
from config import SOFTWARE_JOB_KEYWORDS as KEYWORDS

class JobScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("软件开发职位筛选")
        self.root.geometry("800x600")
        
        # 设置样式
        self.setup_style()
        
        # 创建界面元素
        self.create_widgets()
        
    def setup_style(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 文件选择区域
        ttk.Label(main_frame, text="职位链接文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.filename_var = tk.StringVar(value="joburl.txt")
        self.filename_entry = ttk.Entry(file_frame, textvariable=self.filename_var, width=40)
        self.filename_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="浏览...", command=self.browse_file).grid(row=0, column=1)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        self.filter_button = ttk.Button(button_frame, text="开始筛选", 
                                       command=self.start_filtering, style="Accent.TButton")
        self.filter_button.grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="清空结果", command=self.clear_results).grid(row=0, column=1, padx=5)
        
        # 结果显示区域
        ttk.Label(main_frame, text="筛选结果:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        # 创建文本框和滚动条
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(result_frame, height=20, width=80, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_file(self):
        """浏览文件"""
        filename = filedialog.askopenfilename(
            title="选择职位链接文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.filename_var.set(filename)
            
    def clear_results(self):
        """清空结果显示"""
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("准备就绪")
        
    def match_keywords(self, text):
        """匹配关键词"""
        return [kw for kw in KEYWORDS if kw.lower() in text.lower()]
        
    def start_filtering(self):
        """开始筛选"""
        filename = self.filename_var.get().strip()
        
        if not filename:
            messagebox.showwarning("警告", "请输入文件名")
            return
            
        if not os.path.exists(filename):
            messagebox.showerror("错误", f"文件不存在: {filename}")
            return
            
        # 清空之前的结果
        self.clear_results()
        self.filter_button.config(state="disabled")
        self.status_var.set("正在筛选职位...")
        
        # 在新线程中运行筛选，避免界面卡顿
        thread = threading.Thread(target=self.run_filtering, args=(filename,))
        thread.daemon = True
        thread.start()
        
    def run_filtering(self, filename):
        """运行筛选"""
        try:
            # 读取URL文件
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    urls = [url.strip() for url in f if url.strip()]
            except Exception as e:
                self.root.after(0, self.append_text, f"读取文件失败: {str(e)}\n")
                return
            
            if not urls:
                self.root.after(0, self.append_text, "文件中没有找到有效的URL\n")
                return
                
            self.root.after(0, self.append_text, f"找到 {len(urls)} 个职位链接，开始筛选...\n\n")
            
            matched = []
            total_urls = len(urls)
            
            for i, url in enumerate(urls):
                self.root.after(0, self.append_text, f"[{i+1}/{total_urls}] {url}\n")
                
                try:
                    # 获取页面
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.get(url, headers=headers, timeout=10)
                    html = response.text
                    
                    # 解析页面
                    soup = BeautifulSoup(html, 'html.parser')
                    title = soup.title.text.split('_')[0].strip() if soup.title else "未知职位"
                    content = soup.get_text(separator=' ', strip=True)[:1000]
                    
                    # 匹配关键词
                    title_matches = self.match_keywords(title)
                    if title_matches:
                        matched.append({
                            'url': url,
                            'title': title,
                            'reason': f"职位名称: {', '.join(title_matches)}"
                        })
                        self.root.after(0, self.append_text, f"✅ 匹配: {title}\n")
                    else:
                        content_matches = self.match_keywords(content)
                        if content_matches:
                            matched.append({
                                'url': url,
                                'title': title,
                                'reason': f"内容匹配: {', '.join(content_matches[:2])}"
                            })
                            self.root.after(0, self.append_text, f"✅ 匹配: {title}\n")
                        else:
                            self.root.after(0, self.append_text, f"❌ 不匹配: {title}\n")
                            
                except Exception as e:
                    self.root.after(0, self.append_text, f"访问失败: {str(e)}\n")
                
                self.root.after(0, self.append_text, "-" * 40 + "\n")
            
            # 显示最终结果
            self.root.after(0, self.show_final_results, matched)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
            
    def append_text(self, text):
        """追加文本到结果框"""
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)
        
    def show_final_results(self, matched):
        """显示最终结果"""
        self.append_text("\n筛选结果:\n")
        if matched:
            for i, job in enumerate(matched, 1):
                self.append_text(f"{i}. {job['title']}\n")
                self.append_text(f"   URL: {job['url']}\n")
                self.append_text(f"   匹配理由: {job['reason']}\n\n")
        else:
            self.append_text("未找到招聘软件开发人员的职位\n")
            
        self.status_var.set(f"筛选完成 - 找到 {len(matched)} 个匹配职位")
        self.filter_button.config(state="normal")
        
    def show_error(self, error):
        """显示错误信息"""
        self.append_text(f"\n错误: {error}\n")
        self.status_var.set("筛选失败")
        self.filter_button.config(state="normal")

def main():
    """主函数"""
    root = tk.Tk()
    app = JobScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()