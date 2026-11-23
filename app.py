import base64
from datetime import date
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

from orcamento import (
    calcular_total,
    calcular_validade,
    converter_numero,
    formatar_moeda,
    gerar_orcamento,
)
from pdf_orcamento import gerar_pdf

PASTA = Path(__file__).parent


def abrir_icone():
    caminho = PASTA / "logo.png"
    if caminho.exists():
        try:
            icone = Image.open(caminho)
            icone.thumbnail((128, 128))
            return icone
        except Exception:
            pass
    return "⚡"


st.set_page_config(page_title="orçeJá", page_icon=abrir_icone(), layout="wide")

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    html, body, [class*="st-"] {font-size: 18px;}
    .block-container {padding-top: 2rem; max-width: 1200px;}

    h3 {font-size: 1.7rem !important;}

    /* ---------- Barra lateral ---------- */
    section[data-testid="stSidebar"] {
        background-color: #0F1B2D;
        border-right: 1px solid #2A3F5C;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 380px !important;
        width: 380px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #14243A;
        border: 1px solid #2A3F5C !important;
        border-radius: 10px;
        padding: 0.5rem 0.5rem;
    }
    .sidebar-titulo {
        color: #FFFFFF;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin: 0;
    }
    .sidebar-sub {
        color: #B8C7D9;
        font-size: 0.95rem;
        margin: 0.25rem 0 1.25rem 0;
    }
    .sidebar-secao {
        color: #7FB4E8;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        border-left: 3px solid #1976D2;
        padding-left: 0.6rem;
        margin: 0 0 0.5rem 0;
    }
    .mini-linha {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 0.35rem 0;
        color: #B8C7D9;
        font-size: 1rem;
    }
    .mini-linha strong {
        color: #FFFFFF;
        font-size: 1.15rem;
    }
    .mini-total {
        border-top: 1px solid #2A3F5C;
        margin-top: 0.4rem;
        padding-top: 0.7rem;
    }
    .mini-total strong {
        color: #7FB4E8;
        font-size: 1.5rem;
    }

    /* ---------- Cabeçalho ---------- */
    .cabecalho {
        background-color: #14243A;
        border: 1px solid #2A3F5C;
        border-top: 4px solid #1976D2;
        border-radius: 8px;
        padding: 1.75rem 2.25rem;
        min-height: 170px;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 2rem;
    }
    .cabecalho .logo {
        height: 110px;
        width: auto;
        border-radius: 22%;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45);
    }
    .cabecalho .app {
        color: #FFFFFF;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: 0.02em;
        margin: 0;
        line-height: 1.1;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
    }
    .cabecalho .titulo-proposta {
        color: #FFFFFF;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin: 0;
        line-height: 1.15;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
    }
    .cabecalho .selo-data {
        display: inline-block;
        margin-top: 0.9rem;
        margin-right: 0.6rem;
        padding: 0.4rem 1.1rem;
        background-color: rgba(25, 118, 210, 0.3);
        border: 1px solid #1976D2;
        border-radius: 999px;
        color: #E2EAF3;
        font-size: 1.05rem;
    }
    .cabecalho .selo-data strong {
        color: #FFFFFF;
    }

    /* ---------- Conteúdo ---------- */
    .titulo-coluna {
        color: #B8C7D9;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    div[data-testid="stWidgetLabel"] p {font-size: 1.1rem !important;}
    div[data-baseweb="input"] {min-height: 3.4rem;}
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        font-size: 1.2rem !important;
        padding-top: 0.8rem !important;
        padding-bottom: 0.8rem !important;
    }
    div[data-testid="stTextArea"] textarea {
        font-size: 1.2rem !important;
    }

    .stButton button, .stDownloadButton button {
        font-size: 1.15rem !important;
        min-height: 3.2rem;
        padding: 0.6rem 1.5rem;
    }

    div[data-testid="stMetric"] {
        background-color: #14243A !important;
        border: 1px solid #2A3F5C;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] label p,
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p {
        color: #B8C7D9 !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
        font-size: 2.3rem !important;
    }

    div[data-testid="stText"] {font-size: 1.05rem;}
        div[data-testid="InputInstructions"],
    div[data-testid="stTextInputInstructions"],
    div[data-testid="stNumberInputInstructions"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

EXEMPLOS = [
    ("Ex.: Ponto de tomada", "Ex.: 10", "Ex.: 85,50"),
    ("Ex.: Disjuntor 20A", "Ex.: 3", "Ex.: 42,00"),
    ("Ex.: Mão de obra (horas)", "Ex.: 8", "Ex.: 60,00"),
]

if "n_itens" not in st.session_state:
    st.session_state.n_itens = 3


def adicionar_item():
    st.session_state.n_itens += 1


def remover_item():
    if st.session_state.n_itens > 1:
        ultimo = st.session_state.n_itens - 1
        for prefixo in ("desc", "qtd", "valor"):
            st.session_state.pop(f"{prefixo}_{ultimo}", None)
        st.session_state.n_itens -= 1


def carregar_logo(altura_px):
    """Devolve o logo reduzido e pronto para o cabeçalho, ou texto vazio."""
    caminho = PASTA / "logo.png"
    if not caminho.exists():
        return ""
    try:
        imagem = Image.open(caminho)
        imagem.thumbnail((altura_px * 4, altura_px))
        buffer = BytesIO()
        imagem.save(buffer, format="PNG")
    except Exception:
        return ""
    codificado = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{codificado}"


def carregar_fundo():
    """Devolve a imagem de fundo do cabeçalho, ou texto vazio se não houver."""
    for nome, tipo in (
        ("fundo.jpg", "image/jpeg"),
        ("fundo.jpeg", "image/jpeg"),
        ("fundo.png", "image/png"),
    ):
        caminho = PASTA / nome
        if caminho.exists():
            codificado = base64.b64encode(caminho.read_bytes()).decode()
            return f"data:{tipo};base64,{codificado}"
    return ""


with st.sidebar:
    st.markdown('<p class="sidebar-titulo">Dados do orçamento</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sidebar-sub">Preencha as informações abaixo.</p>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<p class="sidebar-secao">Empresa</p>', unsafe_allow_html=True)
        empresa = st.text_input(
            "Nome da empresa",
            placeholder="Ex.: CF Instalações Elétricas",
            help="Aparece no topo do orçamento baixado.",
        )
        cnpj = st.text_input("CNPJ (opcional)", placeholder="Ex.: 00.000.000/0001-00")
        telefone_empresa = st.text_input(
            "Telefone da empresa (opcional)", placeholder="Ex.: (15) 99999-0000"
        )
        email_empresa = st.text_input(
            "E-mail da empresa (opcional)", placeholder="Ex.: contato@empresa.com.br"
        )

    with st.container(border=True):
        st.markdown('<p class="sidebar-secao">Cliente</p>', unsafe_allow_html=True)
        cliente = st.text_input("Nome do cliente", placeholder="Ex.: João da Silva")
        telefone_cliente = st.text_input(
            "Telefone do cliente (opcional)", placeholder="Ex.: (15) 98888-0000"
        )
        endereco_cliente = st.text_input(
            "Endereço do cliente (opcional)", placeholder="Ex.: Rua das Flores, 123"
        )

    with st.container(border=True):
        st.markdown('<p class="sidebar-secao">Condições</p>', unsafe_allow_html=True)
        desconto = st.number_input(
            "Desconto (%)",
            min_value=0.0,
            max_value=100.0,
            value=None,
            step=1.0,
            placeholder="Ex.: 10",
            help="Percentual aplicado sobre o subtotal.",
        )
        validade_dias = st.number_input(
            "Validade da proposta (dias)",
            min_value=1,
            max_value=365,
            value=None,
            step=1,
            placeholder="Ex.: 15",
            help="A data limite é calculada a partir de hoje.",
        )
        observacoes = st.text_area(
            "Observações (opcional)",
            placeholder="Ex.: Pagamento em 2x. Prazo de execução: 5 dias úteis.",
            height=120,
        )

desconto = desconto or 0.0
validade_dias = int(validade_dias) if validade_dias else None

fundo_uri = carregar_fundo()
if fundo_uri:
    st.markdown(
        f"""
        <style>
        .cabecalho {{
            background-image:
                linear-gradient(90deg, rgba(11, 22, 35, 0.88) 0%, rgba(11, 22, 35, 0.45) 100%),
                url("{fundo_uri}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

logo_uri = carregar_logo(220)
if logo_uri:
    marca_html = f'<img class="logo" src="{logo_uri}" alt="orçeJá">'
else:
    marca_html = '<p class="app">orçeJá</p>'

hoje = date.today()
selos_html = (
    f'<span class="selo-data">Data de emissão: <strong>{hoje.strftime("%d/%m/%Y")}</strong></span>'
)
if validade_dias:
    validade = calcular_validade(hoje, validade_dias)
    selos_html += (
        f'<span class="selo-data">Válido até: <strong>{validade.strftime("%d/%m/%Y")}</strong></span>'
    )

st.markdown(
    f"""
    <div class="cabecalho">
        {marca_html}
        <div>
            <p class="titulo-proposta">Proposta de orçamento</p>
            {selos_html}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Itens do orçamento")

cab1, cab2, cab3 = st.columns([5, 2, 2])
cab1.markdown('<p class="titulo-coluna">Descrição</p>', unsafe_allow_html=True)
cab2.markdown('<p class="titulo-coluna">Quantidade</p>', unsafe_allow_html=True)
cab3.markdown('<p class="titulo-coluna">Valor unitário (R$)</p>', unsafe_allow_html=True)

itens = []
linhas_invalidas = 0
for i in range(st.session_state.n_itens):
    ex_desc, ex_qtd, ex_valor = EXEMPLOS[i % len(EXEMPLOS)]
    c1, c2, c3 = st.columns([5, 2, 2])
    descricao = c1.text_input(
        "Descrição",
        key=f"desc_{i}",
        placeholder=ex_desc,
        label_visibility="collapsed",
    )
    texto_qtd = c2.text_input(
        "Quantidade",
        key=f"qtd_{i}",
        placeholder=ex_qtd,
        label_visibility="collapsed",
    )
    texto_valor = c3.text_input(
        "Valor unitário",
        key=f"valor_{i}",
        placeholder=ex_valor,
        label_visibility="collapsed",
    )
    quantidade = converter_numero(texto_qtd)
    valor_unitario = converter_numero(texto_valor)
    if (texto_qtd.strip() and quantidade is None) or (
        texto_valor.strip() and valor_unitario is None
    ):
        linhas_invalidas += 1
    if descricao.strip() and quantidade is not None and valor_unitario is not None:
        itens.append(
            {
                "descricao": descricao.strip(),
                "quantidade": quantidade,
                "valor_unitario": valor_unitario,
            }
        )

if linhas_invalidas:
    st.warning(
        "Alguns números não foram entendidos. "
        "Use só dígitos, vírgula ou ponto (ex.: 85,50)."
    )

b1, b2, _ = st.columns([2, 2, 4])
b1.button("＋ Adicionar item", on_click=adicionar_item)
b2.button("－ Remover último", on_click=remover_item)

subtotal, valor_desconto, total = calcular_total(itens, desconto)

with st.sidebar:
    with st.container(border=True):
        st.markdown('<p class="sidebar-secao">Resumo rápido</p>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="mini-linha"><span>Itens preenchidos</span><strong>{len(itens)}</strong></div>
            <div class="mini-linha"><span>Desconto</span><strong>{desconto:g}%</strong></div>
            <div class="mini-linha mini-total"><span>Total</span><strong>{formatar_moeda(total)}</strong></div>
            """,
            unsafe_allow_html=True,
        )

st.subheader("Resumo")
col1, col2, col3 = st.columns(3)
col1.metric("Subtotal", formatar_moeda(subtotal))
col2.metric("Desconto", formatar_moeda(valor_desconto))
col3.metric("Total", formatar_moeda(total))

st.write("")
if st.button("Gerar orçamento", type="primary"):
    if not cliente.strip():
        st.warning("Digite o nome do cliente na barra lateral.")
    elif not itens:
        st.warning("Preencha pelo menos um item completo (descrição, quantidade e valor).")
    else:
        dados_empresa = {
            "nome": empresa.strip(),
            "cnpj": cnpj.strip(),
            "telefone": telefone_empresa.strip(),
            "email": email_empresa.strip(),
        }
        dados_cliente = {
            "telefone": telefone_cliente.strip(),
            "endereco": endereco_cliente.strip(),
        }
        texto = gerar_orcamento(
            cliente.strip(),
            itens,
            desconto,
            empresa=dados_empresa,
            contato_cliente=dados_cliente,
            validade_dias=validade_dias,
            observacoes=observacoes,
        )
        pdf = gerar_pdf(
            cliente.strip(),
            itens,
            desconto,
            empresa=dados_empresa,
            contato_cliente=dados_cliente,
            validade_dias=validade_dias,
            observacoes=observacoes,
            caminho_logo=PASTA / "logo.png",
        )
        st.session_state.orcamento_gerado = {
            "texto": texto,
            "pdf": pdf,
            "nome": cliente.strip().replace(" ", "_"),
        }

gerado = st.session_state.get("orcamento_gerado")
if gerado:
    st.success("Orçamento gerado! Baixe no formato que preferir.")
    d1, d2, _ = st.columns([2, 2, 3])
    d1.download_button(
        "Baixar PDF",
        gerado["pdf"],
        file_name=f"orcamento_{gerado['nome']}.pdf",
        mime="application/pdf",
        type="primary",
    )
    d2.download_button(
        "Baixar .txt",
        gerado["texto"],
        file_name=f"orcamento_{gerado['nome']}.txt",
    )
    st.caption(
        "Se mudar algum dado, clique de novo em Gerar orçamento para atualizar os arquivos."
    )
    with st.expander("Ver texto do orçamento"):
        st.text(gerado["texto"])