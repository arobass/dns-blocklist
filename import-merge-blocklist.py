import importlib.util
import subprocess
import sys

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

# Now that all required modules are installed, import them and run the main script
import multiprocessing
import requests
import re
import warnings

def get_cpu_cores():
    """Get the number of CPU cores available."""
    try:
        import os
        return os.cpu_count()
    except NotImplementedError:
        return 1

def process_url(url, output_filename, error_filename='lists-errors.txt'):
    """Process a single URL."""
    try:
        # Make a request to the URL with a timeout of 10 seconds
        response = requests.get(url, timeout=10)
        # If the response is successful (status code 200)
        if response.status_code == 200:
            # Extract the content and remove duplicate and commented lines
            content = response.text.split('\n')
            content = [line.strip() for line in content if line.strip() and not line.startswith(("#", "<", "!"))]
            content = list(set(content))  # Remove identical lines
            # Write the processed content to the output file
            with open(output_filename, 'a', encoding='utf-8') as file:
                for line in content:
                    file.write(line + '\n')
        else:
            # Log non-200 status codes as errors
            with open(error_filename, 'a', encoding='utf-8') as error_file:
                error_file.write(f"HTTP Error {response.status_code} for URL: {url}\n")
    # Catch timeout exceptions and log them
    except requests.Timeout as e:
        warnings.warn(f"Timeout occurred for URL {url}: {e}", Warning)
        with open(error_filename, 'a', encoding='utf-8') as error_file:
            error_file.write(f"Timeout Error for URL: {url}\nError: {str(e)}\n\n")
    # Catch other exceptions and log them
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        with open(error_filename, 'a', encoding='utf-8') as error_file:
            error_file.write(f"Error for URL: {url}\nError: {str(e)}\n\n")

def main(input_filename, output_filename):
    """Main function to process URLs."""
    try:
        # Read URLs from the input file
        with open(input_filename, 'r', encoding='utf-8') as file:
            urls = file.readlines()
        urls = [url.strip() for url in urls if url.strip()]
        
        # Get the number of CPU cores
        cpu_cores = get_cpu_cores()
        # Create a multiprocessing pool with the number of CPU cores
        pool = multiprocessing.Pool(cpu_cores)

        # Process each URL asynchronously using the pool of workers
        for url in urls:
            pool.apply_async(process_url, args=(url, output_filename))

        # Close the pool and wait for all tasks to complete
        pool.close()
        pool.join()

        # Remove duplicates from the merged file
        print("Removing duplicate entries from the merged file...")
        with open(output_filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Remove duplicates while preserving order
        unique_lines = []
        seen = set()
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                unique_lines.append(line)

        # Write back the deduplicated content
        with open(output_filename, 'w', encoding='utf-8') as file:
            for line in unique_lines:
                file.write(line + '\n')
        
        print(f"URLs processed successfully. {len(lines) - len(unique_lines)} duplicate entries removed.")
        
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
