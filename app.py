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

    # =========================
    # VERTICAL (SEM ROTATE)
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

    largura = 1240
    altura = 1754

    img = Image.new("RGB", (largura, altura), "white")
    draw = ImageDraw.Draw(img)

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

    def centralizar(texto, fonte, x, y):
        bbox = draw.textbbox((0, 0), texto, font=fonte)
        lw = bbox[2] - bbox[0]
        draw.text((x - lw//2, y), texto, font=fonte, fill="black")

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
        # PRODUTO (MAIS ESPAÇO)
        # =========================
        fonte_produto = ajustar_fonte(draw, produto, bloco_w, 60)
        linhas = quebrar_texto(draw, produto, fonte_produto, bloco_w)

        y_local = y + 20

        for linha in linhas:
            centralizar(linha, fonte_produto, x + bloco_w//2, y_local)
            y_local += 45

        # =========================
        # MARCA
        # =========================
        if marca:
            centralizar(marca, fonte_marca, x + bloco_w//2, y_local + 10)

        # =========================
        # PREÇO
        # =========================
        bbox_val = draw.textbbox((0, 0), preco, font=fonte_preco)
        bbox_rs = draw.textbbox((0, 0), "R$", font=fonte_rs)

        lw_val = bbox_val[2] - bbox_val[0]
        lw_rs = bbox_rs[2] - bbox_rs[0]

        total = lw_val + lw_rs + 10

        x_inicio = x + (bloco_w - total)//2
        y_preco = y + (bloco_h//2) - 20

        draw.text((x_inicio, y_preco + 40), "R$", font=fonte_rs, fill="black")
        draw.text((x_inicio + lw_rs + 10, y_preco), preco, font=fonte_preco, fill="black")

        # =========================
        # PESO
        # =========================
        if peso:
            centralizar(peso, fonte_peso, x + bloco_w//2, y + bloco_h - 70)

    # =========================
    nome = f"placas_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf"
    img.save(nome, "PDF")

    return send_file(nome, as_attachment=True)

# =========================
if __name__ == "__main__":
    app.run()
