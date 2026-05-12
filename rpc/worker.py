from xmlrpc.server import SimpleXMLRPCServer
import sys
import json
import os

data_table = {}


def load_data(group: str):
    global data_table

    group = (group or "").strip().lower()
    filename = f"data-{group}.json"

    # Look in current working directory first, then script directory
    if os.path.exists(filename):
        path = filename
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data_table = json.load(f)

def getbyname(name):
    name = (name or "").strip().lower()
    if not name:
        return {"error": True, "result": [], "message": "name is empty"}

    rec = data_table.get(name)
    return {"error": False, "result": [rec] if rec else []}

def getbylocation(location):

    # Return all records whose location matches.

    location = (location or "").strip()
    if not location:
        return {"error": True, "result": [], "message": "location is empty"}

    matches = []
    for rec in data_table.values():
        if rec.get("location") == location:
            matches.append(rec)

    return {"error": False, "result": matches}

def getbyyear(location, year):

    location = (location or "").strip()
    if not location:
        return {"error": True, "result": [], "message": "location is empty"}

    try:
        year = int(year)
    except Exception:
        return {"error": True, "result": [], "message": "year must be an integer"}

    matches = []
    for rec in data_table.values():
        try:
            rec_year = int(rec.get("year"))
        except Exception:
            continue

        if rec.get("location") == location and rec_year == year:
            matches.append(rec)

    return {"error": False, "result": matches}

def main():
    if len(sys.argv) < 3:
        print("Usage: worker.py <port> <group: am or nz>")
        sys.exit(1)

    port = int(sys.argv[1])
    group = sys.argv[2].strip().lower()

    if group not in ("am", "nz"):
        print("Group must be 'am' or 'nz'")
        sys.exit(1)

    load_data(group)
    print(f"Worker({group}) loaded {len(data_table)} records.")
    print(f"Worker({group}) listening on port {port}...")

    server = SimpleXMLRPCServer(("localhost", port), allow_none=True, logRequests=True)
    server.register_function(getbyname, "getbyname")
    server.register_function(getbylocation, "getbylocation")
    server.register_function(getbyyear, "getbyyear")

    server.serve_forever()


if __name__ == "__main__":
    main()