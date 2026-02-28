import os
import json
from fastapi import FastAPI, Query, HTTPException

app = FastAPI(title="Worker API")

DATA = {}  #global variable to hold the data loaded from the JSON file
GROUP = "" #global variable to hold the worker group (either "am" or "nz")
FILENAME = ""  #global variable to hold the filename of the JSON file being used

#this function loads the data from the appropriate JSON file based on the WORKER_GROUP environment variable. It raises a RuntimeError if the WORKER_GROUP is not set to "am" or "nz". The loaded data is stored in the global DATA variable, and the group and filename are stored in the GROUP and FILENAME variables, respectively.
def load_data():
    global DATA, GROUP, FILENAME
    GROUP = os.getenv("WORKER_GROUP", "").lower().strip() #get the WORKER_GROUP environment variable, convert it to lowercase, and strip any whitespace
    if GROUP not in ("am", "nz"):  #if the WORKER_GROUP is not set to "am" or "nz", raise a RuntimeError
        raise RuntimeError("WORKER_GROUP must be set to 'am' or 'nz'") #raise a RuntimeError if the WORKER_GROUP is not set to "am" or "nz"

    FILENAME = "data-am.json" if GROUP == "am" else "data-nz.json" #set the FILENAME variable based on the WORKER_GROUP value. If the group is "am", use "data-am.json"; if it's "nz", use "data-nz.json".

    with open(FILENAME, "r", encoding="utf-8") as f:   #open the JSON file specified by FILENAME in read mode with UTF-8 encoding
        DATA = json.load(f)

@app.on_event("startup")  #this decorator registers the startup() function to be called when the FastAPI application starts up. The startup() function calls load_data() to load the data from the appropriate JSON file based on the WORKER_GROUP environment variable.
def startup():
    load_data()  #load the data from the appropriate JSON file based on the WORKER_GROUP environment variable when the FastAPI application starts up.

@app.get("/health")
def health():        #this endpoint returns a JSON response indicating that the worker API is healthy, along with the worker group and filename being used. It can be used for health checks and monitoring.
    return {"ok": True, "group": GROUP, "file": FILENAME, "records": len(DATA)}

@app.get("/getbyname")  #this endpoint retrieves a record from the loaded data based on the provided name parameter. It returns a JSON response containing the result, which is either the matching record or an empty list if no match is found. The name parameter is cleaned by converting it to lowercase and stripping whitespace before searching in the DATA dictionary.
def getbyname(name: str = Query(...)):
    name = name.lower().strip()
    if name in DATA: #if the cleaned name exists in the DATA dictionary, return the corresponding record in a JSON response with "error" set to False.
        return {"error": False, "result": [DATA[name]]}
    return {"error": False, "result": []}

@app.get("/getbylocation")  #this endpoint retrieves records from the loaded data based on the provided location parameter. It returns a JSON response containing the result, which is a list of matching records or an empty list if no matches are found. The location parameter is cleaned by stripping whitespace before searching in the DATA dictionary.
def getbylocation(location: str = Query(...)):
    loc = location.strip()
    #this response retrieves records from the loaded data based on the provided location parameter. It returns a JSON response containing the result, which is a list of matching records or an empty list if no matches are found. The location parameter is cleaned by stripping whitespace before searching in the DATA dictionary.
    res = [rec for rec in DATA.values() if rec.get("location") == loc]    
    return {"error": False, "result": res}

@app.get("/getbyyear")
def getbyyear(location: str = Query(...), year: int = Query(...)):
    loc = location.strip()
    #this response retrieves records from the loaded data based on the provided location and year parameters. It returns a JSON response containing the result, which is a list of matching records or an empty list if no matches are found. The location parameter is cleaned by stripping whitespace before searching in the DATA dictionary, and the year parameter is used to filter records by their "year" field.
    res = [
        rec for rec in DATA.values()
        if rec.get("location") == loc and rec.get("year") == year
    ]
    return {"error": False, "result": res}