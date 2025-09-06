`markdown

🧠 Sistema Multi-Agentes A2A para Cálculo de VR/VA

Este projeto implementa um pipeline distribuído para cálculo de vale-refeição (VR) e vale-alimentação (VA) utilizando agentes autônomos que se comunicam via protocolo A2A (Agent-to-Agent). Cada etapa do processo é executada por um agente remoto, coordenado por um orquestrador central com interface visual em Streamlit.

---

🚀 Funcionalidades

- 📁 Upload de arquivo .zip com planilhas
- 🧠 Execução do pipeline distribuído via orquestrador A2A
- 🔄 Lógica de recuperação e rollback por agente
- 📊 Interface Streamlit com barra de progresso e mensagens contextuais
- 📥 Download do arquivo final .xlsx
- 📜 Histórico persistente por usuário
- 🔍 Painel de auditoria com rastreamento por agente
- 🚨 Alertas inteligentes para falhas e lentidão

---

🧩 Componentes

🔗 Orquestrador

- API FastAPI que coordena o pipeline
- Endpoint: POST /executar_pipeline/
- Entrada: dados.zip
- Saída: BaseVRPronta.xlsx
- Registro de tentativas, tempo e status por agente

🧠 Agentes A2A

| Agente                  | Skill ID              | Função Técnica                                 |
|------------------------|-----------------------|------------------------------------------------|
| FileIngestAgent        | load-zip            | Extrai planilhas do ZIP                       |
| ConsolidationAgent     | consolidate-bases   | Mescla ATIVOS + ADMISSÃO_ABRIL                |
| EligibilityFilterAgent | filter-ineligible   | Remove colaboradores não elegíveis            |
| DataImputationAgent    | impute-data         | Preenche sindicato, estado, dias úteis, valor |
| AdjustmentAgent        | apply-adjustments   | Desconta férias, feriados e afastamentos      |
| CalculationAgent       | calculate-values    | Calcula valores finais de VR                  |
| ExcelExportAgent       | export-excel        | Gera planilha final .xlsx                   |

---

📊 Interface Streamlit

- Autenticação por usuário e senha
- Upload do ZIP e execução do pipeline
- Barra de progresso com mensagens por agente
- Download do arquivo final
- Histórico persistente com SQLite
- Painel de auditoria com filtros, gráficos e exportação
- Rastreamento por agente com tentativas, tempo e status
- Alertas visuais para agentes com falhas ou lentidão

---

🔁 Recuperação e Rollback

- Cada agente tenta até 2 vezes
- Falhas são registradas com mensagem de erro
- Rollback usa o último estado válido
- Pipeline continua mesmo com dados parciais

---

🚨 Alertas Inteligentes

- Detecta agentes com ≥3 falhas (erro/timeout)
- Detecta agentes com tempo médio ≥5s
- Exibe alertas visuais no painel
- Pode ser estendido para notificações externas (Slack, e-mail, webhook)

---

🗃️ Banco de Dados

- SQLite local (historico.db)
- Tabelas:
  - execucoes: histórico por usuário
  - rastreamento_agente: detalhes por agente
- Suporte a PostgreSQL para produção

---

🧪 Teste de Integração

1. Gere dados.zip com planilhas simuladas
2. Envie via Swagger ou interface Streamlit
3. Verifique resposta: BaseVRPronta.xlsx ou dados intermediários
4. Acompanhe rastreamento e alertas no painel

---

🐳 Deploy com Docker

`Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
`

---

🌐 Deploy na Render

1. Crie repositório vr-streamlit-app no GitHub
2. Suba os arquivos: app.py, db.py, Dockerfile, requirements.txt, .env
3. Acesse Render.com
4. Crie um Web Service com ambiente Docker
5. Acesse sua interface em:  
   https://vr-streamlit-app.onrender.com

---

📁 Estrutura do Projeto

`
vr-streamlit-app/
├── app.py               # Interface Streamlit
├── db.py                # Persistência SQLite
├── requirements.txt     # Dependências
├── Dockerfile           # Container da aplicação
├── .env                 # Usuários e senhas
└── README.md            # Documentação
`

---

🧠 Autor

Ramon — São Paulo, Brasil  
Sistema desenvolvido com apoio do Microsoft Copilot 🤖
`
