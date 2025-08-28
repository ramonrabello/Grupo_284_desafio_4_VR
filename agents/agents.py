from abc import ABC, abstractmethod
import pandas as pd
import zipfile, io
import streamlit as st

class Agent(ABC):
    @abstractmethod
    def run(self, context: dict) -> dict:
        pass

class FileIngestAgent(Agent):
    def run(self, context):
        st.spinner("Extraindo planilhas...")
        zip_bytes = context['zip_bytes']
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            xlsx_files = [f for f in z.namelist() if f.endswith(".xlsx")]
            if not xlsx_files:
                st.warning("Nenhum arquivo .xlsx encontrado dentro do ZIP.")
            else:
                st.write(f"Encontrados {len(xlsx_files)} arquivos XLSX.")
                for file_name in xlsx_files:
                    with z.open(file_name) as f:
                        # Carrega o Excel diretamente do BytesIO
                        df = pd.read_excel(io.BytesIO(f.read()))
                        st.subheader(file_name)
                        st.dataframe(df)
                        dfs = {name: pd.read_excel(z.open(name)) for name in z.namelist() if name.endswith('.xlsx')}
                context.update(dfs)
                st.success(f"{len(xlsx_files)} planilhas lidas com sucesso")
        return context

class ActivesConsolidationAgent(Agent):
    def run(self, context):
        st.spinner("Consolidando planilha de ativos...")
        actives = context['ATIVOS']
        hired_in_april = context['ADMISSAO_ABRIL']
        context['base_principal'] = pd.concat([actives, hired_in_april], ignore_index=True)
        st.success("Planilhas de ativos consolidadas com sucesso")
        return context

class ElegibilityFilterAgent(Agent):
    def run(self, context):
        st.spinner("Excluindo não elegíveis ao benefício...")
        df_desligados = context['DESLIGADOS']['MATRICULA'].astype(str).tolist()
        base_final = context['base_final']
        base_final[~base_final['MATRICULA'].astype(str).isin(df_desligados)]

        df_afastados = context['AFASTAMENTOS']['MATRICULA'].astype(str).tolist()
        base_final = base_final[~base_final['MATRICULA'].astype(str).isin(df_afastados)]

        # Excluir de férias (se a coluna 'DESC. SITUACAO' for 'Férias')
        base_final = base_final[~base_final['DESC. SITUACAO'].str.contains('FÉRIAS', na=False, case=False)]
            
        # Excluir estagiários e aprendizes com base no TÍTULO DO CARGO
        titulos_a_excluir = pd.concat([
                context['ESTAGIO']['TITULO DO CARGO'], 
                context['APRENDIZ']['TITULO DO CARGO']
            ]).unique().tolist()
        base_final = base_final[~base_final['TITULO DO CARGO'].isin(titulos_a_excluir)]
            
        # Excluir quem está no exterior
        df_exterior = context['EXTERIOR']['CADASTRO'].astype(str).tolist()
        base_final = base_final[~base_final['MATRICULA'].astype(str).isin(df_exterior)]
        st.success("Registros excluídos do cálculo com sucesso")
        return context

class DataMergingAgent(Agent):
    def run(self, context):
        st.spinner("Mesclando base com base de dias úteis...")
        base_final = context['base_final']
        base_final['SINDICATO'] = base_final['SINDICATO'].str.strip()

        # Mesclar com a base de dias úteis
        dias_uteis_df = context['DIAS_UTEIS'].copy()
        dias_uteis_df.rename(columns={'SINDICADO': 'SINDICATO', 'DIAS UTEIS ': 'DIAS'}, inplace=True) # Ajuste nos nomes das colunas
        dias_uteis_df['SINDICATO'] = dias_uteis_df['SINDICATO'].str.strip()
        base_final = pd.merge(base_final, dias_uteis_df[['SINDICATO', 'DIAS']], on='SINDICATO', how='left')
            
        # Mapear a sigla do estado para o nome completo para o merge com a base de valores
        sindicato_valor_df = context['SINDICATO_VALOR'].copy()
        sindicato_valor_df.rename(columns={'ESTADO': 'ESTADO', 'VALOR': 'VALOR DIÁRIO VR'}, inplace=True)
        sindicato_valor_df['ESTADO'] = sindicato_valor_df['ESTADO'].str.strip().str.upper()

        sindicato_mapping = {
                'SP': 'SÃO PAULO',
                'RS': 'RIO GRANDE DO SUL',
                'PR': 'PARANÁ',
                'RJ': 'RIO DE JANEIRO'
        }
        # Extração mais robusta da sigla do estado
        base_final['ESTADO'] = base_final['SINDICATO'].str.split(' - ').str[0].str[-2:].str.strip().str.upper().map(sindicato_mapping)
            
        # Fazer o merge com a base de valores de sindicato
        base_final = pd.merge(base_final, sindicato_valor_df, on='ESTADO', how='left')
        context.update(base_final)
        st.success("Mesclagem finalizada com sucesso")
        return context
    
class AdjustmentAgent(Agent):
    def run(self, context):
        st.spinner("Ajustando dados finais...")
        st.success("Registros ajustados com sucesso")
        return context
    
class CalculationAgent(Agent):
    def run(self, context):
        st.spinner("Realizando os cálculos finais...")
        base_final = context['base_final']
        base_final['TOTAL'] = base_final['DIAS'] * base_final['VALOR DIÁRIO VR']
        base_final['Custo empresa'] = base_final['TOTAL'] * 0.80
        base_final['Desconto profissional'] = base_final['TOTAL'] * 0.20
            
        # Limpar colunas de mesclagem para o relatório final
        base_final.drop(columns=['ESTADO'], inplace=True, errors='ignore')
        st.success('Processamento concluído! O arquivo está pronto para download.')
        return context

class ExcelExportAgent(Agent):
    def run(self, context):
        st.spinner("Gerando planilha com base final...")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            base_final = context['base_final'].to_excel(writer, index=False, sheet_name='Base Final')
        output.seek(0)
        context.update(output)
        return context