import urllib.request, sys
url = 'http://127.0.0.1:8000/tickets/create/'
try:
    html = urllib.request.urlopen(url, timeout=5).read().decode('utf-8')
    hpos = html.find('<h2>New Ticket')
    if hpos==-1:
        print('HEADER_NOT_FOUND')
    else:
        start = html.find('<form', hpos)
        end = html.find('</form>', start)
        if start!=-1 and end!=-1:
            print(html[start:end+7])
        else:
            print('FORM_NOT_FOUND_AFTER_HEADER')
except Exception as e:
    print('FETCH_ERROR:', e)
    sys.exit(1)
