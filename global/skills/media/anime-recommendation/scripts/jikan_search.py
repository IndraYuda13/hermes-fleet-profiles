import urllib.request
import urllib.parse
import json
import sys
import time

def search_jikan(query, limit=10):
    url = f"https://api.jikan.moe/v4/anime?q={urllib.parse.quote(query)}&order_by=score&sort=desc&limit={limit}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                results = []
                for anime in data.get('data', []):
                    results.append({
                        'title': anime.get('title'),
                        'score': anime.get('score'),
                        'url': anime.get('url'),
                        'synopsis': anime.get('synopsis', '')[:200] + '...' if anime.get('synopsis') else ''
                    })
                return results
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}", file=sys.stderr)
            time.sleep(2)
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 jikan_search.py <query>")
        sys.exit(1)
    
    query = sys.argv[1]
    results = search_jikan(query)
    if results:
        print(json.dumps(results, indent=2))
    else:
        print("Failed to fetch data from Jikan API after 3 attempts.", file=sys.stderr)
        sys.exit(1)
