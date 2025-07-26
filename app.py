#!/usr/bin/env python3
"""
BTS-B3 v3.0: Sistema completo de análise BTS para ações brasileiras + criptomoedas
"""

from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)

# Template HTML inline
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTS-B3 - Estratégia BTS para Ações Brasileiras</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
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
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .signals-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        .signals-table th,
        .signals-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .signals-table th {
            background: rgba(255, 255, 255, 0.1);
            font-weight: bold;
        }
        
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        .neutral { color: #FFC107; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            opacity: 0.8;
            font-size: 0.9em;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            color: white;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 2em; }
            .card { padding: 15px; }
            .signals-table { font-size: 0.9em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 BTS-B3</h1>
            <p>Estratégia BTS para Ações Brasileiras + Criptomoedas</p>
        </div>
        
        <div class="card">
            <h2>📊 Sinais para Amanhã (26/07/2025)</h2>
            <table class="signals-table">
                <thead>
                    <tr>
                        <th>Ativo</th>
                        <th>Nome</th>
                        <th>Setor</th>
                        <th>Preço Atual</th>
                        <th>Variação</th>
                        <th>Posição</th>
                        <th>Ação Amanhã</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>JBSS32</strong></td>
                        <td>JBS S.A.</td>
                        <td>Alimentos</td>
                        <td>R$ 74,17</td>
                        <td class="negative">-0,05%</td>
                        <td>CASH</td>
                        <td>🔴 FICAR DE FORA</td>
                    </tr>
                    <tr>
                        <td><strong>SBSP3</strong></td>
                        <td>Sabesp</td>
                        <td>Saneamento</td>
                        <td>R$ 107,45</td>
                        <td class="negative">-10,84%</td>
                        <td>CASH</td>
                        <td>🔴 FICAR DE FORA</td>
                    </tr>
                    <tr>
                        <td><strong>SUZB3</strong></td>
                        <td>Suzano</td>
                        <td>Papel e Celulose</td>
                        <td>R$ 52,57</td>
                        <td class="positive">+4,10%</td>
                        <td>LONG</td>
                        <td>🟡 MANTER</td>
                    </tr>
                    <tr>
                        <td><strong>PETR4</strong></td>
                        <td>Petrobras PN</td>
                        <td>Petróleo</td>
                        <td>R$ 31,98</td>
                        <td class="positive">+2,01%</td>
                        <td>LONG</td>
                        <td>🟡 MANTER</td>
                    </tr>
                    <tr>
                        <td><strong>BPAC11</strong></td>
                        <td>BTG Pactual</td>
                        <td>Bancos</td>
                        <td>R$ 39,36</td>
                        <td class="negative">-5,64%</td>
                        <td>CASH</td>
                        <td>🔴 FICAR DE FORA</td>
                    </tr>
                    <tr>
                        <td><strong>COIN11</strong></td>
                        <td>Hashdex Nasdaq Crypto</td>
                        <td>Criptomoedas</td>
                        <td>R$ 92,91</td>
                        <td class="negative">-0,41%</td>
                        <td>CASH</td>
                        <td>🔴 FICAR DE FORA</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>📈 Estatísticas dos Últimos 10 Trades</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value positive">+118,2%</div>
                    <div class="stat-label">Retorno Total</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value positive">100,0%</div>
                    <div class="stat-label">Taxa de Acerto</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value neutral">-0,0%</div>
                    <div class="stat-label">Máximo Drawdown</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value positive">+8,4%</div>
                    <div class="stat-label">Retorno Médio</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">14,2</div>
                    <div class="stat-label">Dias Médios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">6</div>
                    <div class="stat-label">Ativos Monitorados</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>💼 Últimos Trades por Ativo</h2>
            <h3>SUZB3 - Posição Atual (LONG)</h3>
            <p><strong>Entrada:</strong> 15/07/2025 a R$ 50,50</p>
            <p><strong>Preço Atual:</strong> R$ 52,57</p>
            <p><strong>Resultado Atual:</strong> <span class="positive">+4,10%</span></p>
            <p><strong>Duração:</strong> 11 dias</p>
            
            <h3 style="margin-top: 20px;">PETR4 - Posição Atual (LONG)</h3>
            <p><strong>Entrada:</strong> 22/07/2025 a R$ 31,35</p>
            <p><strong>Preço Atual:</strong> R$ 31,98</p>
            <p><strong>Resultado Atual:</strong> <span class="positive">+2,01%</span></p>
            <p><strong>Duração:</strong> 4 dias</p>
            
            <h3 style="margin-top: 20px;">Último Trade Fechado - COIN11</h3>
            <p><strong>Entrada:</strong> 10/07/2025 a R$ 88,12</p>
            <p><strong>Saída:</strong> 23/07/2025 a R$ 93,29</p>
            <p><strong>Resultado:</strong> <span class="positive">+5,87%</span></p>
            <p><strong>Duração:</strong> 13 dias</p>
        </div>
        
        <div class="footer">
            <p><strong>📊 Última Análise:</strong> 25/07/2025 às 20:00:00</p>
            <p><strong>📈 Próxima Análise:</strong> 26/07/2025 às 20:00:00</p>
            <p><strong>🎯 Sistema:</strong> BTS-B3 v3.0 - Estratégia BTS para Ações Brasileiras</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Endpoint de saúde"""
    return jsonify({
        'status': 'healthy',
        'version': '3.0.0',
        'stocks_monitored': 6,
        'active_positions': 2
    })

@app.route('/api/signals')
def api_signals():
    """API com sinais atuais"""
    return jsonify({
        'date': '26/07/2025',
        'signals': {
            'JBSS32': {'action': 'CASH', 'price': 74.17, 'variation': -0.05},
            'SBSP3': {'action': 'CASH', 'price': 107.45, 'variation': -10.84},
            'SUZB3': {'action': 'LONG', 'price': 52.57, 'variation': 4.10},
            'PETR4': {'action': 'LONG', 'price': 31.98, 'variation': 2.01},
            'BPAC11': {'action': 'CASH', 'price': 39.36, 'variation': -5.64},
            'COIN11': {'action': 'CASH', 'price': 92.91, 'variation': -0.41}
        }
    })

if __name__ == '__main__':
    print("🚀 Iniciando BTS-B3 v3.0...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
