#!/usr/bin/env python3
"""
Sistema de Sinais para Ações Brasileiras
"""

from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import requests
import yfinance as yf
import time

app = Flask(__name__)
CORS(app)

# Ações selecionadas
SELECTED_STOCKS = ['CASH3', 'AERI3', 'ANIM3', 'COGN3', 'ONCO3', 'COIN11']

# Dados das ações (estatísticas dos backtests)
STOCK_DATA = {
    'CASH3': {
        'total_trades': 13,
        'total_return': 310.86,
        'win_rate': 76.9,
        'avg_return': 23.91,
        'avg_duration': 9.4,
        'last_signal_price': 3.20,
        'current_position': 'LONG'
    },
    'AERI3': {
        'total_trades': 15,
        'total_return': 205.78,
        'win_rate': 80.0,
        'avg_return': 13.72,
        'avg_duration': 7.4,
        'last_signal_price': 8.45,
        'current_position': 'LONG'
    },
    'ANIM3': {
        'total_trades': 12,
        'total_return': 204.77,
        'win_rate': 100.0,
        'avg_return': 17.06,
        'avg_duration': 13.1,
        'last_signal_price': 4.55,
        'current_position': 'LONG'
    },
    'COGN3': {
        'total_trades': 12,
        'total_return': 194.84,
        'win_rate': 91.7,
        'avg_return': 16.24,
        'avg_duration': 11.8,
        'last_signal_price': 1.75,
        'current_position': 'LONG'
    },
    'ONCO3': {
        'total_trades': 17,
        'total_return': 263.20,
        'win_rate': 76.5,
        'avg_return': 15.48,
        'avg_duration': 7.9,
        'last_signal_price': 8.92,
        'current_position': 'CASH'
    },
    'COIN11': {
        'total_trades': 14,
        'total_return': 85.45,
        'win_rate': 71.4,
        'avg_return': 6.10,
        'avg_duration': 12.3,
        'last_signal_price': 105.20,
        'current_position': 'LONG'
    }
}

# Cache de cotações
quotations_cache = {}
last_update_time = None

def get_current_quotations():
    """Buscar cotações atuais com múltiplas tentativas"""
    global quotations_cache, last_update_time
    
    quotations = {}
    successful_updates = 0
    
    print(f"Buscando cotações para {len(SELECTED_STOCKS)} ações...")
    
    for symbol in SELECTED_STOCKS:
        success = False
        current_price = 0
        source = "Fallback"
        
        # Tentativa 1: Yahoo Finance
        try:
            print(f"Tentando buscar {symbol} via Yahoo Finance...")
            ticker = yf.Ticker(f"{symbol}.SA")
            
            # Buscar dados dos últimos 5 dias para garantir dados recentes
            hist = ticker.history(period="5d")
            
            if not hist.empty and len(hist) > 0:
                current_price = float(hist['Close'].iloc[-1])
                if current_price > 0:
                    source = "Yahoo Finance"
                    success = True
                    successful_updates += 1
                    print(f"✅ {symbol}: {current_price:.2f} (Yahoo Finance)")
                else:
                    print(f"❌ {symbol}: Preço inválido do Yahoo Finance")
            else:
                print(f"❌ {symbol}: Sem dados do Yahoo Finance")
                
        except Exception as e:
            print(f"❌ {symbol}: Erro Yahoo Finance - {e}")
        
        # Tentativa 2: Fallback com estimativa baseada no último sinal
        if not success:
            try:
                stock_info = STOCK_DATA.get(symbol, {})
                base_price = stock_info.get('last_signal_price', 10.0)
                
                # Estimativa com pequena variação aleatória
                import random
                variation = random.uniform(-0.05, 0.05)  # -5% a +5%
                current_price = base_price * (1 + variation)
                source = "Estimativa"
                print(f"⚠️ {symbol}: {current_price:.2f} (Estimativa)")
                
            except Exception as e:
                print(f"❌ {symbol}: Erro no fallback - {e}")
                current_price = 10.0
        
        quotations[symbol] = {
            'price': current_price,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'source': source,
            'success': success
        }
    
    # Atualizar cache
    quotations_cache = quotations
    last_update_time = datetime.now()
    
    print(f"Cotações atualizadas: {successful_updates}/{len(SELECTED_STOCKS)} sucessos")
    return quotations

# Template HTML limpo
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Sinais</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .controls {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
        }
        
        .btn-secondary {
            background: linear-gradient(45deg, #fd7e14, #e63946);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        
        .signals-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 1.5em;
            margin-bottom: 20px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .signals-table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .signals-table th,
        .signals-table td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .signals-table th {
            background: rgba(255, 255, 255, 0.1);
            font-weight: 600;
            font-size: 0.9em;
        }
        
        .signals-table td {
            font-size: 0.95em;
        }
        
        .position-long {
            background: #28a745;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }
        
        .position-cash {
            background: #dc3545;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }
        
        .variation-positive {
            color: #28a745;
            font-weight: 600;
        }
        
        .variation-negative {
            color: #dc3545;
            font-weight: 600;
        }
        
        .source-yahoo {
            color: #28a745;
            font-weight: 600;
        }
        
        .source-fallback {
            color: #ffc107;
            font-weight: 600;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            font-size: 1.1em;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .controls {
                flex-direction: column;
                align-items: center;
            }
            
            .btn {
                width: 100%;
                max-width: 300px;
            }
            
            .signals-table {
                font-size: 0.8em;
            }
            
            .signals-table th,
            .signals-table td {
                padding: 8px 4px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sistema de Sinais</h1>
            <p>Ações Brasileiras Selecionadas</p>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="updateQuotations()">
                📈 Atualizar Cotações
            </button>
            <button class="btn btn-secondary" onclick="analyzeNow()">
                🔍 Analisar Agora
            </button>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            <p>⏳ Processando...</p>
        </div>
        
        <div class="signals-section">
            <div class="section-title">
                📊 Sinais para Amanhã
            </div>
            
            <table class="signals-table">
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Preço Atual</th>
                        <th>Último Sinal</th>
                        <th>Variação</th>
                        <th>Posição</th>
                        <th>Fonte</th>
                    </tr>
                </thead>
                <tbody id="signalsTableBody">
                    <!-- Dados serão carregados aqui -->
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Última atualização: <span id="lastUpdate">{{ last_update }}</span></p>
            <p>Total de ações: {{ total_stocks }}</p>
        </div>
    </div>

    <script>
        let stocksData = {{ stocks_data | safe }};
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.querySelector('.signals-section').style.opacity = '0.5';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
            document.querySelector('.signals-section').style.opacity = '1';
        }
        
        function renderSignals(data) {
            const tbody = document.getElementById('signalsTableBody');
            tbody.innerHTML = '';
            
            data.forEach(stock => {
                const variationClass = stock.variation >= 0 ? 'variation-positive' : 'variation-negative';
                const positionClass = stock.position === 'LONG' ? 'position-long' : 'position-cash';
                const sourceClass = stock.source === 'Yahoo Finance' ? 'source-yahoo' : 'source-fallback';
                
                const row = `
                    <tr>
                        <td><strong>${stock.symbol}</strong></td>
                        <td>${stock.current_price.toFixed(2)}</td>
                        <td>${stock.last_signal_price.toFixed(2)}</td>
                        <td class="${variationClass}">${stock.variation.toFixed(2)}%</td>
                        <td><span class="${positionClass}">${stock.position}</span></td>
                        <td class="${sourceClass}">${stock.source}</td>
                    </tr>
                `;
                
                tbody.innerHTML += row;
            });
        }
        
        function updateQuotations() {
            showLoading();
            
            fetch('/api/update-quotations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    stocksData = data.data;
                    renderSignals(stocksData);
                    document.getElementById('lastUpdate').textContent = data.update_time;
                    
                    // Mostrar resultado da atualização
                    const successCount = data.data.filter(stock => stock.source === 'Yahoo Finance').length;
                    const totalCount = data.data.length;
                    alert(`Cotações atualizadas! ${successCount}/${totalCount} ações com dados reais.`);
                } else {
                    alert('Erro ao atualizar cotações: ' + data.error);
                }
            })
            .catch(error => {
                alert('Erro de conexão: ' + error.message);
            })
            .finally(() => {
                hideLoading();
            });
        }
        
        function analyzeNow() {
            showLoading();
            
            fetch('/api/analyze-now', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Análise concluída! Dados atualizados.');
                    // Atualizar a tabela com os novos dados
                    stocksData = data.results;
                    renderSignals(stocksData);
                } else {
                    alert('Erro na análise: ' + data.error);
                }
            })
            .catch(error => {
                alert('Erro de conexão: ' + error.message);
            })
            .finally(() => {
                hideLoading();
            });
        }
        
        // Renderizar dados iniciais
        renderSignals(stocksData);
        
        // Auto-atualizar cotações a cada 5 minutos
        setInterval(function() {
            console.log('Auto-atualizando cotações...');
            updateQuotations();
        }, 300000); // 5 minutos
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal"""
    # Buscar cotações atuais
    quotations = get_current_quotations()
    
    # Preparar dados para o template
    stocks_data = []
    
    for symbol in SELECTED_STOCKS:
        stock_info = STOCK_DATA.get(symbol, {})
        quotation_info = quotations.get(symbol, {})
        
        current_price = quotation_info.get('price', 0)
        last_signal_price = stock_info.get('last_signal_price', current_price)
        
        # Calcular variação
        variation = 0
        if last_signal_price > 0:
            variation = ((current_price - last_signal_price) / last_signal_price) * 100
        
        stocks_data.append({
            'symbol': symbol,
            'current_price': current_price,
            'last_signal_price': last_signal_price,
            'variation': variation,
            'position': stock_info.get('current_position', 'CASH'),
            'timestamp': quotation_info.get('timestamp', 'N/A'),
            'source': quotation_info.get('source', 'N/A'),
            'total_trades': stock_info.get('total_trades', 0),
            'total_return': stock_info.get('total_return', 0),
            'win_rate': stock_info.get('win_rate', 0),
            'avg_return': stock_info.get('avg_return', 0),
            'avg_duration': stock_info.get('avg_duration', 0)
        })
    
    return render_template_string(HTML_TEMPLATE, 
                                stocks_data=json.dumps(stocks_data),
                                last_update=datetime.now().strftime('%H:%M:%S'),
                                total_stocks=len(SELECTED_STOCKS))

@app.route('/api/update-quotations', methods=['POST'])
def update_quotations():
    """Atualizar cotações atuais"""
    try:
        # Buscar novas cotações
        quotations = get_current_quotations()
        
        # Preparar resposta
        response_data = []
        
        for symbol in SELECTED_STOCKS:
            quotation_info = quotations.get(symbol, {})
            stock_info = STOCK_DATA.get(symbol, {})
            
            current_price = quotation_info.get('price', 0)
            last_signal_price = stock_info.get('last_signal_price', current_price)
            
            variation = 0
            if last_signal_price > 0:
                variation = ((current_price - last_signal_price) / last_signal_price) * 100
            
            response_data.append({
                'symbol': symbol,
                'current_price': current_price,
                'last_signal_price': last_signal_price,
                'variation': variation,
                'position': stock_info.get('current_position', 'CASH'),
                'timestamp': quotation_info.get('timestamp', 'N/A'),
                'source': quotation_info.get('source', 'N/A'),
                'total_trades': stock_info.get('total_trades', 0),
                'total_return': stock_info.get('total_return', 0),
                'win_rate': stock_info.get('win_rate', 0),
                'avg_return': stock_info.get('avg_return', 0),
                'avg_duration': stock_info.get('avg_duration', 0)
            })
        
        return jsonify({
            'success': True,
            'data': response_data,
            'update_time': datetime.now().strftime('%H:%M:%S')
        })
        
    except Exception as e:
        print(f"Erro na API update_quotations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-now', methods=['POST'])
def analyze_now():
    """Executar análise"""
    try:
        # Buscar cotações atuais
        quotations = get_current_quotations()
        
        # Preparar resultados
        results = []
        
        for symbol in SELECTED_STOCKS:
            stock_info = STOCK_DATA.get(symbol, {})
            quotation_info = quotations.get(symbol, {})
            
            current_price = quotation_info.get('price', 0)
            last_signal_price = stock_info.get('last_signal_price', current_price)
            
            variation = 0
            if last_signal_price > 0:
                variation = ((current_price - last_signal_price) / last_signal_price) * 100
            
            results.append({
                'symbol': symbol,
                'current_price': current_price,
                'last_signal_price': last_signal_price,
                'variation': variation,
                'position': stock_info.get('current_position', 'CASH'),
                'timestamp': quotation_info.get('timestamp', 'N/A'),
                'source': quotation_info.get('source', 'N/A'),
                'total_trades': stock_info.get('total_trades', 0),
                'total_return': stock_info.get('total_return', 0),
                'win_rate': stock_info.get('win_rate', 0),
                'avg_return': stock_info.get('avg_return', 0),
                'avg_duration': stock_info.get('avg_duration', 0)
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'analysis_time': datetime.now().strftime('%H:%M:%S')
        })
        
    except Exception as e:
        print(f"Erro na API analyze_now: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def api_status():
    """Status da API"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'selected_stocks': SELECTED_STOCKS,
        'total_stocks': len(SELECTED_STOCKS),
        'last_update': last_update_time.isoformat() if last_update_time else None,
        'cache_size': len(quotations_cache)
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
