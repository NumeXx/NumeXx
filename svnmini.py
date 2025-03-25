#!/usr/bin/env python3  
# minisvn.py - Python-based SVN-like client 
# Author: @NumeXx

import os  
import sys  
import urllib.request  
import re  
from html.parser import HTMLParser  
import shutil  
import argparse
import concurrent.futures
import threading
from queue import Queue
import time

# Global variables
silent_mode = False
max_threads = 50
download_queue = Queue()
semaphore = threading.Semaphore(max_threads)

class DirectoryParser(HTMLParser):  
    def __init__(self):  
        super().__init__()  
        self.links = []  
        
    def handle_starttag(self, tag, attrs):  
        if tag == 'a':  
            for name, value in attrs:  
                if name == 'href' and value != '../' and not value.startswith('?'):  
                    if not (value.startswith('http://') or value.startswith('https://')):  
                        self.links.append(value)  

def get_directory_contents(url):  
    with urllib.request.urlopen(url) as response:  
        html = response.read().decode('utf-8')  
        parser = DirectoryParser()  
        parser.feed(html)  
        return parser.links  

def download_file(url, target_path):  
    if not silent_mode:
        print(f"Downloading: {url} -> {target_path}")  
    try:  
        with urllib.request.urlopen(url) as response:  
            with open(target_path, 'wb') as out_file:  
                out_file.write(response.read())  
    except Exception as e:  
        if not silent_mode:
            print(f"Error downloading {url}: {e}")  

def download_worker():
    while True:
        try:
            url, target_path = download_queue.get_nowait()
            with semaphore:
                download_file(url, target_path)
            download_queue.task_done()
        except Queue.Empty:
            break

def export_recursively(url, target_dir):  
    if not url.endswith('/'):  
        url += '/'  
    
    os.makedirs(target_dir, exist_ok=True)  
    
    try:  
        links = get_directory_contents(url)  
        
        # Create thread pool for downloads
        threads = []
        for _ in range(min(max_threads, len(links))):
            t = threading.Thread(target=download_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        for link in links:  
            if link.endswith('/'):  
                # This is a directory  
                subdir_name = link[:-1]  # Remove trailing slash  
                subdir_path = os.path.join(target_dir, subdir_name)  
                export_recursively(url + link, subdir_path)  
            else:  
                # This is a file  
                file_path = os.path.join(target_dir, link)  
                download_queue.put((url + link, file_path))
        
        # Wait for all downloads to complete
        download_queue.join()
        
    except Exception as e:  
        if not silent_mode:
            print(f"Error processing {url}: {e}")  

def cleanup_folders(basedir):  
    # Clean up unwanted folders  
    for root, dirs, files in os.walk(basedir, topdown=False):  
        for dirname in dirs:  
            if dirname == "http:" or dirname.startswith("http:"):  
                try:  
                    path = os.path.join(root, dirname)  
                    if not silent_mode:
                        print(f"Removing unwanted directory: {path}")  
                    shutil.rmtree(path)  
                except Exception as e:  
                    if not silent_mode:
                        print(f"Error removing {path}: {e}")  

def main():  
    parser = argparse.ArgumentParser(description='MiniSVN - Simple SVN-like client')
    parser.add_argument('--export', required=True, help='URL to export from')
    parser.add_argument('--target', required=True, help='Target directory to save files')
    parser.add_argument('--silent', action='store_true', help='Run in silent mode')
    parser.add_argument('--thread', type=int, default=50, help='Maximum number of concurrent downloads (max 50)')
    
    args = parser.parse_args()
    
    # Set global variables
    global silent_mode, max_threads
    silent_mode = args.silent
    max_threads = min(args.thread, 50)  # Cap at 50 threads
    
    # Start export
    export_recursively(args.export, args.target)
    cleanup_folders(args.target)
    print(f"Done! Export completed to: {args.target}")

if __name__ == "__main__":  
    main()
