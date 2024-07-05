import yfinance as yfinance
import time
import yaml
from decimal import Decimal


def informacoes(nome_acao):
    informacoes_acao = yfinance.Ticker(nome_acao)
    informacoes_acao.history(period='5y')
    return informacoes_acao


def informacoes_dividendos(informacoes_acao):
    dividendos = informacoes_acao.dividends
    soma_dividendos = dividendos.values.sum()
    pagamento_medio = Decimal(soma_dividendos) / Decimal(5)
    return pagamento_medio, soma_dividendos


def printar_tabela(dados):

    nome_acao = dados['nome_acao']
    nome_empresa = dados['nome_empresa']
    preco_atual = dados['preco_atual']
    preco_teto = f'{dados['preco_teto']:.2f}'
    preco_teto2 = f"{dados['preco_teto2']:.2f}" if 'preco_teto2' in dados else 'Não configurado'
    preco_teto3 = f"{dados['preco_teto3']:.2f}" if 'preco_teto3' in dados else 'Não configurado'
    diferenca = f'{(Decimal(dados['preco_teto']) - Decimal(dados['preco_atual'])):.2f}'
    diferenca2 = f'{(Decimal(dados['preco_teto2']) - Decimal(dados['preco_atual'])):.2f}' if 'preco_teto2' in dados else 'Não configurado'
    diferenca3 = f'{(Decimal(dados['preco_teto3']) - Decimal(dados['preco_atual'])):.2f}' if 'preco_teto3' in dados else 'Não configurado'
    dividendo_medio = f'{dados["pagamento_medio"]:.2f}'
    dividendo_soma = f'{dados["soma_dividendos"]:.2f}'
    numero_acoes = f'{dados['numero_acoes']:,}'

    print('\n')
    print(f'[{nome_acao}] - {nome_empresa}')
    print(f'Preço atual: R$ {preco_atual}')
    print(f'Preço teto yield: R$ {preco_teto} - Diferença: R$ {diferenca}')
    if 'preco_teto2' in dados:
        print(f'Preço teto estimado: R$ {preco_teto2} - Diferença: R$ {diferenca2}')
    if 'preco_teto3' in dados:
        print(f'Preço teto conservador: R$ {preco_teto3} - Diferença: R$ {diferenca3}')
    print(f'Dividendo médio: R$ {dividendo_medio} - Soma dos dividendos (5 anos): R${dividendo_soma}')
    print(f'Nº de ações: {numero_acoes}')


def calcular_preco_teto_estimado(acao, numero_acoes):
    if 'lucro-liquido-estimado' in acao and 'media-payout' in acao:
        lucro_liquido_estimado = Decimal(acao['lucro-liquido-estimado'])
        media_payout = Decimal(acao['media-payout']) / Decimal(100)
        return ((lucro_liquido_estimado * media_payout) / Decimal(numero_acoes)) / Decimal(0.06)


def calcular_preco_teto_conservador(acao, numero_acoes):
    if 'lucro-liquido-estimado' in acao and 'media-payout' in acao:
        lucro_liquido_estimado = Decimal(acao['lucro-liquido-estimado'])
        return ((lucro_liquido_estimado * Decimal(0.5)) / Decimal(numero_acoes)) / Decimal(0.06)


def calcular_preco_teto_yield(pagamento_medio):
    return Decimal(pagamento_medio) / Decimal(0.06)


def iniciar():
    acoes = []
    with open('config.yml', 'r') as stream:
        dados_yml = yaml.load(stream, Loader=yaml.FullLoader)
        for acao in dados_yml['acoes']:
            acoes.append(acao)

    for acao in acoes:
        nome_acao = f'{acao['nome']}.SA'
        informacoes_acao = informacoes(nome_acao)

        pagamento_medio, soma_dividendos = informacoes_dividendos(informacoes_acao)
        numero_acoes = informacoes_acao.info['impliedSharesOutstanding']

        preco_teto = calcular_preco_teto_yield(pagamento_medio)
        preco_teto_2 = calcular_preco_teto_estimado(acao, numero_acoes)
        preco_teto_3 = calcular_preco_teto_conservador(acao, numero_acoes)

        dados = {
            'nome_acao': informacoes_acao.info['symbol'],
            'nome_empresa': informacoes_acao.info['longName'],
            'numero_acoes': numero_acoes,
            'preco_atual': informacoes_acao.info['currentPrice'],
            'preco_teto': preco_teto,
            'soma_dividendos': soma_dividendos,
            'pagamento_medio': pagamento_medio,
            'informacoes_completas': informacoes_acao.info
        }

        if preco_teto_2:
            dados['preco_teto2'] = preco_teto_2
        if preco_teto_3:
            dados['preco_teto3'] = preco_teto_3

        printar_tabela(dados)


def main():
    inicio = time.perf_counter()
    iniciar()
    fim = time.perf_counter()

    print(f"\nExecutado em {fim - inicio:0.4f} segundos")


main()
