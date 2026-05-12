import xmlrpc.client
import sys

if len(sys.argv) < 2:
    print("Usage: client.py <master_port>")
    sys.exit(1)

master_port = int(sys.argv[1])
with xmlrpc.client.ServerProxy(f"http://localhost:{master_port}/", allow_none=True) as proxy:
    name = 'xander'
    print(f'Client => Asking for person with {name}')
    result = proxy.getbyname(name)
    print(result)
    print()

    location = 'Kansas City'
    print(f'Client => Asking for person lived at {location}')
    result = proxy.getbylocation(location)
    print(result)
    print()

    location = 'New York City'
    year = 2002
    print(f'Client => Asking for person lived in {location} in {year}')
    result = proxy.getbyyear(location, year)  
    print(result)
    print()