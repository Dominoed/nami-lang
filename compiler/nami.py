# compiler/nami.py

import sys, os
from parser import lex_nami, parse_nami
from codegen import ast_to_html

def compile_file(source_path, outdir='build'):
    with open(source_path, "r", encoding="utf-8") as f:
        source = f.read()
    tokens = lex_nami(source)
    ast = parse_nami(tokens)
    assets = set()
    html, css, js = ast_to_html(ast, assets, source_path)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f: f.write(html)
    with open(os.path.join(outdir, "style.css"), "w", encoding="utf-8") as f: f.write(css)
    with open(os.path.join(outdir, "app.js"), "w", encoding="utf-8") as f: f.write(js)
    print(f"Nami: Compiled to {outdir}/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nami.py path/to/app.nami [output_dir]")
    else:
        compile_file(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "build")