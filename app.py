from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

app = Flask(__name__)

def formatar_preco(valor):
    try:
        v = float(valor.replace(",", "."))
        return f"{v:.2f}".replace(".", ",")
    except:
        return valor

def ajustar_fonte(draw, texto, largura_max, fonte_path, tamanho):
    while tamanho > 10:
        fonte = ImageFont.truetype(fonte_path, tamanho)
        w, h = draw.textbbox((0,0), texto, font=fonte)[2:]

        if w <= largura_max - 20:
            return fonte

        tamanho -= 2

    return ImageFont.truetype(fonte_path, tamanho)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/gerar", methods=["POST"])
def gerar():
    dados = request.form
    qtd = int(dados.get("qtd"))

    if qtd == 6:
        colunas, linhas = 2, 3
    elif qtd == 8:
        colunas, linhas = 2, 4
    else:
        colunas, linhas = 3, 4

    largura, altura = 1240, 1754
    img = Image.new("RGB", (largura, altura), "white")
    draw = ImageDraw.Draw(img)

    bloco_w = largura // colunas
    bloco_h = altura // linhas

    fonte_marca = ImageFont.truetype("ariali.ttf", 35)
    fonte_preco = ImageFont.truetype("arialbd.ttf", 120)
    fonte_rs = ImageFont.truetype("arialbd.ttf", 40)
    fonte_peso = ImageFont.truetype("arialbd.ttf", 40)

    for i in range(qtd):
        produto = dados.get(f"produto{i}", "").upper()
        marca = dados.get(f"marca{i}", "").upper()
        preco = formatar_preco(dados.get(f"preco{i}", ""))
        peso = dados.get(f"peso{i}", "").upper()

        col = i % colunas
        lin = i // colunas

        x = col * bloco_w
        y = lin * bloco_h

        draw.rectangle([x, y, x+bloco_w, y+bloco_h], outline="black", width=3)

        def centralizar(texto, fonte, y_offset):
            if not texto:
                return
            w, h = draw.textbbox((0,0), texto, font=fonte)[2:]
            draw.text((x + (bloco_w-w)//2, y + y_offset), texto, font=fonte, fill="black")

        # 🔥 ajuste automático do produto
        fonte_auto = ajustar_fonte(draw, produto, bloco_w, "arialbd.ttf", 55)

        centralizar(produto, fonte_auto, 20)
        centralizar(marca, fonte_marca, 90)

        # preço centralizado
        w_val, h_val = draw.textbbox((0,0), preco, font=fonte_preco)[2:]
        w_rs, h_rs = draw.textbbox((0,0), "R$", font=fonte_rs)[2:]

        total = w_rs + w_val + 10
        x_start = x + (bloco_w - total)//2
        y_price = y + bloco_h//2 - 20

        draw.text((x_start, y_price), "R$", font=fonte_rs, fill="black")
        draw.text((x_start + w_rs + 10, y_price - 15), preco, font=fonte_preco, fill="black")

        centralizar(peso, fonte_peso, bloco_h - 70)

    nome = f"placas_{datetime.now().strftime('%d-%m-%Y_%H-%M')}.pdf"
    img.save(nome, "PDF")

    return send_file(nome, as_attachment=True)

if __name__ == "__main__":
    app.run()
