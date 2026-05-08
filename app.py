from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

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

        if (bbox[2] - bbox[0]) <= largura_max - 40:
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

        bbox = draw.textbbox(
            (0, 0),
            teste,
            font=fonte
        )

        if (bbox[2] - bbox[0]) <= largura_max - 50:

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

    qtd = int(dados.get("qtd", 8))

    # =========================
    # A4 RETRATO
    # =========================
    largura = 1240
    altura = 1754

    # =========================
    # CONFIGURAÇÃO POR QUANTIDADE
    # =========================
    if qtd == 6:

        colunas = 2
        linhas_grid = 3

        fonte_produto_tam = 75
        fonte_marca_tam = 55
        fonte_preco_tam = 190
        fonte_rs_tam = 60
        fonte_peso_tam = 55

    elif qtd == 8:

        # SEU LAYOUT PERFEITO
        colunas = 2
        linhas_grid = 4

        fonte_produto_tam = 60
        fonte_marca_tam = 45
        fonte_preco_tam = 160
        fonte_rs_tam = 50
        fonte_peso_tam = 45

    else:

        # 12 PLACAS
        colunas = 3
        linhas_grid = 4

        fonte_produto_tam = 38
        fonte_marca_tam = 30
        fonte_preco_tam = 85
        fonte_rs_tam = 28
        fonte_peso_tam = 28

    bloco_w = largura // colunas
    bloco_h = altura // linhas_grid

    # =========================
    # FONTES
    # =========================
    try:

        fonte_marca = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            fonte_marca_tam
        )

        fonte_preco = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            fonte_preco_tam
        )

        fonte_rs = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            fonte_rs_tam
        )

        fonte_peso = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            fonte_peso_tam
        )

    except:

        fonte_marca = ImageFont.load_default()
        fonte_preco = ImageFont.load_default()
        fonte_rs = ImageFont.load_default()
        fonte_peso = ImageFont.load_default()

    # =========================
    def centralizar(draw, texto, fonte, x, y):

        if not texto:
            return

        bbox = draw.textbbox(
            (0, 0),
            texto,
            font=fonte
        )

        lw = bbox[2] - bbox[0]

        draw.text(
            (x - lw // 2, y),
            texto,
            font=fonte,
            fill="black"
        )

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
            width=5
        )

        # =========================
        # PLACA VAZIA
        # =========================
        if (
            not produto
            and not preco
        ) or preco == "0,00":

            centralizar(
                draw,
                "R$",
                fonte_rs,
                x + bloco_w // 2,
                y + bloco_h // 2
            )

            continue

        # =========================
        # PRODUTO
        # =========================
        fonte_p = ajustar_fonte(
            draw,
            produto,
            bloco_w,
            fonte_produto_tam
        )

        linhas_texto = quebrar_texto(
            draw,
            produto,
            fonte_p,
            bloco_w
        )

        y_local = y + 40

        espacamento = 65

        if qtd == 12:
            espacamento = 40

        for linha in linhas_texto:

            centralizar(
                draw,
                linha,
                fonte_p,
                x + bloco_w // 2,
                y_local
            )

            y_local += espacamento

        # =========================
        # MARCA
        # =========================
        if marca:

            centralizar(
                draw,
                marca,
                fonte_marca,
                x + bloco_w // 2,
                y_local + 10
            )

            if qtd == 12:
                y_local += 35
            else:
                y_local += 60

        # =========================
        # PREÇO
        # =========================
        if preco and preco != "0,00":

            bbox_val = draw.textbbox(
                (0, 0),
                preco,
                font=fonte_preco
            )

            lw_val = bbox_val[2] - bbox_val[0]

            x_centro = x + bloco_w // 2

            if qtd == 12:
                y_preco = y + (bloco_h // 2) - 10
            else:
                y_preco = y + (bloco_h // 2) - 30

            draw.text(
                (
                    x_centro - (lw_val // 2) - (
                        40 if qtd == 12 else 80
                    ),
                    y_preco + (
                        30 if qtd == 12 else 60
                    )
                ),
                "R$",
                font=fonte_rs,
                fill="black"
            )

            draw.text(
                (
                    x_centro - (lw_val // 2),
                    y_preco
                ),
                preco,
                font=fonte_preco,
                fill="black"
            )

        else:

            centralizar(
                draw,
                "R$",
                fonte_rs,
                x + bloco_w // 2,
                y + bloco_h // 2
            )

        # =========================
        # PESO
        # =========================
        if peso:

            centralizar(
                draw,
                peso,
                fonte_peso,
                x + bloco_w // 2,
                y + bloco_h - (
                    50 if qtd == 12 else 80
                )
            )

    # =========================
    # SALVAR PDF
    # =========================
    nome = (
        f"placas_"
        f"{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf"
    )

    img.save(nome, "PDF")

    return send_file(
        nome,
        as_attachment=True
    )

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
