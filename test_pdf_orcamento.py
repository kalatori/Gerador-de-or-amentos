from datetime import date

from PIL import Image

from pdf_orcamento import gerar_pdf

ITENS = [{"descricao": "Ponto de tomada", "quantidade": 10, "valor_unitario": 85.5}]


def test_pdf_basico():
    pdf = gerar_pdf("João", ITENS, 10, data_emissao=date(2026, 11, 22))
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_pdf_com_todos_os_dados(tmp_path):
    logo = tmp_path / "logo.png"
    Image.new("RGB", (200, 200), "navy").save(logo)
    pdf = gerar_pdf(
        "Maria & Filhos <Ltda>",
        ITENS,
        5,
        empresa={
            "nome": "CF Instalações",
            "cnpj": "00.000.000/0001-00",
            "telefone": "(15) 99999-0000",
            "email": "contato@empresa.com.br",
        },
        contato_cliente={"telefone": "(15) 98888-0000", "endereco": "Rua A, 123"},
        validade_dias=15,
        observacoes="Pagamento em 2x\nPrazo: 5 dias úteis",
        data_emissao=date(2026, 11, 22),
        caminho_logo=logo,
    )
    assert pdf.startswith(b"%PDF")


def test_pdf_logo_inexistente():
    pdf = gerar_pdf("João", ITENS, caminho_logo="nao_existe.png")
    assert pdf.startswith(b"%PDF")


def test_pdf_muitos_itens():
    itens = [
        {"descricao": f"Item {i}", "quantidade": 1, "valor_unitario": 10.0}
        for i in range(120)
    ]
    pdf = gerar_pdf("João", itens)
    assert pdf.startswith(b"%PDF")