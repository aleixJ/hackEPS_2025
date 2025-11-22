import requests
import json

API_key = "https://data.lacity.org/resource/h73f-gn57.json"


def fetch_noise_data(endpoint: str = None):
    """
    Fetch noise data from LA City API and print the output to PowerShell
    
    Args:
        endpoint: Custom API endpoint (optional). If not provided, uses the default API_key
    """
    url = endpoint or API_key
    
    try:
        print("🔍 Fetching data from LA City API...")
        print(f"URL: {url}\n")
        
        response = requests.get(url, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 404:
            print("\n❌ HTTP Error 404: API endpoint not found")
            print("\nPossible solutions:")
            print("1. The dataset ID 'dict-i866' may have changed")
            print("2. Check if the LA City data portal URL is correct")
            print("3. Try visiting: https://data.lacity.org/browse to find available datasets\n")
            return None
        
        response.raise_for_status()
        
        data = response.json()
        
        print("✅ Data fetched successfully!\n")
        print(json.dumps(data, indent=2))
        
        return data
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout - API took too long to respond")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code} - {e}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Could not connect to the API")
    except json.JSONDecodeError:
        print("❌ Error parsing JSON response")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None


if __name__ == "__main__":
    # You can pass a custom endpoint if needed:
    # fetch_noise_data(endpoint="https://data.lacity.org/api/views/dict-i866/rows.json")
    
    fetch_noise_data()