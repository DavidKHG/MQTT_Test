import io
import cv2
import logging
import socketserver
from threading import Condition
from http import server

framerate = 25
# resolution = (1920,1080)
resolution = (640,480)

# streams to: http://127.0.0.1:8000/stream.mjpg


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True





# with cv2.VideoCapture(0) as camera:
camera = cv2.VideoCapture(0)
output = StreamingOutput()
address = ('127.0.0.1', 8000)
server = StreamingServer(address, StreamingHandler)
server.timeout = 0.01

camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
camera.set(cv2.CAP_PROP_FPS, framerate)

#camera.rotation = 90

# camera.start_recording(output, format='mjpeg')
try:
    while True:
        success, frame = camera.read()

        if not success:
            break

        ret, jpeg = cv2.imencode('.jpg', frame)

        if not ret:
            continue

        output.write(jpeg.tobytes())

        server.handle_request()
finally:
    camera.release()