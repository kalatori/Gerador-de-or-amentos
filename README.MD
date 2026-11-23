# Gerador de Orçamentos

![Testes](https://github.com/kalatori/Gerador-de-or-amentos/actions/workflows/testes.yml/badge.svg)

Programa em Python que gera um orçamento rápido e pronto para enviar ao cliente, com subtotal, desconto e total.

## Problema que resolve
Pequenas empresas, como prestadores de serviços elétricos, perdem tempo montando orçamentos à mão em planilhas ou até diretamente no whatsapp. Aqui a ideia é o orçamento sair em poucos minutos.

## Como rodar
1. Instale o Python 3.12 ou mais recente.
2. `pip install -r requirements.txt`
3. Edite o arquivo `itens.csv` com seus itens.
4. `python orcamento.py`

## Como rodar os testes
`pytest`

Os testes também rodam automaticamente no GitHub Actions a cada envio de código.

## O que aprendi
- Ler arquivos CSV com Python
- Escrever testes automatizados com pytest
- Configurar integração contínua com GitHub Actions
- Usar Git e GitHub
