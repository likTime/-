# 嗅觉视频下载器 (Video Sniffer Downloader)

*Note: English version is available below. / 注意：下方有英文版本*

### 项目简介

视频嗅探下载器是一个功能强大的视频下载工具，能够通过监控剪贴板或扫描网站自动检测并下载视频。支持多种视频格式和主流视频平台，提供直观的GUI界面和实时下载进度显示

功能特点

***·自动剪贴板监控***：实时监控剪贴板，自动检测并下载复制的视频链接

***·智能网站扫描***：扫描指定网站，提取页面中的所有视频链接

***·多平台支持***：支持B站、抖音、优酷、爱奇艺、腾讯视频、芒果TV、西瓜视频、快手等主流平台

***·多种视频格式***：支持mp4、mkv、avi、flv、wmv、mov、webm、m3u8等格式

***·实时进度显示***：显示下载进度、文件大小和下载速度

***·智能反爬绕过***：模拟浏览器请求头，绕过部分网站的反爬机制

***·自定义下载路径***：支持选择自定义下载目录

***·友好GUI界面***：简洁直观的用户界面，操作便捷

## 安装说明

#### 系统要求

·Python 3.7+

·Windows 10/11 (推荐) 或 Linux/macOS

#### 依赖安装

```pip install -r requirements.txt```

### 快速开始

##### 1. 克隆项目到本地
```git clone https://github.com/likTime/视频嗅探下载器.git```

```cd 视频嗅探下载器```


##### 2. 安装依赖
```pip install -r requirements.txt```

##### 3. 运行程序
```python 视频嗅探下载器.py```

### 使用方法

#### 方法一：剪贴板监控

1.点击"开始监控剪贴板"按钮

2.复制任意视频链接到剪贴板

3.程序自动检测并开始下载
#### 方法二：网站扫描

1.在URL输入框中输入网站地址

2.点击"扫描网站"按钮

3.程序自动提取页面中的视频链接并下载

### 自定义设置
***·下载路径***：点击"选择下载路径"按钮设置保存目录
***·查看日志***：点击"详细日志"查看完整操作记录
***·更新信息***：点击"更新日志"查看版本更新历史

### 技术架构
```视频嗅探下载器/
├── 核心功能模块
│   ├── 剪贴板监控 (pyperclip)
│   ├── 网络请求 (requests)
│   ├── 链接解析 (正则表达式)
│   └── 多线程下载
├── GUI界面
│   ├── tkinter主窗口
│   ├── 进度条显示
│   ├── 实时日志
│   └── 状态栏
└── 平台适配
    ├── 各视频平台解析器
    ├── 请求头模拟
    └── 错误处理机制
```
## 工作原理

1.  **链接捕获**：通过监控剪贴板或扫描网页HTML内容，利用预定义的正则表达式模式匹配视频流URL。
2.  **请求模拟**：添加完整的浏览器请求头（User-Agent, Referer, Cookie等），模拟真实浏览器行为，以绕过简单的反爬虫机制。
3.  **流媒体识别**：通过检查HTTP响应头中的`Content-Type`和URL文件扩展名，验证链接是否为有效的视频流。
4.  **分块下载**：使用HTTP流式下载，将大文件分割为多个块（Chunk）进行传输，支持断点续传（通过`Range`头）。
5.  **实时更新**：在主线程中通过Tkinter的变量（`DoubleVar`, `StringVar`）实时更新进度条和下载信息标签。
6.  **文件保存**：根据当前时间戳和源URL信息生成唯一文件名，并将数据写入本地文件系统。

## 常见问题 (FAQ)

**Q: 扫描网站时出现"412 Client Error"或"403 Forbidden"错误怎么办？**

**A:** 程序已内置模拟浏览器请求头，但某些网站的反爬策略较强。可以尝试以下方法：
*   确保输入的URL格式正确（包含`http://`或`https://`）。
*   程序会自动尝试修复常见的域名格式错误（如`wwwbilibilicom` -> `www.bilibili.com`）。
*   网络环境或目标网站暂时不可访问。

**Q: 下载的视频文件无法播放或文件大小异常小？**

**A:** 程序具备文件完整性检查功能。如果文件小于1MB或远小于预期大小，会自动将其识别为无效文件并删除。请确保源视频链接有效且可公开访问。

**Q: 如何下载B站、抖音等需要登录才能观看的视频？**

**A:** 当前版本主要针对公开可访问的视频内容。对于需要登录或会员的视频，程序内置的通用请求头可能权限不足。您可以尝试手动复制视频链接到剪贴板使用监控下载功能，有时可直接获取到视频流。

**Q: 程序无法启动或缺少模块？**

**A:** 请确保已正确安装`requirements.txt`中的所有依赖（`requests`, `pyperclip`）。如果使用Linux系统，可能还需要安装Tkinter相关包（例如在Ubuntu上：`sudo apt-get install python3-tk`）。

## 更新日志

*   **v1.2.0 (2026-01-30)**: 新增下载进度条与实时速度显示；优化B站视频解析逻辑。
*   **v1.1.0 (2025-12-27)**: 优化UI布局；增强日志系统；修复B站403错误。
*   **v1.0.5 (2025-12-25)**: 重写为GUI界面；添加剪贴板监控与网站扫描功能。
*   **v1.0.0 (2025-12-01)**: 初始版本发布，支持基础视频流下载。

（详细更新内容请点击程序内的"更新日志"按钮查看。）

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。对于新视频平台的支持或功能建议尤其欢迎。

## 免责声明

本工具仅供学习和研究目的使用。请尊重版权，仅下载您拥有合法权限或授权下载的视频内容。使用者应对其下载行为负责，作者不承担任何法律责任。

## 作者

*   **李健辉 (likTime)** - [GitHub主页](https://github.com/likTime)

    **邮箱**：3849730216@qq.com
---

**如果觉得这个项目对你有帮助，请给它一个Star！⭐**



# Video Sniffer Downloader

## Project Introduction

Video Sniffer Downloader is a powerful video downloading tool that can automatically detect and download videos by monitoring the clipboard or scanning websites. It supports multiple video formats and mainstream video platforms, providing an intuitive GUI interface and real-time download progress display.

## Features

• **Automatic Clipboard Monitoring**: Real-time clipboard monitoring, automatically detects and downloads copied video links

• **Intelligent Website Scanning**: Scans specified websites to extract all video links from the page

• **Multi-Platform Support**: Supports Bilibili, Douyin, Youku, iQiyi, Tencent Video, Mango TV, Xigua Video, Kuaishou and other mainstream platforms

• **Multiple Video Formats**: Supports mp4, mkv, avi, flv, wmv, mov, webm, m3u8 and other formats

• **Real-time Progress Display**: Shows download progress, file size and download speed

• **Smart Anti-Scraping Bypass**: Simulates browser headers to bypass anti-scraping mechanisms

• **Custom Download Path**: Supports selecting custom download directory

• **User-Friendly GUI**: Simple and intuitive user interface, easy to operate

## Installation Instructions

#### System Requirements
• Python 3.7+
• Windows 10/11 (Recommended) or Linux/macOS

#### Dependency Installation

```pip install -r requirements.txt```

### Quick Start

#### 1. Clone the repository

```git clone https://github.com/likTime/视频嗅探下载器.git```

```cd 视频嗅觉下载器```

#### 2. Install dependencies

```pip install -r requirements.txt```

#### 3. Run the program

```python 视频嗅探下载器.py```

## Usage

#### Method 1: Clipboard Monitoring
1. Click "Start Monitoring Clipboard" button
2. Copy any video link to clipboard
3. Program automatically detects and starts downloading

#### Method 2: Website Scanning
1. Enter website URL in URL input box
2. Click "Scan Website" button
3. Program automatically extracts video links from page and downloads them

## Custom Settings
• **Download Path**: Click "Select Download Path" to set save directory
• **View Logs**: Click "Detailed Logs" to view complete operation history
• **Update Info**: Click "Update Log" to view version update history

## Technical Architecture

```Video-Sniffer-Downloader/

├── Core Modules

│   ├── Clipboard Monitoring (pyperclip)

│   ├── Network Requests (requests)

│   ├── Link Parsing (Regular Expressions)

│   └── Multi-threaded Downloading

├── GUI Interface

│   ├── tkinter Main Window

│   ├── Progress Bar Display

│   ├── Real-time Logs

│   └── Status Bar

└── Platform Adaptation

├── Video Platform Parsers

├── Request Header Simulation

└── Error Handling
```

## How It Works

1. **Link Capture**: Monitor clipboard or scan webpage HTML, use regex patterns to match video URLs
2. **Request Simulation**: Add browser headers to simulate real browser behavior
3. **Stream Identification**: Verify links by checking Content-Type and file extensions
4. **Chunked Downloading**: Download in chunks with resume support (Range header)
5. **Real-time Updates**: Update progress using Tkinter variables
6. **File Saving**: Generate unique filenames and save to local storage

## FAQ

**Q: Getting "412 Client Error" or "403 Forbidden" when scanning websites?**

**A:** Program has built-in browser headers, but some sites have strong anti-scraping. Try:
• Ensure correct URL format (http:// or https://)
• Program auto-fixes common domain format errors
• Check network/target site accessibility

**Q: Downloaded video won't play or file is too small?**

**A:** Program checks file integrity. Files <1MB or significantly smaller than expected are auto-deleted.

**Q: How to download login-required videos?**

**A:** Current version targets publicly accessible content. For member-only videos, try copying direct video links to clipboard.

**Q: Program won't start or missing modules?**

**A:** Ensure all dependencies in requirements.txt are installed. On Linux, may need: 
```sudo apt-get install python3-tk```

## Changelog

• **v1.2.0 (2026-01-30)**: Added progress bar and speed display; optimized Bilibili parsing

• **v1.1.0 (2025-12-27)**: Improved UI; enhanced logs; fixed Bilibili 403 errors

• **v1.0.5 (2025-12-25)**: GUI version; added clipboard monitoring and website scanning

• **v1.0.0 (2025-12-01)**: Initial release with basic video downloading

## Disclaimer

This tool is for learning and research only. Respect copyrights and only download content you have rights to. Users are responsible for their activities.

Translated by DeepSeek. Please email me if you find any errors.

## Author

**Li Jianhui** ([likTime](https://github.com/likTime) on GitHub)  
**Email**: 3849730216@qq.com

---

**If this project helps you, please give it a Star! ⭐**
