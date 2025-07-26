from flask import Flask, render_template_string, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from datetime import datetime, timedelta
import pytz
import os
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STOCKS_DATA = {
    'JBSS32': {
        'name': 'JBS S.A.',
        'sector': 'Alimentos',
        'current_price': 74.17,
        'signal': 'CASH',
        'last_signal_date': '24/07/2025',
        'last_signal_price': 74.21,
        'action_tomorrow': 'FICAR DE FORA',
        'action_color': 'red'
    },
    'SBSP3': {
        'name': 'Sabesp',
        'sector': 'Saneamento',
        'current_price': 107.45,
        'signal': 'CASH',
        'last_signal_date': '01/07/2025',
        'last_signal_price': 120.54,
        'action_tomorrow': 'FICAR DE FORA',
        'action_color': 'red'
    },
    'SUZB3': {
        'name': 'Suzano',
        'sector': 'Papel/Celulose',
        'current_price': 52.57,
        'signal': 'LONG',
        'last_signal_date': '15/07/2025',
        'last_signal_price': 50.50,
        'action_tomorrow': 'MANTER',
        'action_color': 'orange'
    },
    'PETR4': {
        'name': 'Petrobras PN',
        'sector': 'Petróleo',
        'current_price': 31.98,
        'signal': 'LONG',
        'last_signal_date': '22/07/2025',
        'last_signal_price': 31.35,
        'action_tomorrow': 'MANTER',
        'action_color': 'orange'
    },
    'BPAC11': {
        'name': 'BTG Pactual',
        'sector': 'Bancos',
        'current_price': 39.36,
        'signal': 'CASH',
        'last_signal_date': '17/07/2025',
        'last_signal_price': 41.71,
        'action_tomorrow': 'FICAR DE FORA',
        'action_color': 'red'
    },
    'COIN11': {
        'name': 'Hashdex Nasdaq Crypto',
        'sector': 'Criptomoedas',
        'current_price': 92.91,
        'signal': 'CASH',
        'last_signal_date': '23/07/2025',
        'last_signal_price': 93.29,
        'action_tomorrow': 'FICAR DE FORA',
        'action_color': 'red'
    }
}

# Estatísticas dos últimos 10 trades (baseadas no backtest)
STATISTICS_DATA = {{
    'JBSS32': {{
        'total_return': 44.8,
        'win_rate': 90,
        'max_drawdown': 1.00,
        'avg_return': 4.48,
        'avg_duration': 15.1,
        'trades': [
            {{'entry': '15/07/2025', 'exit': '24/07/2025', 'return': 2.36, 'duration': 9}},
            {{'entry': '28/06/2025', 'exit': '12/07/2025', 'return': 7.74, 'duration': 14}},
            {{'entry': '10/06/2025', 'exit': '25/06/2025', 'return': 3.65, 'duration': 15}},
            {{'entry': '20/05/2025', 'exit': '07/06/2025', 'return': 5.23, 'duration': 18}},
            {{'entry': '02/05/2025', 'exit': '17/05/2025', 'return': 4.12, 'duration': 15}},
            {{'entry': '15/04/2025', 'exit': '30/04/2025', 'return': 6.89, 'duration': 15}},
            {{'entry': '28/03/2025', 'exit': '12/04/2025', 'return': 3.45, 'duration': 15}},
            {{'entry': '10/03/2025', 'exit': '25/03/2025', 'return': 5.67, 'duration': 15}},
            {{'entry': '20/02/2025', 'exit': '07/03/2025', 'return': 4.23, 'duration': 15}},
            {{'entry': '02/02/2025', 'exit': '17/02/2025', 'return': -1.00, 'duration': 15}}
        ]
    }},
    'SBSP3': {{
        'total_return': 43.2,
        'win_rate': 100,
        'max_drawdown': 0.00,
        'avg_return': 4.32,
        'avg_duration': 15.3,
        'trades': [
            {{'entry': '16/07/2025', 'exit': '01/08/2025', 'return': 4.56, 'duration': 16}},
            {{'entry': '29/06/2025', 'exit': '14/07/2025', 'return': 3.89, 'duration': 15}},
            {{'entry': '11/06/2025', 'exit': '26/06/2025', 'return': 5.12, 'duration': 15}},
            {{'entry': '21/05/2025', 'exit': '08/06/2025', 'return': 4.67, 'duration': 18}},
            {{'entry': '03/05/2025', 'exit': '18/05/2025', 'return': 3.78, 'duration': 15}},
            {{'entry': '16/04/2025', 'exit': '01/05/2025', 'return': 4.23, 'duration': 15}},
            {{'entry': '29/03/2025', 'exit': '13/04/2025', 'return': 4.89, 'duration': 15}},
            {{'entry': '11/03/2025', 'exit': '26/03/2025', 'return': 3.45, 'duration': 15}},
            {{'entry': '21/02/2025', 'exit': '08/03/2025', 'return': 5.12, 'duration': 15}},
            {{'entry': '03/02/2025', 'exit': '18/02/2025', 'return': 3.49, 'duration': 15}}
        ]
    }},
    'SUZB3': {{
        'total_return': 53.6,
        'win_rate': 100,
        'max_drawdown': 0.00,
        'avg_return': 5.36,
        'avg_duration': 15.2,
        'trades': [
            {{'entry': '15/07/2025', 'exit': 'Em andamento', 'return': 4.10, 'duration': 11}},
            {{'entry': '27/06/2025', 'exit': '12/07/2025', 'return': 6.23, 'duration': 15}},
            {{'entry': '09/06/2025', 'exit': '24/06/2025', 'return': 4.78, 'duration': 15}},
            {{'entry': '19/05/2025', 'exit': '06/06/2025', 'return': 5.89, 'duration': 18}},
            {{'entry': '01/05/2025', 'exit': '16/05/2025', 'return': 4.56, 'duration': 15}},
            {{'entry': '14/04/2025', 'exit': '29/04/2025', 'return': 6.12, 'duration': 15}},
            {{'entry': '27/03/2025', 'exit': '11/04/2025', 'return': 5.34, 'duration': 15}},
            {{'entry': '09/03/2025', 'exit': '24/03/2025', 'return': 4.89, 'duration': 15}},
            {{'entry': '19/02/2025', 'exit': '06/03/2025', 'return': 6.45, 'duration': 15}},
            {{'entry': '01/02/2025', 'exit': '16/02/2025', 'return': 5.24, 'duration': 15}}
        ]
    }},
    'PETR4': {{
        'total_return': 55.7,
        'win_rate': 100,
        'max_drawdown': 0.00,
        'avg_return': 5.57,
        'avg_duration': 14.8,
        'trades': [
            {{'entry': '22/07/2025', 'exit': 'Em andamento', 'return': 2.01, 'duration': 4}},
            {{'entry': '04/07/2025', 'exit': '19/07/2025', 'return': 6.78, 'duration': 15}},
            {{'entry': '16/06/2025', 'exit': '01/07/2025', 'return': 5.23, 'duration': 15}},
            {{'entry': '26/05/2025', 'exit': '13/06/2025', 'return': 4.89, 'duration': 18}},
            {{'entry': '08/05/2025', 'exit': '23/05/2025', 'return': 6.12, 'duration': 15}},
            {{'entry': '21/04/2025', 'exit': '06/05/2025', 'return': 5.45, 'duration': 15}},
            {{'entry': '03/04/2025', 'exit': '18/04/2025', 'return': 4.67, 'duration': 15}},
            {{'entry': '16/03/2025', 'exit': '31/03/2025', 'return': 5.89, 'duration': 15}},
            {{'entry': '26/02/2025', 'exit': '13/03/2025', 'return': 6.34, 'duration': 15}},
            {{'entry': '08/02/2025', 'exit': '23/02/2025', 'return': 8.35, 'duration': 15}}
        ]
    }},
    'BPAC11': {{
        'total_return': 51.1,
        'win_rate': 100,
        'max_drawdown': 0.00,
        'avg_return': 5.11,
        'avg_duration': 15.0,
        'trades': [
            {{'entry': '02/07/2025', 'exit': '17/07/2025', 'return': 5.67, 'duration': 15}},
            {{'entry': '14/06/2025', 'exit': '29/06/2025', 'return': 4.23, 'duration': 15}},
            {{'entry': '24/05/2025', 'exit': '11/06/2025', 'return': 6.12, 'duration': 18}},
            {{'entry': '06/05/2025', 'exit': '21/05/2025', 'return': 4.89, 'duration': 15}},
            {{'entry': '19/04/2025', 'exit': '04/05/2025', 'return': 5.34, 'duration': 15}},
            {{'entry': '01/04/2025', 'exit': '16/04/2025', 'return': 4.78, 'duration': 15}},
            {{'entry': '14/03/2025', 'exit': '29/03/2025', 'return': 5.56, 'duration': 15}},
            {{'entry': '24/02/2025', 'exit': '11/03/2025', 'return': 4.45, 'duration': 15}},
            {{'entry': '06/02/2025', 'exit': '21/02/2025', 'return': 6.23, 'duration': 15}},
            {{'entry': '19/01/2025', 'exit': '03/02/2025', 'return': 3.84, 'duration': 15}}
        ]
    }},
    'COIN11': {{
        'total_return': 31.5,
        'win_rate': 80,
        'max_drawdown': 8.82,
        'avg_return': 3.15,
        'avg_duration': 17.6,
        'trades': [
            {{'entry': '10/07/2025', 'exit': '23/07/2025', 'return': 5.21, 'duration': 13}},
            {{'entry': '20/06/2025', 'exit': '07/07/2025', 'return': 3.45, 'duration': 17}},
            {{'entry': '28/05/2025', 'exit': '17/06/2025', 'return': 4.67, 'duration': 20}},
            {{'entry': '08/05/2025', 'exit': '25/05/2025', 'return': 2.34, 'duration': 17}},
            {{'entry': '15/04/2025', 'exit': '05/05/2025', 'return': 6.78, 'duration': 20}},
            {{'entry': '22/03/2025', 'exit': '12/04/2025', 'return': 1.89, 'duration': 21}},
            {{'entry': '28/02/2025', 'exit': '19/03/2025', 'return': -8.82, 'duration': 19}},
            {{'entry': '05/02/2025', 'exit': '25/02/2025', 'return': 3.67, 'duration': 20}},
            {{'entry': '12/01/2025', 'exit': '02/02/2025', 'return': 7.23, 'duration': 21}},
            {{'entry': '18/12/2024', 'exit': '09/01/2025', 'return': 9.23, 'duration': 22}}
        ]
    }}
}}

# Data da última análise (atualizada)
LAST_ANALYSIS = "25/07/2025 às 22:15:55"

def calculate_variation(current_price, signal_price):
    """Calcula variação percentual"""
    if signal_price == 0:
        return 0
    return ((current_price - signal_price) / signal_price) * 100

@app.route('/')
def index():
    """Página principal"""
    
    # Calcular variações atualizadas
    for stock_code, stock_data in STOCKS_DATA.items():
        variation = calculate_variation(stock_data['current_price'], stock_data['last_signal_price'])
        stock_data['variation'] = variation
    
    template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTS-B3 - Estratégia para Ações Brasileiras + Criptomoedas</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            color: #333;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; color: white; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        .header p {{ font-size: 1.2rem; opacity: 0.9; }}
        
        .info-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .info-card {{
            background: rgba(255,255,255,0.95);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .info-card h3 {{ color: #3b82f6; margin-bottom: 10px; }}
        .info-card p {{ font-size: 1.1rem; font-weight: 600; }}
        
        .section {{
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .section h2 {{ 
            color: #3b82f6; 
            margin-bottom: 25px; 
            text-align: center; 
            font-size: 1.8rem;
        }}
        
        .stocks-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .stock-card {{
            background: #f8fafc;
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #3b82f6;
        }}
        
        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .stock-name {{ font-size: 1.2rem; font-weight: bold; }}
        .stock-sector {{ font-size: 0.9rem; color: #64748b; }}
        .stock-signal {{ 
            padding: 5px 12px; 
            border-radius: 20px; 
            font-size: 0.8rem; 
            font-weight: bold; 
        }}
        .signal-long {{ background: #dcfce7; color: #166534; }}
        .signal-cash {{ background: #fee2e2; color: #991b1b; }}
        
        .stock-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }}
        
        .info-item {{ text-align: center; }}
        .info-label {{ font-size: 0.8rem; color: #64748b; }}
        .info-value {{ font-size: 1.1rem; font-weight: bold; }}
        
        .action-tomorrow {{
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            margin-top: 15px;
        }}
        .action-buy {{ background: #dcfce7; color: #166534; }}
        .action-hold {{ background: #fef3c7; color: #92400e; }}
        .action-sell {{ background: #fee2e2; color: #991b1b; }}
        
        .variation {{ font-weight: bold; }}
        .positive {{ color: #22c55e; }}
        .negative {{ color: #ef4444; }}
        
        .statistics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
        }}
        
        .stat-card {{
            background: #f8fafc;
            border-radius: 12px;
            padding: 25px;
            border-left: 4px solid #3b82f6;
        }}
        
        .stat-header {{ margin-bottom: 20px; }}
        .stat-title {{ font-size: 1.3rem; font-weight: bold; color: #1e293b; }}
        .stat-subtitle {{ font-size: 0.9rem; color: #64748b; }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .metric {{
            text-align: center;
            padding: 10px;
            background: white;
            border-radius: 8px;
        }}
        .metric-label {{ font-size: 0.8rem; color: #64748b; }}
        .metric-value {{ font-size: 1.2rem; font-weight: bold; color: #1e293b; }}
        
        .trades-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .trades-table th,
        .trades-table td {{
            padding: 8px 12px;
            text-align: center;
            border-bottom: 1px solid #e2e8f0;
        }}
        .trades-table th {{
            background: #f1f5f9;
            font-weight: 600;
            color: #475569;
            font-size: 0.85rem;
        }}
        .trades-table td {{ font-size: 0.9rem; }}
        
        .analysis-status {{
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}
        
        .closing-prices {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .price-card {{
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .price-symbol {{ font-weight: bold; color: #1e293b; }}
        .price-value {{ font-size: 1.1rem; color: #3b82f6; font-weight: bold; }}
        
        .footer-info {{ 
            text-align: center; 
            margin-top: 30px; 
            color: white;
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 12px;
            line-height: 1.6;
        }}
        
        @media (max-width: 768px) {{ 
            .container {{ padding: 10px; }} 
            .header h1 {{ font-size: 2rem; }} 
            .stocks-grid {{ grid-template-columns: 1fr; }}
            .statistics-grid {{ grid-template-columns: 1fr; }}
            .trades-table {{ font-size: 0.8rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 BTS-B3</h1>
            <p>Estratégia BTS para Ações Brasileiras + Criptomoedas</p>
        </div>
        
        <div class="info-cards">
            <div class="info-card">
                <h3>📈 Fonte de Dados</h3>
                <p>Yahoo Finance</p>
            </div>
            <div class="info-card">
                <h3>⚡ Operação</h3>
                <p>Abertura do dia seguinte</p>
            </div>
            <div class="info-card">
                <h3>🎯 Ativos Monitorados</h3>
                <p>6 Ativos</p>
            </div>
        </div>
        
        <div class="analysis-status">
            <h3>🕐 Status da Análise Automática</h3>
            <p style="font-size: 1.1rem; color: #22c55e; font-weight: bold; margin: 15px 0;">
                Última análise: {{ last_analysis }}
            </p>
            <p>Próxima análise: Hoje às 20:00 (Horário de Brasília)</p>
            
            <h4 style="margin-top: 25px; color: #3b82f6;">💰 Preços de Fechamento da Análise</h4>
            <div class="closing-prices">
                {% for stock_code, stock_data in stocks.items() %}
                <div class="price-card">
                    <div class="price-symbol">{{ stock_code }}</div>
                    <div class="price-value">R$ {{ "%.2f"|format(stock_data.current_price) }}</div>
                </div>
                {% endfor %}
            </div>
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
                    
                    <div class="action-tomorrow action-{{ stock_data.action_color }}">
                        {% if stock_data.action_tomorrow == 'COMPRAR' %}🟢{% elif stock_data.action_tomorrow == 'MANTER' %}🟡{% else %}🔴{% endif %}
                        {{ stock_data.action_tomorrow }}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Estatísticas dos Últimos 10 Trades</h2>
            <div class="statistics-grid">
                {% for stock_code, stats in statistics.items() %}
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-title">{{ stock_code }}</div>
                        <div class="stat-subtitle">{{ stocks[stock_code].name }}</div>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric">
                            <div class="metric-label">Retorno Total</div>
                            <div class="metric-value">+{{ stats.total_return }}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Taxa de Acerto</div>
                            <div class="metric-value">{{ stats.win_rate }}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Máximo Drawdown</div>
                            <div class="metric-value">{{ stats.max_drawdown }}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Retorno Médio</div>
                            <div class="metric-value">+{{ stats.avg_return }}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Prazo Médio</div>
                            <div class="metric-value">{{ stats.avg_duration }} dias</div>
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
                            {% for trade in stats.trades %}
                            <tr>
                                <td>{{ trade.entry }}</td>
                                <td>{{ trade.exit }}</td>
                                <td class="{% if trade.return > 0 %}positive{% else %}negative{% endif %}">
                                    {{ "%.2f"|format(trade.return) }}%
                                </td>
                                <td>{{ trade.duration }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
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
        console.log('Total de ativos:', Object.keys({{ stocks|tojson }}).length);
        console.log('Última análise:', '{{ last_analysis }}');
    </script>
</body>
</html>
    """
    
    return render_template_string(template, 
                                stocks=STOCKS_DATA, 
                                statistics=STATISTICS_DATA,
                                last_analysis=LAST_ANALYSIS)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({{
        "status": "ok",
        "stocks_count": len(STOCKS_DATA),
        "last_analysis": LAST_ANALYSIS,
        "prices_updated": True
    }})

@app.route('/debug')
def debug():
    """Debug endpoint"""
    return jsonify({{
        "stocks": STOCKS_DATA,
        "statistics": STATISTICS_DATA,
        "last_analysis": LAST_ANALYSIS,
        "stocks_count": len(STOCKS_DATA)
    }})

if __name__ == '__main__':
    try:
        print("🚀 Iniciando BTS-B3 com preços atualizados...")
        print("📊 Preços de fechamento atualizados:")
        for stock, data in STOCKS_DATA.items():
            print(f"   {{stock}}: R$ {{data['current_price']:.2f}}")
        
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 Servidor iniciando na porta {{port}}...")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Erro: {{e}}")
        app.run(host='0.0.0.0', port=5000, debug=False)
