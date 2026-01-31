# 视频嗅探下载器

## 功能特点

* 通过监控剪贴板自动检测视频链接
* 通过网站扫描提取视频链接
* 支持多种视频格式：mp4、mkv、avi、flv、wmv、mov、webm、m3u8等
* 自动提取视频URL并下载
* 实时显示下载进度和日志
* 友好的GUI界面
* 支持自定义下载路径
* 支持模拟浏览器访问，绕过部分反爬机制

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：

```bash
   python 视频嗅探下载器.py
   ```

2. 方法一：监控剪贴板

   * 点击"开始监控剪贴板"按钮
   * 复制视频链接到剪贴板
   * 程序会自动检测并下载视频

3. 方法二：扫描网站

   * 在URL输入框中输入网站地址
   * 点击"扫描网站"按钮
   * 程序会扫描该网站上的视频链接并下载

4. 自定义下载路径

   * 点击"选择下载路径"按钮
   * 在弹出的对话框中选择保存视频的目录

5. 点击"停止监控"按钮停止剪贴板监控
6. 下载的视频会保存在指定的下载目录中

## 注意事项

* 部分网站可能有反爬虫机制，导致无法获取视频URL
* 下载视频时请遵守相关法律法规
* 建议在测试时使用较小的视频文件

## 工作原理

1. **剪贴板监控**：使用pyperclip库监控剪贴板内容，当检测到视频链接时自动下载
2. **网站扫描**：使用requests库访问网站，提取页面中的链接，通过正则表达式匹配视频URL
3. **模拟浏览器**：添加浏览器请求头，绕过部分网站的反爬机制
4. **视频下载**：使用requests库下载视频文件，保存到本地目录

## 常见问题

### 1\. 扫描网站时出现"412 Client Error"错误

* 原因：网站的反爬机制检测到了爬虫访问
* 解决方法：程序已经内置了浏览器请求头模拟，大多数情况下可以解决此问题

### 2\. 无法捕获到视频URL

* 原因：可能是视频流使用了特殊的加密或播放方式
* 解决方法：尝试使用浏览器开发者工具查看视频流URL，然后复制到剪贴板

### 3\. 下载的视频文件无法播放

* 原因：可能是视频流不完整或格式不支持
* 解决方法：尝试使用其他视频播放器或检查视频流URL是否正确

## 可扩展方向

* 支持更多视频网站的视频流解析
* 添加视频格式转换功能
* 实现多线程下载，提高下载速度
* 添加视频质量选择功能
* 支持批量下载视频

## 更新日志

### v1.2.0 (2024-01-25)

* 添加了自定义下载路径功能
* 优化了GUI界面布局
* 增加了路径选择按钮和路径显示

### v1.1.0 (2024-01-25)

* 重写为GUI界面，提高用户体验
* 添加了剪贴板监控功能
* 添加了网站扫描功能
* 添加了完整的浏览器请求头模拟，绕过反爬机制
* 移除了对Scapy库的依赖，解决了winpcap安装问题

### v1.0.0 (2024-01-25)

* 初始版本
* 基于Scapy库的网络数据包捕获
* 命令行界面

## 作者

* 李健辉
* 版本：1.2.0
* 发布日期：2024-01-25





# Video Sniffer Downloader

## Features

* Automatically detects video links by monitoring the clipboard
* Extracts video links by scanning websites
* Supports multiple video formats: mp4, mkv, avi, flv, wmv, mov, webm, m3u8, etc.
* Automatically extracts and downloads video URLs
* Displays real-time download progress and logs
* User-friendly GUI interface
* Supports custom download paths
* Simulates browser access to bypass certain anti-scraping mechanisms

## Installation Dependencies

```bash  
pip install -r requirements.txt  
```  

## Usage Instructions

1. Run the program:

```bash  
   python Video\_Sniffer\_Downloader.py  
   ```  

2. Method 1: Clipboard Monitoring

   * Click the "Start Clipboard Monitoring" button
   * Copy a video link to the clipboard
   * The program will automatically detect and download the video

3. Method 2: Website Scanning

   * Enter the website URL in the input box
   * Click the "Scan Website" button
   * The program will scan for video links on the website and download them

4. Custom Download Path

   * Click the "Select Download Path" button
   * Choose the directory to save videos in the pop-up dialog

5. Click the "Stop Monitoring" button to halt clipboard monitoring
6. Downloaded videos will be saved in the specified directory

## Notes

* Some websites may have anti-scraping mechanisms that prevent video URL extraction
* Ensure compliance with relevant laws and regulations when downloading videos
* It is recommended to test with smaller video files

## How It Works

1. **Clipboard Monitoring**: Uses the `pyperclip` library to monitor clipboard content and automatically downloads detected video links
2. **Website Scanning**: Uses the `requests` library to access websites, extract links, and match video URLs via regular expressions
3. **Browser Simulation**: Adds browser request headers to bypass certain anti-scraping measures
4. **Video Downloading**: Uses the `requests` library to download video files and save them locally

## Frequently Asked Questions

### 1\. "412 Client Error" appears when scanning a website

* Cause: The website's anti-scraping mechanism detected the crawler
* Solution: The program already includes simulated browser headers, which should resolve the issue in most cases

### 2\. Unable to capture video URLs

* Cause: The video stream may use special encryption or playback methods
* Solution: Try using browser developer tools to inspect the video stream URL and copy it to the clipboard

### 3\. Downloaded video files cannot be played

* Cause: The video stream may be incomplete or the format is unsupported
* Solution: Try using another video player or check if the video stream URL is correct

## Future Enhancements

* Support parsing video streams from more websites
* Add video format conversion functionality
* Implement multi-threaded downloads for faster speeds
* Add video quality selection options
* Support batch video downloads

## Changelog

### v1.2.0 (2024-01-25)

* Added custom download path functionality
* Optimized GUI layout
* Added path selection button and path display

### v1.1.0 (2024-01-25)

* Rewritten with a GUI interface for better user experience
* Added clipboard monitoring functionality
* Added website scanning functionality
* Added full browser header simulation to bypass anti-scraping mechanisms
* Removed dependency on the Scapy library, resolving winpcap installation issues

### v1.0.0 (2024-01-25)

* Initial release
* Network packet capture based on the Scapy library
* Command-line interface

## Author

* Jianhui Li
* Version: 1.2.0
* Release Date: 2024-01-25
