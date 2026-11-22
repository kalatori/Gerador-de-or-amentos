import pytest
from orcamento import calcular_total, formatar_moeda, ler_itens


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