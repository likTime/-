# 视频嗅探下载器
# 作者：李健辉
# 功能：通过监控网络请求，分析视频流，提取URL并下载

import requests
import re
import os
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
import queue
import pyperclip
import time

# 视频流协议的正则表达式（优化版，支持国内主流视频平台）
# 支持的平台：B站、抖音、优酷、爱奇艺、腾讯视频、芒果TV、西瓜视频、快手
VIDEO_PATTERNS = [
    r'\.(mp4|mkv|avi|flv|wmv|mov|webm)(\?.*)?$',  # 常见视频格式
    r'\.m3u8(\?.*)?$',  # M3U8播放列表
    r'(?i)(video|mp4|stream)\.(php|asp|aspx|jsp)(\?.*)?$',  # 视频播放页面
    r'(?i)/video/.*\.(mp4|mkv|avi|flv|wmv|mov|webm)(\?.*)?$',  # 视频路径
    r'(?i)/stream/.*\.(mp4|mkv|avi|flv|wmv|mov|webm)(\?.*)?$',  # 流路径
    # B站视频
    r'(?i)bilibili\.com.*\.flv(\?.*)?$',  # B站FLV格式
    r'(?i)bilibili\.com.*\.mp4(\?.*)?$',  # B站MP4格式
    r'(?i)api\.bilibili\.com.*playurl.*$',  # B站播放API
    r'(?i)upos-hz-mirrorks3\.bilivideo\.com.*$',  # B站视频存储服务器
    r'(?i)upos-sz-mirrorks3\.bilivideo\.com.*$',  # B站视频存储服务器
    # 抖音视频
    r'(?i)douyin\.com.*video/.*$',  # 抖音视频页面
    r'(?i)v\.douyin\.com/.*$',  # 抖音短链接
    r'(?i)aweme\.snsvideocdn\.com.*$',  # 抖音视频CDN
    r'(?i)douyin\.tiktokcdn-us\.com.*$',  # 抖音国际版CDN
    r'(?i)music\.douyin\.com.*$',  # 抖音音乐
    # 优酷视频
    r'(?i)youku\.com.*id_.*\.html$',  # 优酷视频页面
    r'(?i)player\.youku\.com/embed/.*$',  # 优酷播放器
    r'(?i)vali\.youku\.com/.*$',  # 优酷视频CDN
    r'(?i)ups\.youku\.com/.*$',  # 优酷视频存储
    # 爱奇艺视频
    r'(?i)iqiyi\.com/v_.*\.html$',  # 爱奇艺视频页面
    r'(?i)www\.iqiyi\.com/.*\.html$',  # 爱奇艺其他页面
    r'(?i)cache\.m\.iqiyi\.com/.*$',  # 爱奇艺缓存
    r'(?i)data\.m\.iqiyi\.com/.*$',  # 爱奇艺数据
    # 腾讯视频
    r'(?i)v\.qq\.com/.*\.html$',  # 腾讯视频页面
    r'(?i)film\.qq\.com/.*$',  # 腾讯电影页面
    r'(?i)imgcache\.qq\.com/.*$',  # 腾讯视频CDN
    r'(?i)vd\.qq\.com/.*$',  # 腾讯视频播放
    # 芒果TV
    r'(?i)mgtv\.com/b/.*\.html$',  # 芒果TV视频页面
    r'(?i)www\.mgtv\.com/.*$',  # 芒果TV其他页面
    r'(?i)gslb\.mgtv\.com/.*$',  # 芒果TV CDN
    r'(?i)video\.mgtv\.com/.*$',  # 芒果TV视频
    # 西瓜视频
    r'(?i)ixigua\.com/.*$',  # 西瓜视频页面
    r'(?i)v\.ixigua\.com/.*$',  # 西瓜视频短链接
    r'(?i)snssdk\.com/.*$',  # 西瓜视频CDN
    # 快手视频
    r'(?i)kuaishou\.com/f/.*$',  # 快手视频页面
    r'(?i)v\.kuaishou\.com/.*$',  # 快手短链接
    r'(?i)aweme\.kuaishoucdn\.com/.*$'  # 快手视频CDN
]

# 已捕获的视频URL列表
captured_urls = set()

# 下载目录
DOWNLOAD_DIR = os.path.join("D:", "视频下载")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# 全局变量
running = False

# 下载任务队列
download_queue = queue.Queue()

# 当前下载任务
current_download = None

# 线程池
download_threads = []
MAX_THREADS = 3

# 下载视频
def download_video(url):
    """
    将下载任务添加到队列中，由专门的下载线程处理
    """
    global captured_urls
    
    # 跳过已处理的URL
    if url in captured_urls:
        return
    
    captured_urls.add(url)
    log_message(f"[+] 开始处理视频URL: {url}", is_detailed=True)
    
    # 将任务添加到队列
    download_queue.put(url)

# 下载工作线程
def download_worker():
    """
    下载工作线程，负责实际的视频下载操作
    """
    while True:  # 始终运行，直到程序退出
        try:
            # 从队列中获取任务，设置超时避免线程阻塞
            url = download_queue.get(timeout=1)
            
            # 执行实际的下载操作
            _download_video(url)
            
            # 标记任务完成
            download_queue.task_done()
        except queue.Empty:
            # 队列为空，继续等待
            continue
        except Exception as e:
            log_message(f"[-] 下载工作线程错误: {str(e)}")
            # 标记任务完成，避免队列阻塞
            try:
                download_queue.task_done()
            except:
                pass

# 实际的下载函数
def _download_video(url):
    """
    实际执行视频下载操作
    """
    try:
        # 添加请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com'
        }
        
        # 对于B站视频流，添加额外的请求头
        if 'bilivideo.com' in url:
            headers.update({
                'Cookie': 'buvid3=33F03F5E-D644-1683-8352-B640E53DF6E170193infoc; bili_jct=1234567890abcdef; SESSDATA=1234567890abcdef; DedeUserID=123456789; DedeUserID__ckMd5=1234567890abcdef;',
                'Host': url.split('/')[2],
                'Range': 'bytes=0-',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
        
        # 对于抖音视频流，添加额外的请求头
        elif 'snsvideocdn.com' in url or 'tiktokcdn-us.com' in url:
            headers.update({
                'Cookie': 'tt_webid=1234567890abcdef; tt_webid_v2=1234567890abcdef;',
                'Host': url.split('/')[2],
                'Range': 'bytes=0-',
                'Referer': 'https://www.douyin.com/',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
        
        # 对于优酷视频流，添加额外的请求头
        elif 'youku.com' in url or 'vali.youku.com' in url:
            headers.update({
                'Cookie': 'cna=1234567890abcdef; l=1234567890abcdef;',
                'Host': url.split('/')[2],
                'Range': 'bytes=0-',
                'Referer': 'https://www.youku.com/',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
        
        # 对于爱奇艺视频流，添加额外的请求头
        elif 'iqiyi.com' in url or 'cache.m.iqiyi.com' in url:
            headers.update({
                'Cookie': 'QED=1234567890abcdef; P00001=1234567890abcdef;',
                'Host': url.split('/')[2],
                'Range': 'bytes=0-',
                'Referer': 'https://www.iqiyi.com/',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
        
        # 对于腾讯视频流，添加额外的请求头
        elif 'qq.com' in url:
            headers.update({
                'Cookie': 'pgv_pvid=1234567890; pgv_info=1234567890;',
                'Host': url.split('/')[2],
                'Range': 'bytes=0-',
                'Referer': 'https://v.qq.com/',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
        
        # 对于芒果TV视频流，添加额外的请求头
        elif 'mgtv.com' in url:
            headers.update({
                'Cookie': '芒果TV_COOKIE=1234567890abcdef;',
                'Host': url.split('/')[2],
                'Range': 'bytes=0-',
                'Referer': 'https://www.mgtv.com/',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
        
        # 对于西瓜视频流，添加额外的请求头
        elif 'ixigua.com' in url or 'snssdk.com' in url:
            headers.update({
                'Cookie': 'tt_webid=1234567890abcdef; tt_webid_v2=1234567890abcdef;',
                'Host': url.split('/')[2],
                'Range': 'bytes=0-',
                'Referer': 'https://www.ixigua.com/',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
        
        # 对于快手视频流，添加额外的请求头
        elif 'kuaishou.com' in url or 'kuaishoucdn.com' in url:
            headers.update({
                'Cookie': 'kuaishou_webid=1234567890abcdef;',
                'Host': url.split('/')[2],
                'Range': 'bytes=0-',
                'Referer': 'https://www.kuaishou.com/',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
        
        # 对于B站视频流，添加额外的请求头
        elif 'bilivideo.com' in url or 'bilibili.com' in url:
            headers.update({
                'Cookie': 'buvid3=33F03F5E-D644-1683-8352-B640E53DF6E170193infoc;',
                'Host': url.split('/')[2],
                'Range': 'bytes=0-',
                'Referer': 'https://www.bilibili.com/',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
        
        # 检查URL是否为真实视频链接
        response = None
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=30, allow_redirects=True)
            
            # 处理常见的HTTP状态码
            if response.status_code == 200:
                log_message(f"[+] 成功连接到视频服务器")
            elif response.status_code == 206:
                log_message(f"[+] 成功连接到视频服务器 (部分内容)")
            elif response.status_code == 403:
                log_message(f"[-] 下载失败，状态码: 403 Forbidden (可能需要登录)", is_detailed=True)
                log_message(f"[+] 尝试使用不同的请求头重试...", is_detailed=True)
                # 尝试简化请求头
                simple_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': 'https://www.bilibili.com/',
                    'Range': 'bytes=0-'
                }
                response = requests.get(url, headers=simple_headers, stream=True, timeout=30, allow_redirects=True)
                if response.status_code not in [200, 206]:
                    log_message(f"[-] 重试失败，状态码: {response.status_code}", is_detailed=True)
                    return
            elif response.status_code == 404:
                log_message(f"[-] 下载失败，状态码: 404 Not Found", is_detailed=True)
                return
            elif response.status_code >= 500:
                log_message(f"[-] 下载失败，状态码: {response.status_code} (服务器错误)", is_detailed=True)
                return
            else:
                log_message(f"[-] 下载失败，状态码: {response.status_code}", is_detailed=True)
                return
        except requests.RequestException as e:
            log_message(f"[-] 网络请求错误: {str(e)}", is_detailed=True)
            return
        
        # 确保response对象有效且状态码正确
        if not response or response.status_code not in [200, 206]:
            log_message(f"[-] 无效的响应，状态码: {response.status_code if response else '无'}", is_detailed=True)
            return
        
        # 检查内容类型
        content_type = response.headers.get('Content-Type', '')
        if not any(ext in content_type for ext in ['video', 'mp4', 'flv', 'webm', 'mov']):
            # 如果没有Content-Type或不是视频类型，检查文件扩展名
            if not any(ext in url.lower() for ext in ['.mp4', '.mkv', '.avi', '.flv', '.wmv', '.mov', '.webm']):
                log_message(f"[-] 跳过非视频文件: {url}", is_detailed=True)
                return
        
        # 生成文件名（优化版）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 尝试从URL中提取有意义的文件名
        filename_match = re.search(r'/([^/]+)\.(mp4|mkv|avi|flv|wmv|mov|webm)(\?.*)?$', url)
        if filename_match:
            base_name = filename_match.group(1)
            # 清理文件名中的特殊字符
            base_name = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5]', '_', base_name)
            ext = filename_match.group(2)
        else:
            # 从Content-Disposition中提取文件名
            content_disposition = response.headers.get('Content-Disposition', '')
            disp_match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if disp_match:
                base_name = disp_match.group(1)
                # 清理文件名
                base_name = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5]', '_', base_name)
                ext = 'mp4'  # 默认扩展名
            else:
                # 使用时间戳作为文件名
                base_name = f"video_{timestamp}"
                ext = 'mp4'
        
        # 确保文件名唯一
        filename = f"{base_name}.{ext}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        
        # 如果文件已存在，添加序号
        counter = 1
        while os.path.exists(filepath):
            filename = f"{base_name}_{counter}.{ext}"
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            counter += 1
        
        # 在GUI中显示消息
        log_message(f"[+] 发现视频URL")
        log_message(f"[+] 开始下载视频")
        log_message(f"[+] 保存路径: {filepath}")
        # 详细日志
        log_message(f"[+] 视频URL: {url}", is_detailed=True)
        log_message(f"[+] 完整保存路径: {filepath}", is_detailed=True)
        
        # 下载视频
        total_size = int(response.headers.get('Content-Length', 0))
        downloaded_size = 0
        start_time = time.time()
        last_time = start_time
        last_downloaded = 0
        
        # 打开文件进行写入
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                if not chunk:
                    continue
                
                # 写入数据
                f.write(chunk)
                downloaded_size += len(chunk)
                
                # 定期刷新缓冲区，确保数据及时写入
                if downloaded_size % (1024*1024*5) == 0:  # 每5MB刷新一次
                    f.flush()
                    os.fsync(f.fileno())
                
                # 更新进度条和下载信息
                if total_size > 0:
                    progress = (downloaded_size / total_size) * 100
                    # 计算下载速度
                    current_time = time.time()
                    time_elapsed = current_time - last_time
                    if time_elapsed > 0.5:  # 每0.5秒更新一次速度
                        # 转换为MB
                        total_mb = total_size / (1024 * 1024)
                        downloaded_mb = downloaded_size / (1024 * 1024)
                        # 计算速度
                        speed_mb = (downloaded_size - last_downloaded) / (1024 * 1024) / time_elapsed
                        
                        # 只在主线程中更新GUI
                        if 'progress_var' in globals():
                            import tkinter as tk
                            progress_var.set(progress)
                            # 更新下载信息标签
                            if 'download_info_label' in globals():
                                download_info_label.config(text=f"总大小: {total_mb:.2f} MB | 已下载: {downloaded_mb:.2f} MB | 速度: {speed_mb:.2f} MB/s")
                            # 强制更新GUI（尝试使用root窗口）
                            try:
                                # 获取root窗口并更新
                                root = tk._default_root
                                if root:
                                    root.update_idletasks()
                            except:
                                pass
                        
                        last_time = current_time
                        last_downloaded = downloaded_size
        
        # 检查文件大小，过滤空文件或过小的文件
        file_size = os.path.getsize(filepath)
        if file_size < 1024 * 1024:  # 小于1MB的文件可能不是完整视频
            os.remove(filepath)
            log_message(f"[-] 移除过小文件: {filename} (可能不是完整视频)", is_detailed=True)
            return
        
        # 检查文件是否完整（如果有Content-Length头）
        if total_size > 0 and file_size < total_size * 0.9:  # 文件大小小于预期的90%，可能不完整
            os.remove(filepath)
            log_message(f"[-] 移除不完整文件: {filename} (仅下载了 {file_size/total_size*100:.1f}%)", is_detailed=True)
            return
        
        # 下载完成，添加可点击的日志
        log_message(f"[+] 下载完成: {filename}")
        # 添加可点击的打开链接
        log_message(f"[+] 点击查看: {filepath}")
        
        # 重置进度条和下载信息
        if 'progress_var' in globals():
            import tkinter as tk
            progress_var.set(0)
            # 重置下载信息标签
            if 'download_info_label' in globals():
                download_info_label.config(text="总大小: 0 MB | 已下载: 0 MB | 速度: 0 MB/s")
            try:
                root = tk._default_root
                if root:
                    root.update_idletasks()
            except:
                pass
    except Exception as e:
        log_message(f"[-] 下载错误: {str(e)}", is_detailed=True)
        # 清理可能的不完整文件
        try:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
                log_message(f"[-] 清理不完整文件: {filename}", is_detailed=True)
        except:
            pass
        
        # 重置进度条和下载信息
        if 'progress_var' in globals():
            import tkinter as tk
            progress_var.set(0)
            # 重置下载信息标签
            if 'download_info_label' in globals():
                download_info_label.config(text="总大小: 0 MB | 已下载: 0 MB | 速度: 0 MB/s")
            try:
                root = tk._default_root
                if root:
                    root.update_idletasks()
            except:
                pass

# 从剪贴板获取URL并检查是否是视频链接
def check_clipboard():
    global running
    while running:
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content and clipboard_content not in captured_urls:
                # 检查是否是视频URL
                for pattern in VIDEO_PATTERNS:
                    if re.search(pattern, clipboard_content, re.IGNORECASE):
                        captured_urls.add(clipboard_content)
                        download_video(clipboard_content)
                        break
        except Exception as e:
            pass
        time.sleep(1)  # 每秒检查一次剪贴板

# 扫描指定网站的视频链接
def scan_website():
    url = url_entry.get()
    if not url:
        messagebox.showerror("错误", "请输入网站URL")
        return
    
    # 确保URL有正确的协议前缀
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    
    # 修复域名格式错误（确保域名包含必要的点）
    domain_match = re.search(r'https?://([^/]+)', url)
    if domain_match:
        domain = domain_match.group(1)
        # 检查域名是否缺少点或格式不正确
        if '.' not in domain or ('www' in domain and not domain.startswith('www.')):
            # 尝试修复常见的域名格式错误
            # 例如：wwwbilibilicom -> www.bilibili.com
            fixed_domain = domain
            
            # 首先处理www前缀
            if fixed_domain.startswith('www') and not fixed_domain.startswith('www.'):
                fixed_domain = 'www.' + fixed_domain[3:]
            
            # 检查是否包含常见的域名后缀
            suffixes = ['.com', '.net', '.org', '.cn', '.io', '.dev']
            for suffix in suffixes:
                suffix_no_dot = suffix[1:]  # 移除点
                if suffix_no_dot in fixed_domain and not fixed_domain.endswith(suffix):
                    # 在后缀前添加点
                    pos = fixed_domain.find(suffix_no_dot)
                    if pos > 0:
                        fixed_domain = fixed_domain[:pos] + '.' + fixed_domain[pos:]
                        break
            
            # 特殊处理：如果域名中仍然没有点，尝试在中间添加点
            if '.' not in fixed_domain and len(fixed_domain) > 6:
                # 尝试在合适的位置添加点
                # 例如：bilibilicom -> bilibili.com
                for i in range(3, len(fixed_domain) - 2):
                    if fixed_domain[i:].startswith('com') or fixed_domain[i:].startswith('net') or fixed_domain[i:].startswith('org'):
                        fixed_domain = fixed_domain[:i] + '.' + fixed_domain[i:]
                        break
            
            # 如果域名已修复，更新链接
            if fixed_domain != domain:
                old_url = url
                url = url.replace(domain, fixed_domain)
                log_message(f"[+] 修复域名格式错误: {old_url} -> {url}")
    
    log_message(f"[+] 开始扫描网站: {url}")
    
    try:
        # 添加请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # 发送请求获取网页内容
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 提取所有链接
        links = re.findall(r'href=["\'](.*?)["\']', response.text)
        
        # 检查每个链接是否是视频URL
        for link in links:
            # 处理相对路径
            if not link.startswith('http'):
                if link.startswith('/'):
                    # 绝对路径，基于域名
                    domain_match = re.search(r'https?://([^/]+)', url)
                    if domain_match:
                        domain = domain_match.group(0)
                        link = domain + link
                else:
                    # 相对路径，基于当前URL
                    link = url.rstrip('/') + '/' + link
            
            # 修复域名格式错误（确保域名包含必要的点）
            domain_match = re.search(r'https?://([^/]+)', link)
            if domain_match:
                domain = domain_match.group(1)
                # 检查域名是否缺少点或格式不正确
                if '.' not in domain or ('www' in domain and not domain.startswith('www.')):
                    # 尝试修复常见的域名格式错误
                    # 例如：wwwbilibilicom -> www.bilibili.com
                    fixed_domain = domain
                    
                    # 首先处理www前缀
                    if fixed_domain.startswith('www') and not fixed_domain.startswith('www.'):
                        fixed_domain = 'www.' + fixed_domain[3:]
                    
                    # 检查是否包含常见的域名后缀
                    suffixes = ['.com', '.net', '.org', '.cn', '.io', '.dev']
                    for suffix in suffixes:
                        suffix_no_dot = suffix[1:]  # 移除点
                        if suffix_no_dot in fixed_domain and not fixed_domain.endswith(suffix):
                            # 在后缀前添加点
                            pos = fixed_domain.find(suffix_no_dot)
                            if pos > 0:
                                fixed_domain = fixed_domain[:pos] + '.' + fixed_domain[pos:]
                                break
                    
                    # 特殊处理：如果域名中仍然没有点，尝试在中间添加点
                    if '.' not in fixed_domain and len(fixed_domain) > 6:
                        # 尝试在合适的位置添加点
                        # 例如：bilibilicom -> bilibili.com
                        for i in range(3, len(fixed_domain) - 2):
                            if fixed_domain[i:].startswith('com') or fixed_domain[i:].startswith('net') or fixed_domain[i:].startswith('org'):
                                fixed_domain = fixed_domain[:i] + '.' + fixed_domain[i:]
                                break
                    
                    # 如果域名已修复，更新链接
                    if fixed_domain != domain:
                        # 使用更可靠的方式更新链接，确保只替换域名部分
                        old_domain_part = domain_match.group(0)
                        new_domain_part = old_domain_part.replace(domain, fixed_domain)
                        link = link.replace(old_domain_part, new_domain_part)
                        log_message(f"[+] 修复域名格式", is_detailed=True)
                        log_message(f"[+] 修复前: {domain} -> 修复后: {fixed_domain}", is_detailed=True)
            
            # 检查是否是视频URL
            for pattern in VIDEO_PATTERNS:
                if re.search(pattern, link, re.IGNORECASE):
                    if link not in captured_urls:
                        captured_urls.add(link)
                        download_video(link)
                        break
        
        # 特殊处理B站视频页面
        if 'bilibili.com/video/' in url:
            log_message("[+] 检测到B站视频页面，尝试提取视频流...")
            # 从B站视频页面中提取cid和aid参数
            
            # 方法1: 直接从URL中提取bvid
            bvid_from_url = re.search(r'B[Vv][0-9A-Za-z]+', url)
            if bvid_from_url:
                bvid = bvid_from_url.group(0)
                log_message(f"[+] 从URL提取到bvid: {bvid}", is_detailed=True)
            else:
                bvid = ''
            
            # 方法2: 从HTML中提取参数
            cid_match = re.search(r'cid=(\d+)', response.text)
            aid_match = re.search(r'aid=(\d+)', response.text)
            bvid_match = re.search(r'bvid=["\']([^"\']+)["\']', response.text)
            
            if bvid_match:
                bvid = bvid_match.group(1)
                log_message(f"[+] 从HTML提取到bvid: {bvid}", is_detailed=True)
            
            if cid_match:
                cid = cid_match.group(1)
                log_message(f"[+] 提取到cid: {cid}", is_detailed=True)
            else:
                cid = ''
            
            if aid_match:
                aid = aid_match.group(1)
                log_message(f"[+] 提取到aid: {aid}", is_detailed=True)
            else:
                aid = ''
            
            # 方法3: 尝试从window.__INITIAL_STATE__中提取
            if not cid:
                initial_state_match = re.search(r'window\.__INITIAL_STATE__=(\{.*?\});', response.text, re.DOTALL)
                if initial_state_match:
                    initial_state = initial_state_match.group(1)
                    cid_match2 = re.search(r'cid":(\d+)', initial_state)
                    if cid_match2:
                        cid = cid_match2.group(1)
                        log_message(f"[+] 从INITIAL_STATE提取到cid: {cid}", is_detailed=True)
            
            if cid and (aid or bvid):
                log_message(f"[+] 提取到B站视频参数: cid={cid}, aid={aid}, bvid={bvid}", is_detailed=True)
                
                # 构造B站视频API请求
                api_url = f"https://api.bilibili.com/x/player/playurl?cid={cid}&aid={aid}&bvid={bvid}&qn=80&type=&otype=json"
                log_message(f"[+] 尝试访问B站API: {api_url}", is_detailed=True)
                
                try:
                    api_response = requests.get(api_url, headers=headers, timeout=10)
                    if api_response.status_code == 200:
                        log_message("[+] B站API访问成功，尝试解析视频流链接...")
                        # 解析API响应
                        import json
                        api_data = json.loads(api_response.text)
                        if api_data.get('code') == 0:
                            data = api_data.get('data', {})
                            durl = data.get('durl', [])
                            for video_info in durl:
                                video_url = video_info.get('url')
                                if video_url:
                                    log_message(f"[+] 发现B站视频流链接: {video_url}", is_detailed=True)
                                    download_video(video_url)
                        else:
                            log_message(f"[-] B站API返回错误: {api_data.get('message', '未知错误')}")
                except Exception as api_e:
                    log_message(f"[-] B站API访问错误: {str(api_e)}")
            else:
                log_message("[-] 未能提取到B站视频参数，尝试直接从HTML中搜索视频链接...")
                # 尝试直接从HTML中搜索视频链接
                video_links = re.findall(r'https?://[^"\']*\.(mp4|flv)(\?.*)?', response.text)
                for link_tuple in video_links:
                    video_url = link_tuple[0]
                    if video_url and video_url not in captured_urls:
                        captured_urls.add(video_url)
                        download_video(video_url)
        
        # 特殊处理抖音视频页面
        if 'douyin.com/video/' in url or 'v.douyin.com/' in url:
            log_message("[+] 检测到抖音视频页面，尝试提取视频流...")
            
            # 方法1: 从URL中提取视频ID
            video_id_match = re.search(r'douyin\.com/video/(\d+)', url)
            short_code_match = re.search(r'v\.douyin\.com/([^/]+)', url)
            
            video_id = ''
            short_code = ''
            
            if video_id_match:
                video_id = video_id_match.group(1)
                log_message(f"[+] 从URL提取到视频ID: {video_id}")
            elif short_code_match:
                short_code = short_code_match.group(1)
                log_message(f"[+] 从URL提取到短链接代码: {short_code}")
            
            # 方法2: 从HTML中提取视频参数
            sec_uid_match = re.search(r'sec_uid=["\']([^"\']+)["\']', response.text)
            item_id_match = re.search(r'item_id=["\']([^"\']+)["\']', response.text)
            
            sec_uid = ''
            item_id = ''
            
            if sec_uid_match:
                sec_uid = sec_uid_match.group(1)
                log_message(f"[+] 从HTML提取到sec_uid: {sec_uid}")
            
            if item_id_match:
                item_id = item_id_match.group(1)
                log_message(f"[+] 从HTML提取到item_id: {item_id}")
            elif not video_id:
                item_id = video_id
            
            # 尝试从window.__INITIAL_STATE__中提取参数
            initial_state_match = re.search(r'window\.__INITIAL_STATE__=(\{.*?\});', response.text, re.DOTALL)
            if initial_state_match:
                initial_state = initial_state_match.group(1)
                item_id_match2 = re.search(r'item_id=["\']([^"\']+)["\']', initial_state)
                if item_id_match2 and not item_id:
                    item_id = item_id_match2.group(1)
                    log_message(f"[+] 从INITIAL_STATE提取到item_id: {item_id}")
            
            # 尝试直接从HTML中搜索视频流链接
            log_message("[+] 尝试直接从HTML中搜索抖音视频流链接...")
            # 抖音视频CDN链接格式
            douyin_video_patterns = [
                r'https?://aweme\.snsvideocdn\.com/[^"\']+',
                r'https?://douyin\.tiktokcdn-us\.com/[^"\']+',
                r'https?://[^"\']+\.mp4(\?.*)?'
            ]
            
            for pattern in douyin_video_patterns:
                video_links = re.findall(pattern, response.text)
                for video_link in video_links:
                    if video_link and 'mp4' in video_link:
                        log_message(f"[+] 发现抖音视频流链接: {video_link}")
                        download_video(video_link)
        
        # 特殊处理优酷视频页面
        elif 'youku.com' in url:
            log_message("[+] 检测到优酷视频页面，尝试提取视频流...")
            # 尝试直接从HTML中搜索视频流链接
            log_message("[+] 尝试直接从HTML中搜索优酷视频流链接...")
            # 优酷视频链接格式
            youku_video_patterns = [
                r'https?://vali\.youku\.com/[^"\']+',
                r'https?://[^"\']+\.mp4(\?.*)?',
                r'https?://[^"\']+\.flv(\?.*)?'
            ]
            
            for pattern in youku_video_patterns:
                video_links = re.findall(pattern, response.text)
                for video_link in video_links:
                    if video_link and ('.mp4' in video_link or '.flv' in video_link):
                        log_message(f"[+] 发现优酷视频流链接: {video_link}")
                        download_video(video_link)
        
        # 特殊处理爱奇艺视频页面
        elif 'iqiyi.com' in url:
            log_message("[+] 检测到爱奇艺视频页面，尝试提取视频流...")
            # 尝试直接从HTML中搜索视频流链接
            log_message("[+] 尝试直接从HTML中搜索爱奇艺视频流链接...")
            # 爱奇艺视频链接格式
            iqiyi_video_patterns = [
                r'https?://cache\.m\.iqiyi\.com/[^"\']+',
                r'https?://[^"\']+\.mp4(\?.*)?',
                r'https?://[^"\']+\.m3u8(\?.*)?'
            ]
            
            for pattern in iqiyi_video_patterns:
                video_links = re.findall(pattern, response.text)
                for video_link in video_links:
                    if video_link and ('.mp4' in video_link or '.m3u8' in video_link):
                        log_message(f"[+] 发现爱奇艺视频流链接: {video_link}")
                        download_video(video_link)
        
        # 特殊处理腾讯视频页面
        elif 'v.qq.com' in url:
            log_message("[+] 检测到腾讯视频页面，尝试提取视频流...")
            # 尝试直接从HTML中搜索视频流链接
            log_message("[+] 尝试直接从HTML中搜索腾讯视频流链接...")
            # 腾讯视频链接格式
            tencent_video_patterns = [
                r'https?://[^"\']+\.mp4(\?.*)?',
                r'https?://[^"\']+\.m3u8(\?.*)?',
                r'https?://[^"\']+\.ts(\?.*)?'
            ]
            
            for pattern in tencent_video_patterns:
                video_links = re.findall(pattern, response.text)
                for video_link in video_links:
                    if video_link and ('.mp4' in video_link or '.m3u8' in video_link or '.ts' in video_link):
                        log_message(f"[+] 发现腾讯视频流链接: {video_link}")
                        download_video(video_link)
        
        # 特殊处理芒果TV视频页面
        elif 'mgtv.com' in url:
            log_message("[+] 检测到芒果TV视频页面，尝试提取视频流...")
            # 尝试直接从HTML中搜索视频流链接
            log_message("[+] 尝试直接从HTML中搜索芒果TV视频流链接...")
            # 芒果TV视频链接格式
            mgtv_video_patterns = [
                r'https?://[^"\']+\.mp4(\?.*)?',
                r'https?://[^"\']+\.m3u8(\?.*)?'
            ]
            
            for pattern in mgtv_video_patterns:
                video_links = re.findall(pattern, response.text)
                for video_link in video_links:
                    if video_link and ('.mp4' in video_link or '.m3u8' in video_link):
                        log_message(f"[+] 发现芒果TV视频流链接: {video_link}")
                        download_video(video_link)
        
        # 特殊处理西瓜视频页面
        elif 'ixigua.com' in url:
            log_message("[+] 检测到西瓜视频页面，尝试提取视频流...")
            # 尝试直接从HTML中搜索视频流链接
            log_message("[+] 尝试直接从HTML中搜索西瓜视频流链接...")
            # 西瓜视频链接格式
            ixigua_video_patterns = [
                r'https?://[^"\']+\.snssdk\.com/[^"\']+',
                r'https?://[^"\']+\.mp4(\?.*)?',
                r'https?://[^"\']+\.m3u8(\?.*)?'
            ]
            
            for pattern in ixigua_video_patterns:
                video_links = re.findall(pattern, response.text)
                for video_link in video_links:
                    if video_link and ('.mp4' in video_link or '.m3u8' in video_link):
                        log_message(f"[+] 发现西瓜视频流链接: {video_link}")
                        download_video(video_link)
        
        # 特殊处理快手视频页面
        elif 'kuaishou.com' in url:
            log_message("[+] 检测到快手视频页面，尝试提取视频流...")
            # 尝试直接从HTML中搜索视频流链接
            log_message("[+] 尝试直接从HTML中搜索快手视频流链接...")
            # 快手视频链接格式
            kuaishou_video_patterns = [
                r'https?://[^"\']+\.kuaishoucdn\.com/[^"\']+',
                r'https?://[^"\']+\.mp4(\?.*)?',
                r'https?://[^"\']+\.m3u8(\?.*)?'
            ]
            
            for pattern in kuaishou_video_patterns:
                video_links = re.findall(pattern, response.text)
                for video_link in video_links:
                    if video_link and ('.mp4' in video_link or '.m3u8' in video_link):
                        log_message(f"[+] 发现快手视频流链接: {video_link}")
                        download_video(video_link)
        
        log_message(f"[+] 网站扫描完成")
    except Exception as e:
        log_message(f"[-] 扫描错误: {str(e)}")



# 开始监控
def start_monitoring():
    global running
    if not running:
        running = True
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        log_message("[+] 开始监控剪贴板...")
        log_message("[+] 请复制视频链接到剪贴板")
        # 启动剪贴板监控线程
        clipboard_thread = threading.Thread(target=check_clipboard)
        clipboard_thread.daemon = True
        clipboard_thread.start()

# 停止监控
def stop_monitoring():
    global running
    if running:
        running = False
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        log_message("[+] 停止监控")
        log_message(f"[+] 共捕获 {len(captured_urls)} 个视频URL")

# 选择下载路径
def select_download_path():
    global DOWNLOAD_DIR
    global path_label
    
    # 打开文件夹选择对话框
    new_path = filedialog.askdirectory(title="选择下载路径")
    
    if new_path:
        DOWNLOAD_DIR = new_path
        # 更新路径标签
        path_label.config(text=f"当前下载路径: {DOWNLOAD_DIR}")
        # 确保路径存在
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        log_message(f"[+] 下载路径已更改为: {DOWNLOAD_DIR}")



# 打开文件
def open_file(file_path):
    try:
        if os.path.exists(file_path):
            # 使用系统默认程序打开文件
            os.startfile(file_path)
            log_message(f"[+] 正在打开文件: {file_path}")
        else:
            log_message(f"[-] 文件不存在: {file_path}")
    except Exception as e:
        log_message(f"[-] 打开文件错误: {str(e)}")

# 显示更新日志
def show_update_log():
    # 创建更新日志窗口
    log_window = tk.Toplevel()
    log_window.title("更新日志")
    log_window.geometry("600x400")
    
    # 创建文本框显示更新日志
    log_text = scrolledtext.ScrolledText(log_window, width=70, height=20)
    log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 更新日志内容
    update_log = """=====================================
视频嗅探下载器 - 更新日志
=====================================

[2026-1-30] v1.2.0
- 新增下载进度条功能，实时显示下载进度
- 新增下载信息显示，包括总大小(MB)、已下载量(MB)和下载速度(MB/s)
- 优化进度条重置机制，下载完成或失败时自动重置
- 优化下载信息标签重置机制，确保下载状态正确显示
- 修复B站视频处理时详细信息显示问题，将详细参数隐藏到详细日志
- 改进B站视频流链接提取逻辑，提高视频识别率
- 增强下载速度计算精度，使用更准确的时间间隔计算

[2025-12-27] v1.1.0
- 优化UI界面布局，窗口大小调整为800x400
- 新增状态栏显示关键操作信息
- 新增详细日志按钮，点击查看完整日志
- 优化日志显示逻辑，区分关键信息和详细参数
- 修复B站视频下载403错误问题
- 增强响应内容验证和错误处理

[2025-12-25] v1.0.5
- 优化了视频URL检测逻辑
- 改进了文件名生成算法
- 添加了文件大小检查，过滤无效文件
- 优化了日志显示，支持点击打开文件
- 优化了GUI界面布局
- 改进了错误处理机制
- 重写为GUI界面
- 添加了模拟浏览器请求头
- 基于Scapy库的网络数据包捕获
- 支持视频流URL提取和下载

[2025-12-01] v1.0.0
- 新增B站视频下载功能
- 新增快手视频下载功能
- 新增剪贴板监控功能
- 新增网站扫描功能
- 新增多线程下载功能
- 新增文件完整性检查功能
- 新增自定义下载路径功能
- 新增更新日志功能

=====================================
"""
    
    # 插入更新日志
    log_text.insert(tk.END, update_log)
    log_text.config(state=tk.DISABLED)  # 设置为只读

# 详细日志存储
detailed_logs = []

# 显示详细日志
def show_detailed_logs():
    # 创建详细日志窗口
    log_window = tk.Toplevel()
    log_window.title("详细日志")
    log_window.geometry("800x600")
    
    # 创建文本框显示详细日志
    log_text_widget = scrolledtext.ScrolledText(log_window, width=100, height=30)
    log_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 插入详细日志
    for log in detailed_logs:
        # 检查是否包含文件路径
        path_match = re.search(r'\[\+\] 点击查看: (.*)$', log)
        if path_match:
            # 插入普通文本
            log_text_widget.insert(tk.END, "[+] 点击查看: ")
            # 插入可点击的文件路径
            file_path = path_match.group(1)
            log_text_widget.insert(tk.END, file_path)
            # 为文件路径添加标签
            log_text_widget.tag_add("file_path", "end - %dc" % len(file_path), "end")
            # 设置标签样式
            log_text_widget.tag_config("file_path", foreground="blue", underline=1)
            # 绑定点击事件
            log_text_widget.tag_bind("file_path", "<Button-1>", lambda e, fp=file_path: open_file(fp))
            log_text_widget.insert(tk.END, "\n")
        else:
            log_text_widget.insert(tk.END, log + "\n")
    
    log_text_widget.see(tk.END)
    log_text_widget.config(state=tk.DISABLED)  # 设置为只读

# 在日志中显示消息
def log_message(message, show_in_status=True, is_detailed=False):
    # 保存到详细日志
    detailed_logs.append(message)
    
    # 只在主界面显示非详细信息
    if not is_detailed and 'log_text' in globals():
        log_text.config(state=tk.NORMAL)
        # 检查是否包含文件路径
        path_match = re.search(r'\[\+\] 点击查看: (.*)$', message)
        if path_match:
            # 插入普通文本
            log_text.insert(tk.END, "[+] 点击查看: ")
            # 插入可点击的文件路径
            file_path = path_match.group(1)
            log_text.insert(tk.END, file_path)
            # 为文件路径添加标签
            log_text.tag_add("file_path", "end - %dc" % len(file_path), "end")
            # 设置标签样式
            log_text.tag_config("file_path", foreground="blue", underline=1)
            # 绑定点击事件
            log_text.tag_bind("file_path", "<Button-1>", lambda e, fp=file_path: open_file(fp))
            log_text.insert(tk.END, "\n")
        else:
            log_text.insert(tk.END, message + "\n")
        log_text.see(tk.END)
        log_text.config(state=tk.DISABLED)
    
    # 显示在状态栏
    if show_in_status and not is_detailed:
        # 检查是否包含文件路径
        path_match = re.search(r'\[\+\] 点击查看: (.*)$', message)
        if path_match:
            status_var.set("[+] 视频下载完成，点击查看详细日志")
        else:
            # 只显示简洁信息
            if "[+] 下载完成:" in message:
                status_var.set(f"[+] 下载完成: {message.split(': ')[1]}")
            elif "[+] 开始下载:" in message:
                status_var.set("[+] 开始下载视频...")
            elif "[-] 下载失败" in message or "[-] 网络请求错误" in message:
                status_var.set("[-] 下载失败，请查看详细日志")
            elif "[+] 开始监控剪贴板" in message:
                status_var.set("[+] 开始监控剪贴板")
            elif "[+] 停止监控" in message:
                status_var.set("[+] 停止监控")
            elif "[+] 网站扫描完成" in message:
                status_var.set("[+] 网站扫描完成")
            elif "[+] 下载路径已更改为:" in message:
                status_var.set(f"[+] 下载路径已更改")
            elif "[+] 成功连接到视频服务器" in message:
                status_var.set("[+] 正在下载视频...")
            elif "[+] 发现视频URL:" in message or "[+] 发现" in message and "视频流链接" in message:
                status_var.set("[+] 发现视频链接")
            elif "[+] 检测到" in message and "视频页面" in message:
                status_var.set(f"[+] 检测到视频页面")
            elif "[+] 扫描错误" in message:
                status_var.set("[-] 扫描错误，请查看详细日志")

# 按钮点击效果函数
def button_click_effect(button, original_bg):
    """为按钮添加点击效果"""
    # 点击时的效果
    button.config(bg="#d0d0d0")
    # 模拟点击后恢复
    button.after(100, lambda: button.config(bg=original_bg))

# 主函数
def main():
    global start_button, stop_button, url_entry, status_var
    
    # 创建GUI窗口
    window = tk.Tk()
    window.title("视频嗅探下载器")
    window.geometry("800x400")
    window.resizable(True, True)
    
    # 创建主框架
    main_frame = tk.Frame(window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 移除标题标签
    
    # 创建URL输入框
    url_frame = tk.Frame(main_frame)
    url_frame.pack(pady=5, fill=tk.X)
    
    url_label = tk.Label(url_frame, text="网站URL:", font=("微软雅黑", 9))
    url_label.pack(side=tk.LEFT, padx=(0, 5))
    
    url_entry = tk.Entry(url_frame, width=60, font=("微软雅黑", 9))
    url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    # 创建扫描按钮并添加点击效果
    scan_button = tk.Button(url_frame, text="扫描网站", command=lambda: [button_click_effect(scan_button, "#f0f0f0"), scan_website()], font=("微软雅黑", 9))
    scan_button.pack(side=tk.LEFT, padx=5)
    
    # 创建控制按钮
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)
    
    # 按钮原始背景色
    original_bg = "#f0f0f0"
    
    # 创建开始监控按钮并添加点击效果
    start_button = tk.Button(button_frame, text="开始监控剪贴板", command=lambda: [button_click_effect(start_button, original_bg), start_monitoring()], width=15, font=("微软雅黑", 9))
    start_button.pack(side=tk.LEFT, padx=5)
    
    # 创建停止监控按钮并添加点击效果
    stop_button = tk.Button(button_frame, text="停止监控", command=lambda: [button_click_effect(stop_button, original_bg), stop_monitoring()], state=tk.DISABLED, width=15, font=("微软雅黑", 9))
    stop_button.pack(side=tk.LEFT, padx=5)
    
    # 添加选择下载路径按钮并添加点击效果
    path_button = tk.Button(button_frame, text="选择下载路径", command=lambda: [button_click_effect(path_button, original_bg), select_download_path()], width=15, font=("微软雅黑", 9))
    path_button.pack(side=tk.LEFT, padx=5)
    
    # 添加详细日志按钮并添加点击效果
    log_button = tk.Button(button_frame, text="详细日志", command=lambda: [button_click_effect(log_button, original_bg), show_detailed_logs()], width=15, font=("微软雅黑", 9))
    log_button.pack(side=tk.LEFT, padx=5)
    
    # 添加更新日志按钮并添加点击效果
    update_log_button = tk.Button(button_frame, text="更新日志", command=lambda: [button_click_effect(update_log_button, original_bg), show_update_log()], width=15, font=("微软雅黑", 9))
    update_log_button.pack(side=tk.LEFT, padx=5)
    
    # 显示当前下载路径
    global path_label
    path_label = tk.Label(main_frame, text=f"当前下载路径: {DOWNLOAD_DIR}", anchor=tk.W, font=("微软雅黑", 9))
    path_label.pack(pady=5, fill=tk.X)
    
    # 创建进度条
    global progress_var, progress_bar, download_info_label
    progress_var = tk.DoubleVar()
    # 从ttk模块导入Progressbar
    from tkinter import ttk
    
    progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100, length=750)
    progress_bar.pack(pady=5, fill=tk.X)
    progress_var.set(0)  # 初始进度为0
    
    # 创建下载信息标签
    download_info_label = tk.Label(main_frame, text="总大小: 0 MB | 已下载: 0 MB | 速度: 0 MB/s", anchor=tk.W, font=("微软雅黑", 9))
    download_info_label.pack(pady=2, fill=tk.X)
    
    # 创建日志显示区域
    global log_text
    log_frame = tk.Frame(main_frame, bd=1, relief=tk.GROOVE)
    log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # 创建日志标题
    log_title = tk.Label(log_frame, text="日志信息", font=("微软雅黑", 10, "bold"), anchor=tk.W)
    log_title.pack(fill=tk.X, padx=5, pady=2)
    
    log_text = scrolledtext.ScrolledText(log_frame, width=100, height=12, font=("微软雅黑", 9))
    log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    log_text.config(state=tk.DISABLED)  # 设置为只读
    
    # 创建状态栏
    status_frame = tk.Frame(window, relief=tk.SUNKEN, bd=1)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    status_var = tk.StringVar()
    status_var.set("就绪")
    
    status_label = tk.Label(status_frame, textvariable=status_var, bd=1, relief=tk.FLAT, anchor=tk.W, font=("微软雅黑", 9))
    status_label.pack(fill=tk.X, padx=5, pady=2)
    
    # 启动下载工作线程
    global download_threads
    for i in range(MAX_THREADS):
        thread = threading.Thread(target=download_worker)
        thread.daemon = True  # 设置为守护线程，程序退出时自动结束
        thread.start()
        download_threads.append(thread)
    
    # 显示欢迎消息
    log_message("=====================================", show_in_status=False)
    log_message("视频嗅探下载器", show_in_status=False)
    log_message("作者：李健辉", show_in_status=False)
    log_message("=====================================", show_in_status=False)
    log_message(f"[+] 启动了 {MAX_THREADS} 个下载工作线程", show_in_status=False)
    log_message("使用说明：", show_in_status=False)
    log_message("1. 点击'开始监控剪贴板'，然后复制视频链接到剪贴板", show_in_status=False)
    log_message("2. 或在URL输入框中输入网站地址，点击'扫描网站'提取视频链接", show_in_status=False)
    log_message("3. 程序会自动下载检测到的视频", show_in_status=False)
    log_message("4. 下载的视频保存在'下载的视频'目录中", show_in_status=False)
    log_message("=====================================", show_in_status=False)
    
    # 在状态栏显示欢迎信息
    status_var.set("就绪 - 请开始使用视频嗅探下载器")
    
    # 运行GUI
    window.mainloop()

if __name__ == "__main__":
    main()