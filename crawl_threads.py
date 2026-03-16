import requests
import json
from bs4 import BeautifulSoup

def find_and_parse_json(text, start_str, end_str):
    """Find and parse JSON data embedded in a string."""
    try:
        start_index = text.find(start_str)
        if start_index == -1:
            return None
            
        start_index += len(start_str)
        end_index = text.find(end_str, start_index)
        
        if end_index == -1:
            return None
            
        json_str = text[start_index:end_index]
        return json.loads(json_str)
        
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Could not parse JSON: {e}")
        return None

def crawl_threads_first_post(username):
    url = f"https://www.threads.net/@{username}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Threads embeds data in a script tag as JSON.
        scripts = soup.find_all('script', type='application/ld+json')
        
        first_post_text = None
        
        if scripts:
            for script in scripts:
                data = json.loads(script.string)
                if data.get('@type') == 'SocialMediaPosting':
                    article_body = data.get('articleBody')
                    if article_body:
                        first_post_text = article_body
                        break # Found the first post
        
        # Fallback if ld+json is not found or empty
        if not first_post_text:
            print("No 'application/ld+json' script found. Trying another method...")
            all_scripts = soup.find_all('script')
            for script in all_scripts:
                if 'ScheduledServerJS' in script.text:
                    json_data = find_and_parse_json(script.text, '{"props":', '};</script>')
                    if json_data:
                        # The structure can be complex, this is an educated guess
                        # Based on common Next.js/React app structures
                        try:
                            # This path is highly subject to change
                            posts = json_data['props']['pageProps']['posts']
                            if posts:
                                first_post = posts[0]['thread_items'][0]['post']
                                first_post_text = first_post['caption']['text']
                                break
                        except (KeyError, IndexError):
                            continue

        if first_post_text:
            print("\n--- First Post Found ---")
            print(first_post_text)
            print("------------------------\n")
        else:
            print("Could not find the first post. The page structure might have changed.")

    except requests.RequestException as e:
        print(f"Failed to fetch page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    crawl_threads_first_post("unclestocknotes")
