from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import sys

workers = {
    "worker-1": ServerProxy("http://localhost:23003/", allow_none=True),
    "worker-2": ServerProxy("http://localhost:23004/", allow_none=True),
}


def _route_worker_by_name(name: str) -> str:

    name = (name or "").strip().lower()
    if not name:
        return "worker-1"
    first = name[0]
    if "a" <= first <= "m":
        return "worker-1"
    return "worker-2"


def _safe_worker_call(worker_key: str, method: str, *args):
    try:
        proxy = workers[worker_key]
        fn = getattr(proxy, method)
        resp = fn(*args)
        if isinstance(resp, dict) and "result" in resp:
            return (resp.get("error") is False, resp)

        # Unexpected format
        return (False, {"error": True, "result": [], "message": "Bad worker response format"})

    except Exception as e:
        return (False, {"error": True, "result": [], "message": str(e)})


def getbyname(name):

    name = (name or "").strip().lower()
    if not name:
        return {"error": True, "result": [], "partial": False, "message": "name is empty"}

    wk = _route_worker_by_name(name)
    ok, resp = _safe_worker_call(wk, "getbyname", name)

    if ok:
        return {"error": False, "result": resp["result"], "partial": False}

    return {
        "error": True,
        "result": [],
        "partial": True,
        "message": f"{wk} failed: {resp.get('message', 'unknown error')}",
    }

def getbylocation(location):
    
    
    location = (location or "").strip()
    if not location:
        return {"error": True, "result": [], "partial": False, "message": "location is empty"}

    combined = []
    failures = []

    for wk in ("worker-1", "worker-2"):
        ok, resp = _safe_worker_call(wk, "getbylocation", location)
        if ok:
            combined.extend(resp["result"])
        else:
            failures.append(f"{wk}: {resp.get('message', 'unknown error')}")

    if not failures:
        return {"error": False, "result": combined, "partial": False}

    return {
        "error": False,          
        "result": combined,
        "partial": True,
        "message": "One or more workers failed: " + " | ".join(failures),
    }


def getbyyear(location, year):
    
    # Query both location, year.
    
    location = (location or "").strip()
    if not location:
        return {"error": True, "result": [], "partial": False, "message": "location is empty"}

    try:
        year = int(year)
    except Exception:
        return {"error": True, "result": [], "partial": False, "message": "year must be an integer"}

    combined = []
    failures = []

    for wk in ("worker-1", "worker-2"):
        ok, resp = _safe_worker_call(wk, "getbyyear", location, year)
        if ok:
            combined.extend(resp["result"])
        else:
            failures.append(f"{wk}: {resp.get('message', 'unknown error')}")

    if not failures:
        return {"error": False, "result": combined, "partial": False}

    return {
        "error": False,
        "result": combined,
        "partial": True,
        "message": "One or more workers failed: " + " | ".join(failures),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: master.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    server = SimpleXMLRPCServer(("localhost", port), allow_none=True, logRequests=True)
    print(f"Master listening on port {port}...")
    server.register_function(getbyname, "getbyname")
    server.register_function(getbylocation, "getbylocation")
    server.register_function(getbyyear, "getbyyear")

    server.serve_forever()

if __name__ == "__main__":
    main()