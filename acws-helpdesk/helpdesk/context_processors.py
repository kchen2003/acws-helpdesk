from .models import Ticket


def ticket_statuses(request):
    return {"ticket_statuses": Ticket.STATUS_CHOICES}


def acws_logo_data(request):
    """Provide base64 data URI for ACWS logo if present in static files."""
    import os
    data = None
    # common locations where we've stored the uploaded logo
    base = os.path.join(os.path.dirname(__file__), "static")
    candidates = [
        os.path.join(base, "helpdesk", "acws_logo.b64"),
        os.path.join(base, "helpdesk", "acws_logo.jpg"),
        os.path.join(base, "acws_logo.jpg"),
    ]
    for p in candidates:
        try:
            if p.endswith('.b64') and os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    data = f.read().strip()
                    break
            if p.endswith('.jpg') and os.path.exists(p):
                # build data URI
                import base64
                with open(p, 'rb') as f:
                    b = base64.b64encode(f.read()).decode('ascii')
                data = 'data:image/jpeg;base64,' + b
                break
        except Exception:
            data = None
    return {"acws_logo_data": data}
