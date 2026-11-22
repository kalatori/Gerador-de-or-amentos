import csv
from datetime import date


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


def calcular_total(itens, desconto_percentual=0):
    if desconto_percentual < 0 or desconto_percentual > 100:
        raise ValueError("O desconto deve estar entre 0 e 100.")
    subtotal = sum(i["quantidade"] * i["valor_unitario"] for i in itens)
    desconto = subtotal * desconto_percentual / 100
    total = subtotal - desconto
    return round(subtotal, 2), round(desconto, 2), round(total, 2)


def formatar_moeda(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_orcamento(cliente, itens, desconto_percentual=0):
    subtotal, desconto, total = calcular_total(itens, desconto_percentual)
    linhas = [
        "ORCAMENTO",
        f"Cliente: {cliente}",
        f"Data: {date.today().strftime('%d/%m/%Y')}",
        "-" * 50,
    ]
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