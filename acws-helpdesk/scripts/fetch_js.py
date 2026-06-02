import urllib.request
urls = [
    'https://code.jquery.com/jquery-3.5.1.slim.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js'
]
for u in urls:
    try:
        with urllib.request.urlopen(u, timeout=10) as r:
            print(u, '->', r.status, 'bytes=', r.length)
    except Exception as e:
        print(u, '-> ERROR', e)
