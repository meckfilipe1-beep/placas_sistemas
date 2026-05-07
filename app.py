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
    # CONFIGURAÇÃO DAS PLACAS
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
        fonte_marca = ImageFont.truetype("DejaVuSans.ttf", 32)
        fonte_preco = ImageFont.truetype("DejaVuSans-Bold.ttf", fonte_preco_tam)
        fonte_rs = ImageFont.truetype("DejaVuSans-Bold.ttf", int(fonte_preco_tam * 0.35))
        fonte_peso = ImageFont.truetype("DejaVuSans-Bold.ttf", 35)

    except:
        fonte_marca = ImageFont.load_default()
        fonte_preco = ImageFont.load_default()
        fonte_rs = ImageFont.load_default()
        fonte_peso = ImageFont.load_default()

    # =========================
    # GERAR CADA PLACA
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

        # =========================
        # BORDA
        # =========================
        draw.rectangle(
            [x, y, x + bloco_w, y + bloco_h],
            outline="black",
            width=4
        )

        # =========================
        # CENTRALIZAR TEXTO
        # =========================
        def centralizar(texto, fonte, y_local):

            if not texto:
                return

            bbox = draw.textbbox((0, 0), texto, font=fonte)

            largura_texto = bbox[2] - bbox[0]

            x_texto = x + (bloco_w - largura_texto) // 2

            draw.text(
                (x_texto, y + y_local),
                texto,
                font=fonte,
                fill="black"
            )

        # =========================
        # AJUSTE AUTOMÁTICO PRODUTO
        # =========================
        fonte_produto = ajustar_fonte(
            draw,
            produto,
            bloco_w,
            60
        )

        # =========================
        # PRODUTO
        # =========================
        centralizar(produto, fonte_produto, 20)

        # =========================
        # MARCA
        # =========================
        centralizar(marca, fonte_marca, 95)

        # =========================
        # PREÇO CENTRALIZADO
        # =========================
        bbox_val = draw.textbbox((0, 0), preco, font=fonte_preco)
        bbox_rs = draw.textbbox((0, 0), "R$", font=fonte_rs)

        largura_val = bbox_val[2] - bbox_val[0]
        largura_rs = bbox_rs[2] - bbox_rs[0]

        espaco = 10

        largura_total = largura_rs + espaco + largura_val

        x_inicio = x + (bloco_w - largura_total) // 2

        y_preco = y + (bloco_h // 2) - 20

        # R$
        draw.text(
            (x_inicio, y_preco + 40),
            "R$",
            font=fonte_rs,
            fill="black"
        )

        # VALOR
        draw.text(
            (x_inicio + largura_rs + espaco, y_preco),
            preco,
            font=fonte_preco,
            fill="black"
        )

        # =========================
        # PESO
        # =========================
        centralizar(
            peso,
            fonte_peso,
            bloco_h - 70
        )

    # =========================
    # SALVAR PDF
    # =========================
    nome_pdf = f"placas_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf"

    img.save(nome_pdf, "PDF")

    return send_file(
        nome_pdf,
        as_attachment=True
    )

# =========================
# INICIAR SISTEMA
# =========================
if __name__ == "__main__":
    app.run()
