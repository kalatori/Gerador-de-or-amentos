import csv
import math
from datetime import date, timedelta


def ler_itens(caminho_csv):
    itens = []
    with open(caminho_csv, newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            itens.append({
                "descricao": linha["descricao"],
                "quantidade": float(linha["quantidade"]),
                "valor_unitario": float(linha["valor_unitario"]),
            })
    return itens


def converter_numero(texto):
    """Converte '85,50', '85.50' ou '1.234,50' em número. Devolve None se inválido."""
    if texto is None:
        return None
    texto = str(texto).strip().replace("R$", "").replace(" ", "")
    if not texto:
        return None
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        return None
    if not math.isfinite(valor) or valor < 0:
        return None
    return valor


def calcular_total(itens, desconto_percentual=0):
    if desconto_percentual < 0 or desconto_percentual > 100:
        raise ValueError("O desconto deve estar entre 0 e 100.")
    subtotal = sum(i["quantidade"] * i["valor_unitario"] for i in itens)
    desconto = subtotal * desconto_percentual / 100
    total = subtotal - desconto
    return round(subtotal, 2), round(desconto, 2), round(total, 2)


def calcular_validade(data_emissao, dias):
    """Devolve a data até quando a proposta é válida."""
    return data_emissao + timedelta(days=dias)


def formatar_moeda(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_orcamento(
    cliente,
    itens,
    desconto_percentual=0,
    empresa=None,
    contato_cliente=None,
    validade_dias=None,
    observacoes="",
    data_emissao=None,
):
    subtotal, desconto, total = calcular_total(itens, desconto_percentual)
    data_emissao = data_emissao or date.today()
    empresa = empresa or {}
    contato_cliente = contato_cliente or {}

    linhas = []
    if empresa.get("nome"):
        linhas.append(empresa["nome"].upper())
    for rotulo, chave in (("CNPJ", "cnpj"), ("Telefone", "telefone"), ("E-mail", "email")):
        if empresa.get(chave):
            linhas.append(f"{rotulo}: {empresa[chave]}")
    if linhas:
        linhas.append("")

    linhas.append("PROPOSTA DE ORÇAMENTO")
    linhas.append(f"Data de emissão: {data_emissao.strftime('%d/%m/%Y')}")
    if validade_dias:
        validade = calcular_validade(data_emissao, validade_dias)
        linhas.append(
            f"Válido até: {validade.strftime('%d/%m/%Y')} ({validade_dias} dias)"
        )

    linhas.append("")
    linhas.append(f"Cliente: {cliente}")
    if contato_cliente.get("telefone"):
        linhas.append(f"Telefone: {contato_cliente['telefone']}")
    if contato_cliente.get("endereco"):
        linhas.append(f"Endereço: {contato_cliente['endereco']}")

    linhas.append("-" * 50)
    for item in itens:
        valor_item = item["quantidade"] * item["valor_unitario"]
        linhas.append(
            f"{item['descricao']} | {item['quantidade']:g} x "
            f"{formatar_moeda(item['valor_unitario'])} = {formatar_moeda(valor_item)}"
        )
    linhas += [
        "-" * 50,
        f"Subtotal: {formatar_moeda(subtotal)}",
        f"Desconto ({desconto_percentual:g}%): {formatar_moeda(desconto)}",
        f"TOTAL: {formatar_moeda(total)}",
    ]

    if observacoes and observacoes.strip():
        linhas += ["", "Observações:", observacoes.strip()]

    return "\n".join(linhas)


def main():
    cliente = input("Nome do cliente: ")
    desconto = float(input("Desconto em % (0 se nao houver): "))
    itens = ler_itens("itens.csv")
    texto = gerar_orcamento(cliente, itens, desconto)
    nome_arquivo = f"orcamento_{cliente.replace(' ', '_')}.txt"
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)
    print(texto)
    print(f"\nArquivo salvo: {nome_arquivo}")


if __name__ == "__main__":
    main()