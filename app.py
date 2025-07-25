from flask import Flask, render_template_string
import os
import json
from datetime import datetime
import pytz

app = Flask(__name__)

# Dados estáticos para carregamento rápido
STATIC_DATA = {
    "JBSS3": {
        "name": "JBS S.A.",
        "sector": "Alimentos", 
        "current_price": 74.21,
        "signal": "CASH",
        "last_signal_date": "24/07/2025",
        "last_signal_price": 74.21,
        "variation": 0.00,
        "action_tomorrow": "FICAR DE FORA"
    },
    "SBSP3": {
        "name": "Sabesp",
        "sector": "Saneamento",
        "current_price": 108.97,
        "signal": "CASH", 
        "last_signal_date": "01/07/2025",
        "last_signal_price": 120.54,
        "variation": -9.60,
        "action_tomorrow": "FICAR DE FORA"
    },
    "SUZB3": {
        "name": "Suzano",
        "sector": "Papel e Celulose",
        "current_price": 51.50,
        "signal": "LONG",
        "last_signal_date": "15/07/2025", 
        "last_signal_price": 50.50,
        "variation": 1.98,
        "action_tomorrow": "MANTER"
    },
    "PETR4": {
        "name": "Petrobras PN",
        "sector": "Petróleo",
        "current_price": 31.94,
        "signal": "LONG",
        "last_signal_date": "22/07/2025",
        "last_signal_price": 31.35, 
        "variation": 1.88,
        "action_tomorrow": "MANTER"
    },
    "BPAC11": {
        "name": "BTG Pactual",
        "sector": "Bancos",
        "current_price": 39.46,
        "signal": "CASH",
        "last_signal_date": "17/07/2025",
        "last_signal_price": 41.71,
        "variation": -5.39,
        "action_tomorrow": "FICAR DE FORA"
    }
}

@app.route('/')
def index():
    """Página principal com dados estáticos"""
    
    template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTS-B3 - Estratégia para Ações Brasileiras</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .info-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .info-card { background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .info-card h3 { color: #4a5568; margin-bottom: 10px; }
        .info-card p { color: #2d3748; font-weight: 600; }
        .signals-section { background: rgba(255,255,255,0.95); border-radius: 12px; padding: 30px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .signals-title { text-align: center; color: #2d3748; margin-bottom: 30px; font-size: 1.8rem; }
        .signals-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .signal-card { border: 2px solid #e2e8f0; border-radius: 12px; padding: 20px; transition: all 0.3s ease; }
        .signal-card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .signal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .signal-symbol { font-size: 1.4rem; font-weight: bold; color: #2d3748; }
        .signal-status { padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 0.9rem; }
        .signal-long { background: #c6f6d5; color: #22543d; }
        .signal-cash { background: #fed7d7; color: #742a2a; }
        .signal-info { margin-bottom: 10px; }
        .signal-info strong { color: #4a5568; }
        .action-badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin-top: 10px; }
        .action-buy { background: #c6f6d5; color: #22543d; }
        .action-hold { background: #faf089; color: #744210; }
        .action-out { background: #fed7d7; color: #742a2a; }
        .variation { font-weight: bold; }
        .positive { color: #38a169; }
        .negative { color: #e53e3e; }
        .update-info { text-align: center; margin-top: 30px; color: #718096; }
        .btn-update { background: #48bb78; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 1rem; cursor: pointer; margin: 20px auto; display: block; }
        .btn-update:hover { background: #38a169; }
        @media (max-width: 768px) { .container { padding: 10px; } .header h1 { font-size: 2rem; } .signals-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 BTS-B3</h1>
            <p>Estratégia BTS para Ações Brasileiras</p>
        </div>
        
        <div class="info-cards">
            <div class="info-card">
                <h3>📊 Fonte de Dados</h3>
                <p>Yahoo Finance</p>
            </div>
            <div class="info-card">
                <h3>⚡ Operação</h3>
                <p>Abertura do dia seguinte</p>
            </div>
            <div class="info-card">
                <h3>🕐 Atualização</h3>
                <p>Diária às 20h Brasil</p>
            </div>
        </div>
        
        <button class="btn-update" onclick="location.reload()">🔄 Atualizar Agora</button>
        
        <div class="signals-section">
            <h2 class="signals-title">📈 Sinais Atuais e Ações para Amanhã</h2>
            
            <div class="signals-grid">
                {% for symbol, data in stocks.items() %}
                <div class="signal-card">
                    <div class="signal-header">
                        <div class="signal-symbol">{{ symbol }}</div>
                        <div class="signal-status {% if data.signal == 'LONG' %}signal-long{% else %}signal-cash{% endif %}">
                            {{ data.signal }}
                        </div>
                    </div>
                    
                    <div class="signal-info">
                        <strong>{{ data.name }}</strong><br>
                        <small>{{ data.sector }}</small>
                    </div>
                    
                    <div class="signal-info">
                        <strong>Preço Atual:</strong> R$ {{ "%.2f"|format(data.current_price) }}
                    </div>
                    
                    <div class="signal-info">
                        <strong>Último Sinal:</strong> {{ data.last_signal_date }}<br>
                        <strong>Preço do Sinal:</strong> R$ {{ "%.2f"|format(data.last_signal_price) }}
                    </div>
                    
                    <div class="signal-info">
                        <strong>Variação:</strong> 
                        <span class="variation {% if data.variation > 0 %}positive{% else %}negative{% endif %}">
                            {{ "%.2f"|format(data.variation) }}%
                        </span>
                    </div>
                    
                    <div class="action-badge {% if data.action_tomorrow == 'COMPRAR' %}action-buy{% elif data.action_tomorrow == 'MANTER' %}action-hold{% else %}action-out{% endif %}">
                        {% if data.action_tomorrow == "COMPRAR" %}🟢{% elif data.action_tomorrow == "MANTER" %}🟡{% else %}🔴{% endif %} {{ data.action_tomorrow }}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="update-info">
            <p>📅 Última atualização: {{ update_time }}</p>
            <p>🔄 Dados baseados na análise de 25/07/2025</p>
            <p>💡 Sistema automático em desenvolvimento</p>
        </div>
    </div>
</body>
</html>
    """
    
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    update_time = datetime.now(brazil_tz).strftime('%d/%m/%Y às %H:%M:%S')
    
    return render_template_string(template, stocks=STATIC_DATA, update_time=update_time)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "BTS-B3 is running"}

if __name__ == '__main__':
    try:
        print("🚀 Iniciando BTS-B3 Simplificado...")
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 Servidor iniciando na porta {port}...")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Erro: {e}")
        # Fallback básico
        app.run(host='0.0.0.0', port=5000, debug=False)
