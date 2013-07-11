import os.path as op
import io
import subprocess
import html.parser


class CompileException(Exception):
    pass

def parse(markup):
    parser = Parser()
    parser.feed(markup)

    gen = HtmlGenerator(parser.parse_result)
    try:
        return gen.get_html()
    except CompileException as ex:
        return '<h1>Error</h1><pre>{}</pre>'.format(ex)


class Parser(html.parser.HTMLParser):
    def __init__(self):
        super(Parser, self).__init__()

        self.parse_result = ParseResult()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == 'title':
            self.parse_result.current_tag = 'title'
        elif tag == 'link':
            self.parse_result.add_link(attrs)
        elif tag == 'script':
            if 'src' in attrs:
                self.parse_result.add_script(attrs['src'], None)
            else:
                self.parse_result.current_tag = 'script'
        elif tag == 'style':
            self.parse_result.current_tag = 'style'
        else:
            self.parse_result.add_tag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'script' and not self.parse_result.current_tag:
            pass
        else:
            self.parse_result.close_tag(tag)

    def handle_data(self, data):
        self.parse_result.add(data)


class ParseResult(object):
    def __init__(self):
        self.title = ''
        self.sio = io.StringIO()  # accumulate body
        self.scripts = []
        self.links = []
        self.styles = []

        self.current_tag = None
        self.current_text = None

    @property
    def body(self):
        return self.sio.getvalue()

    def add(self, text):
        "Add generic text."
        if self.current_tag:
            self.current_text = text
        else:
            self.sio.write(text)

    def add_tag(self, tag, attrs):
        if attrs:
            html = '<{} {}>'.format(tag, attrs_to_str(attrs))
        else:
            html = '<' + tag + '>'
        self.add(html)

    def close_tag(self, tag):
        if self.current_tag:
            if tag == 'script':
                self.add_script(None, self.current_text)
            elif tag == 'style':
                self.add_style(self.current_text)
            elif tag == 'title':
                self.title = self.current_text
            self.current_tag = self.current_text = None
        else:
            self.add('</{}>'.format(tag))

    def add_script(self, src, body):
        self.scripts.append((src, body))

    def add_style(self, body):
        self.styles.append(body)

    def add_link(self, attrs):
        self.links.append(attrs)


HTML_PREFIX = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{}</title>
"""

class HtmlGenerator(object):
    def __init__(self, parse_result):
        self.parse_result = parse_result

    def get_html(self):
        sio = io.StringIO()
        pr = self.parse_result
        sio.write(HTML_PREFIX.format(self.parse_result.title))

        for attrs in pr.links:
            sio.write(self.get_link(attrs))
            sio.write('\n')

        for body in pr.styles:
            sio.write(self.get_style(body))
            sio.write('\n')

        sio.write('</head>\n<body>\n')
        sio.write(pr.body)
        sio.write('\n')

        for src, body in pr.scripts:
            sio.write(self.get_script(src, body))
            sio.write('\n')

        sio.write('</body>\n</html>')
        return sio.getvalue()

    def get_link(self, attrs):
        if 'rel' not in attrs:
            attrs['rel'] = 'stylesheet'

        href = attrs.get('href')
        if href and href.endswith('.scss'):
            css_file = op.splitext(href)[0] + '.css'
            compile_sass(href, css_file)
            attrs['href'] = css_file 

        return '<link ' + attrs_to_str(attrs) + '>'

    def get_style(self, body):
        return '<style>' + body + '</style>'

    def get_script(self, src, body):
        if src and src.endswith('.coffee'):
            js_file = op.splitext(src)[0] + '.js'
            compile_coffeescript(src, js_file)
            src = js_file

        return '<script{}>{}</script>'.format(
            ' src="{}"'.format(src) if src else '',
            body or '')


def attrs_to_str(attrs):
    result = []
    for k, v in attrs.items():
        if v is None:
            result.append(k)
        else:
            result.append('{}="{}"'.format(k, v))
    return ' '.join(result)


def compile_coffeescript(coffee_file, js_file):
    """
    Compile given .coffee file to given .js file. Generate source map for
    compiled file.
    """
    if not need_to_compile(coffee_file, js_file):
        return

    cmd = ['coffee', '-m', '-c', coffee_file]
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as ex:
        raise CompileException(ex.output.decode('utf-8'))

def compile_sass(scss_file, css_file):
    import sass

    if not need_to_compile(scss_file, css_file):
        return

    try:
        result = sass.compile_file(scss_file.encode())
        with open(css_file, 'wb') as fout:
            fout.write(result)
    except Exception as ex:
        raise CompileException(str(ex))

def need_to_compile(src_file, target_file):
    if not op.exists(target_file):
        return True

    if op.getmtime(src_file) > op.getmtime(target_file):
        return True

    return False