import streamlit as st
import pandas as pd
import models as md
import agents.orchestrator as orch

# Título da aplicação
st.title('Valle.ai - Assistente inteligente para cálculo de Vale-Alimentação/Refeição')
st.markdown('### Carregue o arquivo zip contendo as planilhas para processamento')

# Passo 1: Upload do arquivo ZIP
zip_file = st.file_uploader("Selecione ou arraste o arquivo ZIP aqui", type=["zip"])

if zip_file is not None: 
    zip_bytes = zip_file.getvalue()
    
    # Botão para iniciar o processamento
    if st.button('Processar'):
        st.spinner("Iniciando o processamento dos dados...")
        try:
            orchestrator = orch.AgentOrchestrator()
            output = orchestrator.orchestrate(zip_bytes)
            st.download_button(
                label="Clique para baixar o arquivo",
                data=output,
                file_name="Base_VR_Pronta.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
                st.error(f"Ocorreu um erro durante o processamento: {e}")
                st.warning("Por favor, verifique se os arquivos estão corretos e tente novamente.")
else:
    st.warning('Por favor, carregue todos os arquivos antes de processar.')