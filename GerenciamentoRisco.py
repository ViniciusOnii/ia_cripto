import config as k
import ccxt
import decimal as dc
import pandas as pd
import time

# Inicialização da API da Binance com as credenciais fornecidas no arquivo de configuração.
binance = ccxt.binance({
    'enableRateLimit': True,  # Habilita o limite de taxa para evitar excesso de chamadas à API.
    'apiKey': k.binancekey,  # Chave da API armazenada no módulo de configuração.
    'secret': k.binance_secret,  # Chave secreta da API.
    'options': {
        'defaultType': 'future'  # Define o tipo padrão como "future", o que significa que as operações serão no mercado de futuros.
    },
})

# Função para obter informações sobre as posições abertas de uma moeda específica.
def posicoes_abertas(symbol):
    lado = []
    tamanho = []
    preco_entrada = []
    notional = []
    percetage = []
    pnl = []
    
    # Busca as posições abertas para o símbolo especificado.
    bal = binance.fetch_positions(symbols=[symbol])

    for i in bal:
        lado = i['side']  # Direção da posição (long ou short).
        tamanho = i['info']['positionAmt'].replace('-', '')  # Tamanho da posição, remove o sinal negativo se houver.
        preco_entrada = i['entryPrice']  # Preço de entrada da posição.
        notional = i['notional']  # Valor nominal da posição.
        percetage = i['percetage']  # Porcentagem de lucro/perda (parece estar incorreto, deveria ser 'percentage').
        pnl = i['info']['umRealizeProfit']  # Lucro ou perda não realizado.

    # Verifica se há uma posição aberta.
    if lado == 'long' or lado == 'short':
        pos_aberta = True
    else:
        pos_aberta = False

    # Retorna as informações relevantes da posição.
    return lado, tamanho, preco_entrada, pos_aberta, notional, percetage, pnl

# Função para obter o livro de ofertas (order book) de uma moeda específica.
def livro_ofertas(symbol):
    livro_ofertas = binance.fetch_order_book(symbol)  # Busca o livro de ofertas para o símbolo especificado.
    bid = dc.Decimal(livro_ofertas['bids'][0][0])  # Preço de compra mais alto.
    ask = dc.Decimal(livro_ofertas['asks'][0][0])  # Preço de venda mais baixo.

    return bid, ask 

# Função para encerrar uma posição aberta de uma moeda específica.
def encerra_posicao(symbol):
    pos_aberta = posicoes_abertas(symbol=symbol)[3]  # Verifica se há uma posição aberta.

    while pos_aberta:
        lado = posicoes_abertas(symbol=symbol)[0]  # Direção da posição (long ou short).
        tamanho = posicoes_abertas(symbol=symbol)[1]  # Tamanho da posição.

        if lado == 'long':
            binance.cancel_all_orders(symbol)  # Cancela todas as ordens pendentes.
            bid, ask = livro_ofertas(symbol)  # Obtém os preços de bid e ask.
            ask = binance.price_to_precision(symbol, ask)  # Ajusta o preço de ask para a precisão correta.
            # Cria uma ordem de venda para encerrar a posição long.
            binance.create_order(symbol, side='sell', type='limit', price=ask, amount=tamanho, params={'hedged': 'True'})
            print(f'Vendendo posição long de {tamanho} moedas de {symbol}')
            time.sleep(20)  # Aguarda 20 segundos antes de continuar.

        elif lado == 'short':
            binance.cancel_all_orders(symbol)  # Cancela todas as ordens pendentes.
            bid, ask = livro_ofertas(symbol)  # Obtém os preços de bid e ask.
            bid = binance.price_to_precision(symbol, bid)  # Ajusta o preço de bid para a precisão correta.
            # Cria uma ordem de compra para encerrar a posição short.
            binance.create_order(symbol, side='buy', type='limit', price=bid, amount=tamanho, params={'hedged': 'True'})
            print(f'Comprando posição short de {tamanho} moedas de {symbol}')
            time.sleep(20)  # Aguarda 20 segundos antes de continuar.

        else:
            print('Impossível encerrar a posição')

        # Atualiza o status da posição aberta para verificar se a posição foi encerrada.
        pos_aberta = posicoes_abertas(symbol=symbol)[3]

def fecha_pnl(symbol, loss, target):
    percent = posicoes_abertas(symbol=symbol)[5]
    pnl = posicoes_abertas(symbol=symbol)[6]
    
    if percent:
        if percent <= loss:
            print(f"Encerrando posição por loss! {pnl}")
            encerra_posicao(symbol)
            # telegram
        elif percent >= target:
            print(f"Encerrando posição por gain! {pnl}")
            # telegram
