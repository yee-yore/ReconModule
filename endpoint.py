#!/usr/bin/env python3
"""
URL Endpoint Extractor
Read wayback_urls.txt from subdomain folders and extract unique URL endpoints
"""

import os
import sys
from urllib.parse import urlparse

def extract_endpoint(url):
    """Extract endpoint from URL (domain + first level subdirectory only)"""
    try:
        parsed = urlparse(url)
        # Get domain and path, remove query parameters and fragment
        domain = parsed.netloc
        path = parsed.path
        
        # Split path and get only first level subdirectory
        path_parts = [part for part in path.split('/') if part]
        
        if path_parts:
            # Take only the first directory level
            first_level = '/' + path_parts[0] + '/'
        else:
            # Root path
            first_level = '/'
        
        # Combine domain and first level path
        endpoint = f"{domain}{first_level}"
        return endpoint
    except Exception:
        return None

def process_domain_endpoints(domain, subdomain_file):
    """Process endpoints for a specific domain"""
    domain_dir = domain
    wayback_file = os.path.join(domain_dir, 'wayback_urls.txt')
    
    if not os.path.exists(wayback_file):
        print(f"[-] File not found: {wayback_file}")
        return 0
    
    endpoints = set()
    
    try:
        with open(wayback_file, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url:
                    endpoint = extract_endpoint(url)
                    if endpoint:
                        endpoints.add(endpoint)
    
    except Exception as e:
        print(f"[-] Error reading {wayback_file}: {e}")
        return 0
    
    # Sort endpoints for better readability
    sorted_endpoints = sorted(list(endpoints))
    
    # Save to domain-specific endpoints.txt
    output_file = os.path.join(domain_dir, 'endpoints.txt')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for endpoint in sorted_endpoints:
                f.write(endpoint + '\n')
        
        print(f"[+] Processed {domain}: {len(sorted_endpoints)} unique endpoints")
        print(f"[+] Saved to {output_file}")
        return len(sorted_endpoints)
        
    except Exception as e:
        print(f"[-] Error saving endpoints for {domain}: {e}")
        return 0

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python endpoint.py subdomain.txt")
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
    
    # Process each domain individually
    total_endpoints = 0
    
    for i, domain in enumerate(domains, 1):
        print(f"\n[{i}/{len(domains)}] Processing {domain}")
        endpoints_count = process_domain_endpoints(domain, subdomain_file)
        total_endpoints += endpoints_count
    
    print(f"\n[+] Complete!")
    print(f"[+] Total endpoints across all domains: {total_endpoints}")

if __name__ == "__main__":
    main()