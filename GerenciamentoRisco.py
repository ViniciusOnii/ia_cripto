#----------------------------Conexão com a binace----------------------------------#

import config as k
import ccxt




binance = ccxt.binance({
    'enableRateLimit': True,
    'apiKey': k.binancekey,
    'secret': k.binance_secret,
    'options': {
        'defaultType': 'future'
    },
})

bal = binance.fetch_positions(symbols=['XRPUSDT']) #moeda entra aqui 


#----------------------Rotina para Confirmacoes das entradas------------------#
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
        

            return lado, tamanho, preco_entrada, notional, percetage,pnl
    
    posicoes_abertas('XRPUSDT')
    tamanho_exposto = posicoes_abertas('XRPUSDT')[2] #Caso queira retirar alguma informacao especifica
    print(pos_aberta)