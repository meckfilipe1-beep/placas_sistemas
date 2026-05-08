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

        valor = float(
            valor.replace(",", ".")
        )

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

        if largura <= largura_max - 30:

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

    return render_template(
        "index.html"
    )

# =========================
# GERAR PDF
# =========================
@app.route("/gerar", methods=["POST"])
def gerar():

    dados = request.form

    qtd = int(
        dados.get("qtd")
    )

    # =========================
    # TAMANHO A4 NORMAL
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
    # IMAGEM BASE
    # =========================
    img = Image.new(
        "RGB",
        (largura, altura),
        "white"
    )

    draw = ImageDraw.Draw(img)

    # =========================
    # LOOP DAS PLACAS
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
        # BORDA DA PLACA
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
        # ÁREA INTERNA ROTACIONADA
        # =========================
        interno = Image.new(
            "RGBA",
            (bloco_h, bloco_w),
            (255, 255, 255, 0)
        )

        d = ImageDraw.Draw(interno)

        # =========================
        # FONTES
        # =========================
        try:

            fonte_produto = ajustar_fonte(
                d,
                produto,
                bloco_h,
                70
            )

            fonte_marca = ImageFont.truetype(
                "DejaVuSans-BoldOblique.ttf",
                42
            )

            if qtd == 12:

                fonte_preco = ImageFont.truetype(
                    "DejaVuSans-Bold.ttf",
                    90
                )

            elif qtd == 8:

                fonte_preco = ImageFont.truetype(
                    "DejaVuSans-Bold.ttf",
                    110
                )

            else:

                fonte_preco = ImageFont.truetype(
                    "DejaVuSans-Bold.ttf",
                    130
                )

            fonte_rs = ImageFont.truetype(
                "DejaVuSans-Bold.ttf",
                45
            )

            fonte_peso = ImageFont.truetype(
                "DejaVuSans-Bold.ttf",
                42
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
            bloco_h
        )

        y_texto = 30

        for linha in linhas:

            bbox = d.textbbox(
                (0, 0),
                linha,
                font=fonte_produto
            )

            largura_txt = bbox[2] - bbox[0]

            d.text(
                (
                    (bloco_h - largura_txt) // 2,
                    y_texto
                ),
                linha,
                font=fonte_produto,
                fill="black"
            )

            y_texto += 65

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
                    (bloco_h - largura_txt) // 2,
                    y_texto + 10
                ),
                marca,
                font=fonte_marca,
                fill="black"
            )

        # =========================
        # PREÇO
        # =========================
        y_preco = (bloco_w // 2) - 40

        d.text(
            (80, y_preco + 45),
            "R$",
            font=fonte_rs,
            fill="black"
        )

        d.text(
            (170, y_preco),
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
                    (bloco_h - largura_txt) // 2,
                    bloco_w - 80
                ),
                peso,
                font=fonte_peso,
                fill="black"
            )

        # =========================
        # ROTACIONA APENAS CONTEÚDO
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
    # SALVAR PDF
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
