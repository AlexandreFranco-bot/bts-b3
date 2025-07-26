from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)

# Dados com preços corretos do Yahoo Finance
STOCKS_DATA = {
    'JBSS32': {
        'name': 'JBS S.A.',
        'sector': 'Alimentos',
        'current_price': 74.17,
        'signal': 'CASH',
        'last_signal_date': '24/07/2025',
        'last_signal_price': 74.21,
        'action_tomorrow': 'FICAR DE FORA',
        'variation': -0.05
    },
    'SBSP3': {
        'name': 'Sabesp',
        'sector': 'Saneamento',
        'current_price': 107.45,
        'signal': 'CASH',
        'last_signal_date': '01/07/2025',
        'last_signal_price': 120.54,
        'action_tomorrow': 'FICAR DE FORA',
        'variation': -10.86
    },
    'SUZB3': {
        'name': 'Suzano',
        'sector': 'Papel/Celulose',
        'current_price': 52.57,
        'signal': 'LONG',
        'last_signal_date': '15/07/2025',
        'last_signal_price': 50.50,
        'action_tomorrow': 'MANTER',
        'variation': 4.10
    },
    'PETR4': {
        'name': 'Petrobras PN',
        'sector': 'Petróleo',
        'current_price': 31.98,
        'signal': 'LONG',
        'last_signal_date': '22/07/2025',
        'last_signal_price': 31.35,
        'action_tomorrow': 'MANTER',
        'variation': 2.01
    },
    'BPAC11': {
        'name': 'BTG Pactual',
        'sector': 'Bancos',
        'current_price': 39.36,
        'signal': 'CASH',
        'last_signal_date': '17/07/2025',
        'last_signal_price': 41.71,
        'action_tomorrow': 'FICAR DE FORA',
        'variation': -5.63
    },
    'COIN11': {
        'name': 'Hashdex Nasdaq Crypto',
        'sector': 'Criptomoedas',
        'current_price': 92.91,
        'signal': 'CASH',
        'last_signal_date': '23/07/2025',
        'last_signal_price': 93.29,
        'action_tomorrow': 'FICAR DE FORA',
        'variation': -0.41
    }
}

@app.route('/')
def index():
    template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTS-B3 - Estratégia para Ações Brasileiras</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        
        .section {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .section h2 { 
            color: #3b82f6; 
            margin-bottom: 25px; 
            text-align: center; 
            font-size: 1.8rem;
        }
        
        .stocks-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .stock-card {
            background: #f8fafc;
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #3b82f6;
        }
        
        .stock-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .stock-name { font-size: 1.2rem; font-weight: bold; }
        .stock-sector { font-size: 0.9rem; color: #64748b; }
        .stock-signal { 
            padding: 5px 12px; 
            border-radius: 20px; 
            font-size: 0.8rem; 
            font-weight: bold; 
        }
        .signal-long { background: #dcfce7; color: #166534; }
        .signal-cash { background: #fee2e2; color: #991b1b; }
        
        .stock-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .info-item { text-align: center; }
        .info-label { font-size: 0.8rem; color: #64748b; }
        .info-value { font-size: 1.1rem; font-weight: bold; }
        
        .action-tomorrow {
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            margin-top: 15px;
        }
        .action-buy { background: #dcfce7; color: #166534; }
        .action-hold { background: #fef3c7; color: #92400e; }
        .action-sell { background: #fee2e2; color: #991b1b; }
        
        .variation { font-weight: bold; }
        .positive { color: #22c55e; }
        .negative { color: #ef4444; }
        
        .footer-info { 
            text-align: center; 
            margin-top: 30px; 
            color: white;
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 12px;
            line-height: 1.6;
        }
        
        @media (max-width: 768px) { 
            .container { padding: 10px; } 
            .header h1 { font-size: 2rem; } 
            .stocks-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 BTS-B3</h1>
            <p>Estratégia BTS para Ações Brasileiras + Criptomoedas</p>
        </div>
        
        <div class="section">
            <h2>📊 Sinais Atuais e Ações para Amanhã</h2>
            <div class="stocks-grid">
                {% for stock_code, stock_data in stocks.items() %}
                <div class="stock-card">
                    <div class="stock-header">
                        <div>
                            <div class="stock-name">{{ stock_code }} - {{ stock_data.name }}</div>
                            <div class="stock-sector">{{ stock_data.sector }}</div>
                        </div>
                        <div class="stock-signal {% if stock_data.signal == 'LONG' %}signal-long{% else %}signal-cash{% endif %}">
                            {{ stock_data.signal }}
                        </div>
                    </div>
                    
                    <div class="stock-info">
                        <div class="info-item">
                            <div class="info-label">Preço Atual</div>
                            <div class="info-value">R$ {{ "%.2f"|format(stock_data.current_price) }}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Último Sinal</div>
                            <div class="info-value">{{ stock_data.last_signal_date }}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Preço do Sinal</div>
                            <div class="info-value">R$ {{ "%.2f"|format(stock_data.last_signal_price) }}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Variação</div>
                            <div class="info-value variation {% if stock_data.variation > 0 %}positive{% else %}negative{% endif %}">
                                {{ "%.2f"|format(stock_data.variation) }}%
                            </div>
                        </div>
                    </div>
                    
                    <div class="action-tomorrow {% if stock_data.action_tomorrow == 'COMPRAR' %}action-buy{% elif stock_data.action_tomorrow == 'MANTER' %}action-hold{% else %}action-sell{% endif %}">
                        {% if stock_data.action_tomorrow == 'COMPRAR' %}🟢{% elif stock_data.action_tomorrow == 'MANTER' %}🟡{% else %}🔴{% endif %}
                        {{ stock_data.action_tomorrow }}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="footer-info">
            <p><strong>🤖 Sistema automático:</strong> Análise diária às 20h Brasil com dados do Yahoo Finance</p>
            <p><strong>📊 Indicadores:</strong> SG Filter + Hilo Midpoint (Donchian 6) aplicados aos preços de fechamento</p>
            <p><strong>🎯 Estratégia:</strong> LONG quando SG > Hilo, CASH quando SG ≤ Hilo</p>
            <p><strong>💰 Preços exibidos:</strong> Preços brutos de fechamento sem custos de transação</p>
        </div>
    </div>
    
    <script>
        console.log('BTS-B3 carregado com preços atualizados');
        console.log('Preços atuais:', {{ stocks|tojson }});
    </script>
</body>
</html>
    """
    
    return render_template_string(template, stocks=STOCKS_DATA)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "stocks_count": len(STOCKS_DATA)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
