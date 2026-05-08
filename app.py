from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

app = Flask(__name__)

# =========================
def formatar_preco(valor):
    try:
        valor = float(valor.replace(",", "."))
        return f"{valor:.2f}".replace(".", ",")
    except:
        return valor

# =========================
def ajustar_fonte(draw, texto, largura_max, tamanho):
    while tamanho > 10:
        try:
            fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", tamanho)
        except:
            fonte = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), texto, font=fonte)
        if (bbox[2] - bbox[0]) <= largura_max - 20:
            return fonte

        tamanho -= 2

    return ImageFont.load_default()

# =========================
def quebrar_texto(draw, texto, fonte, largura_max):
    palavras = texto.split()
    linhas = []
    linha = ""

    for p in palavras:
        teste = linha + " " + p if linha else p
        bbox = draw.textbbox((0, 0), teste, font=fonte)

        if (bbox[2] - bbox[0]) <= largura_max - 30:
            linha = teste
        else:
            linhas.append(linha)
            linha = p

    if linha:
        linhas.append(linha)

    return linhas

# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
@app.route("/gerar", methods=["POST"])
def gerar():

    dados = request.form
    qtd = int(dados.get("qtd"))

    if qtd == 6:
        colunas, linhas = 2, 3
        fonte_preco_tam = 120
    elif qtd == 8:
        colunas, linhas = 2, 4
        fonte_preco_tam = 95
    else:
        colunas, linhas = 3, 4
        fonte_preco_tam = 70

    largura = 1240
    altura = 1754

    bloco_w = largura // colunas
    bloco_h = altura // linhas

    # =========================
    # FONTES
    # =========================
    try:
        fonte_marca = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        fonte_produto = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
        fonte_preco = ImageFont.truetype("DejaVuSans-Bold.ttf", fonte_preco_tam)
        fonte_rs = ImageFont.truetype("DejaVuSans-Bold.ttf", int(fonte_preco_tam * 0.35))
        fonte_peso = ImageFont.truetype("DejaVuSans-Bold.ttf", 35)
    except:
        fonte_marca = fonte_produto = fonte_preco = fonte_rs = fonte_peso = ImageFont.load_default()

    def centralizar(draw, texto, fonte, x, y):
        if not texto:
            return
        bbox = draw.textbbox((0, 0), texto, font=fonte)
        lw = bbox[2] - bbox[0]
        draw.text((x - lw//2, y), texto, font=fonte, fill="black")

    img = Image.new("RGB", (largura, altura), "white")
    draw = ImageDraw.Draw(img)

    # =========================
    for i in range(qtd):

        produto = dados.get(f"produto{i}", "").upper()
        marca = dados.get(f"marca{i}", "").upper()
        preco = formatar_preco(dados.get(f"preco{i}", ""))
        peso = dados.get(f"peso{i}", "").upper()

        col = i % colunas
        lin = i // colunas

        x = col * bloco_w
        y = lin * bloco_h

        draw.rectangle([x, y, x + bloco_w, y + bloco_h], outline="black", width=4)

        # =========================
        # 🔥 CONTEÚDO (ANTES DA ROTAÇÃO)
        # =========================
        conteudo = Image.new("RGB", (bloco_w, bloco_h), "white")
        dc = ImageDraw.Draw(conteudo)

        # PRODUTO
        fonte_p = ajustar_fonte(dc, produto, bloco_w, 55)
        linhas = quebrar_texto(dc, produto, fonte_p, bloco_w)

        y_local = 20
        for linha in linhas:
            bbox = dc.textbbox((0, 0), linha, font=fonte_p)
            lw = bbox[2] - bbox[0]
            dc.text(((bloco_w - lw)//2, y_local), linha, font=fonte_p, fill="black")
            y_local += 45

        # MARCA
        if marca:
            bbox = dc.textbbox((0, 0), marca, font=fonte_marca)
            lw = bbox[2] - bbox[0]
            dc.text(((bloco_w - lw)//2, y_local + 10), marca, font=fonte_marca, fill="black")

        # PREÇO
        bbox_val = dc.textbbox((0, 0), preco, font=fonte_preco)
        bbox_rs = dc.textbbox((0, 0), "R$", font=fonte_rs)

        lw_val = bbox_val[2] - bbox_val[0]
        lw_rs = bbox_rs[2] - bbox_rs[0]

        total = lw_val + lw_rs + 10

        x_preco = (bloco_w - total)//2
        y_preco = bloco_h//2

        dc.text((x_preco, y_preco), "R$", font=fonte_rs, fill="black")
        dc.text((x_preco + lw_rs + 10, y_preco), preco, font=fonte_preco, fill="black")

        # PESO
        if peso:
            bbox = dc.textbbox((0, 0), peso, font=fonte_peso)
            lw = bbox[2] - bbox[0]
            dc.text(((bloco_w - lw)//2, bloco_h - 60), peso, font=fonte_peso, fill="black")

        # =========================
        # 🔄 R
