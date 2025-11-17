import importlib.util
import subprocess
import sys
import multiprocessing
import requests
import re
import warnings

# List of required modules
required_modules = ['multiprocessing', 'requests', 'warnings']

# Function to check if a module is installed
def is_module_installed(module_name):
    spec = importlib.util.find_spec(module_name)
    return spec is not None

# Function to install missing modules
def install_missing_modules():
    for module in required_modules:
        if not is_module_installed(module):
            print(f"Installing {module}...")
            subprocess.run([sys.executable, "-m", "pip", "install", module])

# Install missing modules
install_missing_modules()

# Function to get number of CPU cores available
def get_cpu_cores():
    """Get the number of CPU cores available."""
    try:
        import os
        return os.cpu_count()
    except NotImplementedError:
        return 1

# Function to extract valid domain rules from content
def extract_valid_lines(content):
    """Filter valid lines (remove empty lines and comments)."""
    return [line.strip() for line in content if line.strip() and not line.startswith(("#", "<", "!"))]

# Process a single URL
def process_url(url, seen, error_filename='lists-errors.txt'):
    """Process a single URL and collect unique rules."""
    try:
        # Make a request to the URL with a timeout of 10 seconds
        response = requests.get(url, timeout=10)
        # If the response is successful (status code 200)
        if response.status_code == 200:
            # Extract and clean content, remove invalid lines
            content = response.text.split('\n')
            valid_lines = extract_valid_lines(content)

            # Add the valid lines to the 'seen' set for deduplication
            for line in valid_lines:
                seen.add(line)
        else:
            # Log non-200 status codes as errors
            with open(error_filename, 'a', encoding='utf-8') as error_file:
                error_file.write(f"HTTP Error {response.status_code} for URL: {url}\n")
    except requests.Timeout as e:
        warnings.warn(f"Timeout occurred for URL {url}: {e}", Warning)
        with open(error_filename, 'a', encoding='utf-8') as error_file:
            error_file.write(f"Timeout Error for URL: {url}\nError: {str(e)}\n\n")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        with open(error_filename, 'a', encoding='utf-8') as error_file:
            error_file.write(f"Error for URL: {url}\nError: {str(e)}\n\n")

# Main function to process URLs
def main(input_filename, output_filename):
    """Main function to process URLs and output a deduplicated rule list."""
    try:
        # Read URLs from the input file
        with open(input_filename, 'r', encoding='utf-8') as file:
            urls = file.readlines()
        urls = [url.strip() for url in urls if url.strip()]

        # Set to hold all unique rules
        seen = set()

        # Get the number of CPU cores
        cpu_cores = get_cpu_cores()
        # Create a multiprocessing pool with the number of CPU cores
        pool = multiprocessing.Pool(cpu_cores)

        # Process each URL asynchronously
        for url in urls:
            pool.apply_async(process_url, args=(url, seen))

        # Close the pool and wait for all tasks to complete
        pool.close()
        pool.join()

        # Write deduplicated rules to the output file
        print("Writing deduplicated entries to the output file...")
        with open(output_filename, 'w', encoding='utf-8') as file:
            for line in seen:
                file.write(line + '\n')

        print(f"URLs processed successfully. {len(seen)} unique rules written to {output_filename}.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_filename = "adlist.txt"  # Input file name
    output_filename = "merged-dns-blocklist.txt"  # Output file name
    # Ensure both output and error files are overwritten each time
    with open(output_filename, 'w', encoding='utf-8'):
        pass
    with open('lists-errors.txt', 'w', encoding='utf-8'):
        pass
    # Run the main script
    main(input_filename, output_filename)
