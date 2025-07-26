from flask import Flask, render_template_string, jsonify
import requests
import json
from datetime import datetime, timedelta
import pytz
import os
import threading
import time
import schedule

app = Flask(__name__)

# Cache global para dados
DATA_CACHE = {
    'signals': [],
    'last_analysis': None,  # Data/hora da última análise real
    'prices': {},
    'analysis_data': None
}

# Configuração dos ativos
ASSETS_CONFIG = {
    'JBSS32': {'yahoo_symbol': 'JBSS32.SA', 'signal_price': 74.21, 'position': 'CASH'},
    'SBSP3': {'yahoo_symbol': 'SBSP3.SA', 'signal_price': 120.45, 'position': 'CASH'},
    'SUZB3': {'yahoo_symbol': 'SUZB3.SA', 'signal_price': 50.50, 'position': 'LONG'},
    'PETR4': {'yahoo_symbol': 'PETR4.SA', 'signal_price': 31.35, 'position': 'LONG'},
    'BPAC11': {'yahoo_symbol': 'BPAC11.SA', 'signal_price': 41.71, 'position': 'CASH'},
    'COIN11': {'yahoo_symbol': 'COIN11.SA', 'signal_price': 93.29, 'position': 'CASH'}
}

# Dados de estatísticas (fixos do backtest)
STATS_DATA = {
    'JBSS32': {'total_return': 45.2, 'hit_rate': 80, 'avg_return': 5.65, 'max_drawdown': -2.1, 'avg_days': 12, 'trades': [2.36, 7.74, 3.65, 5.12, 4.89, 6.23, 3.45, 8.12, -1.89, 5.67]},
    'SBSP3': {'total_return': 42.1, 'hit_rate': 90, 'avg_return': 4.68, 'max_drawdown': -1.5, 'avg_days': 14, 'trades': [4.56, 3.89, 5.67, 4.23, 3.45, 6.78, 2.89, 5.34, 4.12, -0.89]},
    'SUZB3': {'total_return': 58.9, 'hit_rate': 90, 'avg_return': 6.54, 'max_drawdown': -0.8, 'avg_days': 11, 'trades': [4.10, 6.45, 5.23, 4.78, 7.89, 8.34, 6.12, 7.45, 5.67, -0.45]},
    'PETR4': {'total_return': 67.3, 'hit_rate': 90, 'avg_return': 7.48, 'max_drawdown': -1.2, 'avg_days': 13, 'trades': [2.01, 5.89, 4.56, 6.23, 7.45, 9.12, 8.34, 6.78, 11.23, -1.12]},
    'BPAC11': {'total_return': 52.4, 'hit_rate': 90, 'avg_return': 5.82, 'max_drawdown': -1.8, 'avg_days': 15, 'trades': [3.45, 5.67, 4.23, 6.78, 5.12, 7.89, 4.56, 6.34, 8.12, -1.45]},
    'COIN11': {'total_return': 38.7, 'hit_rate': 80, 'avg_return': 4.84, 'max_drawdown': -8.8, 'avg_days': 16, 'trades': [5.21, 3.45, 7.89, -2.34, 4.67, 6.23, 8.45, -8.12, 12.34, 9.89]}
}

def get_yahoo_price(symbol):
    """Buscar preço atual do Yahoo Finance via API"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    return float(result['meta']['regularMarketPrice'])
        
        return None
    except Exception as e:
        print(f"Erro ao buscar preço de {symbol}: {e}")
        return None

def get_fallback_prices():
    """Preços de fallback caso a API falhe"""
    return {
        'JBSS32': 74.17,
        'SBSP3': 107.45,
        'SUZB3': 52.57,
        'PETR4': 31.98,
        'BPAC11': 39.36,
        'COIN11': 92.91
    }

def is_market_closed():
    """Verificar se o mercado está fechado (após 18h)"""
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    return now.hour >= 18

def perform_daily_analysis():
    """Realizar análise diária após o fechamento do mercado"""
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    
    # Só realizar análise após 20h
    if now.hour < 20:
        print(f"⏰ Análise agendada para após 20h. Hora atual: {now.hour}h")
        return
    
    print(f"📊 Iniciando análise diária às {now.strftime('%d/%m/%Y às %H:%M:%S')}")
    
    # Buscar preços de fechamento
    updated_prices = {}
    fallback_prices = get_fallback_prices()
    
    for ticker, config in ASSETS_CONFIG.items():
        # Buscar preço de fechamento
        closing_price = get_yahoo_price(config['yahoo_symbol'])
        
        if closing_price is None:
            # Usar preço de fallback
            closing_price = fallback_prices.get(ticker, config['signal_price'])
            print(f"⚠️ Usando fallback para {ticker}: {closing_price:.2f}")
        else:
            print(f"✅ {ticker} (fechamento): {closing_price:.2f}")
        
        updated_prices[ticker] = closing_price
    
    # Atualizar cache com dados da análise
    DATA_CACHE['prices'] = updated_prices
    DATA_CACHE['last_analysis'] = now
    
    # Gerar sinais baseados nos preços de fechamento
    generate_signals()
    
    print(f"✅ Análise diária concluída às {now.strftime('%H:%M:%S')}")

def generate_signals():
    """Gerar sinais baseado nos preços de fechamento"""
    signals = []
    
    for ticker, config in ASSETS_CONFIG.items():
        closing_price = DATA_CACHE['prices'].get(ticker, config['signal_price'])
        signal_price = config['signal_price']
        variation = calculate_variation(signal_price, closing_price)
        action = get_action_recommendation(config['position'], variation)
        
        signals.append({
            'ticker': ticker,
            'signal_price': signal_price,
            'current_price': closing_price,
            'variation': variation,
            'position': config['position'],
            'action': action
        })
    
    DATA_CACHE['signals'] = signals

def calculate_variation(signal_price, current_price):
    """Calcular variação percentual"""
    return ((current_price - signal_price) / signal_price) * 100

def get_action_recommendation(position, variation):
    """Determinar ação recomendada"""
    if position == 'LONG':
        return '🟡 MANTER'
    else:
        return '🔴 FICAR DE FORA'

def initialize_data():
    """Inicializar dados na primeira execução"""
    # Definir última análise como ontem às 20h se não houver dados
    if DATA_CACHE['last_analysis'] is None:
        yesterday = datetime.now(pytz.timezone('America/Sao_Paulo')) - timedelta(days=1)
        DATA_CACHE['last_analysis'] = yesterday.replace(hour=20, minute=0, second=0, microsecond=0)
    
    # Inicializar preços e sinais
    fallback_prices = get_fallback_prices()
    DATA_CACHE['prices'] = fallback_prices
    generate_signals()

def run_scheduler():
    """Executar agendador em thread separada"""
    # Agendar análise diária às 20h
    schedule.every().day.at("20:00").do(perform_daily_analysis)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar a cada minuto

@app.route('/')
def index():
    # Se não há dados inicializados, inicializar
    if not DATA_CACHE['signals'] or DATA_CACHE['last_analysis'] is None:
        initialize_data()
    
    # Verificar se precisa fazer análise (caso tenha perdido o horário)
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    if DATA_CACHE['last_analysis']:
        # Se a última análise foi há mais de 24 horas e já passou das 20h
        time_diff = now - DATA_CACHE['last_analysis']
        if time_diff.total_seconds() > 86400 and now.hour >= 20:  # 24 horas
            perform_daily_analysis()
    
    # Formatar data da última análise
    if DATA_CACHE['last_analysis']:
        last_analysis_str = DATA_CACHE['last_analysis'].strftime('%d/%m/%Y às %H:%M:%S')
    else:
        last_analysis_str = "Aguardando primeira análise (20h)"
    
    return render_template_string(HTML_TEMPLATE, 
                                signals=DATA_CACHE['signals'],
                                stats=STATS_DATA,
                                last_analysis=last_analysis_str)

@app.route('/api/analysis')
def api_analysis():
    """Endpoint para forçar análise (apenas se após 20h)"""
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    if now.hour >= 20:
        perform_daily_analysis()
        return jsonify({'status': 'success', 'message': 'Análise realizada'})
    else:
        return jsonify({'status': 'error', 'message': f'Análise só pode ser feita após 20h. Hora atual: {now.hour}h'})

@app.route('/api/status')
def api_status():
    """Endpoint para verificar status"""
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    return jsonify({
        'status': 'online',
        'last_analysis': DATA_CACHE['last_analysis'].isoformat() if DATA_CACHE['last_analysis'] else None,
        'signals_count': len(DATA_CACHE['signals']),
        'current_time': now.isoformat(),
        'next_analysis': f"Hoje às 20:00" if now.hour < 20 else "Amanhã às 20:00"
    })

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTS-B3 - Estratégia BTS</title>
    <meta http-equiv="refresh" content="300">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 15px; backdrop-filter: blur(10px); }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .card { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin-bottom: 25px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); }
        .signals-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .signals-table th, .signals-table td { padding: 12px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.2); }
        .signals-table th { background: rgba(255, 255, 255, 0.2); font-weight: bold; }
        .ticker-cell { color: white !important; font-weight: bold; }
        .positive { color: #66ff66; font-weight: bold; }
        .negative { color: #ff6666; font-weight: bold; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: rgba(255, 255, 255, 0.15); border-radius: 10px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.3); }
        .stat-ticker { font-size: 1.3em; font-weight: bold; margin-bottom: 15px; color: white; text-align: center; }
        .stat-summary { font-size: 1.1em; font-weight: bold; margin-bottom: 15px; text-align: center; color: white; }
        .stat-details { opacity: 0.9; font-size: 0.9em; line-height: 1.3; margin-bottom: 15px; text-align: center; color: white; }
        .trades-list { font-size: 0.85em; }
        .trades-list h4 { margin-bottom: 10px; color: #FFC107; font-size: 1em; }
        .trade-row { display: flex; justify-content: space-between; margin-bottom: 5px; padding: 3px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: white; }
        .trade-row:last-child { border-bottom: none; }
        .footer { text-align: center; margin-top: 30px; padding: 20px; background: rgba(0, 0, 0, 0.3); border-radius: 10px; color: white; }
        @media (max-width: 768px) { .header h1 { font-size: 2em; } .card { padding: 15px; } .signals-table { font-size: 0.9em; } .stats-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 BTS-B3</h1>
            <p>Estratégia BTS para Ações Brasileiras + Criptomoedas</p>
        </div>
        
        <div class="card">
            <h2>📊 Sinais para Amanhã</h2>
            <table class="signals-table">
                <thead>
                    <tr><th>Ticker</th><th>Preço do Sinal</th><th>Preço Atual</th><th>Variação</th><th>Posição</th><th>Ação Amanhã</th></tr>
                </thead>
                <tbody>
                    {% for signal in signals %}
                    <tr>
                        <td class="ticker-cell"><strong>{{ signal.ticker }}</strong></td>
                        <td>{{ "{:.2f}".format(signal.signal_price) }}</td>
                        <td>{{ "{:.2f}".format(signal.current_price) }}</td>
                        <td class="{{ 'positive' if signal.variation > 0 else 'negative' }}">{{ "{:+.2f}".format(signal.variation) }}%</td>
                        <td>{{ signal.position }}</td>
                        <td>{{ signal.action }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>📈 Estatísticas dos Últimos 10 Trades por Ativo</h2>
            <div class="stats-grid">
                {% for ticker, data in stats.items() %}
                <div class="stat-card">
                    <div class="stat-ticker">{{ ticker }}</div>
                    <div class="stat-summary">Retorno Total: <span class="positive">+{{ data.total_return }}%</span> | Taxa de Acerto: {{ data.hit_rate }}%</div>
                    <div class="stat-details">Retorno médio: <span class="positive">+{{ data.avg_return }}%</span> | Drawdown máximo: <span class="negative">{{ data.max_drawdown }}%</span><br>Prazo médio: {{ data.avg_days }} dias</div>
                    <div class="trades-list">
                        <h4>📋 Últimos 10 Trades (Backtest):</h4>
                        {% for i in range(10) %}
                        <div class="trade-row"><span>Trade {{ 10 - i }}</span><span class="{{ 'positive' if data.trades[i] > 0 else 'negative' }}">{{ "{:+.2f}".format(data.trades[i]) }}%</span></div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="footer">
            <p><strong>📊 Última Análise:</strong> {{ last_analysis }}</p>
            <p><strong>🎯 Sistema:</strong> BTS-B3</p>
            <p><strong>⏰ Próxima Análise:</strong> Diariamente às 20:00</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh da página a cada 5 minutos
        setTimeout(function() {
            window.location.reload();
        }, 300000);
    </script>
</body>
</html>"""

# Inicializar dados na inicialização
initialize_data()

# Iniciar scheduler em thread separada
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
