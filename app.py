from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

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
            fonte = ImageFont.truetype(
                "DejaVuSans-Bold.ttf",
                tamanho
            )

        except:
            fonte = ImageFont.load_default()

        bbox = draw.textbbox(
            (0, 0),
            texto,
            font=fonte
        )

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

    for palavra in palavras:

        teste = linha + " " + palavra if linha else palavra

        bbox = draw.textbbox(
            (0, 0),
            teste,
            font=fonte
        )

        largura = bbox[2] - bbox[0]

        if largura <= largura_max - 30:
            linha = teste

        else:
            linhas.append(linha)
            linha = palavra

    if linha:
        linhas.append(linha)

    return linhas

# =========================
# CENTRALIZAR
# =========================
def centralizar(draw, texto, fonte, centro_x, y):

    if not texto:
        return

    bbox = draw.textbbox(
        (0, 0),
        texto,
        font=fonte
    )

    largura = bbox[2] - bbox[0]

    x = centro_x - (largura // 2)

    draw.text(
        (x, y),
        texto,
        font=fonte,
        fill="black"
    )

# =========================
# HOME
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

    # A4 horizontal
    largura = 1754
    altura = 1240

    if qtd == 6:

        colunas = 3
        linhas = 2
        fonte_preco_tam = 120

    elif qtd == 8:

        colunas = 4
        linhas = 2
        fonte_preco_tam = 95

    else:

        colunas = 4
        linhas = 3
        fonte_preco_tam = 75

    bloco_w = largura // colunas
    bloco_h = altura // linhas

    img = Image.new(
        "RGB",
        (largura, altura),
        "white"
    )

    draw = ImageDraw.Draw(img)

    # FONTES
    try:

        fonte_marca = ImageFont.truetype(
            "DejaVuSans-BoldOblique.ttf",
            30
        )

        fonte_preco = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            fonte_preco_tam
        )

        fonte_rs = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            int(fonte_preco_tam * 0.35)
        )

        fonte_peso = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            32
        )

    except:

        fonte_marca = ImageFont.load_default()
        fonte_preco = ImageFont.load_default()
        fonte_rs = ImageFont.load_default()
        fonte_peso = ImageFont.load_default()

    # LOOP DAS PLACAS
    for i in range(qtd):

        produto = dados.get(
            f"produto{i}",
            ""
        ).upper()

        marca = dados.get(
            f"marca{i}",
            ""
        ).upper()

        preco = formatar_preco(
            dados.get(
                f"preco{i}",
                ""
            )
        )

        peso = dados.get(
            f"peso{i}",
            ""
        ).upper()

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

        # PRODUTO
        fonte_produto = ajustar_fonte(
            draw,
            produto,
            bloco_w,
            55
        )

        linhas_texto = quebrar_texto(
            draw,
            produto,
            fonte_produto,
            bloco_w
        )

        y_texto = y + 20

        for linha in linhas_texto:

            centralizar(
                draw,
                linha,
                fonte_produto,
                x + bloco_w // 2,
                y_texto
            )

            y_texto += 45

        # MARCA
        if marca:

            centralizar(
                draw,
                marca,
                fonte_marca,
                x + bloco_w // 2,
                y_texto + 10
            )

        # PREÇO
        bbox_val = draw.textbbox(
            (0, 0),
            preco,
            font=fonte_preco
        )

        bbox_rs = draw.textbbox(
            (0, 0),
            "R$",
            font=fonte_rs
        )

        largura_val = bbox_val[2] - bbox_val[0]
        largura_rs = bbox_rs[2] - bbox_rs[0]

        total = largura_val + largura_rs + 10

        x_preco = x + (bloco_w - total) // 2

        y_preco = y + (bloco_h // 2) - 20

        draw.text(
            (x_preco, y_preco + 35),
            "R$",
            font=fonte_rs,
            fill="black"
        )

        draw.text(
            (x_preco + largura_rs + 10, y_preco),
            preco,
            font=fonte_preco,
            fill="black"
        )

        # PESO
        if peso:

            centralizar(
                draw,
                peso,
                fonte_peso,
                x + bloco_w // 2,
                y + bloco_h - 60
            )

    # SALVAR PDF
    nome_pdf = (
        f"placas_"
        f"{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf"
    )

    img.save(nome_pdf, "PDF")

    return send_file(
        nome_pdf,
        as_attachment=True
    )

# =========================
# INICIAR APP
# =========================
if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
