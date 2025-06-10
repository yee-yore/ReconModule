#!/usr/bin/env python3
"""
Simple Wayback Machine URL Collector
Read subdomain file and collect URLs for each domain through CDX API
"""

import requests
import os
import sys

def has_file_extension(url):
    """Check if URL is a file (based on extension, excluding images/fonts/styles)"""
    # Remove query parameters
    url_path = url.split('?')[0].split('#')[0]
    
    # File extensions to include (excluding images, fonts, styles)
    file_extensions = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.xml', '.json', '.csv', '.zip', 
        '.rar', '.tar', '.gz', '.7z', '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.swf','.php', '.asp', 
        '.aspx', '.jsp', '.cfm', '.pl', '.py', '.rb', '.sql', '.db', '.bak', '.backup', '.old', '.tmp', '.log',
        '.conf', '.cfg', '.ini', '.yaml', '.yml', '.properties', '.js', '.exe', '.html'
    ]
    
    return any(url_path.lower().endswith(ext) for ext in file_extensions)

def is_static_resource(url):
    """Check if URL is a static resource (images, CSS, fonts, etc.)"""
    # Remove query parameters
    url_path = url.split('?')[0].split('#')[0]
    
    # Static resource extensions to exclude
    static_extensions = [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp', '.ico', '.css', 
        '.scss', '.sass', '.less', '.woff', '.woff2', '.ttf', '.otf', '.eot', '.map', '.min.js', '.min.css'
    ]
    
    return any(url_path.lower().endswith(ext) for ext in static_extensions)

def collect_wayback_urls(domain, domain_dir):
    """Collect Wayback Machine URLs for specific domain"""
    print(f"[+] Collecting URLs for {domain}...")
    
    # CDX API parameters
    params = {
        'url': f"{domain}/*",
        'output': 'text',
        'matchType': 'domain',
        'collapse': 'urlkey',
        'fl': 'original'
    }
    
    try:
        response = requests.get(
            "http://web.archive.org/cdx/search/cdx",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        # Parse results and filter static resources
        lines = response.text.strip().split('\n')
        all_urls = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('original') and not is_static_resource(line):
                all_urls.append(line)
        
        # Remove duplicates and sort
        unique_urls = sorted(list(set(all_urls)))
        
        # Classify URLs and files
        regular_urls = []
        file_urls_by_ext = {}
        
        for url in unique_urls:
            if has_file_extension(url):
                # Extract extension
                url_path = url.split('?')[0].split('#')[0]
                ext = None
                for extension in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                                '.txt', '.xml', '.json', '.csv', '.zip', '.rar', '.tar', '.gz', '.7z',
                                '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.swf',
                                '.php', '.asp', '.aspx', '.jsp', '.cfm', '.pl', '.py', '.rb',
                                '.sql', '.db', '.bak', '.backup', '.old', '.tmp', '.log',
                                '.conf', '.cfg', '.ini', '.yaml', '.yml', '.properties', '.js']:
                    if url_path.lower().endswith(extension):
                        ext = extension[1:]  # Remove dot(.)
                        break
                
                if ext:
                    if ext not in file_urls_by_ext:
                        file_urls_by_ext[ext] = []
                    file_urls_by_ext[ext].append(url)
            else:
                regular_urls.append(url)
        
        # Create directory
        os.makedirs(domain_dir, exist_ok=True)
        
        # Save all URLs (wayback_urls.txt)
        all_urls_file = os.path.join(domain_dir, 'wayback_urls.txt')
        with open(all_urls_file, 'w', encoding='utf-8') as f:
            for url in unique_urls:
                f.write(url + '\n')
        
        # Save regular URLs (wayback_url.txt)
        urls_file = os.path.join(domain_dir, 'wayback_url.txt')
        with open(urls_file, 'w', encoding='utf-8') as f:
            for url in regular_urls:
                f.write(url + '\n')
        
        # Save file URLs by extension
        total_files = 0
        for ext, urls in file_urls_by_ext.items():
            ext_file = os.path.join(domain_dir, f'{ext}.txt')
            with open(ext_file, 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(url + '\n')
            total_files += len(urls)
        
        print(f"[+] Found {len(unique_urls)} total URLs for {domain}")
        print(f"[+] URLs: {len(regular_urls)}, Files: {total_files}")
        if file_urls_by_ext:
            ext_summary = ", ".join([f"{ext}: {len(urls)}" for ext, urls in file_urls_by_ext.items()])
            print(f"[+] File types: {ext_summary}")
        print(f"[+] Saved to {domain_dir}/")
        
        return len(unique_urls)
        
    except requests.exceptions.RequestException as e:
        print(f"[-] Error collecting URLs for {domain}: {e}")
        return 0

def main():
    if len(sys.argv) != 2:
        print("Usage: python wayback.py subdomain.txt")
        sys.exit(1)
    
    subdomain_file = sys.argv[1]
    
    # Read subdomain file
    try:
        with open(subdomain_file, 'r', encoding='utf-8') as f:
            domains = [line.strip() for line in f.readlines()]
        domains = [d for d in domains if d]
        
        if not domains:
            print("[-] No valid domains found in the file")
            sys.exit(1)
            
        print(f"[+] Found {len(domains)} domains to process")
        
    except Exception as e:
        print(f"[-] Error reading file {subdomain_file}: {e}")
        sys.exit(1)
    
    # Collect URLs for each domain
    for i, domain in enumerate(domains, 1):
        print(f"\n[{i}/{len(domains)}] Processing {domain}")
        
        # Create output directory
        domain_dir = domain
        
        # Collect URLs
        collect_wayback_urls(domain, domain_dir)
    
    print(f"\n[+] Complete!")

if __name__ == "__main__":
    main()