# 职位爬虫程序

## 文件说明

### 核心程序
- **selenium_job_scraper.py** - 主程序（推荐），支持JavaScript渲染页面
- **job_scraper.py** - 基础版本，使用requests+BeautifulSoup
- **joburl.txt** - 职位URL配置文件

### 分析工具
- **analyze_mismatched_job.py** - 分析不匹配职位的原因

## 使用方法

### 1. 安装依赖
```bash
pip install requests beautifulsoup4 selenium
```

### 2. 配置URL
编辑 `joburl.txt` 文件，每行添加一个职位URL

### 3. 运行程序
```bash
# 推荐：使用完整功能的Selenium版本
python selenium_job_scraper.py

# 或者：使用基础版本
python job_scraper.py
```

### 4. 分析不匹配职位（可选）
```bash
python analyze_mismatched_job.py
```

## 功能特点
- ✅ 自动筛选软件开发类职位
- ✅ 处理JavaScript渲染页面
- ✅ 反爬虫保护措施
- ✅ 详细的匹配结果分析
- ✅ 异常处理和错误恢复