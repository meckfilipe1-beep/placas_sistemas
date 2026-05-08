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
# AJUSTAR FONTE
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
# QUEBRAR TEXTO
# =========================
def quebrar_texto(draw, texto, fonte, largura_max):

    palavras = texto.split()
    linhas = []
    linha = ""

    for p in palavras:
        teste = linha + " " + p if linha else p

        bbox = draw.textbbox((0, 0), teste, font=fonte)
        largura = bbox[2] - bbox[0]

        if largura <= largura_max - 30:
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

    # =========================
    # CONFIG
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
    # A4
    # =========================
    largura = 1240
    altura = 1754

    bloco_w = largura // colunas
    bloco_h = altura // linhas

    # =========================
    FONTES
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
    # LISTA DE PLACAS
    # =========================
    placas = []

    for i in range(qtd):

        temp = Image.new("RGB", (bloco_w, bloco_h), "white")
        d = ImageDraw.Draw(temp)

        produto = dados.get(f"produto{i}", "").upper()
        marca = dados.get(f"marca{i}", "").upper()
        preco = formatar_preco(dados.get(f"preco{i}", ""))
        peso = dados.get(f"peso{i}", "").upper()

        # BORDA
        d.rectangle([0, 0, bloco_w, bloco_h], outline="black", width=4)

        # =========================
        # PRODUTO
        # =========================
        fonte_produto = ajustar_fonte(d, produto, bloco_w, 52)
        linhas = quebrar_texto(d, produto, fonte_produto, bloco_w)

        y = 20

        for linha in linhas:
            bbox = d.textbbox((0, 0), linha, font=fonte_produto)
            lw = bbox[2] - bbox[0]

            d.text(((bloco_w - lw)//2, y), linha, font=fonte_produto, fill="black")
            y += 45

        # =========================
        # MARCA
        # =========================
        if marca:
            bbox = d.textbbox((0, 0), marca, font=fonte_marca)
            lw = bbox[2] - bbox[0]

            d.text(((bloco_w - lw)//2, y + 10), marca, font=fonte_marca, fill="black")

        # =========================
        # PREÇO
        # =========================
        bbox_val = d.textbbox((0, 0), preco, font=fonte_preco)
        bbox_rs = d.textbbox((0, 0), "R$", font=fonte_rs)

        lw_val = bbox_val[2] - bbox_val[0]
        lw_rs = bbox_rs[2] - bbox_rs[0]

        total = lw_val + lw_rs + 10

        x_inicio = (bloco_w - total)//2
        y_preco = bloco_h//2

        d.text((x_inicio, y_preco), "R$", font=fonte_rs, fill="black")
        d.text((x_inicio + lw_rs + 10, y_preco), preco, font=fonte_preco, fill="black")

        # =========================
        # PESO
        # =========================
        if peso:
            bbox = d.textbbox((0, 0), peso, font=fonte_peso)
            lw = bbox[2] - bbox[0]

            d.text(((bloco_w - lw)//2, bloco_h - 60), peso, font=fonte_peso, fill="black")

        # =========================
        # ROTACIONA 90°
        # =========================
        temp = temp.rotate(90, expand=True)

        placas.append(temp)

    # =========================
    # PDF FINAL
    # =========================
    img = Image.new("RGB", (largura, altura), "white")

    x = 0
    y = 0

    for p in placas:

        img.paste(p, (x, y))

        x += p.width

        if x >= largura:
            x = 0
            y += p.height

    nome = f"placas_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf"

    img.save(nome, "PDF")

    return send_file(nome, as_attachment=True)

# =========================
if __name__ == "__main__":
    app.run()
