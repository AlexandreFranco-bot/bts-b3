# BTS-B3 🇧🇷

Sistema de análise da estratégia BTS (Trend Following) para as 5 melhores ações brasileiras da B3.

## 📊 Ações Monitoradas

- **JBSS3** - JBS S.A. (Alimentos) - +790,7% retorno
- **SBSP3** - Sabesp (Saneamento) - +271,3% retorno  
- **SUZB3** - Suzano (Papel e Celulose) - +159,7% retorno
- **PETR4** - Petrobras PN (Petróleo) - +198,5% retorno
- **BPAC11** - BTG Pactual (Bancos) - +171,7% retorno

## 🚀 Funcionalidades

### ✅ Atualização Manual de Preços
- Campos para inserir preços de fechamento diários
- Botão para processar e atualizar análises
- Detecção automática de mudanças de sinal

### 📈 Tabela de Sinais
- Última mudança de tendência de cada ação
- Data e preço do sinal (sem custos de 0,75%)
- Variação atual baseada no novo preço
- Status da posição (LONG/CASH)

### 📊 Estatísticas Individuais
Para cada uma das 5 ações:
- Retorno médio dos últimos 10 trades
- Taxa de acerto
- Retorno total da estratégia BTS
- Comparação com Buy & Hold
- Drawdown máximo
- Sharpe Ratio

## 🛠️ Tecnologias

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5 + JavaScript
- **Análise**: Pandas, NumPy, SciPy
- **Indicadores**: Savitzky-Golay Filter + Donchian Midpoint

## 📦 Instalação

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/bts-b3.git
cd bts-b3

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python app.py
```

## 🌐 Deploy

### Render.com
```bash
# Build Command
pip install -r requirements.txt

# Start Command  
gunicorn app:app
```

### Variáveis de Ambiente
Nenhuma variável especial necessária.

## 📋 Como Usar

1. **Acesse a aplicação** no navegador
2. **Insira os preços** de fechamento do dia nos campos correspondentes
3. **Clique em "Atualizar"** para processar os dados
4. **Visualize** as mudanças de sinal e estatísticas atualizadas

## 🎯 Estratégia BTS

A estratégia BTS utiliza:
- **Savitzky-Golay Filter (25,4)**: Suavização da série de preços
- **Donchian Midpoint (6)**: Canal de referência
- **Sinal de Compra**: SG Filter > Donchian Midpoint
- **Sinal de Venda**: SG Filter ≤ Donchian Midpoint

## 📊 Performance Histórica

| Ação | Retorno BTS | Buy & Hold | Outperformance | Taxa Acerto |
|------|-------------|------------|----------------|-------------|
| JBSS3 | +790,7% | +350,4% | +440,3pp | 76% |
| SBSP3 | +271,3% | +106,5% | +164,8pp | 78% |
| PETR4 | +198,5% | +47,1% | +151,4pp | 79% |
| BPAC11 | +171,7% | +23,3% | +148,4pp | 80% |
| SUZB3 | +159,7% | +20,9% | +138,8pp | 100% |

## ⚠️ Disclaimer

Este sistema é apenas para fins educacionais e de análise. Não constitui recomendação de investimento. Sempre consulte um profissional qualificado antes de tomar decisões de investimento.

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

---

**Desenvolvido com ❤️ para a comunidade de investidores brasileiros**

