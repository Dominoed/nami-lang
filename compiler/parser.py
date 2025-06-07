# compiler/parser.py

import re

def lex_nami(source):
    lines = source.splitlines()
    tokens = []
    for idx, line in enumerate(lines):
        raw = line
        line = line.rstrip('\n')
        if not line.strip() or line.strip().startswith('#'):
            continue
        indent = len(line) - len(line.lstrip(' '))
        line = line.strip()
        tokens.append({'line': idx+1, 'indent': indent, 'raw': raw, 'text': line})
    return tokens

def parse_nami(tokens):
    stack = []
    ast = []
    block_stack = []
    for token in tokens:
        text = token['text']
        indent = token['indent']
        node = {'type': None, 'children': [], 'text': text, 'line': token['line'], 'indent': indent}

        # JS block
        if re.match(r'js:', text):
            node['type'] = 'js'
            node['code'] = None  # Will collect raw code from children
        elif re.match(r'js\s+".+"', text):
            node['type'] = 'js'
            node['code'] = re.findall(r'js\s+"([^"]+)"', text)[0]
        # Route action
        elif re.match(r'route\s+"[^"]+"', text):
            node['type'] = 'route'
            node['target'] = re.findall(r'"([^"]+)"', text)[0]
        # Set action
        elif re.match(r'set\s+[a-zA-Z_]\w*\s*=', text):
            node['type'] = 'set'
            node['assign'] = text
        # Events
        elif re.match(r'on\s+\w+:', text):
            event = re.findall(r'on\s+(\w+):', text)[0]
            node['type'] = 'event'
            node['event'] = event
        # Logic blocks
        elif re.match(r'<-([a-z]+)\s+(.*?)->', text):
            kind, expr = re.findall(r'<-([a-z]+)\s+(.*?)->', text)[0]
            node['type'] = f'logic_{kind}'
            node['expr'] = expr
            block_stack.append({'type': kind, 'node': node})
        elif re.match(r'</-([a-z]+)->', text):
            closing = re.findall(r'</-([a-z]+)->', text)[0]
            while block_stack:
                block = block_stack.pop()
                if block['type'] == closing:
                    node = None
                    break
        elif re.match(r'<-else->', text):
            node['type'] = 'logic_else'
            if block_stack and block_stack[-1]['type'] == 'if':
                parent = block_stack[-1]['node']
                parent.setdefault('else_children', []).append(node)
            else:
                raise Exception(f"<-else-> without matching <-if-> at line {token['line']}")
        # Page/Layout/UI/Asset/Var nodes
        elif re.match(r'page\s+"[^"]+"', text):
            node['type'] = 'page'
            node['name'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'flex:', text):
            node['type'] = 'flex'
        elif re.match(r'grid:', text):
            node['type'] = 'grid'
        elif re.match(r'box:', text):
            node['type'] = 'box'
        elif re.match(r'row:', text):
            node['type'] = 'row'
        elif re.match(r'col:', text):
            node['type'] = 'col'
        elif re.match(r'spacer:', text):
            node['type'] = 'spacer'
        elif re.match(r'image\s+".+"', text):
            node['type'] = 'image'
            node['src'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'audio\s+".+"', text):
            node['type'] = 'audio'
            node['src'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'video\s+".+"', text):
            node['type'] = 'video'
            node['src'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'text\s+".+"', text):
            node['type'] = 'text'
            node['content'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'button\s+".+"', text):
            node['type'] = 'button'
            node['label'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'input\s+".+"', text):
            node['type'] = 'input'
            node['label'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'textarea\s+".+"', text):
            node['type'] = 'textarea'
            node['label'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'checkbox\s+".+"', text):
            node['type'] = 'checkbox'
            node['label'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'select:', text):
            node['type'] = 'select'
        elif re.match(r'option\s+".+"', text):
            node['type'] = 'option'
            node['label'] = re.findall(r'"([^"]+)"', text)[0]
        elif re.match(r'let\s+[a-zA-Z_]\w*\s*=', text):
            node['type'] = 'let'
            node['assign'] = text
        elif re.match(r'loop per frame:', text):
            node['type'] = 'loop'
            node['mode'] = 'frame'
        elif re.match(r'tick every', text):
            node['type'] = 'loop'
            node['mode'] = 'tick'
        else:
            node['type'] = 'raw'

        # Indentation/AST logic
        if node:
            while stack and indent <= stack[-1][1]:
                stack.pop()
            if stack:
                stack[-1][0]['children'].append(node)
            else:
                ast.append(node)
            stack.append((node, indent))
            if block_stack:
                block_stack[-1]['node']['children'].append(node)
    return ast