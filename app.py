import os

from chalice import Chalice, Response
from feedgen.feed import FeedGenerator
import requests

INTERNAL_EVENT_URL = 'https://aws-startup-lofts.com/apj/api/session'
EXTERNAL_EVENT_URL = 'https://aws-startup-lofts.com/apj/api/externalevent'

app = Chalice(app_name='loft-events-feed')


@app.route('/')
def index():
    return { 'tokyo': f'/apj/loft/tokyo/events' }


@app.route('/apj/loft/tokyo/events')
def feed():
    host = 'd1xb4tggvj6fw3.cloudfront.net'
    # Generate feed
    fg = FeedGenerator()
    fg.id(f'https://{host}/apj/loft/tokyo/events')
    fg.title('The feed for events at AWS Startup Loft')
    fg.description('Events')
    fg.link( href='https://aws-startup-lofts.com/apj/loft/tokyo/events' )
    fg.language('ja')

    for e in requests.get(INTERNAL_EVENT_URL).json()['future']:
        if e.get('status', '') == 'live' and e.get('physicalLoft', '') == 'tokyo-loft':
            event_id = e['id']
            event_title = f"[{e['startDate']}] {e['title']}"
            # Add entry
            fe = fg.add_entry()
            fe.id(event_id)
            fe.title(event_title)
            fe.description(e['summary'])
            fe.link( href=f'https://aws-startup-lofts.com/apj/event/{event_id}' )
            fe.pubDate(e['createdDate'])
            fe.category( term=e['type'] )
            fe.author( name=e['presenter'] )
    for e in requests.get(EXTERNAL_EVENT_URL).json()['future']:
        if e.get('status', '') == 'live' and e.get('physicalLoft', '') == 'tokyo-loft':
            event_id = e['id']
            event_title = f"[{e['startDate']}] {e['title']}"
            # Add entry
            fe = fg.add_entry()
            fe.id(event_id)
            fe.title(event_title)
            fe.description(e['summary'])
            fe.link( href=f'https://aws-startup-lofts.com/apj/external-event/{event_id}' )
            fe.pubDate(e['createdDate'])
            fe.category( term=e['type'] )
            fe.author( name=e['presenter'] )
    #feed  = fg.atom_str(pretty=True).decode('utf-8')
    feed  = fg.rss_str(pretty=True).decode('utf-8')
    response_headers = {
        'content-type': 'application/rss+xml; charset=UTF-8',
        'cache-control': 'max-age=600',
    }
    return Response(body=feed,
                    status_code=200,
                    headers=response_headers)
