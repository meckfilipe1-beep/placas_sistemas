from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

app = Flask(__name__)

# =========================
# FORMATAR PREÇO
# =========================
def formatar_preco(valor):
    try:
        valor = float(valor.replace(",", "."))
        return f"{valor:.2f}".replace(".", ",")
    except:
        return valor

# =========================
# AJUSTAR FONTE AUTOMÁTICA
# =========================
def ajustar_fonte(draw, texto, largura_max, tamanho):
    while tamanho > 10:

        try:
            fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", tamanho)
        except:
            fonte = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), texto, font=fonte)
        largura = bbox[2] - bbox[0]

        if largura <= largura_max - 20:
            return fonte

        tamanho -= 2

    return ImageFont.load_default()

# =========================
# QUEBRAR TEXTO AUTOMÁTICO
# =========================
def quebrar_texto(draw, texto, fonte, largura_max):

    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:

        teste = linha_atual + " " + palavra if linha_atual else palavra

        bbox = draw.textbbox((0, 0), teste, font=fonte)
        largura = bbox[2] - bbox[0]

        if largura <= largura_max - 40:
            linha_atual = teste
        else:
            linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas

# =========================
# PÁGINA INICIAL
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# GERAR PDF
# =========================
@app.route("/gerar", methods=["POST"])
def gerar():

    dados = request.form
    qtd = int(dados.get("qtd"))

    # =========================
    # LAYOUT VERTICAL (EM PÉ)
    # =========================
    if qtd == 6:
        colunas, linhas = 2, 3
        fonte_preco_tam = 120

    elif qtd == 8:
        colunas, linhas = 2, 4
        fonte_preco_tam = 95

    else:
        colunas, linhas = 3, 4
        fonte_preco_tam = 70

    # =========================
    # TAMANHO A4
    # =========================
    largura = 1240
    altura = 1754

    img = Image.new("RGB", (largura, altura), "white")
    draw = ImageDraw.Draw(img)

    bloco_w = largura // colunas
    bloco_h = altura // linhas

    # =========================
    # FONTES
    # =========================
    try:
        fonte_marca = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        fonte_preco = ImageFont.truetype("DejaVuSans-Bold.ttf", fonte_preco_tam)
        fonte_rs = ImageFont.truetype("DejaVuSans-Bold.ttf", int(fonte_preco_tam * 0.35))
        fonte_peso = ImageFont.truetype("DejaVuSans-Bold.ttf", 35)

    except:
        fonte_marca = ImageFont.load_default()
        fonte_preco = ImageFont.load_default()
        fonte_rs = ImageFont.load_default()
        fonte_peso = ImageFont.load_default()

    # =========================
    # CENTRALIZAR TEXTO
    # =========================
    def centralizar(texto, fonte, x, y, bloco_w):

        if not texto:
            return

        bbox = draw.textbbox((0, 0), texto, font=fonte)
        largura_texto = bbox[2] - bbox[0]

        x_texto = x + (bloco_w - largura_texto) // 2

        draw.text(
            (x_texto, y),
            texto,
            font=fonte,
            fill="black"
        )

    # =========================
    # GERAR PLACAS
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

        # BORDA
        draw.rectangle(
            [x, y, x + bloco_w, y + bloco_h],
            outline="black",
            width=4
        )

        # =========================
        # PRODUTO
        # =========================
        fonte_produto = ajustar_fonte(draw, produto, bloco_w, 52)
        linhas_produto = quebrar_texto(draw, produto, fonte_produto, bloco_w)

        y_produto = y + 20

        for linha in linhas_produto:
            centralizar(linha, fonte_produto, x, y_produto, bloco_w)
            y_produto += 45

        # =========================
        # MARCA (NEGRITO + EFEITO VISUAL INCLINADO)
        # =========================
        y_marca = y_produto + 10

        if marca:

            bbox = draw.textbbox((0, 0), marca, font=fonte_marca)
            largura_texto = bbox[2] - bbox[0]

            x_texto = x + (bloco_w - largura_texto) // 2

            # sombra leve (efeito inclinado visual)
            draw.text(
                (x_texto + 2, y_marca),
                marca,
                font=fonte_marca,
                fill="black"
            )

            draw.text(
                (x_texto, y_marca),
                marca,
                font=fonte_marca,
                fill="black"
            )

        # =========================
        # PREÇO
        # =========================
        bbox_val = draw.textbbox((0, 0), preco, font=fonte_preco)
        bbox_rs = draw.textbbox((0, 0), "R$", font=fonte_rs)

        largura_val = bbox_val[2] - bbox_val[0]
        largura_rs = bbox_rs[2] - bbox_rs[0]

        espaco = 10
        largura_total = largura_rs +
