#!/usr/bin/env python3
"""
Tree4Ferox.py - Cyber Theme com abertura de arquivos (VERSÃO CORRIGIDA)
"""

import json
import sys
import re
from collections import defaultdict

def parse_feroxbuster_jsonl(file_path):
    """Parse do formato JSON lines do Feroxbuster"""
    paths_with_urls = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                
                if data.get('type') == 'configuration':
                    continue
                
                if 'url' in data:
                    url = data['url']
                    path = extract_path(url)
                    if path and path != '/':
                        paths_with_urls[path] = url
                        print(f"  [+] Encontrado: {path}")
                        
            except json.JSONDecodeError:
                continue
    
    return paths_with_urls

def extract_path(url):
    """Extrai o caminho da URL"""
    match = re.search(r'https?://[^/]+(/.*)', url)
    if match:
        path = match.group(1)
        path = re.sub(r'[?#].*$', '', path)
        return path.rstrip('/')
    return '/'

def build_tree(paths_with_urls):
    """Constrói árvore de diretórios com URLs associadas"""
    tree = {}
    
    # Ordenar paths para garantir consistência
    sorted_paths = sorted(paths_with_urls.keys())
    
    for path in sorted_paths:
        url = paths_with_urls[path]  # Pega a URL do dicionário original
        
        if path == '/' or path == '':
            continue
        
        # Remove leading slash
        clean_path = path.lstrip('/')
        if not clean_path:
            continue
        
        parts = clean_path.split('/')
        current = tree
        
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            
            if part not in current:
                if is_last:
                    # É um arquivo (último elemento)
                    current[part] = {
                        '__url__': url,
                        '__is_file__': True
                    }
                else:
                    # É um diretório
                    current[part] = {}
            
            elif is_last and isinstance(current[part], dict):
                # Atualizar arquivo existente com URL
                current[part]['__url__'] = url
                current[part]['__is_file__'] = True
            
            # Navegar para o próximo nível
            if not is_last:
                if isinstance(current[part], dict):
                    current = current[part]
                else:
                    # Se não for dict, criar um
                    current[part] = {}
                    current = current[part]
    
    return tree

def clean_tree(node):
    """Remove os metadados para o JSON, mantendo apenas estrutura"""
    if isinstance(node, dict):
        result = {}
        for k, v in node.items():
            if k.startswith('__'):
                continue
            result[k] = clean_tree(v)
        return result
    return node

def generate_html(tree, paths_with_urls, output_file='tree4ferox.html'):
    """Gera HTML cyber theme"""
    
    total_files = len([p for p in paths_with_urls.keys() if '.' in p.split('/')[-1]])
    total_dirs = len([p for p in paths_with_urls.keys() if '.' not in p.split('/')[-1]])
    
    html = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tree4Ferox - Cyber Recon</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Share Tech Mono', 'Consolas', monospace;
            background: radial-gradient(circle at 20% 50%, #0a0a0a 0%, #000000 100%);
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }
        
        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 30px 30px;
            pointer-events: none;
            z-index: 0;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(10, 20, 30, 0.85);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 0 50px rgba(0, 255, 255, 0.2), 0 0 0 2px rgba(0, 255, 255, 0.1);
            overflow: hidden;
            border: 1px solid #0ff;
            position: relative;
            z-index: 1;
        }
        
        .header {
            background: linear-gradient(135deg, #0a0a0a 0%, #001a1a 100%);
            color: #0ff;
            padding: 30px;
            text-align: center;
            border-bottom: 2px solid #0ff;
            position: relative;
        }
        
        .header::after {
            content: ">";
            position: absolute;
            bottom: 10px;
            right: 20px;
            font-size: 12px;
            opacity: 0.5;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 0; }
        }
        
        .header h1 {
            font-size: 32px;
            text-shadow: 0 0 10px #0ff, 0 0 20px #0ff;
            letter-spacing: 2px;
        }
        
        .header h1::before {
            content: "🌲 ";
            filter: drop-shadow(0 0 5px #0ff);
        }
        
        .header p {
            opacity: 0.8;
            font-size: 14px;
            color: #0fa;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: rgba(0, 0, 0, 0.6);
            border-bottom: 1px solid rgba(0, 255, 255, 0.3);
        }
        
        .stat-card {
            text-align: center;
            background: rgba(0, 20, 20, 0.8);
            padding: 15px 30px;
            border-radius: 10px;
            border: 1px solid #0ff;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
        }
        
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #0ff;
            text-shadow: 0 0 5px #0ff;
        }
        
        .stat-label {
            font-size: 12px;
            color: #0fa;
            margin-top: 5px;
        }
        
        .search-box {
            padding: 20px 30px;
            background: rgba(0, 0, 0, 0.6);
            border-bottom: 1px solid rgba(0, 255, 255, 0.3);
        }
        
        .search-box input {
            width: 100%;
            padding: 12px 20px;
            background: #0a0a0a;
            border: 1px solid #0ff;
            border-radius: 10px;
            font-size: 14px;
            color: #0ff;
            font-family: 'Share Tech Mono', monospace;
        }
        
        .search-box input:focus {
            outline: none;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
        }
        
        .search-box input::placeholder {
            color: #0a6;
        }
        
        .tree-container {
            padding: 30px;
            background: rgba(0, 0, 0, 0.4);
            max-height: 65vh;
            overflow-y: auto;
        }
        
        .tree-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .tree-container::-webkit-scrollbar-track {
            background: #0a0a0a;
            border-radius: 10px;
        }
        
        .tree-container::-webkit-scrollbar-thumb {
            background: #0ff;
            border-radius: 10px;
        }
        
        .tree {
            font-family: 'Share Tech Mono', 'Consolas', monospace;
            font-size: 13px;
            line-height: 1.8;
            color: #0fa;
        }
        
        .tree-node {
            list-style: none;
            margin-left: 0;
            padding-left: 0;
        }
        
        .node-content {
            cursor: pointer;
            user-select: none;
            padding: 4px 12px;
            border-radius: 6px;
            display: inline-block;
            transition: all 0.2s;
        }
        
        .tree-node.directory > .node-content:hover {
            background: rgba(0, 255, 255, 0.1);
            text-shadow: 0 0 5px #0ff;
            box-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
        }
        
        .tree-node.file > .node-content {
            cursor: pointer;
        }
        
        .tree-node.file > .node-content:hover {
            background: rgba(0, 255, 200, 0.15);
            text-shadow: 0 0 3px #0fa;
        }
        
        .tree-node.directory > .node-content {
            font-weight: 600;
            color: #0ff;
        }
        
        .tree-node.file > .node-content {
            color: #0fa;
        }
        
        .toggle-icon {
            display: inline-block;
            width: 20px;
            font-size: 14px;
            margin-right: 5px;
        }
        
        .children {
            margin-left: 24px;
            padding-left: 0;
            display: block;
        }
        
        .children.collapsed {
            display: none;
        }
        
        .badge {
            display: inline-block;
            background: rgba(0, 255, 255, 0.15);
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 10px;
            margin-left: 10px;
            color: #0fa;
            border: 1px solid rgba(0, 255, 255, 0.3);
        }
        
        .url-tooltip {
            display: none;
            position: absolute;
            background: #0a0a0a;
            border: 1px solid #0ff;
            color: #0ff;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 11px;
            white-space: nowrap;
            z-index: 1000;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
        }
        
        .footer {
            background: rgba(0, 0, 0, 0.6);
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #0a6;
            border-top: 1px solid rgba(0, 255, 255, 0.3);
        }
        
        .status-led {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #0f0;
            box-shadow: 0 0 5px #0f0;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Tree4Ferox</h1>
            <p><span class="status-led"></span> CYBER RECONNAISSANCE MODE | Clique em 📄 para abrir em nova aba</p>
        </div>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder=">_ buscar arquivo/diretório..." autocomplete="off">
        </div>
        
        <div class="stats" id="stats"></div>
        
        <div class="tree-container">
            <div class="tree" id="tree"></div>
        </div>
        
        <div class="footer">
            <span>📊 TOTAL: <span id="totalCount">0</span> recursos</span>
            <span style="margin-left: 20px;">📁 DIRS: <span id="dirsCount">0</span></span>
            <span style="margin-left: 20px;">📄 FILES: <span id="filesCount">0</span></span>
            <span style="margin-left: 20px;">🔗 Clique nos arquivos para abrir</span>
            <span style="margin-left: 20px;">🌲 Tree4Ferox v3.0</span>
        </div>
    </div>
    
    <div id="tooltip" class="url-tooltip"></div>
    
    <script>
        const treeData = ''' + json.dumps(clean_tree(tree), indent=2) + ''';
        const urlsMap = ''' + json.dumps(paths_with_urls) + ''';
        
        console.log("🌲 Tree4Ferox Carregado");
        console.log("URLs mapeadas:", Object.keys(urlsMap).length);
        
        const tooltip = document.getElementById('tooltip');
        
        function showTooltip(event, text) {
            tooltip.style.display = 'block';
            tooltip.style.left = (event.pageX + 15) + 'px';
            tooltip.style.top = (event.pageY - 10) + 'px';
            tooltip.textContent = text;
        }
        
        function hideTooltip() {
            tooltip.style.display = 'none';
        }
        
        function openUrl(url, event) {
            event.stopPropagation();
            if (url) {
                console.log("Abrindo URL:", url);
                window.open(url, '_blank');
            }
        }
        
        function createTree(node, currentPath) {
            currentPath = currentPath || '';
            const ul = document.createElement('ul');
            ul.className = 'tree-root';
            
            const keys = Object.keys(node).sort();
            
            for (const key of keys) {
                const li = document.createElement('li');
                const isDirectory = Object.keys(node[key]).length > 0;
                const fullPath = currentPath + '/' + key;
                const fullPathNormalized = fullPath.replace(/^\/+/, '/');
                
                li.className = isDirectory ? 'tree-node directory' : 'tree-node file';
                li.setAttribute('data-name', key);
                li.setAttribute('data-path', fullPathNormalized);
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'node-content';
                
                const icon = document.createElement('span');
                icon.className = 'toggle-icon';
                icon.textContent = isDirectory ? '📁 ' : '📄 ';
                
                const nameSpan = document.createElement('span');
                nameSpan.textContent = key;
                
                contentDiv.appendChild(icon);
                contentDiv.appendChild(nameSpan);
                
                if (isDirectory) {
                    const badge = document.createElement('span');
                    badge.className = 'badge';
                    const childCount = Object.keys(node[key]).length;
                    badge.textContent = childCount + ' item' + (childCount !== 1 ? 's' : '');
                    contentDiv.appendChild(badge);
                    
                    li.appendChild(contentDiv);
                    
                    const childrenDiv = document.createElement('div');
                    childrenDiv.className = 'children collapsed';
                    childrenDiv.appendChild(createTree(node[key], fullPathNormalized));
                    li.appendChild(childrenDiv);
                    
                    contentDiv.addEventListener('click', function(e) {
                        e.stopPropagation();
                        const children = li.querySelector('.children');
                        if (children) {
                            children.classList.toggle('collapsed');
                            const iconSpan = contentDiv.querySelector('.toggle-icon');
                            if (children.classList.contains('collapsed')) {
                                iconSpan.textContent = '📁 ';
                            } else {
                                iconSpan.textContent = '📂 ';
                            }
                        }
                    });
                    
                    contentDiv.addEventListener('mouseenter', function(e) {
                        showTooltip(e, '📁 ' + key + ' - Clique para expandir');
                    });
                    contentDiv.addEventListener('mouseleave', hideTooltip);
                    
                } else {
                    const fileUrl = urlsMap[fullPathNormalized];
                    
                    if (fileUrl) {
                        contentDiv.style.cursor = 'pointer';
                        
                        contentDiv.addEventListener('click', function(e) {
                            openUrl(fileUrl, e);
                        });
                        
                        contentDiv.addEventListener('mouseenter', function(e) {
                            showTooltip(e, '📄 ' + key + '\\n🔗 ' + fileUrl);
                        });
                        contentDiv.addEventListener('mouseleave', hideTooltip);
                    }
                    
                    li.appendChild(contentDiv);
                }
                
                ul.appendChild(li);
            }
            
            return ul;
        }
        
        function countAllNodes(node) {
            let count = 0;
            for (const key in node) {
                count++;
                if (Object.keys(node[key]).length > 0) {
                    count += countAllNodes(node[key]);
                }
            }
            return count;
        }
        
        function countTypesAll(node) {
            let dirs = 0, files = 0;
            for (const key in node) {
                if (Object.keys(node[key]).length > 0) {
                    dirs++;
                    const childCounts = countTypesAll(node[key]);
                    dirs += childCounts.dirs;
                    files += childCounts.files;
                } else {
                    files++;
                }
            }
            return { dirs, files };
        }
        
        function searchTree() {
            const term = document.getElementById('searchInput').value.toLowerCase().trim();
            const allItems = document.querySelectorAll('.tree-node');

            // Quando a busca estiver vazia, mostra tudo e recolhe os diretórios
            if (term === '') {
                allItems.forEach(item => {
                    item.style.display = '';

                    const children = item.querySelector(':scope > .children');
                    const icon = item.querySelector(':scope > .node-content .toggle-icon');

                    if (children) {
                        children.classList.add('collapsed');
                        if (icon) icon.textContent = '📁 ';
                    }
                });
                return;
            }

            // Primeiro oculta todos os nós da árvore
            allItems.forEach(item => {
                item.style.display = 'none';
            });

            // Depois mostra os resultados encontrados e todos os seus diretórios pais
            allItems.forEach(item => {
                const name = item.getAttribute('data-name')?.toLowerCase() || '';
                const path = item.getAttribute('data-path')?.toLowerCase() || '';

                if (name.includes(term) || path.includes(term)) {
                    item.style.display = '';

                    let parent = item.parentElement;

                    while (parent) {
                        if (parent.classList && parent.classList.contains('children')) {
                            parent.classList.remove('collapsed');

                            const parentLi = parent.closest('.tree-node');
                            if (parentLi) {
                                parentLi.style.display = '';

                                const parentIcon = parentLi.querySelector(':scope > .node-content .toggle-icon');
                                if (parentIcon) parentIcon.textContent = '📂 ';
                            }
                        }

                        parent = parent.parentElement;
                    }
                }
            });
        }
        
        const treeContainer = document.getElementById('tree');
        
        if (Object.keys(treeData).length === 0) {
            treeContainer.innerHTML = '<div style="text-align:center;padding:50px;color:#0a6;">⚠️ NENHUM DIRETÓRIO ENCONTRADO</div>';
        } else {
            const treeElement = createTree(treeData);
            treeContainer.appendChild(treeElement);
        }
        
        const total = countAllNodes(treeData);
        const { dirs, files } = countTypesAll(treeData);
        
        document.getElementById('totalCount').textContent = total;
        document.getElementById('dirsCount').textContent = dirs;
        document.getElementById('filesCount').textContent = files;
        document.getElementById('stats').innerHTML = `
            <div class="stat-card"><div class="stat-number">${total}</div><div class="stat-label">TOTAL</div></div>
            <div class="stat-card"><div class="stat-number">${dirs}</div><div class="stat-label">DIRETÓRIOS</div></div>
            <div class="stat-card"><div class="stat-number">${files}</div><div class="stat-label">ARQUIVOS</div></div>
        `;
        
        document.getElementById('searchInput').addEventListener('keyup', searchTree);
        
        console.log("🌲 Árvore renderizada!");
    </script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("""
🌲 Tree4Ferox - Cyber Reconnaissance Tool

Uso: python3 Tree4Ferox.py arquivo_scan.txt [output.html]

Exemplo:
  python3 Tree4Ferox.py exp_web.txt
  python3 Tree4Ferox.py exp_web.txt recon.html
""")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'tree4ferox_cyber.html'
    
    print("""
    ╔═══════════════════════════════════════╗
    ║   🌲 Tree4Ferox - Cyber Mode 🌲       ║
    ║   Gerando árvore interativa...        ║
    ╚═══════════════════════════════════════╝
    """)
    
    print(f"📁 Lendo: {input_file}")
    print("\n📂 Arquivos encontrados:")
    
    paths_with_urls = parse_feroxbuster_jsonl(input_file)
    
    print(f"\n✓ Total de {len(paths_with_urls)} recursos únicos\n")
    
    if len(paths_with_urls) > 0:
        tree = build_tree(paths_with_urls)
        generate_html(tree, paths_with_urls, output_file)
        
        files_count = len([p for p in paths_with_urls if '.' in p.split('/')[-1]])
        dirs_count = len([p for p in paths_with_urls if '.' not in p.split('/')[-1] and p != ''])
        
        print("📊 ESTATÍSTICAS:")
        print(f"   📁 Diretórios: {dirs_count}")
        print(f"   📄 Arquivos: {files_count}")
        print(f"   🔗 Total: {len(paths_with_urls)}")
        
        print(f"\n✅ Árvore HTML gerada: {output_file}")
        print(f"🌐 Abra no navegador: {output_file}")
        print("\n💡 Clique em qualquer arquivo para abrir em nova aba!")
        
    else:
        print("\n⚠️ NENHUM recurso encontrado!")

if __name__ == "__main__":
    main()
