from fastapi import FastAPI, Query
import httpx

app = FastAPI(title="Master API")  


WORKER1 = "http://127.0.0.1:23001"  #url for worker 1
WORKER2 = "http://127.0.0.1:23002"  #url for worker 2
TIMEOUT = 1.5


async def safe_get(url: str, params: dict):  #function to safely get data from worker APIs with error handling

    try:                                      #except block to handle exceptions during the HTTP request
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:  #Creating Async HTTP Client
            resp = await client.get(url, params=params)   #Sends an HTTP GET request.
            resp.raise_for_status()                       #Check for HTTP Errors
            return resp.json()                      #Return JSON Response
    except Exception:                               #Exception Handling
        return {"error": True, "result": []}        #Return Safe Fallback Response

@app.get("/health")
def health():
    return {"ok": True, "role": "master"}

@app.get("/getbyname")                               
async def getbyname(name: str = Query(...)):

    name = name.lower().strip()                             #Clean input make lowr case and strip whitespace
    if not name:                                        #check if name is empty
        return {"error": False, "result": []}          
    if "a" <= name[0] <= "m":    #If the first letter of the name is between 'a' and 'm', send the request to WORKER1, otherwise send it to WORKER2
        target = WORKER1          
    else:
        target = WORKER2
    response = await safe_get(f"{target}/getbyname", {"name": name}) #retrieve data from the target worker API using the safe_get function
    if response.get("error"):  #If the response from the target worker API indicates an error, the master API will attempt to retrieve data from the other worker API as a fallback.
        other = WORKER2 if target == WORKER1 else WORKER1  #check which worker was the target and set the other worker as the fallback
        response = await safe_get(f"{other}/getbyname", {"name": name}) #retrieve data from the other worker API using the safe_get function
        #return a response indicating that the result is partial, meaning that it may not be complete due to the error encountered when querying the target worker API.
        return {                                         
            "error": False,
            "result": response.get("result", []),
            "partial": True
        }        
   #If the response from the target worker API does not indicate an error, the master API will return the result from that worker API without indicating that it is partial.
    return {
        "error": False,
        "result": response.get("result", []),
        "partial": False
    }

#later we will implement the getbylocation and getbyyear endpoints in a similar way, querying both worker APIs and combining their results.
@app.get("/getbylocation")
async def getbylocation(location: str = Query(...)): #async function to handle the /getbylocation endpoint, which takes a location parameter from the query string and retrieves data from both worker APIs based on that location.

    response1 = await safe_get(f"{WORKER1}/getbylocation", {"location": location}) #retrieve data from WORKER1 using the safe_get function
    response2 = await safe_get(f"{WORKER2}/getbylocation", {"location": location}) #retrieve data from WORKER2 using the safe_get function

    results = []  
    if not response1["error"]:  #if the response from WORKER1 does not indicate an error, add its results to the combined results list
        results += response1["result"]
    if not response2["error"]:  #if the response from WORKER2 does not indicate an error, add its results to the combined results list
        results += response2["result"]
    partial = response1["error"] or response2["error"]  #if either response indicates an error, set the partial flag to True
    
    #return a response indicating whether the result is partial, meaning that it may not be complete due to errors encountered when querying the worker APIs.
    return {
        "error": False,
        "result": results,
        "partial": partial
    }
#this endpoint retrieves data from both worker APIs based on a location and year parameter, and combines their results into a single response. It also indicates whether the result is partial, meaning that it may not be complete due to errors encountered when querying the worker APIs.
@app.get("/getbyyear")
async def getbyyear(location: str = Query(...), year: int = Query(...)): #async function to handle the /getbyyear endpoint, which takes a location and year parameter from the query string and retrieves data from both worker APIs based on those parameters.
    #retrieve data from both worker APIs using the safe_get function, passing in the location and year parameters as query parameters.
    response1 = await safe_get(
        f"{WORKER1}/getbyyear",
        {"location": location, "year": year}
    )
   #retrieve data from WORKER2 using the safe_get function, passing in the location and year parameters as query parameters.
    response2 = await safe_get(
        f"{WORKER2}/getbyyear",
        {"location": location, "year": year}
    )
    results = []
    #if the response from WORKER1 does not indicate an error, add its results to the combined results list
    if not response1["error"]:
        results += response1["result"]
    #if the response from WORKER2 does not indicate an error, add its results to the combined results list
    if not response2["error"]:
        results += response2["result"]
  #if either response indicates an error, set the partial flag to True
    partial = response1["error"] or response2["error"]
    #return a response indicating whether the result is partial, meaning that it may not be complete due to errors encountered when querying the worker APIs.
    return {
        "error": False,
        "result": results,
        "partial": partial
    }