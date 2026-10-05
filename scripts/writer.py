import sys, base64

target = sys.argv[1]
data = sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else 'a'

with open(target, mode, encoding='utf-8') as f:
    f.write(base64.b64decode(data.encode('ascii')).decode('utf-8'))
print('wrote chunk to', target)
