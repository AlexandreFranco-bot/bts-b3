#!/usr/bin/env python3
"""
BTS-B3 Atualizado: Sistema automático de análise BTS para ações brasileiras
- Busca automática de dados do Yahoo Finance
- Análise diária às 20h Brasil
- Entrada/saída no preço de abertura do dia seguinte
"""

from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from datetime import datetime, timedelta
import pytz
import json
import os
import threading
import time

app = Flask(__name__)

# Configuração das ações monitoradas
STOCKS = {
    'JBSS3': {'name': 'JBS S.A.', 'sector': 'Alimentos'},
    'SBSP3': {'name': 'Sabesp', 'sector': 'Saneamento'},
    'SUZB3': {'name': 'Suzano', 'sector': 'Papel e Celulose'},
    'PETR4': {'name': 'Petrobras PN', 'sector': 'Petróleo'},
    'BBDC4': {'name': 'Bradesco PN', 'sector': 'Bancos'}
}

# Performance histórica do backtest (SEM CUSTOS)
HISTORICAL_PERFORMANCE = {
    'JBSS3': {
        'total_return': 1158.5,
        'buy_hold_return': 350.4,
        'win_rate': 86.0,
        'avg_return': 10.45,
        'max_drawdown': 2.8,
        'sharpe_ratio': 2.47,
        'total_trades': 28
    },
    'SBSP3': {
        'total_return': 406.3,
        'buy_hold_return': 106.5,
        'win_rate': 91.0,
        'avg_return': 7.85,
        'max_drawdown': 1.5,
        'sharpe_ratio': 3.87,
        'total_trades': 23
    },
    'SUZB3': {
        'total_return': 242.5,
        'buy_hold_return': 20.9,
        'win_rate': 100.0,
        'avg_return': 5.95,
        'max_drawdown': 0.0,
        'sharpe_ratio': 4.64,
        'total_trades': 22
    },
    'PETR4': {
        'total_return': 282.4,
        'buy_hold_return': 47.1,
        'win_rate': 92.0,
        'avg_return': 6.12,
        'max_drawdown': 2.1,
        'sharpe_ratio': 3.73,
        'total_trades': 24
    },
    'BBDC4': {
        'total_return': 299.6,
        'buy_hold_return': 23.3,
        'win_rate': 87.0,
        'avg_return': 5.18,
        'max_drawdown': 4.5,
        'sharpe_ratio': 4.23,
        'total_trades': 30
    }
}

def get_brazil_time():
    """Obtém horário atual do Brasil"""
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brazil_tz)

def calculate_sg_filter(closes, window=25, polyorder=4):
    """Calcula filtro Savitzky-Golay"""
    if len(closes) < window:
        return closes.copy()
    return savgol_filter(closes, window, polyorder)

def calculate_donchian_midpoint(highs, lows, period=6):
    """Calcula Donchian Midpoint"""
    donchian_high = highs.rolling(window=period).max()
    donchian_low = lows.rolling(window=period).min()
    return (donchian_high + donchian_low) / 2

def fetch_stock_data(symbol, period="3mo"):
    """Busca dados atualizados do Yahoo Finance"""
    try:
        ticker = yf.Ticker(f"{symbol}.SA")
        data = ticker.history(period=period, interval="1d")
        
        if data.empty:
            return None
        
        df = data[['Open', 'High', 'Low', 'Close']].copy()
        df.columns = ['open', 'high', 'low', 'close']
        df.reset_index(inplace=True)
        df.rename(columns={'Date': 'date'}, inplace=True)
        
        return df
        
    except Exception as e:
        print(f"Erro ao buscar dados de {symbol}: {e}")
        return None

def analyze_current_signal(df):
    """Analisa sinal atual da ação"""
    if len(df) < 30:
        return None
    
    # Calcular indicadores
    df['sg_filtered'] = calculate_sg_filter(df['close'].values, window=25, polyorder=4)
    df['hilo_midpoint'] = calculate_donchian_midpoint(df['high'], df['low'], period=6)
    df['sg_above_hilo'] = df['sg_filtered'] > df['hilo_midpoint']
    
    # Detectar mudanças de sinal
    df['signal'] = 0
    df['signal'] = np.where(
        (df['sg_above_hilo'] == True) & (df['sg_above_hilo'].shift(1) == False), 
        1, df['signal']  # Sinal de compra
    )
    df['signal'] = np.where(
        (df['sg_above_hilo'] == False) & (df['sg_above_hilo'].shift(1) == True), 
        -1, df['signal']  # Sinal de venda
    )
    
    # Encontrar último sinal
    signals = df[df['signal'] != 0]
    if len(signals) == 0:
        return None
    
    last_signal = signals.iloc[-1]
    current_data = df.iloc[-1]
    
    # Determinar ação para amanhã
    current_position = 'LONG' if current_data['sg_above_hilo'] else 'CASH'
    
    # Se houve sinal hoje, determinar ação para amanhã
    today_signal = current_data['signal']
    if today_signal == 1:
        tomorrow_action = 'COMPRAR'
    elif today_signal == -1:
        tomorrow_action = 'VENDER'
    else:
        tomorrow_action = 'MANTER'
    
    return {
        'last_signal_date': last_signal['date'].strftime('%Y-%m-%d'),
        'last_signal_type': 'COMPRA' if last_signal['signal'] == 1 else 'VENDA',
        'last_signal_price': last_signal['close'],
        'current_price': current_data['close'],
        'current_position': current_position,
        'tomorrow_action': tomorrow_action,
        'sg_filtered': current_data['sg_filtered'],
        'hilo_midpoint': current_data['hilo_midpoint'],
        'variation': ((current_data['close'] - last_signal['close']) / last_signal['close']) * 100
    }

def update_all_stocks():
    """Atualiza dados de todas as ações"""
    print(f"🔄 Atualizando dados às {get_brazil_time().strftime('%H:%M:%S')}...")
    
    current_data = {}
    
    for stock in STOCKS.keys():
        print(f"📊 Buscando dados de {stock}...")
        df = fetch_stock_data(stock)
        
        if df is not None:
            analysis = analyze_current_signal(df)
            if analysis:
                current_data[stock] = analysis
                print(f"✅ {stock}: {analysis['tomorrow_action']}")
            else:
                print(f"❌ {stock}: Erro na análise")
        else:
            print(f"❌ {stock}: Erro ao buscar dados")
    
    # Salvar dados atualizados
    try:
        with open('current_data.json', 'w') as f:
            json.dump(current_data, f, indent=2, default=str)
        print(f"💾 Dados salvos às {get_brazil_time().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")
    
    return current_data

def load_current_data():
    """Carrega dados atuais das ações"""
    try:
        if os.path.exists('current_data.json'):
            with open('current_data.json', 'r') as f:
                return json.load(f)
        else:
            # Se não existe, buscar dados agora
            return update_all_stocks()
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return {}

def schedule_daily_update():
    """Agenda atualização diária às 20h"""
    def run_scheduler():
        while True:
            now = get_brazil_time()
            
            # Verificar se é 20h (horário de atualização)
            if now.hour == 20 and now.minute == 0:
                update_all_stocks()
                # Aguardar 1 minuto para não executar novamente
                time.sleep(60)
            
            # Verificar a cada 30 segundos
            time.sleep(30)
    
    # Executar em thread separada
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

@app.route('/')
def index():
    """Página principal"""
    current_data = load_current_data()
    
    # Preparar dados para a tabela de sinais
    signals_data = []
    for stock, data in current_data.items():
        if data:  # Verificar se há dados válidos
            signals_data.append({
                'stock': stock,
                'name': STOCKS[stock]['name'],
                'sector': STOCKS[stock]['sector'],
                'last_signal': data['last_signal_type'],
                'signal_date': data['last_signal_date'],
                'signal_price': f"R$ {data['last_signal_price']:.2f}",
                'current_price': f"R$ {data['current_price']:.2f}",
                'variation': f"{data['variation']:+.2f}%",
                'position': data['current_position'],
                'tomorrow_action': data['tomorrow_action']
            })
    
    # Preparar estatísticas históricas
    stats = {}
    for stock in STOCKS.keys():
        perf = HISTORICAL_PERFORMANCE[stock]
        stats[stock] = {
            'avg_return': f"{perf['avg_return']:+.2f}%",
            'win_rate': f"{perf['win_rate']:.0f}%",
            'total_return': f"{perf['total_return']:+.1f}%",
            'buy_hold_return': f"{perf['buy_hold_return']:+.1f}%",
            'max_drawdown': f"{perf['max_drawdown']:.1f}%",
            'sharpe_ratio': f"{perf['sharpe_ratio']:.2f}",
            'outperformance': f"{perf['total_return'] - perf['buy_hold_return']:+.1f}pp",
            'total_trades': perf['total_trades']
        }
    
    # Horário da última atualização
    try:
        last_update = datetime.fromtimestamp(os.path.getmtime('current_data.json'))
        last_update_str = last_update.strftime('%d/%m/%Y %H:%M')
    except:
        last_update_str = "Nunca"
    
    return render_template('index.html', 
                         signals_data=signals_data,
                         stats=stats,
                         stocks=STOCKS,
                         last_update=last_update_str,
                         next_update="20:00 (diário)")

@app.route('/update_now')
def update_now():
    """Força atualização imediata"""
    try:
        current_data = update_all_stocks()
        return jsonify({
            'success': True,
            'message': f'Dados atualizados com sucesso às {get_brazil_time().strftime("%H:%M:%S")}',
            'stocks_updated': len(current_data),
            'timestamp': get_brazil_time().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar dados: {str(e)}'
        })

@app.route('/health')
def health():
    """Endpoint de saúde"""
    return jsonify({
        'status': 'healthy',
        'timestamp': get_brazil_time().isoformat(),
        'stocks_monitored': len(STOCKS),
        'next_update': '20:00 Brazil time',
        'version': '2.0.0'
    })

if __name__ == '__main__':
    print("🚀 Iniciando BTS-B3 v2.0...")
    print("📊 Ações monitoradas:", list(STOCKS.keys()))
    print("⏰ Atualização automática: 20h Brasil")
    print("🔄 Entrada/saída: Preço de abertura do dia seguinte")
    
    # Iniciar scheduler
    schedule_daily_update()
    
    # Fazer primeira atualização se não houver dados
    if not os.path.exists('current_data.json'):
        print("📥 Fazendo primeira atualização...")
        update_all_stocks()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

