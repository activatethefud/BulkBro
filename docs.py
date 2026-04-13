#!/usr/bin/env python3
"""BulkBro Documentation Generator.

Generates HTML documentation from project source code.
Includes:
- API documentation from docstrings
- Test coverage report
- Import/dependency graphs

Usage:
    python3 docs.py          # Generate all docs
    python3 docs.py --api    # Generate API only
    python3 docs.py --tests # Generate test coverage only
"""

import os
import re
import sys
import ast
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


PROJECT_ROOT = Path(__file__).parent
DOCS_DIR = PROJECT_ROOT / "docs"


def get_python_files():
    """Get all Python files in project, excluding test and data files."""
    files = []
    for f in PROJECT_ROOT.glob("*.py"):
        if f.name not in ["test_runner.py", "docs.py"]:
            files.append(f)
    return sorted(files)


def parse_docstring(docstring):
    """Parse NumPy-style docstring into components.
    
    NumPy style format:
        Parameters
        ----------
        arg1 : type
            description
        arg2 : type
            description
        
        Returns
        -------
        type
            description
    
    Args:
        docstring: Raw docstring string
        
    Returns:
        dict with 'description', 'args', 'returns', 'raises', 'examples'
    """
    if not docstring:
        return {}
    
    result = {
        "description": "",
        "args": [],
        "returns": None,
        "raises": [],
        "examples": []
    }
    
    lines = docstring.strip().split("\n")
    current_section = "description"
    current_arg = None
    current_arg_type = None
    current_arg_desc = []
    
    for line in lines:
        stripped = line.strip()
        
        # NumPy section headers
        if stripped.lower().startswith("parameters"):
            current_section = "args"
            continue
        elif stripped.lower().startswith("attributes"):
            current_section = "attributes"
            continue
        elif stripped.lower().startswith("returns"):
            current_section = "returns"
            continue
        elif stripped.lower().startswith("raises"):
            current_section = "raises"
            continue
        elif stripped.lower().startswith("examples"):
            current_section = "examples"
            continue
        
        # Section divider line (---- or ====)
        if stripped.startswith("---") or stripped.startswith("==="):
            continue
        
        # Attributes entries (same format as args)
        if current_section == "attributes" and ":" in stripped:
            if stripped.lower().startswith("attributes"):
                continue
            if current_arg:
                result["args"].append({
                    "name": current_arg,
                    "type": current_arg_type,
                    "description": " ".join(current_arg_desc).strip()
                })
            parts = stripped.split(":", 1)
            arg_name = parts[0].strip()
            arg_type = parts[1].strip() if len(parts) > 1 else ""
            current_arg = arg_name
            current_arg_type = arg_type
            current_arg_desc = []
        elif current_arg and stripped:
            current_arg_desc.append(stripped)
        
        # Arg entries (e.g., "arg_name : type" or "name:type")
        elif current_section == "args" and ":" in stripped:
            # Save previous arg
            if current_arg:
                result["args"].append({
                    "name": current_arg,
                    "type": current_arg_type,
                    "description": " ".join(current_arg_desc).strip()
                })
            
            # Parse new arg - format: "name : type" or "name:type"
            parts = stripped.split(":", 1)
            arg_name = parts[0].strip()
            arg_type = parts[1].strip() if len(parts) > 1 else ""
            
            current_arg = arg_name
            current_arg_type = arg_type
            current_arg_desc = []
        elif current_arg and stripped:
            # Continue description (indented lines)
            current_arg_desc.append(stripped)
        
        # Arg or attribute entries (e.g., "arg_name : type" or "name:type")
        if current_section in ("args", "attributes") and ":" in stripped:
            # Skip if this looks like a section header (empty description after type)
            if stripped.startswith("----"):
                continue
            
            # Save previous arg if it has content
            if current_arg and current_arg_desc:
                desc_text = " ".join(current_arg_desc).strip()
                # Deduplicate if the description appears to be repeated
                words = desc_text.split()
                if len(words) >= 2:
                    mid = len(words) // 2
                    first_half = " ".join(words[:mid])
                    second_half = " ".join(words[mid:])
                    if first_half == second_half:
                        desc_text = first_half
                
                result["args"].append({
                    "name": current_arg,
                    "type": current_arg_type,
                    "description": desc_text
                })
                current_arg = None
                current_arg_type = None
                current_arg_desc = []
            
            # Parse new arg - format: "name : type" or "name:type"
            parts = stripped.split(":", 1)
            arg_name = parts[0].strip()
            arg_type = parts[1].strip() if len(parts) > 1 else ""
            
            # Skip if this is just "arg_name :" with no meaningful type
            if not arg_type:
                current_arg = None
                continue
            
            current_arg = arg_name
            current_arg_type = arg_type
            current_arg_desc = []
        elif current_arg and stripped:
            # Continue description (indented lines)
            current_arg_desc.append(stripped)
        
        # Returns entry
        elif current_section == "returns" and stripped:
            if stripped.startswith("-----") or stripped.startswith("===="):
                continue
            if not result["returns"]:
                result["returns"] = stripped
            else:
                result["returns"] += " " + stripped
                
        # Raises entries
        elif current_section == "raises" and stripped:
            result["raises"].append(stripped)
            
        # Description and examples
        elif stripped:
            if current_section == "description":
                result["description"] += stripped + " "
            elif current_section == "examples":
                result["examples"].append(stripped)
    
    # Add final arg (deduplicate description if needed)
    if current_arg and current_arg_desc:
        desc_text = " ".join(current_arg_desc).strip()
        # Deduplicate if the description appears to be repeated
        words = desc_text.split()
        if len(words) >= 2:
            mid = len(words) // 2
            first_half = " ".join(words[:mid])
            second_half = " ".join(words[mid:])
            if first_half == second_half:
                desc_text = first_half
        
        result["args"].append({
            "name": current_arg,
            "type": current_arg_type,
            "description": desc_text
        })
    
    result["description"] = result["description"].strip()
    return result


def parse_file(filepath):
    """Parse a Python file and extract classes, functions, docstrings.
    
    Args:
        filepath: Path to Python file
        
    Returns:
        dict with 'module', 'classes', 'functions', 'imports'
    """
    with open(filepath, 'r') as f:
        source = f.read()
    
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    
    module_name = filepath.stem
    
    # Find imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    # Find classes and functions
    classes = []
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node)
            classes.append({
                "name": node.name,
                "docstring": parse_docstring(docstring),
                "line": node.lineno,
                "methods": [
                    {
                        "name": n.name,
                        "docstring": parse_docstring(ast.get_docstring(n)),
                        "line": n.lineno
                    }
                    for n in node.body
                    if isinstance(n, ast.FunctionDef)
                ]
            })
        elif isinstance(node, ast.FunctionDef):
            # Only top-level functions
            if node.col_offset == 0:
                docstring = ast.get_docstring(node)
                functions.append({
                    "name": node.name,
                    "docstring": parse_docstring(docstring),
                    "line": node.lineno
                })
    
    return {
        "module": module_name,
        "file": str(filepath),
        "imports": imports,
        "classes": classes,
        "functions": functions
    }


def get_test_coverage():
    """Get test coverage information.
    
    Returns:
        dict with test count and test names
    """
    test_file = PROJECT_ROOT / "test_runner.py"
    if not test_file.exists():
        return {"total": 0, "tests": []}
    
    with open(test_file, 'r') as f:
        source = f.read()
    
    # Count tests
    test_names = re.findall(r'^def (test_\w+)', source, re.MULTILINE)
    
    return {
        "total": len(test_names),
        "tests": test_names
    }


def get_import_graph():
    """Build import dependency graph.
    
    Returns:
        dict mapping modules to their dependencies
    """
    graph = {}
    
    for filepath in get_python_files():
        data = parse_file(filepath)
        if data:
            # Filter to local imports only
            local_imports = [
                imp for imp in data["imports"]
                if not imp.startswith("_")
                and not imp.startswith("os")
                and not imp.startswith("sys")
                and not imp.startswith("datetime")
                and not imp.startswith("math")
                and not imp.startswith("random")
                and not imp.startswith("threading")
                and not imp.startswith("heapq")
                and not imp.startswith("functools")
                and not imp.startswith("pickle")
                and not imp.startswith("argparse")
                and not imp.startswith("pprint")
                and not imp.startswith("copy")
                and not imp.startswith("numpy")
                and not imp.startswith("torch")
                and not imp.startswith("sklearn")
                and not imp.startswith("pandas")
            ]
            graph[data["module"]] = local_imports
    
    return graph


def generate_html(parsed_files, test_coverage, import_graph):
    """Generate HTML documentation.
    
    Args:
        parsed_files: List of parsed file data
        test_coverage: Test coverage info
        import_graph: Import dependency graph
        
    Returns:
        HTML string
    """
    # Count classes
    class_count = sum(len(f.get("classes", [])) for f in parsed_files)
    
    # Build HTML in sections
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BulkBro Documentation</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: #2c3e50; color: white; padding: 30px 0; margin-bottom: 30px; }
        header h1 { font-size: 2.5em; }
        header p { opacity: 0.8; margin-top: 10px; }
        .nav { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav a { margin-right: 20px; color: #3498db; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
        .section { background: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }
        .section h3 { color: #34495e; margin: 20px 0 10px; }
        .module { margin-bottom: 30px; }
        .class, .function { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px; border-left: 4px solid #3498db; }
        .class h4, .function h4 { color: #2c3e50; margin-bottom: 10px; }
        .class h4 { color: #e74c3c; }
        .docstring { color: #555; margin: 10px 0; }
        .args, .returns, .raises { margin: 10px 0; padding-left: 20px; }
        .args li, .raises li { margin: 5px 0; }
        .returns { font-style: italic; }
        .code { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .code pre { margin: 0; }
        .test-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
        .test-item { background: #e8f5e9; padding: 8px 12px; border-radius: 4px; }
        .graph { display: flex; flex-wrap: wrap; gap: 10px; }
        .graph-node { background: #3498db; color: white; padding: 8px 15px; border-radius: 20px; }
        .graph-node.local { background: #e74c3c; }
        .graph-arrow { color: #999; }
        footer { text-align: center; padding: 20px; color: #777; }
        .stats { display: flex; gap: 30px; margin: 20px 0; }
        .stat { background: #f8f9fa; padding: 15px 25px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { color: #777; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>BulkBro Documentation</h1>
            <p>Meal Planning and Nutrition Optimization System</p>
        </div>
    </header>
    
    <div class="container">
        <nav class="nav">
            <a href="#overview">Overview</a>
            <a href="#api">API</a>
            <a href="#tests">Tests</a>
            <a href="#architecture">Architecture</a>
        </nav>
        
        <section id="overview" class="section">
            <h2>Overview</h2>
            <p>BulkBro is a meal planning and nutrition optimization system using Harmony Search algorithm. 
            It optimizes meal plans to meet nutritional targets while minimizing cost and waste.</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">""" + str(len(parsed_files)) + """</div>
                    <div class="stat-label">Python Files</div>
                </div>
                <div class="stat">
                    <div class="stat-value">""" + str(test_coverage["total"]) + """</div>
                    <div class="stat-label">Tests</div>
                </div>
                <div class="stat">
                    <div class="stat-value">""" + str(class_count) + """</div>
                    <div class="stat-label">Classes</div>
                </div>
            </div>
        </section>
        
        <section id="api" class="section">
            <h2>API Reference</h2>
"""
    
    # Add module documentation
    for pf in parsed_files:
        module = pf["module"]
        html += '<div class="module" id="' + module + '">\n'
        html += '<h3>Module: ' + module + '</h3>\n'
        
        # Classes
        for cls in pf.get("classes", []):
            html += '<div class="class">\n'
            html += '<h4>' + cls["name"] + '</h4>\n'
            
            doc = cls.get("docstring", {})
            if doc.get("description"):
                html += '<p class="docstring">' + doc["description"] + '</p>\n'
            
            if doc.get("args"):
                html += '<div class="args"><strong>Parameters</strong><br><strong>----------</strong><ul>\n'
                for arg in doc["args"]:
                    type_str = f" : {arg['type']}" if arg.get("type") else ""
                    html += '<li><code>' + arg["name"] + '</code>' + type_str + ' — ' + arg["description"] + '</li>\n'
                html += '</ul></div>\n'
            
            if doc.get("returns"):
                html += '<div class="returns"><strong>Returns</strong><br><strong>-------</strong><br>' + doc["returns"] + '</div>\n'
            
            if doc.get("raises"):
                html += '<div class="raises"><strong>Raises</strong><br><strong>------</strong><ul>\n'
                for r in doc["raises"]:
                    html += '<li>' + r + '</li>\n'
                html += '</ul></div>\n'
            
            # Methods
            for method in cls.get("methods", []):
                html += '<div class="function"><h5>' + method["name"] + '()</h5>\n'
                mdoc = method.get("docstring", {})
                if mdoc.get("description"):
                    html += '<p class="docstring">' + mdoc["description"] + '</p>\n'
                html += '</div>\n'
            
            html += '</div>\n'
        
        # Functions
        for func in pf.get("functions", []):
            html += '<div class="function">\n'
            html += '<h4>' + func["name"] + '()</h4>\n'
            
            doc = func.get("docstring", {})
            if doc.get("description"):
                html += '<p class="docstring">' + doc["description"] + '</p>\n'
            
            if doc.get("args"):
                html += '<div class="args"><strong>Parameters</strong><br><strong>----------</strong><ul>\n'
                for arg in doc["args"]:
                    type_str = f" : {arg['type']}" if arg.get("type") else ""
                    html += '<li><code>' + arg["name"] + '</code>' + type_str + ' — ' + arg["description"] + '</li>\n'
                html += '</ul></div>\n'
            
            if doc.get("returns"):
                html += '<div class="returns"><strong>Returns</strong><br><strong>-------</strong><br>' + doc["returns"] + '</div>\n'
            
            html += '</div>\n'
        
        html += '</div>\n'
    
    html += """
        </section>
        
        <section id="tests" class="section">
            <h2>Test Coverage</h2>
            <p>Total Tests: """ + str(test_coverage["total"]) + """</p>
            <div class="test-list">
"""
    
    for test in test_coverage["tests"]:
        html += '<div class="test-item">' + test + '</div>\n'
    
    html += """
            </div>
        </section>
        
        <section id="architecture" class="section">
            <h2>Architecture</h2>
            <h3>Module Dependencies</h3>
"""
    
    # Add import graph
    for module, deps in import_graph.items():
        if deps:
            html += '<div class="graph">\n'
            html += '<span class="graph-node">' + module + '</span>\n'
            for dep in deps:
                html += '<span class="graph-arrow">→</span>\n'
                html += '<span class="graph-node local">' + dep + '</span>\n'
            html += '</div>\n'
    
    html += """
        </section>
    </div>
    
    <footer>
        <p>Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</p>
    </footer>
</body>
</html>
"""
    
    return html


def generate_api_markdown(parsed_files):
    """Generate API documentation in Markdown format."""
    md = "# BulkBro API Reference\n\n"
    
    for pf in parsed_files:
        module = pf["module"]
        md += f"\n## Module: {module}\n\n"
        
        for cls in pf.get("classes", []):
            md += f"### Class: {cls['name']}\n\n"
            
            doc = cls.get("docstring", {})
            if doc.get("description"):
                md += f"{doc['description']}\n\n"
            
            if doc.get("args"):
                md += "**Parameters**\n"
                md += "----------\n"
                for arg in doc["args"]:
                    type_str = f" : {arg['type']}" if arg.get("type") else ""
                    md += f"{arg['name']}{type_str}\n    {arg['description']}\n"
                md += "\n"
            
            if doc.get("returns"):
                md += "**Returns**\n"
                md += "-------\n"
                md += f"{doc['returns']}\n\n"
        
        for func in pf.get("functions", []):
            md += f"### Function: {func['name']}()\n\n"
            
            doc = func.get("docstring", {})
            if doc.get("description"):
                md += f"{doc['description']}\n\n"
            
            if doc.get("args"):
                md += "**Parameters**\n"
                md += "----------\n"
                for arg in doc["args"]:
                    type_str = f" : {arg['type']}" if arg.get("type") else ""
                    md += f"{arg['name']}{type_str}\n    {arg['description']}\n"
                md += "\n"
            
            if doc.get("returns"):
                md += "**Returns**\n"
                md += "-------\n"
                md += f"{doc['returns']}\n\n"
    
    return md


def main():
    parser = argparse.ArgumentParser(description="BulkBro Documentation Generator")
    parser.add_argument("--api", action="store_true", help="Generate API markdown only")
    parser.add_argument("--tests", action="store_true", help="Show test coverage only")
    parser.add_argument("--html", action="store_true", help="Generate HTML docs")
    args = parser.parse_args()
    
    # If no args, generate all
    if not any([args.api, args.tests, args.html]):
        args.html = True
        args.api = True
    
    print("Parsing Python files...")
    parsed_files = []
    for f in get_python_files():
        data = parse_file(f)
        if data:
            parsed_files.append(data)
    
    print(f"Found {len(parsed_files)} modules")
    
    if args.tests or args.html:
        print("Analyzing test coverage...")
        test_coverage = get_test_coverage()
        print(f"Found {test_coverage['total']} tests")
    
    if args.html:
        print("Building import graph...")
        import_graph = get_import_graph()
        
        print("Generating HTML...")
        html = generate_html(parsed_files, test_coverage, import_graph)
        
        DOCS_DIR.mkdir(exist_ok=True)
        with open(DOCS_DIR / "index.html", "w") as f:
            f.write(html)
        print(f"HTML docs written to {DOCS_DIR / 'index.html'}")
    
    if args.api:
        print("Generating Markdown API docs...")
        md = generate_api_markdown(parsed_files)
        
        DOCS_DIR.mkdir(exist_ok=True)
        with open(DOCS_DIR / "api.md", "w") as f:
            f.write(md)
        print(f"Markdown API docs written to {DOCS_DIR / 'api.md'}")
    
    if args.tests:
        print(f"\nTest Coverage: {test_coverage['total']} tests")
        print("Tests:")
        for test in test_coverage["tests"]:
            print(f"  - {test}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
