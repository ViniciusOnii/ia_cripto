import config as k
import ccxt
import decimal as dc
import pandas as pd
import time

binance = ccxt.binance({
    'enableRateLimit': True,
    'apiKey': k.binancekey,
    'secret': k.binance_secret,
    'options': {
        'defaultType': 'future'
    },
})



def posicoes_abertas(symbol):
    lado = []
    tamanho = []
    preco_entrada = []
    notional = []
    percetage = []
    pnl = []
    bal = binance.fetch_positions(symbols=[symbol]) #moeda entra aqui 

    for i in bal:
        lado = i['side']
        tamanho = i['info']['positionAmt'].replace('-', '')
        preco_entrada = i['entryPrice']
        notional = i['notional']
        percetage = i['percetage']
        pnl = i['info']['umRealizeProfit']

    if lado == 'long':
            pos_aberta = True
    elif lado == 'short':
            pos_aberta = True
    else:
            pos_aberta = False
        

            return lado, tamanho, preco_entrada,pos_aberta, notional, percetage,pnl

    def livro_ofertas(symbol):
        livro_ofertas = binance.fetch_order_book(symbol)
        bid = dc.Decimal(livro_ofertas['bids'][0][0])
        ask = dc.Decimal(livro_ofertas['asks'] [0][0])

        return bid, ask 
    
        #bid, ask = livro_ofertas('XRPUSDT')
        #print(bid,ask)    
        #lado = posicoes_abertas('XRPUSDT')  [0]
        #pos_aberta = posicoes_abertas('XRPUSDT')[3]
        #tamanho = posicoes_abertas('XRPUSDT')[1]
        #print(tamanho,pos_aberta)

    def encerra_posicao(symbol):
        pos_aberta = posicoes_abertas(symbol=symbol)[3]

        while pos_aberta == True:
            lado = posicoes_abertas(symbol=symbol)[0]
            tamanho = posicoes_abertas(symbol=symbol)[1]

            if lado == 'long':
                binance.cancel_all_orders(symbol)
                bid, ask = livro_ofertas(symbol)
                ask = binance.price_to_precision(symbol, ask)
                binance.create_order(symbol, side ='sell', type='limit', price=ask, amount=tamanho, params= {'hedged':'True'} )
                print(f'Vendendo poisição long de {tamanho} modedas de {symbol}')
                time.sleep(20)

            elif lado == 'short':
                binance.cancel_all_orders(symbol)
                bid, ask = livro_ofertas(symbol)
                bid = binance.price_to_precision(symbol, bid)
                binance.create_order(symbol, side ='buy', type='limit', price=bid, amount=tamanho, params= {'hedged':'True'} )
                print(f'Comprando poisição short de {tamanho} modedas de {symbol}')
                time.sleep(20)

            else:
                print('Impossivel encerrar a posição')
                
                pos_aberta = posicoes_abertas(symbol=symbol)[3]
