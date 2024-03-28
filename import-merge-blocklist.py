import importlib.util
import subprocess
import sys
import os

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

def process_url(url, output_filename):
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
    # Catch timeout exceptions as warnings
    except requests.Timeout as e:
        warnings.warn(f"Timeout occurred for URL {url}: {e}", Warning)
    # Catch other exceptions and print them
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

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
        
        print("URLs processed successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_filename = "adlist.txt"  # Input file name
    output_filename = "merged-dns-blocklist.txt"  # Output file name
    # Ensure the output file is overwritten each time
    with open(output_filename, 'w', encoding='utf-8'):
        pass
    # Run the main script
    main(input_filename, output_filename)

    # Add and commit the output file to the Git repository
    os.system('git add output_processed_urls.txt')
    os.system('git commit -m "Add processed URLs"')

    # Push the changes to the remote repository
    os.system('git push')
