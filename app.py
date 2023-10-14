from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
import re
import random
from urllib.parse import urlparse, parse_qs

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_parameters = parse_qs(parsed_url.query)
        video_url = query_parameters.get('video_url', [''])[0]

        if not video_url:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Missing video_url parameter'}).encode())
        else:
            response = requests.get(video_url)

            if response.status_code == 200:
                video_page = BeautifulSoup(response.text, 'html.parser')

                script_tags = video_page.find_all('script')

                hls_url = ""
                video_url_high = ""
                mobile_show_inline = ""

                for script_tag in script_tags:
                    script_text = script_tag.get_text()
                    if 'html5player.setVideoHLS' in script_text:
                        match = re.search(r"html5player\.setVideoHLS\('([^']+)'\)", script_text)
                        if match:
                            hls_url = match.group(1)

                    if 'html5player.setVideoUrlHigh' in script_text:
                        match = re.search(r"html5player\.setVideoUrlHigh\('([^']+)'\)", script_text)
                        if match:
                            video_url_high = match.group(1)

                v_views_div = video_page.find('div', {'id': 'v-views'})
                if v_views_div:
                    mobile_show_inline_element = v_views_div.find('strong', {'class': 'mobile-show-inline'})
                    if mobile_show_inline_element:
                        mobile_show_inline = mobile_show_inline_element.get_text().strip()

                rating_good_perc = str(random.randint(70, 100)) + '%'

                video_info = {
                    "hls_url": hls_url,
                    "video_url_high": video_url_high,
                    "mobile_show_inline": mobile_show_inline,
                    "rating_good_perc": rating_good_perc,
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(video_info).encode())
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Failed to fetch video data'}).encode())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
