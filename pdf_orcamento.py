from datetime import date
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from orcamento import calcular_total, calcular_validade, formatar_moeda

FUNDO = colors.HexColor("#05070A")
CARTAO = colors.HexColor("#0F1822")
CARTAO_ALT = colors.HexColor("#0B121A")
BORDA = colors.HexColor("#22364B")
BRANCO = colors.white
TEXTO_SUAVE = colors.HexColor("#9FB0C3")
AZUL = colors.HexColor("#1976D2")
AZUL_CLARO = colors.HexColor("#7FB4E8")

LARGURA_UTIL = 174 * mm

ESTILO_TITULO = ParagraphStyle(
    "titulo", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=BRANCO
)
ESTILO_PEQUENO = ParagraphStyle(
    "pequeno", fontName="Helvetica", fontSize=10, leading=14, textColor=TEXTO_SUAVE
)
ESTILO_ROTULO = ParagraphStyle(
    "rotulo",
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=11,
    textColor=AZUL_CLARO,
    spaceAfter=3,
)
ESTILO_NORMAL = ParagraphStyle(
    "normal", fontName="Helvetica", fontSize=10, leading=14, textColor=BRANCO
)
ESTILO_CAB_TABELA = ParagraphStyle(
    "cab_tabela",
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=11,
    textColor=BRANCO,
)
ESTILO_CAB_TABELA_DIR = ParagraphStyle(
    "cab_tabela_dir", parent=ESTILO_CAB_TABELA, alignment=TA_RIGHT
)
ESTILO_CELULA = ParagraphStyle(
    "celula", fontName="Helvetica", fontSize=10, leading=13, textColor=BRANCO
)
ESTILO_CELULA_DIR = ParagraphStyle(
    "celula_dir", parent=ESTILO_CELULA, alignment=TA_RIGHT
)


def _carregar_logo(caminho_logo, altura_mm=26):
    """Devolve o logo pronto para o PDF, ou None se não houver imagem."""
    if not caminho_logo:
        return None
    caminho = Path(caminho_logo)
    if not caminho.exists():
        return None
    try:
        imagem = PILImage.open(caminho)
        imagem.thumbnail((400, 400))
        largura_px, altura_px = imagem.size
        buffer = BytesIO()
        imagem.save(buffer, format="PNG")
        buffer.seek(0)
        altura = altura_mm * mm
        largura = altura * largura_px / altura_px
        return Image(buffer, width=largura, height=altura, mask="auto")
    except Exception:
        return None


def _bloco(rotulo, linhas):
    partes = [Paragraph(rotulo, ESTILO_ROTULO)]
    for linha in linhas or ["-"]:
        partes.append(Paragraph(linha, ESTILO_NORMAL))
    return partes


def _pagina(canvas, doc):
    """Pinta o fundo preto da página e desenha o rodapé."""
    canvas.saveState()
    canvas.setFillColor(FUNDO)
    canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(TEXTO_SUAVE)
    canvas.drawString(doc.leftMargin, 10 * mm, "Gerado por orçeJá")
    canvas.drawRightString(A4[0] - doc.rightMargin, 10 * mm, f"Página {doc.page}")
    canvas.restoreState()


def gerar_pdf(
    cliente,
    itens,
    desconto_percentual=0,
    empresa=None,
    contato_cliente=None,
    validade_dias=None,
    observacoes="",
    data_emissao=None,
    caminho_logo=None,
):
    """Gera o orçamento em PDF (fundo preto) e devolve os bytes do arquivo."""
    subtotal, desconto, total = calcular_total(itens, desconto_percentual)
    data_emissao = data_emissao or date.today()
    empresa = empresa or {}
    contato_cliente = contato_cliente or {}

    elementos = []

    # ---------- Cabeçalho ----------
    titulo = [
        Paragraph("PROPOSTA DE ORÇAMENTO", ESTILO_TITULO),
        Paragraph(
            "Data de emissão: "
            f"<font color='#FFFFFF'><b>{data_emissao.strftime('%d/%m/%Y')}</b></font>",
            ESTILO_PEQUENO,
        ),
    ]
    if validade_dias:
        validade = calcular_validade(data_emissao, validade_dias)
        titulo.append(
            Paragraph(
                "Válido até: "
                f"<font color='#FFFFFF'><b>{validade.strftime('%d/%m/%Y')}</b></font> "
                f"({validade_dias} dias)",
                ESTILO_PEQUENO,
            )
        )

    logo = _carregar_logo(caminho_logo)
    if logo:
        largura_logo = logo.drawWidth + 8 * mm
        cabecalho = Table(
            [[logo, titulo]], colWidths=[largura_logo, LARGURA_UTIL - largura_logo]
        )
    else:
        cabecalho = Table([[titulo]], colWidths=[LARGURA_UTIL])
    cabecalho.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, 0), (-1, 0), 2, AZUL),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
            ]
        )
    )
    elementos += [cabecalho, Spacer(1, 7 * mm)]

    # ---------- Empresa e cliente ----------
    linhas_empresa = []
    if empresa.get("nome"):
        linhas_empresa.append(f"<b>{escape(empresa['nome'])}</b>")
    for rotulo, chave in (("CNPJ", "cnpj"), ("Telefone", "telefone"), ("E-mail", "email")):
        if empresa.get(chave):
            linhas_empresa.append(f"{rotulo}: {escape(empresa[chave])}")

    linhas_cliente = [f"<b>{escape(cliente)}</b>"]
    if contato_cliente.get("telefone"):
        linhas_cliente.append(f"Telefone: {escape(contato_cliente['telefone'])}")
    if contato_cliente.get("endereco"):
        linhas_cliente.append(f"Endereço: {escape(contato_cliente['endereco'])}")

    if linhas_empresa:
        info = Table(
            [[_bloco("EMPRESA", linhas_empresa), "", _bloco("CLIENTE", linhas_cliente)]],
            colWidths=[85 * mm, 4 * mm, 85 * mm],
        )
        info.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BACKGROUND", (0, 0), (0, 0), CARTAO),
                    ("BACKGROUND", (2, 0), (2, 0), CARTAO),
                    ("BOX", (0, 0), (0, 0), 0.5, BORDA),
                    ("BOX", (2, 0), (2, 0), 0.5, BORDA),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
    else:
        info = Table([[_bloco("CLIENTE", linhas_cliente)]], colWidths=[LARGURA_UTIL])
        info.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), CARTAO),
                    ("BOX", (0, 0), (0, 0), 0.5, BORDA),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
    elementos += [info, Spacer(1, 8 * mm)]

    # ---------- Tabela de itens ----------
    dados = [
        [
            Paragraph("DESCRIÇÃO", ESTILO_CAB_TABELA),
            Paragraph("QTD.", ESTILO_CAB_TABELA_DIR),
            Paragraph("VALOR UNIT.", ESTILO_CAB_TABELA_DIR),
            Paragraph("SUBTOTAL", ESTILO_CAB_TABELA_DIR),
        ]
    ]
    for item in itens:
        valor_item = item["quantidade"] * item["valor_unitario"]
        dados.append(
            [
                Paragraph(escape(item["descricao"]), ESTILO_CELULA),
                Paragraph(f"{item['quantidade']:g}", ESTILO_CELULA_DIR),
                Paragraph(formatar_moeda(item["valor_unitario"]), ESTILO_CELULA_DIR),
                Paragraph(formatar_moeda(valor_item), ESTILO_CELULA_DIR),
            ]
        )
    tabela = Table(
        dados, colWidths=[84 * mm, 20 * mm, 35 * mm, 35 * mm], repeatRows=1
    )
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AZUL),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CARTAO_ALT, CARTAO]),
                ("LINEBELOW", (0, 1), (-1, -1), 0.5, BORDA),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elementos += [tabela, Spacer(1, 6 * mm)]

    # ---------- Totais ----------
    totais = Table(
        [
            ["Subtotal", formatar_moeda(subtotal)],
            [f"Desconto ({desconto_percentual:g}%)", formatar_moeda(desconto)],
            ["TOTAL", formatar_moeda(total)],
        ],
        colWidths=[48 * mm, 38 * mm],
        hAlign="RIGHT",
    )
    totais.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, 1), 10),
                ("BACKGROUND", (0, 0), (-1, 1), CARTAO),
                ("TEXTCOLOR", (0, 0), (-1, 1), BRANCO),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("BACKGROUND", (0, 2), (-1, 2), AZUL),
                ("TEXTCOLOR", (0, 2), (-1, 2), BRANCO),
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("FONTSIZE", (0, 2), (-1, 2), 12),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDA),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elementos.append(totais)

    # ---------- Observações ----------
    if observacoes and observacoes.strip():
        texto_obs = escape(observacoes.strip()).replace("\n", "<br/>")
        elementos += [
            Spacer(1, 8 * mm),
            Paragraph("OBSERVAÇÕES", ESTILO_ROTULO),
            Paragraph(texto_obs, ESTILO_NORMAL),
        ]

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
        title="Proposta de orçamento",
        author="orçeJá",
    )
    documento.build(elementos, onFirstPage=_pagina, onLaterPages=_pagina)
    return buffer.getvalue()