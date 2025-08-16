# Automação de Cálculo de Benefício de Vale-Refeição (VR)

Este projeto é uma aplicação web interativa desenvolvida em Python para automatizar o processo de cálculo do benefício de Vale-Refeição (VR) para colaboradores.

A aplicação consolida dados de múltiplas planilhas do Excel, realiza filtros e cálculos complexos, e gera um arquivo Excel final com o relatório completo e preciso.

## Funcionalidades Principais

- **Interface Web Interativa:** Desenvolvida com Streamlit, a interface é intuitiva e permite o carregamento de todos os arquivos de dados necessários de forma simples e visual.
- **Consolidação de Dados:** O sistema une as bases de dados de colaboradores Ativos e Admissões.
- **Filtragem Inteligente:** Exclui automaticamente colaboradores que não são elegíveis ao benefício, incluindo:
    - Desligados
    - Afastados
    - Em período de férias
    - Estagiários e Aprendizes
    - Colaboradores no exterior
- **Cálculo Preciso:** Mescla os dados de dias úteis e valores de sindicato para realizar o cálculo final, gerando as colunas de `TOTAL`, `Custo empresa` e `Desconto profissional`.
- **Geração de Relatório:** Cria um arquivo Excel final (`Base_VR_Pronta.xlsx`) com todos os dados processados e os cálculos prontos para análise.

## Requisitos

Para rodar esta aplicação, você precisa ter o Python instalado na sua máquina. As bibliotecas necessárias são:

- `streamlit`
- `pandas`
- `openpyxl` (para ler arquivos .xlsx)
- `xlsxwriter` (para escrever arquivos .xlsx)

Você pode instalar todas as dependências de uma vez usando o `pip`:

```bash
pip install streamlit pandas openpyxl xlsxwriter
