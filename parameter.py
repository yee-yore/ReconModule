#!/usr/bin/env python3
"""
HTTP Parameter Extractor
Read wayback_urls.txt from subdomain folders and extract unique HTTP parameter names
"""

import os
import sys
from urllib.parse import urlparse, parse_qs

def extract_parameters(url):
    """Extract parameter names from URL query string"""
    try:
        # Handle HTML entities in URL
        url = url.replace('&amp;', '&')
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Filter out empty parameter names and clean them
        clean_params = set()
        for param_name in query_params.keys():
            # Remove leading/trailing whitespace
            clean_name = param_name.strip()
            
            # Skip empty parameter names
            if not clean_name:
                continue
                
            # Skip parameters that contain URLs or invalid characters
            if any(invalid in clean_name for invalid in ['http', 'https', '/', '\\', ' ']):
                continue
                
            # Skip parameters starting with HTML entities
            if clean_name.startswith(('amp;', 'nbsp;', 'gt;', 'lt;')):
                continue
                
            clean_params.add(clean_name)
        
        return clean_params
    except Exception:
        return set()

def process_domain_parameters(domain, subdomain_file):
    """Process parameters for a specific domain"""
    domain_dir = domain
    wayback_file = os.path.join(domain_dir, 'wayback_urls.txt')
    
    if not os.path.exists(wayback_file):
        print(f"[-] File not found: {wayback_file}")
        return 0
    
    parameters = set()
    
    try:
        with open(wayback_file, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url:
                    url_params = extract_parameters(url)
                    parameters.update(url_params)
    
    except Exception as e:
        print(f"[-] Error reading {wayback_file}: {e}")
        return 0
    
    # Sort parameters for better readability and filter out empty ones
    sorted_parameters = sorted([param for param in parameters if param.strip()])
    
    # Save to domain-specific parameters.txt
    output_file = os.path.join(domain_dir, 'parameters.txt')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for param in sorted_parameters:
                f.write(param + '=\n')
        
        print(f"[+] Processed {domain}: {len(sorted_parameters)} unique parameters")
        print(f"[+] Saved to {output_file}")
        return len(sorted_parameters)
        
    except Exception as e:
        print(f"[-] Error saving parameters for {domain}: {e}")
        return 0

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python parameter.py subdomain.txt")
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
    total_parameters = 0
    
    for i, domain in enumerate(domains, 1):
        print(f"\n[{i}/{len(domains)}] Processing {domain}")
        parameters_count = process_domain_parameters(domain, subdomain_file)
        total_parameters += parameters_count
    
    print(f"\n[+] Complete!")
    print(f"[+] Total parameters across all domains: {total_parameters}")

if __name__ == "__main__":
    main()