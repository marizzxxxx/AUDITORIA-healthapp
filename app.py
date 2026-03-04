import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard HealthApp", layout="wide", page_icon="📈")

with st.sidebar:
    st.title("🎓 Dados da Aluna")
    st.markdown("---")
    st.markdown("**Aluna:** Maria Eduarda Clementino Aires")
    st.markdown("**Curso:** Sistemas de Informação")
    st.markdown("**Semestre:** 8º Semestre")
    st.markdown("**Disciplina:** Auditoria e Segurança")
    st.markdown("**Professor:** José Olinda da Silva")
    st.markdown("---")
    st.info("Atividade de Análise de Logs utilizando o dataset HealthApp.")

st.title("Análise de Logs - HealthApp")
st.markdown("---")

col_texto, col_vazia = st.columns([2, 1])
with col_texto:
    st.markdown("""
                
    **Dataset:** [Loghub - HealthApp Dataset](https://github.com/logpai/loghub/tree/master/HealthApp)  
    **Tema:** Aplicativo de saúde (monitoramento de passos, calorias e sincronização em background).

    ### 1. Caracterização
    O HealthApp é um aplicativo mobile para Android que roda em background para monitorar exercícios. A amostra que estamos analisando tem **2.000 linhas de registro**, cobrindo um período de pouco mais de duas horas e meia (noite do dia 23/12/2017 até a madrugada do dia 24/12/2017). 
    Os principais eventos registrados foram passadas do usuário, cálculos de caloria/altitude e eventos do sistema.
    """)

@st.cache_data
def carregar_dados():
    df = pd.read_csv('HealthApp_2k.log_structured.csv')
    df['Time'] = pd.to_datetime(df['Time'], format='%Y%m%d-%H:%M:%S:%f')
    df['Minuto'] = df['Time'].dt.strftime('%H:%M')
    return df

df = carregar_dados()

st.markdown("### 2. Análise Estatística Geral")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Logs Lidos", f"{len(df):,}".replace(",", "."))
col2.metric("Período de Tempo", "2h 47m")
col3.metric("Minuto de Maior Pico", df['Minuto'].value_counts().index[0])
col4.metric("Logs no Pico", df['Minuto'].value_counts().iloc[0])

st.write("Abaixo podemos explorar os detalhes visuais do comportamento do aplicativo:")

sns.set_theme(style="whitegrid", palette="pastel")

aba1, aba2, aba3 = st.tabs(["Frequência de Eventos", "Erros e Exceções", "⏱Horários de Pico"])

with aba1:
    st.subheader("Eventos que mais sobrecarregam o aplicativo")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    top5_freq = df['EventTemplate'].value_counts().head(5)
    sns.barplot(x=top5_freq.values, y=top5_freq.index, ax=ax1, palette="Blues_r", hue=top5_freq.index, legend=False)
    
    for i, v in enumerate(top5_freq.values):
        ax1.text(v + 5, i, f" {v} logs", color='black', va='center', fontweight='bold', fontsize=10)
    
    ax1.set_xlabel('Quantidade de Ocorrências')
    ax1.set_ylabel('')
    st.pyplot(fig1)

with aba2:
    st.subheader("Eventos isolados, erros ou bloqueio de tela")
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    top5_raros = df['EventTemplate'].value_counts().tail(5)
    sns.barplot(x=top5_raros.values, y=top5_raros.index, ax=ax2, palette="Reds_r", hue=top5_raros.index, legend=False)
    
    for i, v in enumerate(top5_raros.values):
        ax2.text(v + 0.05, i, f" {v} logs", color='black', va='center', fontweight='bold', fontsize=10)
    
    ax2.set_xlabel('Quantidade de Ocorrências')
    ax2.set_ylabel('')
    st.pyplot(fig2)

with aba3:
    st.subheader("Horários (Minutos) de Pico com Maior Volume de Logs")
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    top5_minutos = df['Minuto'].value_counts().head(5)
    
    sns.barplot(x=top5_minutos.index, y=top5_minutos.values, ax=ax3, palette="crest", hue=top5_minutos.index, legend=False)
    
    for i, v in enumerate(top5_minutos.values):
        ax3.text(i, v + 2, str(v), color='black', ha='center', fontweight='bold', fontsize=10)
        
    ax3.set_xlabel('Horário (HH:MM)')
    ax3.set_ylabel('Quantidade de Logs Gerados')
    st.pyplot(fig3)

st.markdown("---")
st.markdown("""
            
### 3. Análise de Padrões e Conclusão

Observando os gráficos detalhados acima, fica claro que existe um **padrão de repetição muito agressivo**. O aplicativo entra em um loop contínuo:
`Detecta Passo` ➔ `Consulta Banco` ➔ `Calcula Calorias` ➔ `Atualiza Banco de Dados`.

Isso explica os picos altíssimos de atividade no horário das **22h15 até 22h19**, indicando o momento exato em que o usuário estava realizando uma caminhada. De madrugada, a concentração de logs cai para quase zero, registrando apenas o pulso de "TIME_TICK" a cada minuto para avisar que o sistema está operante.

**Conclusão Final:**
A arquitetura atual do HealthApp gera um volume excessivo e desnecessário de logs por ser um app altamente reativo a cada passo isolado. Ficar salvando cada passada individualmente no banco de dados SQLite (o que ocasiona falhas ocasionais de *bulk insert*, visíveis nos eventos raros) força o processamento de disco e drena a bateria do dispositivo. O cenário ideal seria o aplicativo acumular esses passos na memória temporária e descarregar no banco de dados em lotes maiores a cada 5 ou 10 minutos.
""")