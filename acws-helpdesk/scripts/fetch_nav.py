import urllib.request, re, sys
url = 'http://127.0.0.1:8000/'
try:
    html = urllib.request.urlopen(url, timeout=5).read().decode('utf-8')
except Exception as e:
    print('FETCH_ERROR:', e)
    sys.exit(1)
m = re.search(r'(<nav[\s\S]*?</nav>)', html, flags=re.IGNORECASE)
if m:
    print(m.group(1))
else:
    print('NAV_NOT_FOUND')
