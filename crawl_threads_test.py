import requests
from bs4 import BeautifulSoup

def crawl_threads_first_post(username):
    url = f"https://www.threads.net/@{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Threads might require JavaScript to render content.
        # Let's check if the content is in the initial HTML.
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Searching for post content. Meta often uses <div> for posts.
        # Since class names are obfuscated, we might need to look for specific patterns or use Selenium.
        print(f"Status Code: {response.status_code}")
        
        # Try to find any text that looks like a post
        # This is a naive attempt, Threads is highly dynamic.
        posts = soup.find_all('div')
        for post in posts:
            text = post.get_text().strip()
            if text and len(text) > 10:
                # print(f"Found some text: {text[:100]}...")
                pass
                
        # If requests fails to get meaningful content, we'll need undetected_chromedriver.
        return response.text[:500] # Return a bit of HTML for debugging
        
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    content = crawl_threads_first_post("unclestocknotes")
    print(content)
