import sys
import httpx

def main():
    master_port = int(sys.argv[1])
    base = f"http://127.0.0.1:{master_port}"   # Base URL for the master API 
    
    # Define test cases
    tests = [
        ("Person xander", f"{base}/getbyname", {"name": "xander"}),
        ("Location Kansas City", f"{base}/getbylocation", {"location": "Kansas City"}),
        ("NYC in 2002", f"{base}/getbyyear", {"location": "New York City", "year": 2002}),
    ]

# Run tests
    for title, url, params in tests:       #run each test case, printing the title and the response from the master API. If there is a timeout or other exception, print an error message instead.
        print(f"\nClient => {title}")
        try:                                                    #the try block attempts to send an HTTP GET request to the master API using the httpx library, with a timeout of 5 seconds. If the request is successful, it prints the JSON response from the master API. 
            r = httpx.get(url, params=params, timeout=5.0)  #the httpx.get() function sends an HTTP GET request to the specified URL with the given query parameters and timeout. The response is stored in the variable r.
            print(r.json())
        except httpx.ReadTimeout: #If the request times out, print an error message indicating that the server did not respond in time.
            print({"error": True, "message": "ReadTimeout (server did not respond in time)"})
        except Exception as e:
            print({"error": True, "message": str(e)})

if __name__ == "__main__":  
    main()