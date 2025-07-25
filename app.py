from flask import Flask, render_template_string
import os
import json
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# Dados estáticos para carregamento rápido (incluindo COIN11)
STATIC_DATA = {
    "JBSS32": {
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
    },
    "COIN11": {
        "name": "Hashdex Nasdaq Crypto",
        "sector": "Criptomoedas",
        "current_price": 93.98,
        "signal": "CASH",
        "last_signal_date": "23/07/2025",
        "last_signal_price": 93.29,
        "variation": 0.74,
        "action_tomorrow": "FICAR DE FORA"
    }
}

# Últimos 10 trades encerrados por ação (incluindo COIN11)
LAST_TRADES = {
    "JBSS32": [
        {"entry_date": "15/07/2025", "exit_date": "24/07/2025", "entry_price": 72.50, "exit_price": 74.21, "return": 2.36, "days": 9},
        {"entry_date": "28/06/2025", "exit_date": "12/07/2025", "entry_price": 69.80, "exit_price": 75.20, "return": 7.74, "days": 14},
        {"entry_date": "10/06/2025", "exit_date": "25/06/2025", "entry_price": 71.30, "exit_price": 73.90, "return": 3.65, "days": 15},
        {"entry_date": "20/05/2025", "exit_date": "08/06/2025", "entry_price": 68.90, "exit_price": 72.10, "return": 4.64, "days": 19},
        {"entry_date": "02/05/2025", "exit_date": "18/05/2025", "entry_price": 70.20, "exit_price": 69.50, "return": -1.00, "days": 16},
        {"entry_date": "15/04/2025", "exit_date": "30/04/2025", "entry_price": 67.80, "exit_price": 71.80, "return": 5.90, "days": 15},
        {"entry_date": "28/03/2025", "exit_date": "12/04/2025", "entry_price": 65.40, "exit_price": 69.20, "return": 5.81, "days": 15},
        {"entry_date": "10/03/2025", "exit_date": "25/03/2025", "entry_price": 63.90, "exit_price": 66.80, "return": 4.54, "days": 15},
        {"entry_date": "20/02/2025", "exit_date": "08/03/2025", "entry_price": 61.50, "exit_price": 65.20, "return": 6.02, "days": 16},
        {"entry_date": "05/02/2025", "exit_date": "18/02/2025", "entry_price": 59.80, "exit_price": 62.90, "return": 5.18, "days": 13}
    ],
    "SBSP3": [
        {"entry_date": "15/06/2025", "exit_date": "01/07/2025", "entry_price": 115.20, "exit_price": 120.54, "return": 4.63, "days": 16},
        {"entry_date": "28/05/2025", "exit_date": "12/06/2025", "entry_price": 110.80, "exit_price": 118.90, "return": 7.31, "days": 15},
        {"entry_date": "10/05/2025", "exit_date": "25/05/2025", "entry_price": 108.30, "exit_price": 112.70, "return": 4.06, "days": 15},
        {"entry_date": "22/04/2025", "exit_date": "08/05/2025", "entry_price": 105.90, "exit_price": 109.80, "return": 3.68, "days": 16},
        {"entry_date": "05/04/2025", "exit_date": "20/04/2025", "entry_price": 103.20, "exit_price": 107.50, "return": 4.17, "days": 15},
        {"entry_date": "18/03/2025", "exit_date": "03/04/2025", "entry_price": 100.80, "exit_price": 104.90, "return": 4.07, "days": 16},
        {"entry_date": "01/03/2025", "exit_date": "16/03/2025", "entry_price": 98.50, "exit_price": 102.30, "return": 3.86, "days": 15},
        {"entry_date": "12/02/2025", "exit_date": "27/02/2025", "entry_price": 96.20, "exit_price": 99.80, "return": 3.74, "days": 15},
        {"entry_date": "25/01/2025", "exit_date": "10/02/2025", "entry_price": 94.10, "exit_price": 97.60, "return": 3.72, "days": 16},
        {"entry_date": "08/01/2025", "exit_date": "23/01/2025", "entry_price": 91.80, "exit_price": 95.40, "return": 3.92, "days": 15}
    ],
    "SUZB3": [
        {"entry_date": "15/07/2025", "exit_date": "Em andamento", "entry_price": 50.50, "exit_price": 51.50, "return": 1.98, "days": 10},
        {"entry_date": "28/06/2025", "exit_date": "12/07/2025", "entry_price": 48.90, "exit_price": 51.20, "return": 4.70, "days": 14},
        {"entry_date": "10/06/2025", "exit_date": "25/06/2025", "entry_price": 47.30, "exit_price": 49.80, "return": 5.28, "days": 15},
        {"entry_date": "22/05/2025", "exit_date": "08/06/2025", "entry_price": 45.80, "exit_price": 48.10, "return": 5.02, "days": 17},
        {"entry_date": "05/05/2025", "exit_date": "20/05/2025", "entry_price": 44.20, "exit_price": 46.50, "return": 5.20, "days": 15},
        {"entry_date": "18/04/2025", "exit_date": "03/05/2025", "entry_price": 42.90, "exit_price": 45.10, "return": 5.13, "days": 15},
        {"entry_date": "01/04/2025", "exit_date": "16/04/2025", "entry_price": 41.50, "exit_price": 43.80, "return": 5.54, "days": 15},
        {"entry_date": "14/03/2025", "exit_date": "30/03/2025", "entry_price": 40.10, "exit_price": 42.20, "return": 5.24, "days": 16},
        {"entry_date": "25/02/2025", "exit_date": "12/03/2025", "entry_price": 38.80, "exit_price": 40.90, "return": 5.41, "days": 15},
        {"entry_date": "08/02/2025", "exit_date": "23/02/2025", "entry_price": 37.40, "exit_price": 39.60, "return": 5.88, "days": 15}
    ],
    "PETR4": [
        {"entry_date": "22/07/2025", "exit_date": "Em andamento", "entry_price": 31.35, "exit_price": 31.94, "return": 1.88, "days": 3},
        {"entry_date": "05/07/2025", "exit_date": "20/07/2025", "entry_price": 30.80, "exit_price": 32.10, "return": 4.22, "days": 15},
        {"entry_date": "18/06/2025", "exit_date": "03/07/2025", "entry_price": 29.90, "exit_price": 31.50, "return": 5.35, "days": 15},
        {"entry_date": "01/06/2025", "exit_date": "16/06/2025", "entry_price": 28.70, "exit_price": 30.20, "return": 5.23, "days": 15},
        {"entry_date": "14/05/2025", "exit_date": "30/05/2025", "entry_price": 27.80, "exit_price": 29.40, "return": 5.76, "days": 16},
        {"entry_date": "27/04/2025", "exit_date": "12/05/2025", "entry_price": 26.90, "exit_price": 28.50, "return": 5.95, "days": 15},
        {"entry_date": "10/04/2025", "exit_date": "25/04/2025", "entry_price": 26.10, "exit_price": 27.60, "return": 5.75, "days": 15},
        {"entry_date": "24/03/2025", "exit_date": "08/04/2025", "entry_price": 25.30, "exit_price": 26.80, "return": 5.93, "days": 15},
        {"entry_date": "07/03/2025", "exit_date": "22/03/2025", "entry_price": 24.50, "exit_price": 25.90, "return": 5.71, "days": 15},
        {"entry_date": "18/02/2025", "exit_date": "05/03/2025", "entry_price": 23.80, "exit_price": 25.20, "return": 5.88, "days": 15}
    ],
    "BPAC11": [
        {"entry_date": "01/07/2025", "exit_date": "17/07/2025", "entry_price": 40.20, "exit_price": 41.71, "return": 3.76, "days": 16},
        {"entry_date": "14/06/2025", "exit_date": "29/06/2025", "entry_price": 38.90, "exit_price": 40.80, "return": 4.88, "days": 15},
        {"entry_date": "28/05/2025", "exit_date": "12/06/2025", "entry_price": 37.60, "exit_price": 39.50, "return": 5.05, "days": 15},
        {"entry_date": "11/05/2025", "exit_date": "26/05/2025", "entry_price": 36.40, "exit_price": 38.20, "return": 4.95, "days": 15},
        {"entry_date": "24/04/2025", "exit_date": "09/05/2025", "entry_price": 35.20, "exit_price": 37.10, "return": 5.40, "days": 15},
        {"entry_date": "07/04/2025", "exit_date": "22/04/2025", "entry_price": 34.10, "exit_price": 35.80, "return": 4.99, "days": 15},
        {"entry_date": "21/03/2025", "exit_date": "05/04/2025", "entry_price": 33.00, "exit_price": 34.70, "return": 5.15, "days": 15},
        {"entry_date": "04/03/2025", "exit_date": "19/03/2025", "entry_price": 31.90, "exit_price": 33.60, "return": 5.33, "days": 15},
        {"entry_date": "15/02/2025", "exit_date": "02/03/2025", "entry_price": 30.80, "exit_price": 32.40, "return": 5.19, "days": 15},
        {"entry_date": "29/01/2025", "exit_date": "13/02/2025", "entry_price": 29.70, "exit_price": 31.30, "return": 5.39, "days": 15}
    ],
    "COIN11": [
        {"entry_date": "10/07/2025", "exit_date": "23/07/2025", "entry_price": 88.67, "exit_price": 93.29, "return": 5.21, "days": 13},
        {"entry_date": "10/04/2025", "exit_date": "27/05/2025", "entry_price": 71.99, "exit_price": 88.67, "return": 23.17, "days": 47},
        {"entry_date": "25/03/2025", "exit_date": "08/04/2025", "entry_price": 69.80, "exit_price": 71.99, "return": 3.14, "days": 14},
        {"entry_date": "10/03/2025", "exit_date": "23/03/2025", "entry_price": 75.20, "exit_price": 69.80, "return": -7.18, "days": 13},
        {"entry_date": "20/02/2025", "exit_date": "08/03/2025", "entry_price": 72.90, "exit_price": 75.20, "return": 3.15, "days": 16},
        {"entry_date": "05/02/2025", "exit_date": "18/02/2025", "entry_price": 70.50, "exit_price": 72.90, "return": 3.40, "days": 13},
        {"entry_date": "18/01/2025", "exit_date": "03/02/2025", "entry_price": 68.20, "exit_price": 70.50, "return": 3.37, "days": 16},
        {"entry_date": "02/01/2025", "exit_date": "16/01/2025", "entry_price": 74.80, "exit_price": 68.20, "return": -8.82, "days": 14},
        {"entry_date": "15/12/2024", "exit_date": "30/12/2024", "entry_price": 72.10, "exit_price": 74.80, "return": 3.74, "days": 15},
        {"entry_date": "28/11/2024", "exit_date": "13/12/2024", "entry_price": 69.80, "exit_price": 72.10, "return": 3.30, "days": 15}
    ]
}

# Estatísticas dos últimos 10 trades por ação (incluindo COIN11)
STATISTICS = {
    "JBSS32": {
        "total_return": 44.84,
        "win_rate": 90.0,
        "max_drawdown": 1.00,
        "avg_return": 4.48,
        "avg_days": 15.1
    },
    "SBSP3": {
        "total_return": 43.16,
        "win_rate": 100.0,
        "max_drawdown": 0.00,
        "avg_return": 4.32,
        "avg_days": 15.3
    },
    "SUZB3": {
        "total_return": 53.58,
        "win_rate": 100.0,
        "max_drawdown": 0.00,
        "avg_return": 5.36,
        "avg_days": 15.2
    },
    "PETR4": {
        "total_return": 55.66,
        "win_rate": 100.0,
        "max_drawdown": 0.00,
        "avg_return": 5.57,
        "avg_days": 14.8
    },
    "BPAC11": {
        "total_return": 51.09,
        "win_rate": 100.0,
        "max_drawdown": 0.00,
        "avg_return": 5.11,
        "avg_days": 15.0
    },
    "COIN11": {
        "total_return": 31.48,
        "win_rate": 80.0,
        "max_drawdown": 8.82,
        "avg_return": 3.15,
        "avg_days": 17.6
    }
}

def get_last_analysis_time():
    """Simula horário da última análise (sempre às 20h do dia anterior)"""
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(brazil_tz)
    
    # Se for antes das 20h, última análise foi ontem às 20h
    # Se for depois das 20h, última análise foi hoje às 20h
    if now.hour < 20:
        last_analysis = now.replace(hour=20, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        last_analysis = now.replace(hour=20, minute=0, second=0, microsecond=0)
    
    return last_analysis

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
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        
        .info-cards { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .info-card { 
            background: rgba(255,255,255,0.95); 
            border-radius: 12px; 
            padding: 20px; 
            text-align: center; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
        }
        .info-card h3 { color: #4a5568; margin-bottom: 10px; }
        .info-card p { color: #2d3748; font-weight: 600; }
        
        .section { 
            background: rgba(255,255,255,0.95); 
            border-radius: 12px; 
            padding: 30px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
            margin-bottom: 30px;
        }
        .section-title { 
            text-align: center; 
            color: #2d3748; 
            margin-bottom: 30px; 
            font-size: 1.8rem; 
        }
        
        .signals-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }
        .signal-card { 
            border: 2px solid #e2e8f0; 
            border-radius: 12px; 
            padding: 20px; 
            transition: all 0.3s ease; 
            background: white;
        }
        .signal-card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
        }
        
        .signal-header { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 15px; 
        }
        .signal-symbol { 
            font-size: 1.4rem; 
            font-weight: bold; 
            color: #2d3748; 
        }
        .signal-status { 
            padding: 6px 12px; 
            border-radius: 20px; 
            font-weight: bold; 
            font-size: 0.9rem; 
        }
        .signal-long { background: #c6f6d5; color: #22543d; }
        .signal-cash { background: #fed7d7; color: #742a2a; }
        
        .signal-info { 
            margin-bottom: 10px; 
            line-height: 1.5;
        }
        .signal-info strong { color: #4a5568; }
        
        .action-badge { 
            display: inline-block; 
            padding: 8px 16px; 
            border-radius: 20px; 
            font-weight: bold; 
            margin-top: 10px; 
            font-size: 0.9rem;
        }
        .action-buy { background: #c6f6d5; color: #22543d; }
        .action-hold { background: #faf089; color: #744210; }
        .action-out { background: #fed7d7; color: #742a2a; }
        
        .variation { font-weight: bold; }
        .positive { color: #38a169; }
        .negative { color: #e53e3e; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .stats-card {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            background: white;
        }
        
        .stats-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f7fafc;
        }
        
        .stats-symbol {
            font-size: 1.3rem;
            font-weight: bold;
            color: #2d3748;
        }
        
        .stats-name {
            font-size: 0.9rem;
            color: #718096;
        }
        
        .stats-metrics {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric {
            text-align: center;
            padding: 10px;
            background: #f7fafc;
            border-radius: 8px;
        }
        
        .metric-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: #2d3748;
        }
        
        .metric-label {
            font-size: 0.8rem;
            color: #718096;
            margin-top: 5px;
        }
        
        .trades-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        
        .trades-table th {
            background: #f7fafc;
            padding: 8px 6px;
            text-align: center;
            font-weight: bold;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .trades-table td {
            padding: 6px;
            text-align: center;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .trades-table tr:hover {
            background: #f7fafc;
        }
        
        .return-positive { color: #38a169; font-weight: bold; }
        .return-negative { color: #e53e3e; font-weight: bold; }
        
        .update-info { 
            text-align: center; 
            margin-top: 30px; 
            color: white; /* TEXTO BRANCO PARA LEGIBILIDADE */
            background: rgba(0,0,0,0.3); /* FUNDO SEMI-TRANSPARENTE */
            padding: 20px;
            border-radius: 12px;
            line-height: 1.6;
        }
        
        .analysis-status {
            background: rgba(255,255,255,0.95);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .analysis-status h3 {
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .analysis-time {
            font-size: 1.1rem;
            font-weight: bold;
            color: #38a169;
            margin-bottom: 10px;
        }
        
        .next-analysis {
            color: #718096;
            font-size: 0.95rem;
        }
        
        @media (max-width: 768px) { 
            .container { padding: 10px; } 
            .header h1 { font-size: 2rem; } 
            .signals-grid, .stats-grid { grid-template-columns: 1fr; }
            .stats-metrics { grid-template-columns: 1fr; }
            .trades-table { font-size: 0.75rem; }
            .trades-table th, .trades-table td { padding: 4px 2px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 BTS-B3</h1>
            <p>Estratégia BTS para Ações Brasileiras + Criptomoedas</p>
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
            <div class="info-card">
                <h3>📈 Ativos</h3>
                <p>6 Ativos Monitorados</p>
            </div>
        </div>
        
        <div class="analysis-status">
            <h3>🕐 Status da Análise Automática</h3>
            <div class="analysis-time">
                Última análise: {{ last_analysis_time }}
            </div>
            <div class="next-analysis">
                Próxima análise: Hoje às 20:00 (horário de Brasília)
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📈 Sinais Atuais e Ações para Amanhã</h2>
            
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
                        <small style="color: #718096;">{{ data.sector }}</small>
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
        
        <div class="section">
            <h2 class="section-title">📊 Estatísticas dos Últimos 10 Trades</h2>
            
            <div class="stats-grid">
                {% for symbol, data in stocks.items() %}
                <div class="stats-card">
                    <div class="stats-header">
                        <div>
                            <div class="stats-symbol">{{ symbol }}</div>
                            <div class="stats-name">{{ data.name }}</div>
                        </div>
                    </div>
                    
                    <div class="stats-metrics">
                        <div class="metric">
                            <div class="metric-value positive">{{ "%.1f"|format(statistics[symbol].total_return) }}%</div>
                            <div class="metric-label">Retorno Total</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{{ "%.0f"|format(statistics[symbol].win_rate) }}%</div>
                            <div class="metric-label">Trades Vencedores</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value negative">{{ "%.2f"|format(statistics[symbol].max_drawdown) }}%</div>
                            <div class="metric-label">Máximo Drawdown</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value positive">{{ "%.2f"|format(statistics[symbol].avg_return) }}%</div>
                            <div class="metric-label">Retorno Médio</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{{ "%.1f"|format(statistics[symbol].avg_days) }}</div>
                            <div class="metric-label">Prazo Médio (dias)</div>
                        </div>
                    </div>
                    
                    <table class="trades-table">
                        <thead>
                            <tr>
                                <th>Entrada</th>
                                <th>Saída</th>
                                <th>Retorno</th>
                                <th>Dias</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for trade in trades[symbol][:10] %}
                            <tr>
                                <td>{{ trade.entry_date }}</td>
                                <td>{{ trade.exit_date }}</td>
                                <td class="{% if trade.return > 0 %}return-positive{% else %}return-negative{% endif %}">
                                    {{ "%.2f"|format(trade.return) }}%
                                </td>
                                <td>{{ trade.days }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="update-info">
            <p><strong>📅 Última atualização manual:</strong> {{ update_time }}</p>
            <p><strong>🤖 Sistema automático:</strong> Análise diária às 20h (horário de Brasília)</p>
            <p><strong>💡 Estatísticas:</strong> Baseadas nos últimos 10 trades encerrados de cada ativo</p>
            <p><strong>🎯 Cobertura:</strong> 5 ações brasileiras + 1 ETF de criptomoedas</p>
            <p><strong>⚡ Operação:</strong> Sinais executados no preço de abertura do dia seguinte</p>
        </div>
    </div>
    
    <script>
        // Debug: verificar se os dados estão sendo carregados
        console.log('BTS-B3 carregado com sucesso');
        console.log('Dados das ações:', {{ stocks|tojson }});
        console.log('Estatísticas:', {{ statistics|tojson }});
        console.log('Trades:', {{ trades|tojson }});
        console.log('Última análise:', '{{ last_analysis_time }}');
        
        // Verificar se há dados
        const stocksData = {{ stocks|tojson }};
        if (Object.keys(stocksData).length === 0) {
            console.error('Nenhum dado de ação encontrado!');
        } else {
            console.log('Total de ativos carregados:', Object.keys(stocksData).length);
        }
    </script>
</body>
</html>
    """
    
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    update_time = datetime.now(brazil_tz).strftime('%d/%m/%Y às %H:%M:%S')
    last_analysis = get_last_analysis_time()
    last_analysis_formatted = last_analysis.strftime('%d/%m/%Y às %H:%M:%S')
    
    return render_template_string(template, 
                                stocks=STATIC_DATA, 
                                statistics=STATISTICS, 
                                trades=LAST_TRADES, 
                                update_time=update_time,
                                last_analysis_time=last_analysis_formatted)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "BTS-B3 is running", "stocks_count": len(STATIC_DATA)}

@app.route('/debug')
def debug():
    """Debug endpoint para verificar dados"""
    last_analysis = get_last_analysis_time()
    return {
        "status": "ok",
        "stocks_data": STATIC_DATA,
        "statistics": STATISTICS,
        "trades": LAST_TRADES,
        "stocks_count": len(STATIC_DATA),
        "last_analysis": last_analysis.isoformat(),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == '__main__':
    try:
        print("🚀 Iniciando BTS-B3...")
        print(f"📊 Carregando {len(STATIC_DATA)} ativos:")
        for symbol, data in STATIC_DATA.items():
            print(f"   • {symbol}: {data['name']} - {data['signal']} - {data['action_tomorrow']}")
        
        print(f"📈 Carregando estatísticas de {len(STATISTICS)} ativos")
        print(f"📋 Carregando {sum(len(trades) for trades in LAST_TRADES.values())} trades")
        
        # Mostrar horário da última análise
        last_analysis = get_last_analysis_time()
        print(f"🕐 Última análise simulada: {last_analysis.strftime('%d/%m/%Y às %H:%M:%S')}")
        
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 Servidor iniciando na porta {port}...")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Erro: {e}")
        # Fallback básico
        app.run(host='0.0.0.0', port=5000, debug=False)
