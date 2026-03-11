import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import requests
import json


PORT=8000
BASEURL = "https://api.opendota.com/api"
def get_search(handler):
    query_components = parse_qs(urlparse(handler.path).query)
    search_term = query_components.get("q", [""])[0]
    

    if not search_term:
        return {
            "error": "Missing Parameter"
        }

    externalurl = f"{BASEURL}/search?q={search_term}"

    try:
        response = requests.get(externalurl)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        return {
            "error" : "External API Failed",
            "details": str(err)
        }

def get_match_history(handler):
    query_id = parse_qs(urlparse(handler.path).query) or 453183858
    
    if not query_id:
        return {
            "error": "Missing Parameter"
        }
    
    externalurl = f"{BASEURL}/players/{int(query_id)}/matches"

    try:
        response = requests.get(externalurl, params={'limit': 10})
        response.raise_for_status()
        if response.json() == []:
            return {
                "error": "Account is private"
            }

        return response.json()
    except Exception as err:
        return{
            "error": "External API Failed",
            "details": str(err)
        }

def get_matches(handler):
    match_id = parse_qs(urlparse(handler.path).query) or 8722975196

    externalurl = f"{BASEURL}/matches/{match_id}"

    try:
        response = requests.get(externalurl)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        return {
            "error": "External API Failed",
            "details": str(err)
        }


routes={
    "/search": get_search,
    "/match_history": get_match_history,
    "/matches": get_matches
}

class DotaAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsedpath = urlparse(self.path).path
        action = routes.get(parsedpath)
        
        if action:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            response = action(self)
            self.wfile.write(json.dumps(response).encode("utf-8"))

        else:
            self.send_error(404, "Endpoint not found")

with socketserver.TCPServer(("", PORT), DotaAPIHandler) as httpd:
    print(f'serving at port {PORT}')
    httpd.serve_forever()
