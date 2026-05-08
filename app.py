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
            fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", tamanho)
        except:
            fonte = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), texto, font=fonte)
        if (bbox[2] - bbox[0]) <= largura_max - 40: # Aumentei margem
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
    # Para o layout da imagem (2 colunas x 4 linhas), fixamos em 8 espaços
    qtd = 8 

    # =========================
    # 🔥 A4 EM RETRATO (Igual à foto 2)
    # =========================
    largura = 1240
    altura = 1754

    # GRID PARA 2 COLUNAS E 4 LINHAS
    colunas = 2
    linhas_grid = 4
    
    bloco_w = largura // colunas
    bloco_h = altura // linhas_grid

    # FONTES (Tamanhos maiores para o formato vertical)
    fonte_preco_tam = 160
    try:
        fonte_marca = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        fonte_produto = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
        fonte_preco = ImageFont.truetype("DejaVuSans-Bold.ttf", fonte_preco_tam)
        fonte_rs = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
        fonte_peso = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
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
    # LOOP DE GERAÇÃO
    # =========================
    for i in range(qtd):
        produto = dados.get(f"produto{i}", "").upper()
        marca = dados.get(f"marca{i}", "").upper()
        preco = formatar_preco(dados.get(f"preco{i}", ""))
        peso = dados.get(f"peso{i}", "").upper()

        # Define posição na grade 2x4
        col = i % colunas
        lin = i // colunas

        x = col * bloco_w
        y = lin * bloco_h

        # Desenha a borda do retângulo
        draw.rectangle([x, y, x + bloco_w, y + bloco_h], outline="black", width=5)

        # Se não houver produto nem preço, escreve apenas o R$ centralizado (como na sua imagem)
        if not produto and not preco or preco == "0,00":
            centralizar(draw, "R$", fonte_rs, x + bloco_w//2, y + bloco_h//2)
            continue

        # --- NOME DO PRODUTO ---
        fonte_p = ajustar_fonte(draw, produto, bloco_w, 60)
        linhas_texto = quebrar_texto(draw, produto, fonte_p, bloco_w)
        y_local = y + 40
        for linha in linhas_texto:
            centralizar(draw, linha, fonte_p, x + bloco_w//2, y_local)
            y_local += 65

        # --- MARCA ---
        if marca:
            centralizar(draw, marca, fonte_marca, x + bloco_w//2, y_local + 10)
            y_local += 60

        # --- PREÇO (CENTRALIZADO NO BLOCO) ---
        if preco and preco != "0,00":
            bbox_val = draw.textbbox((0, 0), preco, font=fonte_preco)
            lw_val = bbox_val[2] - bbox_val[0]
            
            # Desenha o "R$" pequeno à esquerda do preço
            x_centro = x + bloco_w//2
            y_preco = y + (bloco_h // 2) - 30
            
            draw.text((x_centro - (lw_val//2) - 80, y_preco + 60), "R$", font=fonte_rs, fill="black")
            draw.text((x_centro - (lw_val//2), y_preco), preco, font=fonte_preco, fill="black")
        else:
            centralizar(draw, "R$", fonte_rs, x + bloco_w//2, y + bloco_h//2)

        # --- PESO / UNIDADE (RODAPÉ DO BLOCO) ---
        if peso:
            centralizar(draw, peso, fonte_peso, x + bloco_w//2, y + bloco_h - 80)

    # =========================
    # SALVAR E ENVIAR
    # =========================
    nome = f"placas_verticais_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf"
    img.save(nome, "PDF")

    return send_file(nome, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
