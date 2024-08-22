Google deprecated their Search API and it’s no longer available for public use. However, you can use the **Custom Search JSON API** provided by Google, which allows you to integrate Google Search functionality into your applications.

Here's an example of how to use the Google Custom Search JSON API in Python:

### Step 1: Set up your Google Custom Search Engine
1. Go to the [Google Custom Search Engine](https://cse.google.com/cse/) page.
2. Create a new search engine and specify the websites you want to include in the search, or choose to search the entire web.
3. After creating the search engine, you'll get a Search Engine ID (cx).
4. Go to the [Google Developers Console](https://console.developers.google.com/).
5. Create a new project or select an existing one.
6. Go to the "APIs & Services" and enable the "Custom Search API".
7. Create API credentials to get your API key.

### Step 2: Install the Required Libraries
Make sure you have the `requests` library installed:

```bash
pip install requests
```

### Step 3: Implement the Search in Python

```python
import requests

def google_search(api_key, cse_id, query, num_results=10):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": num_results
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        search_results = response.json()
        return search_results.get('items', [])
    else:
        return None

# Example usage
if __name__ == "__main__":
    api_key = "YOUR_API_KEY"
    cse_id = "YOUR_SEARCH_ENGINE_ID"
    query = "Python programming"
    
    results = google_search(api_key, cse_id, query)
    if results:
        for i, result in enumerate(results, start=1):
            print(f"{i}. {result['title']}")
            print(result['link'])
            print(result['snippet'])
            print()
    else:
        print("No results found or an error occurred.")
```

### Step 4: Customize Your Search
- Replace `YOUR_API_KEY` with your Google API key.
- Replace `YOUR_SEARCH_ENGINE_ID` with your Custom Search Engine ID.
- Modify the `query` parameter to search for whatever you need.

### Note
- The `num_results` parameter specifies the number of search results to return (up to 10 per request, the maximum allowed by the API in one call).
- Google may charge for API requests after a certain limit, so make sure to check your quota and pricing details.

This code will perform a Google search using your custom search engine and print out the titles, links, and snippets of the search results.