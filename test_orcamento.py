from datetime import date

import pytest
from orcamento import (
    calcular_total,
    calcular_validade,
    converter_numero,
    formatar_moeda,
    gerar_orcamento,
    ler_itens,
)

ITENS_EXEMPLO = [{"descricao": "Tomada", "quantidade": 2, "valor_unitario": 50}]


def test_total_sem_desconto():
    itens = [{"descricao": "A", "quantidade": 2, "valor_unitario": 10}]
    assert calcular_total(itens) == (20.0, 0.0, 20.0)


def test_total_com_desconto():
    itens = [{"descricao": "A", "quantidade": 2, "valor_unitario": 50}]
    assert calcular_total(itens, 10) == (100.0, 10.0, 90.0)


def test_desconto_invalido():
    with pytest.raises(ValueError):
        calcular_total([], 150)


def test_formatar_moeda():
    assert formatar_moeda(1234.5) == "R$ 1.234,50"


def test_ler_itens(tmp_path):
    arquivo = tmp_path / "itens.csv"
    arquivo.write_text(
        "descricao,quantidade,valor_unitario\nTomada,2,10.5\n",
        encoding="utf-8",
    )
    assert ler_itens(arquivo) == [
        {"descricao": "Tomada", "quantidade": 2.0, "valor_unitario": 10.5}
    ]


def test_converter_numero_com_virgula():
    assert converter_numero("85,50") == 85.5


def test_converter_numero_com_ponto():
    assert converter_numero("85.50") == 85.5


def test_converter_numero_com_milhar():
    assert converter_numero("1.234,50") == 1234.5


def test_converter_numero_inteiro():
    assert converter_numero("10") == 10.0


def test_converter_numero_com_simbolo():
    assert converter_numero("R$ 85,50") == 85.5


def test_converter_numero_invalido():
    assert converter_numero("abc") is None
    assert converter_numero("") is None
    assert converter_numero("-5") is None


def test_calcular_validade():
    assert calcular_validade(date(2026, 11, 22), 15) == date(2026, 12, 7)


def test_gerar_orcamento_basico():
    texto = gerar_orcamento(
        "João", ITENS_EXEMPLO, 10, data_emissao=date(2026, 11, 22)
    )
    assert "PROPOSTA DE ORÇAMENTO" in texto
    assert "Cliente: João" in texto
    assert "TOTAL: R$ 90,00" in texto


def test_gerar_orcamento_com_validade():
    texto = gerar_orcamento(
        "João", ITENS_EXEMPLO, validade_dias=15, data_emissao=date(2026, 11, 22)
    )
    assert "Válido até: 07/12/2026 (15 dias)" in texto


def test_gerar_orcamento_com_empresa_e_observacoes():
    texto = gerar_orcamento(
        "João",
        ITENS_EXEMPLO,
        empresa={"nome": "CF Instalações", "telefone": "(15) 99999-0000"},
        observacoes="Pagamento em 2x",
        data_emissao=date(2026, 11, 22),
    )
    assert "CF INSTALAÇÕES" in texto
    assert "Telefone: (15) 99999-0000" in texto
    assert "Pagamento em 2x" in texto