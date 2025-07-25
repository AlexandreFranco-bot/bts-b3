# BTS-B3 v2.0 🇧🇷🤖

Sistema **automático** de análise da estratégia BTS para as 5 melhores ações brasileiras da B3.

## 🆕 **Novidades v2.0**

### ✅ **Busca Automática de Dados**
- Dados atualizados automaticamente do **Yahoo Finance**
- **Sem necessidade de inserção manual** de preços
- Atualização diária às **20h Brasil** (após fechamento do mercado)

### ✅ **Operação Realista**
- Entrada/saída no **preço de abertura do dia seguinte** ao sinal
- Simulação mais próxima da realidade de trading
- Sistema informa **ação para o próximo dia**: COMPRAR, VENDER ou MANTER

### ✅ **Interface Aprimorada**
- Coluna **"Ação Amanhã"** mostra o que fazer no próximo pregão
- Informações de atualização automática
- Botão para forçar atualização imediata

---

## 📊 **Ações Monitoradas**

| Ação | Empresa | Retorno BTS | Retorno B&H | Outperformance |
|------|---------|-------------|-------------|----------------|
| **JBSS3** | JBS S.A. | **+1158,5%** | +350,4% | +808,1pp |
| **SBSP3** | Sabesp | **+406,3%** | +106,5% | +299,8pp |
| **PETR4** | Petrobras PN | **+282,4%** | +47,1% | +235,3pp |
| **BPAC11** | BTG Pactual | **+299,6%** | +23,3% | +276,3pp |
| **SUZB3** | Suzano | **+242,5%** | +20,9% | +221,6pp |

*Resultados sem custos de transação - preços brutos de abertura*

---

## 🚀 **Como Funciona**

### 📅 **Cronograma Diário**
1. **20h Brasil**: Sistema busca dados atualizados do Yahoo Finance
2. **Análise automática**: Calcula indicadores BTS (SG Filter + Donchian)
3. **Detecção de sinais**: Identifica mudanças de tendência
4. **Ação para amanhã**: Informa se deve COMPRAR, VENDER ou MANTER

### 📈 **Lógica de Operação**
- **Sinal de COMPRA hoje** → **COMPRAR na abertura de amanhã**
- **Sinal de VENDA hoje** → **VENDER na abertura de amanhã**
- **Sem mudança** → **MANTER posição atual**

### 🎯 **Estratégia BTS**
- **Savitzky-Golay Filter (25,4)**: Suavização da série de preços
- **Donchian Midpoint (6)**: Canal de referência
- **Sinal de Compra**: SG Filter > Donchian Midpoint
- **Sinal de Venda**: SG Filter ≤ Donchian Midpoint

---

## 🛠️ **Tecnologias**

### **Backend**
- **Flask** - Framework web Python
- **yfinance** - Dados do Yahoo Finance
- **pandas/numpy** - Análise de dados
- **scipy** - Filtro Savitzky-Golay
- **pytz** - Fuso horário Brasil

### **Frontend**
- **Bootstrap 5** - Design responsivo
- **JavaScript** - Interatividade
- **Auto-refresh** - Atualização automática da interface

---

## 📦 **Instalação e Deploy**

### **Local**
```bash
git clone https://github.com/seu-usuario/bts-b3.git
cd bts-b3
pip install -r requirements.txt
python app.py
```

### **Render.com**
```yaml
# render.yaml
services:
  - type: web
    name: bts-b3-v2
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

---

## 📊 **Performance Comprovada**

### **Comparação: Performance Sem Custos**

| Ação | Retorno BTS | Taxa Acerto | Sharpe | Drawdown | Trades |
|------|-------------|-------------|--------|----------|--------|
| JBSS3 | +1158,5% | 86% | 2,47 | 2,8% | 28 |
| SBSP3 | +406,3% | 91% | 3,87 | 1,5% | 23 |
| PETR4 | +282,4% | 92% | 3,73 | 2,1% | 24 |
| BPAC11 | +299,6% | 87% | 4,23 | 4,5% | 30 |
| SUZB3 | +242,5% | 100% | 4,64 | 0,0% | 22 |

**📈 Resultado:** Performance excepcional sem custos de transação!

---

## 🎯 **Vantagens v2.0**

### ✅ **Automação Total**
- Sem necessidade de inserção manual de dados
- Atualização automática diária
- Sistema funciona 24/7

### ✅ **Operação Realista**
- Entrada/saída em preços executáveis
- Considera gap de abertura
- Simula operação real na B3

### ✅ **Interface Intuitiva**
- Mostra exatamente o que fazer amanhã
- Informações claras e objetivas
- Design responsivo para mobile

### ✅ **Dados Confiáveis**
- Yahoo Finance como fonte
- Dados com delay de 15 minutos
- Histórico completo disponível

---

## ⚠️ **Importante**

### **Horários**
- **Atualização**: 20h Brasil (após fechamento)
- **Ação**: Abertura do próximo pregão (9h30)
- **Dados**: Delay de 15 minutos (Yahoo Finance)

### **Disclaimer**
Este sistema é para fins educacionais. Não constitui recomendação de investimento. Sempre consulte um profissional qualificado.

---

## 📄 **Licença**

MIT License - Sistema aberto para a comunidade

---

**🚀 BTS-B3 v2.0 - Automação completa para estratégia BTS em ações brasileiras!**

