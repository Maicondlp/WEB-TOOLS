### Tree4Ferox - Guia de Uso

Ferramenta para transformar a saída do feroxbuster em uma árvore interativa HTML, facilitando a visualização de diretórios e arquivos descobertos durante enumeração web.

#### 🚀 Passo a passo
###### Executar o feroxbuster

Primeiro, rode o scan com saída em JSON:

feroxbuster -u http://dominio:15808/ \
    -H "Host: dominio:15808" \
    -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-big.txt \
    -x txt,php,ini,info,config \
    -d 8 \
    -o exp_web.txt \
    --json

###### Gerar a árvore interativa

Depois do scan, execute:

python3 Tree4Ferox.py exp_web.txt exp_web.html
