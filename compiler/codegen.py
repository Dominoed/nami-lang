import re, os

def ast_to_html(ast, assets, source_path):
    html = []
    css = ["""
body { font-family: sans-serif; padding: 2em; }
.flex { display: flex; gap: 1em; flex-wrap: wrap; }
.grid { display: grid; gap: 1em; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); }
.row  { display: flex; flex-direction: row; }
.col  { display: flex; flex-direction: column; }
.box  { padding: 1em; background: #f6f6f6; border-radius: 10px; box-shadow: 0 2px 8px #0001; }
.spacer { flex: 1 1 10px; min-width: 10px; min-height: 10px; }
.nami-page { display: none; }
"""]
    js = ["""
// --- Nami Reactive Runtime ---
const state = {};
const subscribers = {};
function setVar(name, value) {
    state[name] = value;
    if (subscribers[name]) { for (const fn of subscribers[name]) fn(value); }
}
function getVar(name) { return state[name]; }
function subscribeVar(name, fn) {
    if (!subscribers[name]) subscribers[name] = [];
    subscribers[name].push(fn);
}
function bindVars() {
    for (const name in state) {
        const el = document.getElementById('nami_var_' + name);
        if (el) {
            subscribeVar(name, val => { el.innerText = val; });
            el.innerText = state[name];
        }
        const input = document.getElementById('nami_input_' + name);
        if (input) {
            input.value = state[name] || "";
            input.addEventListener('input', e => setVar(name, e.target.value));
            subscribeVar(name, val => { input.value = val; });
        }
        const checkbox = document.getElementById('nami_input_' + name + '_checkbox');
        if (checkbox) {
            checkbox.checked = !!state[name];
            checkbox.addEventListener('change', e => setVar(name, checkbox.checked));
            subscribeVar(name, val => { checkbox.checked = !!val; });
        }
    }
}
document.addEventListener("DOMContentLoaded", bindVars);

let running = true;
function gameLoop() {
    if (running) {
        if (typeof namiTick === 'function') namiTick();
        requestAnimationFrame(gameLoop);
    }
}
gameLoop();

function switchPage(pageId) {
    document.querySelectorAll('.nami-page').forEach(div => div.style.display = 'none');
    var el = document.getElementById(pageId);
    if (el) el.style.display = '';
}
"""]
    pages = []
    if_counter = [0]

    def walk(nodes):
        for n in nodes:
            if n['type'] == 'page':
                pid = n['name'].replace(' ','_')
                pages.append(pid)
                html.append(f"<div class='nami-page' id='page_{pid}'>")
                walk(n['children'])
                html.append("</div>")
            elif n['type'] == 'flex':
                html.append("<div class='flex'>")
                walk(n['children'])
                html.append("</div>")
            elif n['type'] == 'grid':
                html.append("<div class='grid'>")
                walk(n['children'])
                html.append("</div>")
            elif n['type'] == 'row':
                html.append("<div class='row'>")
                walk(n['children'])
                html.append("</div>")
            elif n['type'] == 'col':
                html.append("<div class='col'>")
                walk(n['children'])
                html.append("</div>")
            elif n['type'] == 'box':
                html.append("<div class='box'>")
                walk(n['children'])
                html.append("</div>")
            elif n['type'] == 'spacer':
                html.append("<div class='spacer'></div>")
            elif n['type'] == 'select':
                html.append(f"<select id='nami_input_select'>")
                walk(n['children'])
                html.append(f"</select>")
            # --- Leaf nodes ---
            elif n['type'] == 'text':
                txt = n['content']
                txt = re.sub(r'\{([a-zA-Z_]\w*)\}', r'<span id="nami_var_\1"></span>', txt)
                html.append(f"<span>{txt}</span>")
            elif n['type'] == 'button':
                label = n['label']
                btn_id = f"btn_{label.replace(' ', '_')}_{id(n)}"
                click_js = []
                for child in n['children']:
                    if child['type'] == 'route':
                        click_js.append(f"switchPage('page_{child['target']}');")
                    elif child['type'] == 'event' and child['event'] == 'click':
                        for cc in child['children']:
                            if cc['type'] == 'set':
                                var, expr = cc['assign'].split('=', 1)
                                var = var.strip()[4:]
                                expr = expr.strip()
                                click_js.append(f"setVar('{var}', {expr});")
                            elif cc['type'] == 'js':
                                if cc.get('code'):
                                    click_js.append(cc['code'])
                                else:
                                    click_js.extend(
                                        gc['raw'].strip()
                                        if 'raw' in gc else
                                        gc.get('text', '').strip()
                                        if 'text' in gc else
                                        gc.get('content', '').strip()
                                        if 'content' in gc else ''
                                        for gc in cc.get('children', [])
                                    )
                    elif child['type'] == 'set':
                        var, expr = child['assign'].split('=', 1)
                        var = var.strip()[4:]
                        expr = expr.strip()
                        click_js.append(f"setVar('{var}', {expr});")
                    elif child['type'] == 'js':
                        if child.get('code'):
                            click_js.append(child['code'])
                        else:
                            click_js.extend(
                                gc['raw'].strip()
                                if 'raw' in gc else
                                gc.get('text', '').strip()
                                if 'text' in gc else
                                gc.get('content', '').strip()
                                if 'content' in gc else ''
                                for gc in child.get('children', [])
                            )
                click_attr = f" onclick=\"{';'.join(click_js)}\"" if click_js else ""
                html.append(f"<button id='{btn_id}'{click_attr}>{label}</button>")
            elif n['type'] == 'input':
                html.append(f"<label>{n['label']} <input type='text' id='nami_input_{n['label'].replace(' ','_')}'></label>")
            elif n['type'] == 'textarea':
                html.append(f"<label>{n['label']} <textarea id='nami_input_{n['label'].replace(' ','_')}'></textarea></label>")
            elif n['type'] == 'checkbox':
                html.append(f"<label><input type='checkbox' id='nami_input_{n['label'].replace(' ','_')}_checkbox' /> {n['label']}</label>")
            elif n['type'] == 'option':
                html.append(f"<option>{n['label']}</option>")
            elif n['type'] == 'image':
                html.append(f"<img src='assets/{n['src']}' />")
                assets.add(n['src'])
            elif n['type'] == 'audio':
                html.append(f"<audio controls src='assets/{n['src']}'></audio>")
                assets.add(n['src'])
            elif n['type'] == 'video':
                html.append(f"<video controls src='assets/{n['src']}'></video>")
                assets.add(n['src'])
            elif n['type'] == 'let':
                js.append(f"state.{n['assign'].split('=')[0].strip()[4:]} = {n['assign'].split('=',1)[1].strip()};")
            elif n['type'].startswith('logic_if'):
                if_counter[0] += 1
                block_id = f"nami_if_{if_counter[0]}"
                cond_expr = n.get('expr', 'false')
                html.append(f"<div id='{block_id}' style='display:none;'>")
                walk(n['children'])
                html.append(f"</div>")
                var_names = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', cond_expr))
                js.append(f"""
function update_{block_id}() {{
  if ({cond_expr}) {{
    document.getElementById('{block_id}').style.display = '';
  }} else {{
    document.getElementById('{block_id}').style.display = 'none';
  }}
}}
""" + "\n".join([f"subscribeVar('{var}', update_{block_id});" for var in var_names]))
                if n.get('else_children'):
                    if_counter[0] += 1
                    else_id = f"nami_if_{if_counter[0]}"
                    html.append(f"<div id='{else_id}' style='display:none;'>")
                    for else_block in n['else_children']:
                        walk(else_block['children'])
                    html.append(f"</div>")
                    js.append(f"""
function update_{else_id}() {{
  if (!({cond_expr})) {{
    document.getElementById('{else_id}').style.display = '';
  }} else {{
    document.getElementById('{else_id}').style.display = 'none';
  }}
}}
""" + "\n".join([f"subscribeVar('{var}', update_{else_id});" for var in var_names]))
            elif n['type'].startswith('logic_for'):
                html.append(f"<!-- For loop rendering not yet implemented -->")
            elif n['type'] == 'logic_else':
                pass
            elif n['type'] == 'js':
                pass
            elif n['type'] == 'raw':
                html.append(f"<!-- {n['text']} -->")

    walk(ast)
    first_page = pages[0] if pages else None
    if len(pages) > 1:
        nav_html = "<nav>" + " | ".join(
            f"<a href='#' onclick=\"switchPage('page_{p}')\">{p}</a>" for p in pages
        ) + "</nav>"
        html.insert(0, nav_html)
    html_out = "<!DOCTYPE html>\n<html><head><title>Nami App</title><link rel='stylesheet' href='style.css'></head><body>\n"
    html_out += "\n".join(html)
    html_out += "\n<script src='app.js'></script></body></html>"
    css_out = "\n".join(css)
    # Handle global JS blocks
    for node in ast:
        if node['type'] == 'js' and node.get('code') is None:
            code = '\n'.join(
                child['raw'].strip()
                if 'raw' in child else
                child.get('text', '').strip()
                if 'text' in child else
                child.get('content', '').strip()
                if 'content' in child else ''
                for child in node['children']
            )
            js.append(code)
        elif node['type'] == 'js':
            js.append(node['code'])
    if first_page:
        js.append(f"document.addEventListener(\"DOMContentLoaded\", function() {{\n    switchPage('page_{first_page}');\n}});")
    js_out = "\n".join(js)
    # Asset copying
    asset_dir = os.path.join(os.path.dirname(source_path), "build/assets")
    os.makedirs(asset_dir, exist_ok=True)
    for asset in assets:
        src_path = os.path.join(os.path.dirname(source_path), asset)
        if os.path.exists(src_path):
            with open(src_path, "rb") as fin, open(os.path.join(asset_dir, asset), "wb") as fout:
                fout.write(fin.read())
    return html_out, css_out, js_out
