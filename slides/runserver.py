import os
import os.path as op
import copy
import subprocess
import time

import markdown
import lxml.html
from lxml.html import builder as E
import tulip
from viol import connect, app


FILENAME = '../slides.md'
FILEBASE = op.dirname(FILENAME)

app.index_page = 'index.lim'
app.slides = []
app.client = None
app.ypos = None
app.popen = None

@connect('document_ready')
def load_slides(client, data):
    app.client = client
    render_slides()
    
    if app.ypos is not None:
        client.jquery('body', 'scrollTop', app.ypos)

@connect('final_y_position')
def store_ypos(client, data):
    app.ypos = data

@connect('connection_lost')
def close(client, data):
    app.client = None

@connect('demo_path')
def demo_code(client, demo_path):
    client.send('demo_code', open(demo_path).read())

@connect('run_demo')
def run_demo(client, demo_dir):
    # If the previous demo is still running, kill it.
    if app.popen is not None:
        app.popen.kill()

    print('Running demo at {}'.format(demo_dir))
    cmd = ['python', 'demo.py']
    app.popen = subprocess.Popen(cmd, cwd=demo_dir)
    
def render_slides():
    app.client.send('render_slides', get_html())

def get_html():
    app.slides = get_slides()
    result = '\n\n'.join(app.slides)
    # with open('slides.html', 'w') as fout:
    #     fout.write(result)
    return result

def get_slides():
    """
    Return a list of HTML fragments.
    """
    html = markdown.markdown(open(FILENAME).read())
    root = lxml.html.fromstring(html)

    transform(root)
    
    slides = []   # slide divs

    for el in root.iterchildren():
        if el.tag in ('h1', 'h2'):
            slides.append(E.DIV(E.CLASS('slide')))    
            if el.text.lower().strip() == 'notes':
                slides[-1].set('class', 'slide notes')
        if slides:    
            slides[-1].append(el)

    return [lxml.html.tostring(slide).decode('utf-8') for slide in slides]
    
def transform(root):
    transform_meta(root.xpath('//div[@meta]')[0])

    for div in root.xpath('//div[@code]'):
        transform_code(div)

    for div in root.xpath('//div[@center]'):
        transform_center(div)
    
    for div in root.xpath('//div[@demo]'):
        transform_demo(div)

def transform_meta(div):
    html = div.text.strip().replace('\n', '<br>')
    replace(div, lxml.html.fromstring(html))

def transform_code(div):
    path = op.join(FILEBASE, div.get('code'))
    code = open(path).read()
    replace(div, E.PRE(code))

def transform_center(div):
    center = E.CENTER()
    for c in div.getchildren():
        center.append(c)
    replace(div, center)

def transform_demo(div):
    div.append(E.BUTTON('Run demo'))

    demo_dir = op.join(FILEBASE, div.get('demo'))
    div.set('demo', demo_dir)

    files = (f for f in os.listdir(demo_dir) if not f.startswith('.'))
    ul = E.UL(
        *(E.LI(E.A(f, href=op.join(demo_dir, f))) 
            for f in files)
    )
    div.append(ul)
    
def replace(el1, el2):
    parent = el1.getparent()
    parent.replace(el1, el2)

@tulip.task
def watch_input_file():
    mtime = op.getmtime(FILENAME)

    while True:
        new_mtime = op.getmtime(FILENAME)
        if new_mtime > mtime:
            render_slides()
            mtime = new_mtime
            print('Updated page at {}'.format(time.ctime()))
           
        yield from tulip.sleep(.5)


if __name__ == '__main__':
    app.run(port=9000, call_soon=watch_input_file)
