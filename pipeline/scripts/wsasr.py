#!/usr/bin/env python3
"""Tiny client for sherpa-onnx-offline-websocket-server (one utterance at a time, so no batching).

as a module:  from wsasr import recognize; d = recognize('/path/file.wav')  -> dict with text/tokens/timestamps/durations
as a script:  wsasr.py file.wav [file.wav ...]   -> prints  path\\n{json}  per file (same layout as sherpa-onnx-offline)
"""
import sys, os, socket, base64, json, struct, time, subprocess
import numpy as np
import scipy.io.wavfile as wf

PORT = 6123
M = '/home/claude/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8'


def ensure_server():
    try:
        s = socket.create_connection(('127.0.0.1', PORT), timeout=1)
        s.close()
        return
    except OSError:
        pass
    subprocess.Popen(['nohup', '/home/claude/sherpa/bin/sherpa-onnx-offline-websocket-server', f'--port={PORT}',
                      f'--tokens={M}/tokens.txt', f'--encoder={M}/encoder.int8.onnx', f'--decoder={M}/decoder.int8.onnx',
                      f'--joiner={M}/joiner.int8.onnx', '--model-type=nemo_transducer', '--num-threads=2',
                      '--max-batch-size=1', '--num-work-threads=1', '--num-io-threads=1', '--max-utterance-length=120'],
                     stdout=open('/home/claude/models/wsserver.log', 'a'), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                     start_new_session=True)
    for _ in range(120):
        time.sleep(1)
        try:
            s = socket.create_connection(('127.0.0.1', PORT), timeout=1)
            s.close()
            return
        except OSError:
            pass
    raise RuntimeError('websocket server did not start')


def _send_frame(sock, payload, opcode):
    hdr = bytearray([0x80 | opcode])
    n = len(payload)
    if n < 126:
        hdr.append(0x80 | n)
    elif n < 65536:
        hdr.append(0x80 | 126)
        hdr += struct.pack('>H', n)
    else:
        hdr.append(0x80 | 127)
        hdr += struct.pack('>Q', n)
    mask = os.urandom(4)
    hdr += mask
    p = np.frombuffer(payload, np.uint8)
    m = np.frombuffer((mask * (n // 4 + 1))[:n], np.uint8)
    sock.sendall(bytes(hdr) + (p ^ m).tobytes())


def _recv_exact(sock, n):
    b = b''
    while len(b) < n:
        c = sock.recv(n - len(b))
        if not c:
            raise ConnectionError('closed')
        b += c
    return b


def _recv_frame(sock):
    h = _recv_exact(sock, 2)
    op = h[0] & 0x0F
    n = h[1] & 0x7F
    if n == 126:
        n = struct.unpack('>H', _recv_exact(sock, 2))[0]
    elif n == 127:
        n = struct.unpack('>Q', _recv_exact(sock, 8))[0]
    if h[1] & 0x80:
        _recv_exact(sock, 4)
    return op, _recv_exact(sock, n)


def recognize(path):
    sr, x = wf.read(path)
    if x.dtype.kind == 'i':
        x = x.astype(np.float32) / 32768.0
    if x.ndim > 1:
        x = x.mean(1)
    x = x.astype(np.float32)
    sock = socket.create_connection(('127.0.0.1', PORT), timeout=300)
    key = base64.b64encode(os.urandom(16)).decode()
    sock.sendall((f'GET / HTTP/1.1\r\nHost: 127.0.0.1:{PORT}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                  f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
    resp = b''
    while b'\r\n\r\n' not in resp:
        resp += sock.recv(4096)
    buf = int(sr).to_bytes(4, 'little') + (x.size * 4).to_bytes(4, 'little') + x.tobytes()
    for i in range(0, len(buf), 10240):
        _send_frame(sock, buf[i:i + 10240], 0x2)
    while True:
        op, data = _recv_frame(sock)
        if op == 0x1:
            break
        if op == 0x8:
            raise ConnectionError('server closed: ' + data[2:].decode(errors='ignore'))
    _send_frame(sock, b'Done', 0x1)
    try:
        _send_frame(sock, b'\x03\xe8', 0x8)
        sock.close()
    except OSError:
        pass
    return json.loads(data.decode())


if __name__ == '__main__':
    ensure_server()
    for f in sys.argv[1:]:
        d = recognize(f)
        print(f)
        print(json.dumps({'lang': '', 'text': d.get('text', ''), 'timestamps': d.get('timestamps', []),
                          'durations': d.get('durations', []), 'tokens': d.get('tokens', [])}))
        sys.stdout.flush()
