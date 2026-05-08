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
def ajustar_fonte(
    draw,
    texto,
    largura_max,
    tamanho
):

    while tamanho > 20:

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

        if largura <= largura_max - 40:
            return fonte

        tamanho -= 2

    return ImageFont.load_default()

# =========================
# QUEBRAR TEXTO
# =========================
def quebrar_texto(
    draw,
    texto,
    fonte,
    largura_max
):

    palavras = texto.split()

    linhas = []

    linha = ""

    for palavra in palavras:

        teste = (
            linha + " " + palavra
            if linha
            else palavra
        )

        bbox = draw.textbbox(
            (0, 0),
            teste,
            font=fonte
        )

        largura = bbox[2] - bbox[0]

        if largura <= largura_max - 50:

            linha = teste

        else:

            linhas.append(linha)
            linha = palavra

    if linha:
        linhas.append(linha)

    return linhas

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

    # =========================
    # A4 NORMAL
    # =========================
    largura = 1240
    altura = 1754

    # =========================
    # GRID
    # =========================
    if qtd == 6:

        colunas = 2
        linhas = 3

    elif qtd == 8:

        colunas = 2
        linhas = 4

    else:

        colunas = 3
        linhas = 4

    bloco_w = largura // colunas
    bloco_h = altura // linhas

    # =========================
    # IMAGEM
    # =========================
    img = Image.new(
        "RGB",
        (largura, altura),
        "white"
    )

    draw = ImageDraw.Draw(img)

    # =========================
    # LOOP
    # =========================
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

        # =========================
        # BORDA
        # =========================
        draw.rectangle(
            [
                x,
                y,
                x + bloco_w,
                y + bloco_h
            ],
            outline="black",
            width=4
        )

        # =========================
        # CONTEÚDO INTERNO
        # =========================
        interno = Image.new(
            "RGBA",
            (bloco_w, bloco_h),
            (255, 255, 255, 0)
        )

        d = ImageDraw.Draw(interno)

        # =========================
        # FONTES GIGANTES
        # =========================
        try:

            fonte_produto = ajustar_fonte(
                d,
                produto,
                bloco_w,
                140
            )

            fonte_marca = ImageFont.truetype(
                "DejaVuSans-BoldOblique.ttf",
                70
            )

            if qtd == 12:

                preco_tam = 120

            elif qtd == 8:

                preco_tam = 150

            else:

                preco_tam = 180

            fonte_preco = ImageFont.truetype(
                "DejaVuSans-Bold.ttf",
                preco_tam
            )

            fonte_rs = ImageFont.truetype(
                "DejaVuSans-Bold.ttf",
                65
            )

            fonte_peso = ImageFont.truetype(
                "DejaVuSans-Bold.ttf",
                75
            )

        except:

            fonte_produto = ImageFont.load_default()
            fonte_marca = ImageFont.load_default()
            fonte_preco = ImageFont.load_default()
            fonte_rs = ImageFont.load_default()
            fonte_peso = ImageFont.load_default()

        # =========================
        # PRODUTO
        # =========================
        linhas = quebrar_texto(
            d,
            produto,
            fonte_produto,
            bloco_w
        )

        y_texto = 40

        for linha in linhas:

            bbox = d.textbbox(
                (0, 0),
                linha,
                font=fonte_produto
            )

            largura_txt = bbox[2] - bbox[0]

            d.text(
                (
                    (bloco_w - largura_txt) // 2,
                    y_texto
                ),
                linha,
                font=fonte_produto,
                fill="black"
            )

            y_texto += 110

        # =========================
        # MARCA
        # =========================
        if marca:

            bbox = d.textbbox(
                (0, 0),
                marca,
                font=fonte_marca
            )

            largura_txt = bbox[2] - bbox[0]

            d.text(
                (
                    (bloco_w - largura_txt) // 2,
                    y_texto + 20
                ),
                marca,
                font=fonte_marca,
                fill="black"
            )

        # =========================
        # PREÇO
        # =========================
        y_preco = (bloco_h // 2) - 60

        d.text(
            (90, y_preco + 70),
            "R$",
            font=fonte_rs,
            fill="black"
        )

        d.text(
            (220, y_preco),
            preco,
            font=fonte_preco,
            fill="black"
        )

        # =========================
        # PESO
        # =========================
        if peso:

            bbox = d.textbbox(
                (0, 0),
                peso,
                font=fonte_peso
            )

            largura_txt = bbox[2] - bbox[0]

            d.text(
                (
                    (bloco_w - largura_txt) // 2,
                    bloco_h - 120
                ),
                peso,
                font=fonte_peso,
                fill="black"
            )

        # =========================
        # ROTACIONA SOMENTE TEXTO
        # =========================
        interno = interno.rotate(
            90,
            expand=True
        )

        img.paste(
            interno,
            (x, y),
            interno
        )

    # =========================
    # PDF
    # =========================
    nome_pdf = (
        f"placas_"
        f"{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf"
    )

    img.save(
        nome_pdf,
        "PDF"
    )

    return send_file(
        nome_pdf,
        as_attachment=True
    )

# =========================
# INICIAR
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
