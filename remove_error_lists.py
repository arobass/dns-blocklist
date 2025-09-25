def extract_error_urls(error_file):
    urls = set()
    with open(error_file, 'r', encoding='utf-8') as f:
        for line in f:
            if 'URL:' in line:
                # Extract URL from error messages
                url = line.split('URL:')[1].strip()
                urls.add(url)
    return urls

def remove_error_urls(adlist_file, error_urls):
    with open(adlist_file, 'r', encoding='utf-8') as f:
        urls = f.readlines()
    
    # Remove error URLs and keep working ones
    working_urls = [url.strip() for url in urls if url.strip() not in error_urls]
    
    # Write back the working URLs
    with open(adlist_file, 'w', encoding='utf-8') as f:
        for url in working_urls:
            f.write(url + '\n')
    
    return len(urls) - len(working_urls)

if __name__ == '__main__':
    # Extract URLs that had errors
    error_urls = extract_error_urls('lists-errors.txt')
    
    # Remove those URLs from adlist.txt
    removed_count = remove_error_urls('adlist.txt', error_urls)
    
    print(f'Removed {removed_count} problematic URLs from adlist.txt')