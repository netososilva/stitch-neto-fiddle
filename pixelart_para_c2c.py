from PIL import Image
from collections import Counter
import base64
from html import escape
from io import BytesIO
import json
import string
import sys
import os
import zipfile

# ==========================
# Verificação dos argumentos
# ==========================

if len(sys.argv) != 2:
    print("Uso:")
    print("python pixelart_para_c2c.py <arquivo.png>")
    sys.exit(1)

ARQUIVO = sys.argv[1]

if not os.path.isfile(ARQUIVO):
    print(f"Arquivo '{ARQUIVO}' não encontrado.")
    sys.exit(1)

# ==========================
# Leitura da imagem
# ==========================

img = Image.open(ARQUIVO).convert("RGB")

largura, altura = img.size
pixels = img.load()

contador = Counter()

for y in range(altura):
    for x in range(largura):
        contador[pixels[x, y]] += 1


# ==========================
# Geração dos códigos
# ==========================

def cor_texto(r, g, b):
    if r < 140 and g < 140 and b < 140:
        return "white"

    return "black"


def nome_cor(r,g,b):
    import math

    # Paleta extensa de referência (RGB)
    PALETA=[
        ("Preto",(0,0,0)),("Branco",(255,255,255)),
        ("Cinza Escuro",(80,80,80)),("Cinza",(128,128,128)),("Cinza Claro",(200,200,200)),
        ("Creme",(245,245,220)),("Marfim",(255,255,240)),("Bege",(220,210,180)),
        ("Areia",(194,178,128)),("Caqui",(189,183,107)),
        ("Amarelo",(255,255,0)),("Mostarda",(205,171,45)),
        ("Laranja",(255,165,0)),("Terracota",(204,120,92)),
        ("Marrom",(139,69,19)),("Chocolate",(123,63,0)),("Caramelo",(175,111,9)),
        ("Vermelho",(220,20,60)),("Vinho",(114,47,55)),("Bordô",(128,0,32)),
        ("Rosa",(255,105,180)),("Rosa Claro",(255,182,193)),("Coral",(255,127,80)),
        ("Magenta",(255,0,255)),("Lilás",(200,162,200)),("Lavanda",(181,126,220)),
        ("Roxo",(128,0,128)),
        ("Verde Limão",(124,252,0)),("Verde Claro",(144,238,144)),
        ("Verde",(34,139,34)),("Verde Escuro",(0,100,0)),
        ("Oliva",(107,142,35)),("Musgo",(85,107,47)),("Esmeralda",(46,125,50)),
        ("Turquesa",(64,224,208)),("Ciano",(0,255,255)),
        ("Azul Claro",(135,206,235)),("Azul",(30,144,255)),
        ("Azul Marinho",(0,0,128)),("Petróleo",(0,95,106))
    ]

    # Regra especial para verdes muito escuros
    if g>r*1.4 and g>=b and max(r,g,b)<45:
        return "Verde Escuro"

    melhor=None
    dist=1e9
    for nome,(cr,cg,cb) in PALETA:
        d=(r-cr)**2+(g-cg)**2+(b-cb)**2
        if d<dist:
            dist=d
            melhor=nome
    return melhor

def codigo(n):
    letras = string.ascii_uppercase
    s = ""
    n += 1

    while n:
        n, r = divmod(n - 1, 26)
        s = letras[r] + s

    return s


cores = sorted(contador.keys())

mapa = {
    cor: codigo(i)
    for i, cor in enumerate(cores)
}

base = os.path.splitext(ARQUIVO)[0]
saida = base + ".html"

# ==========================
# HTML
# ==========================

html = []

html.append("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
""")

html.append(f"<title>{os.path.basename(ARQUIVO)}</title>")

html.append("""
<style>

body{
    font-family:Arial;
    margin:20px;
    background:#f4f4f4;
}

table{
    border-collapse:collapse;
}

#grid td{

    width:22px;
    height:22px;

    border:1px solid #888;

    text-align:center;
    vertical-align:middle;

    font-size:11px;
    font-weight:bold;

    cursor:pointer;
    user-select:none;

}

#grid_print{
    display:table;
    margin:15px 0;
}
#grid_print td{width:6px;height:6px;border:none;padding:0;}
#grid{display:none;}

#receita_print{
    display:none;
}
            
#titulo-grafico-print{
    display:none;
}

#grid th{
    position:sticky;
    background:#ddd;
    border:1px solid #888;
    font-size:11px;
    min-width:22px;
    height:22px;
    text-align:center;
}

#legenda td,#legenda th{

    border:1px solid #aaa;
    padding:6px 10px;
    background:white;

}

.cor{
    width:28px;
    height:28px;
    border:1px solid black;
}
            
@media print {

    @page{
        margin:15mm;
    }

    html,body{
        margin:0!important;
        padding:0!important;
    }

    h1,h2{
        margin-top:0!important;
    }

    *{
        -webkit-print-color-adjust:exact !important;
        print-color-adjust:exact !important;
        text-shadow:none !important;
    }

    :root{
        --bg:#fff !important;
        --text:#000 !important;
        --panel:#fff !important;
        --border:#888 !important;
        --header:#ddd !important;
        --button:#fff !important;
        --progress:#4CAF50 !important;
    }

    html,body{
        background:#fff !important;
        margin:0 !important;
        padding:0 !important;
    }

    body{
        background:#fff !important;
    }

    #painel_c2c{
        display:block !important;
        background:#fff !important;
        width:auto !important;
        max-width:none !important;
        margin:0 !important;
        padding:0 !important;
        border:none !important;
        border-radius:0 !important;
        box-shadow:none !important;
        position:static !important;
        left:auto !important;
        right:auto !important;
        top:auto !important;
        transform:none !important;
    }

    table,#legenda td,#legenda th{
        background:#fff !important;
        border-color:#888 !important;
    }
    #receita_tela,#controles,#configuracoes,#containerBarra,#textoProgresso,#linhaAtual,#infoLinha,#atalhos,#btnCores,button[onclick="abrirGrafico()"]{display:none !important;}

    #titulo-grafico,#grid{display:none !important;}
    #titulo-grafico-print,#grid_print,#receita_print,#informacoes,#tituloCores,#legenda{display:block !important;}
    #titulo-grafico-print{margin-top:20px !important;margin-bottom:8px !important;}
    #grid_print{display:table !important;border-collapse:collapse;margin-bottom:15px;}
    #grid_print td{width:2px;height:2px;border:none;padding:0;}
    .linha_receita{
        font-size:12px !important;
        line-height:1.6 !important;
        margin:2px 0 !important;
    }
    body.pdf-mode .linha_receita{
        font-size:14px !important;
        line-height:2.1 !important;
        margin:8px 0 !important;
    }
    body.pdf-mode .numero{
        width:55px !important;
        flex-basis:55px !important;
    }
    #legenda{display:table !important;break-inside:avoid;}
}

@media screen{
    #receita_print{display:none;}
}

.cor,
#grid td,
[style*="background"]{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}  

.linha_receita{
    margin:2px 0;
    font-family:Consolas, monospace;
    font-size:14px;
    line-height:1.6;
    display:flex;
    align-items:flex-start;
    flex-wrap:wrap;
}
.numero{
    flex:0 0 48px;
}
.linha_receita::after{
    content:"";
    flex-basis:100%;
    height:0;
}

.numero{
    display:inline-block;
    width:40px;
    font-weight:bold;
}

.bloco{
    display:inline-block;
    padding:2px 6px;
    margin:1px;
    border:1px solid #000;
    font-weight:bold;
    border-radius:3px;
} 

button,
input[type="number"]{
    height:28px;
    padding:2px 8px;
    box-sizing:border-box;
    font-size:13px;
    vertical-align:middle;
}

button{
    margin-left:0;
}

#irLinha{
    width:70px;
    margin:0 4px;
}

#controles{
    display:flex;
    align-items:center;
    gap:6px;
    flex-wrap:wrap;
    margin-bottom:10px;
}

#atalhos{
    margin-top:10px;
    font-size:13px;
    color:#666;
    line-height:1.4;
}

body.focus-mode #informacoes{display:none!important;}
#atalhos{margin-top:14px;font-size:13px;color:#666;}
#btnCores{display:none;}
#layout{display:none;}
body.focus-mode #layout{display:inline-block;}
body.focus-mode span.layoutLabel{display:inline;}
span.layoutLabel{display:none;}
body.focus-mode #btnCores{display:inline-block;}
body.focus-mode #grid,
body.focus-mode #titulo-grafico,
body.focus-mode #grid_print,
body.focus-mode #titulo-grafico-print,
body.focus-mode button[onclick="abrirGrafico()"]{display:none!important;}
body.focus-mode:not(.showMini) #titulo-grafico,
body.focus-mode:not(.showMini) #titulo-grafico-print,
body.focus-mode:not(.showMini) #grid_print,
body.focus-mode:not(.showMini) button[onclick="abrirGrafico()"]{display:none!important;}
body.focus-mode.showMini #titulo-grafico-print{display:block!important;}
body.focus-mode.showMini #grid_print{display:table!important;}
body.focus-mode.layout-left #grid_print{margin-left:0;margin-right:auto;}
body.focus-mode.layout-center #grid_print{margin-left:auto;margin-right:auto;}
body.focus-mode.layout-right #grid_print{margin-left:auto;margin-right:0;}
body.focus-mode.showMini #titulo-grafico-print{display:block!important;}
body.focus-mode.showMini #grid_print{display:table!important;}

.bloco_receita{
    display:inline-block;

    display:inline-block;
    padding:1px 8px;   /* espaço interno */
    margin:0;          /* nenhum espaço externo */
    border:1px solid #000;
    font-weight:bold;
}


:root{
 --bg:#f4f4f4;--text:#111;--panel:#fff;--border:#888;--header:#ddd;--button:#f0f0f0;--progress:#4CAF50;
}
@media screen{
body{
    background:var(--bg)!important;
    color:var(--text)!important;
}
}

@media screen{
table,#legenda td,#legenda th{
    background:var(--panel)!important;
    color:var(--text)!important;
    border-color:var(--border)!important;
}
}
#grid th{background:var(--header)!important;}
button,input[type="number"]{background:var(--button);color:var(--text);border:1px solid var(--border);}
#barraProgresso{background:var(--progress)!important;}
body.theme-dark{--bg:#202124;--text:#eee;--panel:#2b2b2b;--border:#666;--header:#3a3a3a;--button:#444;--progress:#66bb6a;}
body.theme-dracula{--bg:#282A36;--text:#F8F8F2;--panel:#343746;--border:#6272A4;--header:#44475A;--button:#44475A;--progress:#50FA7B;}
body.theme-forest{--bg:#233127;--text:#eef7ee;--panel:#2e4232;--border:#557a55;--header:#3f5b43;--button:#48644c;--progress:#7ed957;}
body.theme-blue{--bg:#eaf3ff;--text:#13294b;--panel:#fff;--border:#6d8fb8;--header:#bfd5f2;--button:#d8e7fb;--progress:#4b8cff;}
body.theme-sepia{--bg:#f4ecd8;--text:#4b382a;--panel:#fbf6ea;--border:#a88d6a;--header:#e7d8bb;--button:#efe2c8;--progress:#8b6b3f;}
body.theme-solarized-light{--bg:#fdf6e3;--text:#657b83;--panel:#fffdf5;--border:#93a1a1;--header:#eee8d5;--button:#eee8d5;--progress:#2aa198;}
body.theme-solarized-dark{--bg:#002b36;--text:#93a1a1;--panel:#073642;--border:#586e75;--header:#09404f;--button:#0b4a5a;--progress:#2aa198;}


body.theme-paper{--bg:#f7f7f7;--text:#222;--panel:#ffffff;--border:#c8c8c8;--header:#ececec;--button:#f2f2f2;--progress:#4CAF50;}
body.theme-ivory{--bg:#fffdf5;--text:#3a342e;--panel:#fffef8;--border:#cdbfae;--header:#f3ead6;--button:#f8f0df;--progress:#b8860b;}
body.theme-matcha{--bg:#eef6ea;--text:#28402b;--panel:#f8fcf6;--border:#93b18d;--header:#dbead5;--button:#e8f2e4;--progress:#5f9f5f;}
body.theme-ice{--bg:#eef8ff;--text:#1d3557;--panel:#ffffff;--border:#9cc7e8;--header:#dcefff;--button:#edf7ff;--progress:#4ea8de;}
body.theme-nord{--bg:#2e3440;--text:#eceff4;--panel:#3b4252;--border:#4c566a;--header:#434c5e;--button:#4c566a;--progress:#88c0d0;}
body.theme-catppuccin-mocha{--bg:#1e1e2e;--text:#cdd6f4;--panel:#313244;--border:#585b70;--header:#45475a;--button:#585b70;--progress:#a6e3a1;}
body.theme-catppuccin-macchiato{--bg:#24273a;--text:#cad3f5;--panel:#363a4f;--border:#5b6078;--header:#494d64;--button:#5b6078;--progress:#8aadf4;}
body.theme-gruvbox-dark{--bg:#282828;--text:#ebdbb2;--panel:#3c3836;--border:#665c54;--header:#504945;--button:#665c54;--progress:#98971a;}
body.theme-gruvbox-light{--bg:#fbf1c7;--text:#3c3836;--panel:#f9f5d7;--border:#bdae93;--header:#ebdbb2;--button:#ebdbb2;--progress:#98971a;}
body.theme-tokyo-night{--bg:#1a1b26;--text:#c0caf5;--panel:#24283b;--border:#565f89;--header:#414868;--button:#414868;--progress:#7aa2f7;}
body.theme-one-dark{--bg:#282c34;--text:#abb2bf;--panel:#353b45;--border:#5c6370;--header:#3e4451;--button:#4b5263;--progress:#98c379;}
body.theme-monokai{--bg:#272822;--text:#f8f8f2;--panel:#383830;--border:#75715e;--header:#49483e;--button:#49483e;--progress:#a6e22e;}
body.theme-synthwave{--bg:#241b2f;--text:#f1f1f1;--panel:#34294f;--border:#7a5cff;--header:#44336b;--button:#44336b;--progress:#ff4fd8;}
body.theme-midnight{--bg:#10131a;--text:#d7e3fc;--panel:#1a2130;--border:#394867;--header:#22304a;--button:#22304a;--progress:#5dade2;}
body.theme-nebula{--bg:#1b1f2a;--text:#e6edf7;--panel:#2b3140;--border:#56627a;--header:#384258;--button:#384258;--progress:#9b59b6;}
body.theme-ember{--bg:#2b1d1a;--text:#f7e7dd;--panel:#3b2924;--border:#8b5a4a;--header:#53352d;--button:#53352d;--progress:#e67e22;}
body.theme-space-gray{--bg:#20242b;--text:#d8dee9;--panel:#2d333b;--border:#5b6574;--header:#3a424d;--button:#3a424d;--progress:#81a1c1;}


body.theme-cotton{--bg:#ffffff;--text:#222;--panel:#fff;--border:#ddd;--header:#f2f2f2;--button:#fafafa;--progress:#4CAF50;}
body.theme-book{--bg:#f8f1df;--text:#4a3d2f;--panel:#fffaf0;--border:#b9a98c;--header:#eadfc5;--button:#f3ead6;--progress:#8b6b3f;}
body.theme-latte{--bg:#eff1f5;--text:#4c4f69;--panel:#fff;--border:#bcc0cc;--header:#dce0e8;--button:#e6e9ef;--progress:#40a02b;}
body.theme-honey{--bg:#fff7d6;--text:#4f3a00;--panel:#fffbea;--border:#d2b04c;--header:#f8e8a1;--button:#f8efc4;--progress:#d48c00;}
body.theme-mint{--bg:#eefcf4;--text:#244;--panel:#fff;--border:#9cc;--header:#dff7ea;--button:#eefcf4;--progress:#2ecc71;}
body.theme-ocean-light{--bg:#eef8ff;--text:#16324f;--panel:#fff;--border:#9ecae1;--header:#d6ecff;--button:#eef8ff;--progress:#3498db;}
body.theme-rose{--bg:#fff4f7;--text:#5a3a45;--panel:#fff;--border:#e4b8c5;--header:#fde3ea;--button:#fff0f4;--progress:#e91e63;}
body.theme-wood{--bg:#f2e4d5;--text:#3d2c21;--panel:#fbf5ef;--border:#b68b68;--header:#e3cfbb;--button:#efe2d4;--progress:#8d6e63;}
body.theme-black-oled{--bg:#000;--text:#eee;--panel:#111;--border:#444;--header:#222;--button:#222;--progress:#00c853;}
body.theme-material-dark{--bg:#263238;--text:#eceff1;--panel:#37474f;--border:#546e7a;--header:#455a64;--button:#455a64;--progress:#66bb6a;}
body.theme-material-palenight{--bg:#292d3e;--text:#d0d0ff;--panel:#353b52;--border:#676e95;--header:#444b6a;--button:#444b6a;--progress:#c792ea;}
body.theme-night-owl{--bg:#011627;--text:#d6deeb;--panel:#102033;--border:#3b536d;--header:#1d3b53;--button:#1d3b53;--progress:#82aaff;}
body.theme-github-dark{--bg:#0d1117;--text:#c9d1d9;--panel:#161b22;--border:#30363d;--header:#21262d;--button:#21262d;--progress:#2ea043;}
body.theme-vscode-dark{--bg:#1e1e1e;--text:#d4d4d4;--panel:#252526;--border:#3c3c3c;--header:#2d2d30;--button:#2d2d30;--progress:#0e639c;}
body.theme-ayu-dark{--bg:#0a0e14;--text:#b3b1ad;--panel:#11151c;--border:#3e4b59;--header:#1f2430;--button:#1f2430;--progress:#39bae6;}
body.theme-ayu-mirage{--bg:#1f2430;--text:#cccac2;--panel:#242936;--border:#4a505a;--header:#343f4c;--button:#343f4c;--progress:#5ccfe6;}
body.theme-everforest{--bg:#2b3339;--text:#d3c6aa;--panel:#374145;--border:#4f5b58;--header:#434f55;--button:#434f55;--progress:#a7c080;}
body.theme-catppuccin-frappe{--bg:#303446;--text:#c6d0f5;--panel:#414559;--border:#626880;--header:#51576d;--button:#51576d;--progress:#a6d189;}
body.theme-galaxy{--bg:#161a2d;--text:#e0e6ff;--panel:#222845;--border:#49507a;--header:#30385d;--button:#30385d;--progress:#7f5af0;}
body.theme-deep-space{--bg:#0b1020;--text:#d9e2ff;--panel:#151b2f;--border:#36405f;--header:#202846;--button:#202846;--progress:#4cc9f0;}
body.theme-cyberpunk{--bg:#120458;--text:#f8f32b;--panel:#1b065e;--border:#ff00a8;--header:#2d0b72;--button:#2d0b72;--progress:#00f7ff;}
body.theme-aurora{--bg:#152238;--text:#eef;--panel:#22324f;--border:#4c6a92;--header:#2b4567;--button:#2b4567;--progress:#7fffd4;}


body.focus-mode.layout-left #painel_c2c{
left:20px;
top:20px;
right:auto;
transform:none;
text-align:left;
}
body.focus-mode.layout-center #painel_c2c{
left:50%;
top:50%;
right:auto;
transform:translate(-50%,-50%);
text-align:center;
}
body.focus-mode.layout-right #painel_c2c{
right:20px;
bottom:20px;
top:auto;
left:auto;
transform:none;
text-align:right;
}


body.focus-mode{
margin:0;
}

body.focus-mode #painel_c2c{
    position:fixed;
    top:50%;
    max-width:900px;
    width:900px;
    transform:translateY(-50%);
}

body.focus-mode.layout-left #painel_c2c{
left:20px;
top:20px;
right:auto;
transform:none;
text-align:left;
}

body.focus-mode.layout-center #painel_c2c{
left:50%;
top:50%;
right:auto;
transform:translate(-50%,-50%);
text-align:center;
}

body.focus-mode.layout-right #painel_c2c{
right:20px;
bottom:20px;
top:auto;
left:auto;
transform:none;
text-align:right;
}

#acoes{
margin:8px 0;
display:flex;
align-items:center;
gap:6px;
flex-wrap:wrap;
}

body.focus-mode.layout-left #controles,
body.focus-mode.layout-left #acoes,
body.focus-mode.layout-left #configuracoes{justify-content:flex-start;}

body.focus-mode.layout-center #controles,
body.focus-mode.layout-center #acoes,
body.focus-mode.layout-center #configuracoes{justify-content:center;}

body.focus-mode.layout-right #controles,
body.focus-mode.layout-right #acoes,
body.focus-mode.layout-right #configuracoes{justify-content:flex-end;}

body.focus-mode.layout-center #linhaAtual,
body.focus-mode.layout-center #infoLinha,
body.focus-mode.layout-center #textoProgresso,
body.focus-mode.layout-center #atalhos{
text-align:center;
}

body.focus-mode.layout-right #linhaAtual,
body.focus-mode.layout-right #infoLinha,
body.focus-mode.layout-right #textoProgresso,
body.focus-mode.layout-right #atalhos{
text-align:right;
}

body.focus-mode.layout-left #linhaAtual,
body.focus-mode.layout-left #infoLinha,
body.focus-mode.layout-left #textoProgresso,
body.focus-mode.layout-left #atalhos{
text-align:left;
}

body.focus-mode #painel_c2c > div[style*="width:420px"]{
margin-left:auto;
margin-right:auto;
}
#containerBarra{
    width:420px;
    height:18px;
    border:1px solid #666;
    background:#ddd;
    margin-bottom:18px;
}

#barraProgresso{
    height:100%;
    width:0%;
    background:var(--progress);
}

body.focus-mode.layout-left #containerBarra{
    margin-left:0;
    margin-right:auto;
}

body.focus-mode.layout-center #containerBarra{
    margin-left:auto;
    margin-right:auto;
}

body.focus-mode.layout-right #containerBarra{
    margin-left:auto;
    margin-right:0;
}

body.focus-mode.layout-left #legenda{
    margin-left:0;
    margin-right:auto;
}

body.focus-mode.layout-center #legenda{
    margin-left:auto;
    margin-right:auto;
}

body.focus-mode.layout-right #legenda{
    margin-left:auto;
    margin-right:0;
}


@media (max-width:1024px){
body.focus-mode.layout-left #painel_c2c{
position:relative!important;
left:auto!important;
top:auto!important;
right:auto!important;
bottom:auto!important;
transform:none!important;
width:100%!important;
max-width:none!important;
}
body.focus-mode.layout-center #painel_c2c{
position:relative!important;
left:auto!important;
top:auto!important;
right:auto!important;
bottom:auto!important;
transform:none!important;
width:100%!important;
max-width:none!important;
}
body.focus-mode.layout-right #painel_c2c{
position:relative!important;
right:auto!important;
bottom:auto!important;
left:auto!important;
top:auto!important;
transform:none!important;
width:100%!important;
max-width:none!important;
}
}


.linhaAtualReceita{
    display:flex;
    flex-wrap:wrap;
    align-items:flex-start;
    gap:2px;
}
.linhaAtualReceita .bloco_receita{
    display:inline-flex;
    margin:0;
}

body.focus-mode.layout-left .linhaAtualReceita{justify-content:flex-start;}
body.focus-mode.layout-center .linhaAtualReceita{justify-content:center;}
body.focus-mode.layout-right .linhaAtualReceita{justify-content:flex-end;}




/* Mobile adjustments */
@media (max-width:1024px){
  body{margin:8px!important;}
  #atalhos{display:none!important;}
  #painel_c2c{
    width:100%!important;
    max-width:100%!important;
    box-sizing:border-box!important;
    padding:8px!important;
  }
  body.focus-mode #painel_c2c{
    position:relative!important;
    left:auto!important;
    top:auto!important;
    right:auto!important;
    bottom:auto!important;
    width:auto!important;
    max-width:none!important;
    min-height:auto!important;
    transform:none!important;
    padding:10px!important;
  }

  html,
  body{
    overflow-y:auto!important;
    -webkit-overflow-scrolling:touch!important;
  }
  .linhaAtualReceita{
    display:flex!important;
    width:100%!important;
    flex-wrap:wrap!important;
    gap:4px!important;
  }
  .bloco_receita{
    font-size:14px!important;
    padding:2px 5px!important;
    white-space:nowrap!important;
  }
}



@media (max-width:1024px){
  #containerBarra{
    width:100%!important;
    max-width:100%!important;
    box-sizing:border-box!important;
  }
}



@media (max-width:1024px){
  html,body{
    height:auto!important;
    min-height:100%!important;
    overflow-y:auto!important;
  }

  body.focus-mode{
    overflow-y:auto!important;
    -webkit-overflow-scrolling:touch!important;
  }

  body.focus-mode #painel_c2c{
    position:relative!important;
    top:auto!important;
    left:auto!important;
    right:auto!important;
    bottom:auto!important;
    width:100%!important;
    max-width:100%!important;
    box-sizing:border-box!important;
    min-height:auto!important;
    transform:none!important;
  }

  #legenda{
    display:block;
    width:100%;
    max-width:100%;
    max-height:40vh;
    overflow:auto;
    box-sizing:border-box;
    -webkit-overflow-scrolling:touch;
  }
}

@media (max-width:600px){
#legenda{
    width:100%;
    table-layout:fixed;
}
#legenda th,#legenda td{
    overflow-wrap:anywhere;
    word-break:break-word;
}
#legenda .cor{margin:auto;}
#legenda th:nth-child(3),
#legenda td:nth-child(3){
    display:none;
}
}
</style>

</head>

<body>
""")

html.append('<div id="painel_c2c">')
html.append(f"<h1>{os.path.basename(ARQUIVO)}</h1>")

html.append('<div id="informacoes">')
html.append(f"<p><b>Tamanho:</b> {largura} x {altura}</p>")
html.append(f"<p><b>Total de quadrados:</b> {largura*altura}</p>")
html.append(f"<p><b>Total de cores:</b> {len(cores)}</p>")
html.append("</span></div>")


# ==========================
# Legenda
# ==========================

html.append('<h2 id="tituloCores">Cores</h2>')

html.append("""
<table id='legenda'>

<tr>

<th>Código</th>
<th>Cor</th>
<th>RGB</th>
<th>Hex</th>
<th>Quantidade</th>

</tr>
""")

for cor in cores:

    r,g,b = cor

    hexa = f"#{r:02X}{g:02X}{b:02X}"

    html.append(f"""

<tr>

<td>{mapa[cor]}</td>

<td>

<div class='cor'
style='background:{hexa};'>
</div>

</td>

<td>{r}, {g}, {b}</td>

<td>{hexa}</td>

<td>{contador[cor]}</td>

</tr>

""")

html.append("</table>")

# ==========================
# Grade
# ==========================

html.append("<h2 id='titulo-grafico'>Gráfico</h2>")
html.append("<table id='grid'>")

# Cabeçalho das colunas
html.append("<tr>")
html.append("<th></th>")

for x in range(largura):
    html.append(f"""
<th style="
background:#ddd;
padding:4px;
border:1px solid #888;
">
{largura - x}
</th>
""")

html.append("</tr>")

# Linhas
for y in range(altura):

    html.append("<tr>")

    # Número da linha
    html.append(f"""
<th style="
background:#ddd;
padding:4px;
border:1px solid #888;
">
{altura - y}
</th>
""")

    for x in range(largura):

        cor = pixels[x, y]

        r, g, b = cor
        hexa = f"#{r:02X}{g:02X}{b:02X}"

        letra = mapa[cor]

        texto = cor_texto(r, g, b)

        html.append(f"""
        <td
        style="
        background:{hexa};
        color:{texto};
        ">

        {letra}

        </td>
        """)

    html.append(f"""
<th style="
background:#ddd;
padding:4px;
border:1px solid #888;
">
{altura - y}
</th>
""")

html.append("</tr>")

# ==========================
# Cabeçalho inferior
# ==========================

html.append("<tr>")

html.append("<th></th>")

for x in range(largura):

    html.append(f"""
<th style="
background:#ddd;
padding:4px;
border:1px solid #888;
">
{largura - x}
</th>
""")

html.append("<th></th>")

html.append("</tr>")

html.append("</table>")
html.append('<button onclick="abrirGrafico()">🔍 Abrir gráfico</button>')

html.append("<h2 id='titulo-grafico-print'>Mini gráfico</h2>")
html.append("<table id='grid_print'>")

for y in range(altura):

    html.append("<tr>")

    for x in range(largura):

        cor = pixels[x, y]
        r, g, b = cor
        hexa = f"#{r:02X}{g:02X}{b:02X}"

        html.append(f"""
<td style="background:{hexa};"></td>
""")

    html.append("</tr>")

html.append("</table>")

# ==========================
# Instruções C2C
# ==========================

html.append('<div id="receita_tela">')
html.append("<h2>Instruções C2C</h2>")
html.append('<div id="infoLinha" style="font-weight:bold;margin-bottom:10px"></div>')
html.append('<div id="containerBarra"><div id="barraProgresso"></div></div>')
html.append('<div id="textoProgresso" style="font-size:13px;margin-bottom:10px"></div>')
html.append('<div id="linhaAtual" style="min-height:60px;margin-top:28px;margin-bottom:10px"></div>')
html.append('<div id="controles">')
html.append('<button onclick="anterior()">⬅ Anterior</button>')
html.append('<button onclick="proxima()">Próxima ➡</button>')
html.append('<span>Ir para:</span>')
html.append('<input id="irLinha" type="number" min="1">')
html.append('<button onclick="irPara()">Ir</button>')

html.append('</div>')
html.append('<div style="height:8px"></div>')
html.append('<div id="acoes" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:8px">')
html.append('<button onclick="imprimirNormal()" id="btnImprimir">Imprimir</button>')
html.append('<button onclick="salvarPDF()" id="btnPDF">Salvar PDF</button>')
html.append('<button onclick="gerarEPUB()" id="btnEPUB">Gerar EPUB</button>')
html.append('<button onclick="toggleZen()">Modo Zen</button>')
html.append('<button id="btnInvert" onclick="toggleInvert()">Inverter ordem</button>')
html.append('<button id="btnCores" onclick="toggleCores()">Ocultar cores</button><button id="btnNomeCor" onclick="toggleNomeCor()">Letras</button>')
html.append('</div>')
html.append('<div id="configuracoes" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:12px">')
html.append('<span>Tema:</span>')
html.append("""
<select id="tema" onchange="trocarTema()">
<optgroup label="Claros">
<option value="">Claro</option><option value="paper">Paper</option><option value="cotton">Cotton</option><option value="book">Book</option><option value="ivory">Ivory</option><option value="latte">Latte</option><option value="sepia">Sepia</option><option value="honey">Honey</option><option value="matcha">Matcha</option><option value="mint">Mint</option><option value="ice">Ice</option><option value="ocean-light">Ocean Light</option><option value="rose">Rose</option><option value="wood">Wood</option><option value="gruvbox-light">Gruvbox Light</option><option value="solarized-light">Solarized Light</option>
</optgroup><optgroup label="Escuros">
<option value="dark">Escuro</option><option value="black-oled">Black OLED</option><option value="dracula">Dracula</option><option value="nord">Nord</option><option value="tokyo-night">Tokyo Night</option><option value="one-dark">One Dark</option><option value="monokai">Monokai</option><option value="material-dark">Material Dark</option><option value="material-palenight">Material Palenight</option><option value="night-owl">Night Owl</option><option value="github-dark">GitHub Dark</option><option value="vscode-dark">VS Code Dark+</option><option value="ayu-dark">Ayu Dark</option><option value="ayu-mirage">Ayu Mirage</option><option value="everforest">Everforest</option><option value="gruvbox-dark">Gruvbox Dark</option><option value="catppuccin-mocha">Catppuccin Mocha</option><option value="catppuccin-macchiato">Catppuccin Macchiato</option><option value="catppuccin-frappe">Catppuccin Frappé</option><option value="forest">Forest</option><option value="blue">Blue</option><option value="midnight">Midnight</option><option value="nebula">Nebula</option><option value="galaxy">Galaxy</option><option value="deep-space">Deep Space</option><option value="cyberpunk">Cyberpunk</option><option value="synthwave">Synthwave</option><option value="ember">Ember</option><option value="aurora">Aurora</option><option value="space-gray">Space Gray</option><option value="solarized-dark">Solarized Dark</option>
</optgroup></select><span class="layoutLabel">Posição:</span><select id="layout" onchange="trocarLayout()"><option value="left">Esquerda</option><option value="center">Centro</option><option value="right">Direita</option></select>
""")
html.append("""
<script>
document.addEventListener("DOMContentLoaded",()=>{
document.querySelectorAll("#receita_print .linha_receita span[style*='flex:1']").forEach(c=>{
 const a=[...c.querySelectorAll("span")];
 a.forEach((e,i)=>{if(i<a.length-1)e.insertAdjacentText("beforeend",", ");});
});
});
</script>
""")
html.append("</div>")
TOTAL = largura + altura - 1
receita_js=[]
for d in range(TOTAL):
    itens=[]
    ultima_cor=None
    quantidade=0
    pontos=[]
    for yy in range(altura):
        xx=d-yy
        if 0<=xx<largura:
            pontos.append((largura-1-xx,altura-1-yy))
    if d % 2 == 0:
        pontos.reverse()
    for x,y in pontos:
        cor=pixels[x,y]
        if cor==ultima_cor:
            quantidade+=1
        else:
            if ultima_cor is not None:
                r,g,b=ultima_cor
                itens.append({
                    "bg":f"#{r:02X}{g:02X}{b:02X}",
                    "fg":cor_texto(r,g,b),
                    "codigo":mapa[ultima_cor],"nome":nome_cor(r,g,b),"qtd":quantidade
                })
            ultima_cor=cor
            quantidade=1
    if ultima_cor is not None:
        r,g,b=ultima_cor
        itens.append({
            "bg":f"#{r:02X}{g:02X}{b:02X}",
            "fg":cor_texto(r,g,b),
            "codigo":mapa[ultima_cor],"nome":nome_cor(r,g,b),"qtd":quantidade
        })
    receita_js.append(itens)

acumulado=[]

soma=0
for d in range(TOTAL):
    qtd=0
    for yy in range(altura):
        xx=d-yy
        if 0<=xx<largura:
            qtd+=1
    soma+=qtd
    acumulado.append(soma)

# O PNG é incorporado ao HTML para que o botão possa gerar um EPUB sem servidor.
mini_grafico_epub = img.copy()
reamostragem_epub = getattr(Image, "Resampling", Image).NEAREST
mini_grafico_epub.thumbnail((900, 900), reamostragem_epub)
mini_grafico_buffer = BytesIO()
mini_grafico_epub.save(mini_grafico_buffer, format="PNG")
mini_grafico_data_uri = "data:image/png;base64," + base64.b64encode(mini_grafico_buffer.getvalue()).decode("ascii")

html.append("<script>")
html.append("const receita="+repr(receita_js)+";")
html.append("const acumulado="+str(acumulado).replace(" ","")+";")
html.append("const epubTitulo=" + json.dumps(os.path.basename(ARQUIVO), ensure_ascii=False) + ";")
html.append("const epubMiniGrafico=" + json.dumps(mini_grafico_data_uri) + ";")
html.append(f"const epubLargura={largura};const epubAltura={altura};const epubTotalCores={len(cores)};")
html.append('''

function epubEscapar(valor){
 return String(valor).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&apos;");
}
function epubDocumento(titulo, corpo){
 return `<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="pt-BR" lang="pt-BR"><head><meta charset="utf-8" /><title>${epubEscapar(titulo)}</title><link rel="stylesheet" type="text/css" href="style.css" /></head><body>${corpo}</body></html>`;
}
function epubBytes(valor){ return typeof valor==="string" ? new TextEncoder().encode(valor) : valor; }
function epubCrc32(bytes){
 let crc=0xffffffff;
 for(const byte of bytes){
  crc^=byte;
  for(let bit=0;bit<8;bit++) crc=(crc>>>1)^((crc&1)?0xedb88320:0);
 }
 return (crc^0xffffffff)>>>0;
}
function epubZip(arquivos){
 const partes=[], central=[], encoder=new TextEncoder(); let deslocamento=0;
 for(const arquivo of arquivos){
  const nome=encoder.encode(arquivo.nome), dados=epubBytes(arquivo.dados), crc=epubCrc32(dados);
  const local=new Uint8Array(30+nome.length+dados.length), view=new DataView(local.buffer);
  view.setUint32(0,0x04034b50,true); view.setUint16(4,20,true); view.setUint16(6,0x0800,true);
  view.setUint16(8,0,true); view.setUint32(14,crc,true); view.setUint32(18,dados.length,true); view.setUint32(22,dados.length,true);
  view.setUint16(26,nome.length,true); local.set(nome,30); local.set(dados,30+nome.length);
  partes.push(local);
  const registro=new Uint8Array(46+nome.length), cview=new DataView(registro.buffer);
  cview.setUint32(0,0x02014b50,true); cview.setUint16(4,20,true); cview.setUint16(6,20,true); cview.setUint16(8,0x0800,true);
  cview.setUint16(10,0,true); cview.setUint32(16,crc,true); cview.setUint32(20,dados.length,true); cview.setUint32(24,dados.length,true);
  cview.setUint16(28,nome.length,true); cview.setUint32(42,deslocamento,true); registro.set(nome,46); central.push(registro);
  deslocamento+=local.length;
 }
 const tamanhoCentral=central.reduce((s,p)=>s+p.length,0), fim=new Uint8Array(22), fview=new DataView(fim.buffer);
 fview.setUint32(0,0x06054b50,true); fview.setUint16(8,arquivos.length,true); fview.setUint16(10,arquivos.length,true);
 fview.setUint32(12,tamanhoCentral,true); fview.setUint32(16,deslocamento,true);
 return new Blob([...partes,...central,fim],{type:"application/epub+zip"});
}
function epubImagemBytes(dataUri){
 const binario=atob(dataUri.split(",",2)[1]), bytes=new Uint8Array(binario.length);
 for(let i=0;i<binario.length;i++) bytes[i]=binario.charCodeAt(i);
 return bytes;
}
async function gerarEPUB(){
 const botao=document.getElementById("btnEPUB");
 botao.disabled=true; botao.textContent="Gerando EPUB…";
 try{
  const total=receita.length, quadrados=epubLargura*epubAltura, base=epubTitulo.replace(/\.[^.]+$/,""), id="urn:c2c:"+base;
  const css=`body{font-family:sans-serif;line-height:1.45;margin:5%;color:#111}h1,h2{text-align:center}.capa,.metadados{text-align:center}.metadados{margin:1.5em 0}.mini-grafico{display:block;width:95%;max-width:900px;max-height:70vh;margin:1.5em auto;object-fit:contain;image-rendering:pixelated}.progresso{height:1em;border:1px solid #555;background:#eee;margin:1em 0 .35em}.progresso-preenchimento{display:block;height:100%;min-height:1em;background:#4caf50}.receita{text-align:center;margin:2em 0}.instrucao{display:inline;font-weight:bold}.bloco{display:inline-block;padding:.25em .45em;margin:.12em;border:1px solid #222;font-weight:bold;border-radius:.2em}nav ol{padding-left:1.4em}`;
  const capa=epubDocumento(epubTitulo,`<section class="capa" epub:type="cover"><h1>${epubEscapar(epubTitulo)}</h1><div class="metadados"><p><strong>Tamanho:</strong> ${epubLargura} × ${epubAltura}</p><p><strong>Total de cores:</strong> ${epubTotalCores}</p><p><strong>Total de quadrados:</strong> ${quadrados}</p></div><img class="mini-grafico" src="mini-grafico.png" alt="Mini gráfico da receita C2C" /></section>`);
  const capitulos=[];
  function adicionarCapitulo(indice,itens,ordem,nome){
   const linha=indice+1, feitos=acumulado[indice], percentual=feitos*100/quadrados;
   const titulo=`Linha ${linha} de ${total} — Ordem ${ordem}`;
   const instrucoes=usarNome
    ? itens.map(item=>`<span class="instrucao">(${item.qtd}) ${epubEscapar(item.nome)}</span>`).join(", ")
    : itens.map(item=>`<span class="bloco" style="background-color:${item.bg};color:${item.fg}">${epubEscapar(item.codigo)}×${item.qtd}</span>`).join("");
   const corpo=`<section epub:type="chapter"><h1>${epubEscapar(titulo)}</h1><div class="progresso" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${percentual.toFixed(1)}"><div class="progresso-preenchimento" style="width:${percentual.toFixed(1)}%"></div></div><p><strong>Progresso acumulado:</strong> ${feitos} de ${quadrados} quadrados (${percentual.toFixed(1)}%)</p><div class="receita">${instrucoes}</div></section>`;
   capitulos.push({nome,titulo,conteudo:epubDocumento(titulo,corpo)});
  }
  receita.forEach((itens,indice)=>adicionarCapitulo(indice,itens,"normal",`linha-${indice+1}.xhtml`));
  receita.forEach((itens,indice)=>adicionarCapitulo(indice,[...itens].reverse(),"inversa",`linha-inversa-${indice+1}.xhtml`));
  const navItens=[`<li><a href="cover.xhtml">Capa</a></li>`,...capitulos.map(c=>`<li><a href="${c.nome}">${epubEscapar(c.titulo)}</a></li>`)].join("");
  const nav=epubDocumento("Sumário",`<nav epub:type="toc" id="toc"><h1>Sumário</h1><ol>${navItens}</ol></nav>`);
  const ncxPontos=[`<navPoint id="nav-cover" playOrder="1"><navLabel><text>Capa</text></navLabel><content src="cover.xhtml" /></navPoint>`,...capitulos.map((c,i)=>`<navPoint id="nav-${i+1}" playOrder="${i+2}"><navLabel><text>${epubEscapar(c.titulo)}</text></navLabel><content src="${c.nome}" /></navPoint>`)].join("");
  const ncx=`<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd"><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="${epubEscapar(id)}" /></head><docTitle><text>${epubEscapar(epubTitulo)}</text></docTitle><navMap>${ncxPontos}</navMap></ncx>`;
  const manifest=capitulos.map((c,i)=>`<item id="capitulo-${i+1}" href="${c.nome}" media-type="application/xhtml+xml" />`).join("");
  const spine=capitulos.map((c,i)=>`<itemref idref="capitulo-${i+1}" />`).join("");
  const opf=`<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" unique-identifier="book-id" version="3.0" xml:lang="pt-BR"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">${epubEscapar(id)}</dc:identifier><dc:title>${epubEscapar(epubTitulo)}</dc:title><dc:language>pt-BR</dc:language><meta name="cover" content="mini-grafico" /></metadata><manifest><item id="cover" href="cover.xhtml" media-type="application/xhtml+xml" /><item id="mini-grafico" href="mini-grafico.png" media-type="image/png" properties="cover-image" /><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav" /><item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" /><item id="style" href="style.css" media-type="text/css" />${manifest}</manifest><spine toc="ncx"><itemref idref="cover" />${spine}</spine><guide><reference type="cover" title="Capa" href="cover.xhtml" /></guide></package>`;
  const arquivos=[{nome:"mimetype",dados:"application/epub+zip"},{nome:"META-INF/container.xml",dados:'<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml" /></rootfiles></container>'},{nome:"OEBPS/style.css",dados:css},{nome:"OEBPS/mini-grafico.png",dados:epubImagemBytes(epubMiniGrafico)},{nome:"OEBPS/cover.xhtml",dados:capa},{nome:"OEBPS/nav.xhtml",dados:nav},{nome:"OEBPS/toc.ncx",dados:ncx},{nome:"OEBPS/content.opf",dados:opf},...capitulos.map(c=>({nome:"OEBPS/"+c.nome,dados:c.conteudo}))];
  const url=URL.createObjectURL(epubZip(arquivos)), link=document.createElement("a"); link.href=url; link.download=base+".epub"; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
 }finally{ botao.disabled=false; botao.textContent="Gerar EPUB"; }
}

function abrirGrafico(){
 const copia=document.getElementById("grid").cloneNode(true);
 copia.querySelectorAll("td").forEach(td=>td.textContent="");
 const w=window.open("","_blank");
 w.document.write("<!DOCTYPE html><html><head><title>Gráfico</title><style>body{font-family:Arial;margin:20px}table{border-collapse:collapse}td,th{border:1px solid #888;width:22px;height:22px;text-align:center;font-size:11px;font-weight:bold;position:static}</style></head><body>"+document.getElementById("titulo-grafico").outerHTML+copia.outerHTML+"</body></html>");
 w.document.close();
}

let i=0;
let invertRecipe=localStorage.getItem('c2c_invert')==='1';
let usarNome=localStorage.getItem('c2c_nomecor')==='1';
function atualizar(){
localStorage.setItem("c2c_linha",i);
document.getElementById("infoLinha").textContent=`Linha ${i+1} de ${receita.length}`;
const alvo=document.getElementById("linhaAtual");
alvo.replaceChildren();
const wrap=document.createElement("div");
wrap.className="linhaAtualReceita";
const lay=document.getElementById("layout")?.value||"left";
wrap.style.justifyContent=lay==="left"?"flex-start":lay==="center"?"center":"flex-end";
const lista=invertRecipe?[...receita[i]].reverse():receita[i];
for(const item of lista){
 const s=document.createElement("span");
 if(usarNome){
  s.textContent='('+item.qtd+') '+item.nome+(lista.indexOf(item)<lista.length-1?', ':'');
 }else{
  s.className='bloco_receita';
  s.textContent=item.codigo+'×'+item.qtd;
  s.style.background=item.bg;
  s.style.color=item.fg;
 }
 wrap.appendChild(s);
}
alvo.appendChild(wrap);
document.getElementById("irLinha").value=i+1;
let feitos=acumulado[i];
let total=acumulado[acumulado.length-1];
let pct=feitos*100/total;
document.getElementById("barraProgresso").style.width=pct+"%";
document.getElementById("textoProgresso").textContent=`${feitos} / ${total} quadrados (${pct.toFixed(1)}%)`;
}
function anterior(){if(i>0){i--;


 atualizar();}}
function proxima(){if(i<receita.length-1){i++;atualizar();}}
function irPara(){
 let v=parseInt(document.getElementById("irLinha").value);
 if(!isNaN(v)&&v>=1&&v<=receita.length){
   i=v-1;
   atualizar();
 }
}

function toggleZen(){
 const entering=!document.body.classList.contains("zen");
 document.body.classList.toggle('zen',entering);
  document.body.classList.toggle('focus-mode',entering);
 document.getElementById('painel_c2c').removeAttribute('style');
 if(entering){
   miniFullscreen=false;
   document.getElementById("grid").style.display="none";
   document.getElementById("titulo-grafico").style.display="none";
   const abrir=[...document.getElementsByTagName("button")].find(b=>b.textContent.includes("Abrir gráfico"));
   if(abrir)abrir.style.display="none";
 }else{
   document.getElementById("grid").style.display="";
   document.getElementById("titulo-grafico").style.display="";
   const abrir=[...document.getElementsByTagName("button")].find(b=>b.textContent.includes("Abrir gráfico"));
   if(abrir)abrir.style.display="";
 }
 toggleCores(true);
}

async function toggleFullscreen(){}

document.addEventListener("keydown", function(e){

    if(e.target.tagName==="INPUT") return;

    switch(e.key){
      case "ArrowLeft":
        e.preventDefault();
        anterior();
        break;
      case "ArrowRight":
        e.preventDefault();
        proxima();
        break;
      case "z":
      case "Z":
        e.preventDefault();
        toggleZen();
        break;
    }

});

function aplicarMini(){}
function toggleMiniGrafico(){}
function trocarTema(){
 const t=document.getElementById("tema").value;
 document.body.className=document.body.className.replace(/theme-[^ ]+/g,"").trim();
 if(t) document.body.classList.add("theme-"+t);
 localStorage.setItem("c2c_theme",t);
}


function trocarLayout(){
 const l=document.getElementById("layout").value;
 document.body.classList.remove("layout-left","layout-center","layout-right");
 document.body.classList.add("layout-"+l);
 localStorage.setItem("c2c_layout",l);
 const wrap=document.querySelector(".linhaAtualReceita");
 if(wrap){
   wrap.style.justifyContent=l==="left"?"flex-start":l==="center"?"center":"flex-end";
 }
 atualizar();
}


function toggleCores(forceHide){
 const fs=!!document.fullscreenElement || document.body.classList.contains('focus-mode');
 const btn=document.getElementById('btnCores');
 if(!fs){
  document.getElementById('tituloCores').style.display='';
  document.getElementById('legenda').style.display='table';
  if(btn) btn.style.display='none';
  return;
 }
 if(btn) btn.style.display='inline-block';
 if(forceHide===true){
  document.getElementById('tituloCores').style.display='none';
  document.getElementById('legenda').style.display='none';
  btn.textContent='Mostrar cores';
  localStorage.setItem('c2c_show_colors','0');
  return;
 }
 const vis=document.getElementById('legenda').style.display!=='none';
 if(vis){
  document.getElementById('tituloCores').style.display='none';
  document.getElementById('legenda').style.display='none';
  btn.textContent='Mostrar cores';
  localStorage.setItem('c2c_show_colors','0');
 }else{
  document.getElementById('tituloCores').style.display='';
  document.getElementById('legenda').style.display='table';
  btn.textContent='Ocultar cores';
  localStorage.setItem('c2c_show_colors','1');
 }
}




function salvarPDF(){
 const zen=document.body.classList.contains('focus-mode');
 if(zen) document.body.classList.remove('focus-mode','zen');
 document.body.classList.add('pdf-mode');
 prepararImpressao();
 const restore=()=>{
   document.body.classList.remove('pdf-mode');
   if(zen) document.body.classList.add('focus-mode','zen');
   window.removeEventListener('afterprint',restore);
 };
 window.addEventListener('afterprint',restore);
 window.print();
}

function imprimirNormal(){
 const zen=document.body.classList.contains('focus-mode');
 if(zen){
  document.body.classList.remove('focus-mode','zen');
 }
 prepararImpressao();
 const restore=()=>{
  if(zen){
   document.body.classList.add('focus-mode','zen');
  }
  window.removeEventListener('afterprint',restore);
 };
 window.addEventListener('afterprint',restore);
 window.print();
}

function prepararImpressao(){
 document.querySelectorAll('[id^="dirprint"]').forEach((e,idx)=>{
   
 });
 const linhas=document.querySelectorAll('#receita_print .linha_receita');
 linhas.forEach((linha)=>{
   const alvo=linha.querySelector('span[style*="flex:1"]');
   if(!alvo)return;
   const blocos=[...alvo.querySelectorAll('.bloco_receita')];
   if(invertRecipe){
      blocos.reverse().forEach(b=>alvo.appendChild(b));
   }
 });
}
window.addEventListener('afterprint',prepararImpressao);


function toggleNomeCor(){
 usarNome=!usarNome;
 localStorage.setItem('c2c_nomecor',usarNome?'1':'0');
 document.getElementById('btnNomeCor').textContent=usarNome?'Letras':'Nomes';
 atualizar();
}

function toggleInvert(){
 invertRecipe=!invertRecipe;
 localStorage.setItem('c2c_invert',invertRecipe?'1':'0');
 document.getElementById('btnInvert').textContent=invertRecipe?'Ordem normal':'Inverter ordem';
 atualizar();
 prepararImpressao();
}

window.onload=function(){

 let s=parseInt(localStorage.getItem("c2c_linha"));
 if(!isNaN(s) && s>=0 && s<receita.length) i=s;
 document.getElementById("atalhos").textContent="← → Navegar • Z Modo Zen • Digite um número para ir para uma linha";
let th=localStorage.getItem("c2c_theme")||"";
let lay=localStorage.getItem("c2c_layout")||"center";
document.getElementById("layout").value=lay;
trocarLayout();
document.getElementById("tema").value=th;
 document.getElementById("btnInvert").textContent=invertRecipe?"Ordem normal":"Inverter ordem";
 document.getElementById("btnNomeCor").textContent=usarNome?"Letras":"Nomes";
let sc=localStorage.getItem("c2c_show_colors");
if(sc==="0"){
 document.getElementById('tituloCores').style.display='none';
 document.getElementById('legenda').style.display='none';
}
toggleCores();
miniNormal=false;
 miniFullscreen=false;
aplicarMini();

trocarTema();
 const mobile=window.matchMedia("(max-width:1024px)").matches;
 if(mobile){
   document.getElementById("layout").value="left";
   trocarLayout();
   if(!document.body.classList.contains("zen")) toggleZen();
   const b=[...document.getElementsByTagName("button")].find(x=>x.textContent.includes("Modo Zen"));
   if(b) b.style.display="none";
    document.getElementById("atalhos").style.display="none";
 }

 atualizar();
};
''')
html.append("</script>")
html.append('<div id="atalhos">← → Navegar • Z Modo Zen • Digite um número para ir para uma linha</div>')
html.append("</div>")

html.append('<div id="receita_print">')
html.append("<h2>Instruções C2C</h2>")

TOTAL = largura + altura - 1

for d in range(TOTAL):

    html.append(f"""
        <div class="linha_receita">
        <span class="numero">{d+1:03}</span><span style="display:inline-block;width:16px">│</span><span style="flex:1;min-width:0">
        """)

    ultima_cor = None
    quantidade = 0

    pontos = []

    # Gera a diagonal começando do canto inferior direito
    for yy in range(altura):

        xx = d - yy

        if 0 <= xx < largura:

            x = largura - 1 - xx
            y = altura - 1 - yy

            pontos.append((x, y))

    # Alterna a direção a cada diagonal
    if d % 2 == 0:
        pontos.reverse()

    for x, y in pontos:

        cor = pixels[x, y]

        if cor == ultima_cor:
            quantidade += 1

        else:

            if ultima_cor is not None:

                r, g, b = ultima_cor
                hexa = f"#{r:02X}{g:02X}{b:02X}"
                texto = cor_texto(r, g, b)

                html.append(
                    f'<span>({quantidade}) {nome_cor(r,g,b)}</span>'
                )

            ultima_cor = cor
            quantidade = 1

    if ultima_cor is not None:

        r, g, b = ultima_cor
        hexa = f"#{r:02X}{g:02X}{b:02X}"
        texto = cor_texto(r, g, b)

        html.append(
            f'<span>({quantidade}) {nome_cor(r,g,b)}</span>'
        )

    html.append("</div>")


html.append("</div>")
html.append("</body></html>")

with open(saida,"w",encoding="utf8") as f:
    f.write("".join(html))

print(f"HTML gerado: {saida}")

# ==========================
# EPUB
# ==========================

def xhtml_document(titulo, corpo):
    """Cria documentos XHTML válidos para leitores EPUB e Kindle."""
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="pt-BR" lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>{escape(titulo)}</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
{corpo}
</body>
</html>
'''


def gerar_epub():
    """Gera um EPUB autocontido; o HTML acima permanece sua saída independente."""
    arquivo_epub = base + ".epub"
    titulo = os.path.basename(ARQUIVO)
    total_quadrados = largura * altura
    identificador = f"urn:c2c:{os.path.basename(base)}"

    style_css = '''
@namespace epub "http://www.idpf.org/2007/ops";
body { font-family: sans-serif; line-height: 1.45; margin: 5%; color: #111; }
h1, h2 { text-align: center; }
.capa, .metadados { text-align: center; }
.metadados { margin: 1.5em 0; }
.mini-grafico { display: block; width: 95%; max-width: 900px; max-height: 70vh; margin: 1.5em auto; object-fit: contain; image-rendering: pixelated; }
.progresso { height: 1em; border: 1px solid #555; background: #eee; margin: 1em 0 .35em; }
.progresso-preenchimento { display: block; height: 100%; min-height: 1em; background: #4caf50; }
.receita { text-align: center; margin: 2em 0; }
.instrucao { display: inline; font-weight: bold; }
nav ol { padding-left: 1.4em; }
'''.strip()

    # Uma imagem PNG é exibida de forma consistente no Kindle, ao contrário de
    # células vazias de tabela coloridas apenas por CSS.
    mini_grafico = img.copy()
    reamostragem = getattr(Image, "Resampling", Image).NEAREST
    mini_grafico.thumbnail((900, 900), reamostragem)
    mini_grafico_png = BytesIO()
    mini_grafico.save(mini_grafico_png, format="PNG")

    capa = xhtml_document(titulo, f'''
<section class="capa" epub:type="cover">
  <h1>{escape(titulo)}</h1>
  <div class="metadados">
    <p><strong>Tamanho:</strong> {largura} × {altura}</p>
    <p><strong>Total de cores:</strong> {len(cores)}</p>
    <p><strong>Total de quadrados:</strong> {total_quadrados}</p>
  </div>
  <h2>Mini gráfico</h2>
  <img class="mini-grafico" src="mini-grafico.png" alt="Mini gráfico da receita C2C" />
</section>''')

    nav_itens = ['<li><a href="cover.xhtml">Capa</a></li>']
    ncx_navpoints = [f'''<navPoint id="nav-cover" playOrder="1">
  <navLabel><text>Capa</text></navLabel><content src="cover.xhtml" />
</navPoint>''']
    capitulos = {}

    def adicionar_capitulo(indice, itens, ordem, nome_arquivo, identificador_capitulo, ordem_toc):
        linha = indice + 1
        feitos = acumulado[indice]
        percentual = feitos * 100 / total_quadrados
        instrucoes = []
        for item in itens:
            instrucoes.append(
                f'<span class="instrucao">({item["qtd"]}) {escape(item["nome"])}</span>'
            )
        titulo_capitulo = f"Linha {linha} de {TOTAL} — Ordem {ordem}"
        capitulos[nome_arquivo] = xhtml_document(titulo_capitulo, f'''
<section epub:type="chapter">
  <h1>{escape(titulo_capitulo)}</h1>
  <div class="progresso" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{percentual:.1f}">
    <div class="progresso-preenchimento" style="width:{percentual:.1f}%"></div>
  </div>
  <p><strong>Progresso acumulado:</strong> {feitos} de {total_quadrados} quadrados ({percentual:.1f}%)</p>
  <div class="receita">{", ".join(instrucoes)}</div>
</section>''')
        nav_itens.append(f'<li><a href="{nome_arquivo}">{escape(titulo_capitulo)}</a></li>')
        ncx_navpoints.append(f'''<navPoint id="nav-{identificador_capitulo}" playOrder="{ordem_toc}">
  <navLabel><text>{escape(titulo_capitulo)}</text></navLabel><content src="{nome_arquivo}" />
</navPoint>''')

    # Primeiro, a receita na ordem de leitura padrão.
    for indice, itens in enumerate(receita_js):
        linha = indice + 1
        adicionar_capitulo(indice, itens, "normal", f"linha-{linha}.xhtml", f"linha-{linha}", linha + 1)

    # Em seguida, a mesma receita com a sequência de cores de cada linha invertida.
    for indice, itens in enumerate(receita_js):
        linha = indice + 1
        adicionar_capitulo(
            indice, list(reversed(itens)), "inversa", f"linha-inversa-{linha}.xhtml",
            f"linha-inversa-{linha}", TOTAL + linha + 1
        )

    nav = xhtml_document("Sumário", f'''<nav epub:type="toc" id="toc">
  <h1>Sumário</h1><ol>{"".join(nav_itens)}</ol>
</nav>''')
    toc_ncx = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head><meta name="dtb:uid" content="{escape(identificador)}" /></head>
<docTitle><text>{escape(titulo)}</text></docTitle>
<navMap>{"".join(ncx_navpoints)}</navMap>
</ncx>'''

    manifest_capitulos = "\n".join(
        f'<item id="linha-{i}" href="linha-{i}.xhtml" media-type="application/xhtml+xml" />'
        for i in range(1, TOTAL + 1)
    ) + "\n" + "\n".join(
        f'<item id="linha-inversa-{i}" href="linha-inversa-{i}.xhtml" media-type="application/xhtml+xml" />'
        for i in range(1, TOTAL + 1)
    )
    spine_capitulos = "\n".join(
        f'<itemref idref="linha-{i}" />' for i in range(1, TOTAL + 1)
    ) + "\n" + "\n".join(
        f'<itemref idref="linha-inversa-{i}" />' for i in range(1, TOTAL + 1)
    )
    content_opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="book-id" version="3.0" xml:lang="pt-BR">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="book-id">{escape(identificador)}</dc:identifier>
  <dc:title>{escape(titulo)}</dc:title>
  <dc:language>pt-BR</dc:language>
  <meta name="cover" content="mini-grafico" />
</metadata>
<manifest>
  <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml" />
  <item id="mini-grafico" href="mini-grafico.png" media-type="image/png" properties="cover-image" />
  <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav" />
  <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
  <item id="style" href="style.css" media-type="text/css" />
  {manifest_capitulos}
</manifest>
<spine toc="ncx"><itemref idref="cover" />{spine_capitulos}</spine>
<guide><reference type="cover" title="Capa" href="cover.xhtml" /></guide>
</package>'''
    container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml" /></rootfiles>
</container>'''

    # O padrão EPUB exige que mimetype seja o primeiro item e não seja comprimido.
    with zipfile.ZipFile(arquivo_epub, "w") as epub:
        epub.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        epub.writestr("META-INF/container.xml", container_xml)
        epub.writestr("OEBPS/style.css", style_css)
        epub.writestr("OEBPS/mini-grafico.png", mini_grafico_png.getvalue())
        epub.writestr("OEBPS/cover.xhtml", capa)
        epub.writestr("OEBPS/nav.xhtml", nav)
        epub.writestr("OEBPS/toc.ncx", toc_ncx)
        epub.writestr("OEBPS/content.opf", content_opf)
        for nome, conteudo in capitulos.items():
            epub.writestr(f"OEBPS/{nome}", conteudo)

    return arquivo_epub


# O EPUB é gerado pelo botão "Gerar EPUB" no HTML produzido acima.
