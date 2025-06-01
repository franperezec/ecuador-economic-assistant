import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from typing import List, Dict, Any
import io
import re

# Importaciones para Claude
import anthropic

# Configuración de la página
st.set_page_config(
    page_title="Ecuador Economic Data Assistant",
    page_icon="🇪🇨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado estilo CEPALSTAT
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem 2rem;
        border-radius: 0;
        color: white;
        text-align: left;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    .main-header p {
        margin: 0.2rem 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .indicator-selector {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .indicator-definition {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .download-section {
        background: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2a5298;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .chat-section {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-top: 1rem;
    }
    
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

def load_weo_data():
    """Cargar datos WEO desde el documento"""
    
    # Datos WEO completos de Ecuador
    weo_raw_data = """WEO Country Code	ISO	WEO Subject Code	Country	Subject Descriptor	Subject Notes	Units	Scale	Country/Series-specific Notes	1980	1981	1982	1983	1984	1985	1986	1987	1988	1989	1990	1991	1992	1993	1994	1995	1996	1997	1998	1999	2000	2001	2002	2003	2004	2005	2006	2007	2008	2009	2010	2011	2012	2013	2014	2015	2016	2017	2018	2019	2020	2021	2022	2023	2024	2025	2026	2027	2028	2029	2030	Estimates Start After
248	ECU	NGDP_R	Ecuador	Gross domestic product, constant prices	Expressed in billions of national currency units; the base year is country-specific. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]	National currency	Billions	Source: Central Bank Latest actual data: 2023 Notes: The national accounts have been updated from 2002 onwards. Prior to 2002 the data are adjusted to produce smooth series with the use of splicing technique. These estimates continue to serve as proxies for historical series when complete information is una National accounts manual used: System of National Accounts (SNA) 2008 GDP valuation: Market prices Reporting in calendar year: Yes Start/end months of reporting year: January/December Base year: 2018 Chain-weighted: Yes, from 2018 Primary domestic currency: US dollar Data last updated: 04/10/2025	33.922	35.245	35.668	34.669	36.125	37.715	38.882	36.56	40.393	40.508	41.727	43.86	45.445	46.354	48.328	49.417	50.273	52.448	54.162	51.595	52.158	54.352	57.03	58.676	62.684	66.069	68.937	70.248	74.86	75.677	78.726	85.403	90.342	96.857	100.95	101.071	100.375	106.368	107.479	107.657	97.704	106.909	113.183	115.434	113.172	115.126	117.563	120.261	123.265	126.376	129.513	2023
248	ECU	NGDP_RPCH	Ecuador	Gross domestic product, constant prices	Annual percentages of constant price GDP are year-on-year changes; the base year is country-specific. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]	Percent change	Units	See notes for:  Gross domestic product, constant prices (National currency).	4.9	3.9	1.2	-2.8	4.2	4.4	3.094	-5.972	10.486	0.285	3.008	5.113	3.614	2	4.258	2.253	1.732	4.328	3.267	-4.739	1.092	4.206	4.928	2.885	6.832	5.399	4.341	1.902	6.565	1.091	4.029	8.481	5.783	7.211	4.226	0.12	-0.688	5.97	1.044	0.165	-9.245	9.422	5.868	1.988	-1.959	1.727	2.117	2.295	2.498	2.524	2.482	2023
248	ECU	NGDP	Ecuador	Gross domestic product, current prices	Expressed in billions of national currency units. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]	National currency	Billions	Source: Central Bank Latest actual data: 2023 Notes: The national accounts have been updated from 2002 onwards. Prior to 2002 the data are adjusted to produce smooth series with the use of splicing technique. These estimates continue to serve as proxies for historical series when complete information is una National accounts manual used: System of National Accounts (SNA) 2008 GDP valuation: Market prices Reporting in calendar year: Yes Start/end months of reporting year: January/December Base year: 2018 Chain-weighted: Yes, from 2018 Primary domestic currency: US dollar Data last updated: 04/10/2025	16.116	16.501	16.474	14.478	15.408	18.02	13.222	12.355	11.749	11.531	11.71	13.139	14.367	16.783	20.238	21.98	23.001	25.847	26.292	18.891	17.531	23.127	27.054	30.965	35.195	40.279	45.691	49.849	61.139	60.095	68.151	78.987	87.735	96.57	102.718	97.21	97.671	104.467	107.479	107.596	95.865	107.179	116.133	121.147	121.728	125.677	130.31	135.35	140.863	146.638	152.588	2023
248	ECU	NGDPD	Ecuador	Gross domestic product, current prices	Values are based upon GDP in national currency converted to U.S. dollars using market exchange rates (yearly average). Exchange rate projections are provided by country economists for the group of other emerging market and developing countries. Exchanges rates for advanced economies are established in the WEO assumptions for each WEO exercise. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]	U.S. dollars	Billions	See notes for:  Gross domestic product, current prices (National currency).	16.116	16.501	16.474	14.478	15.408	18.02	13.222	12.355	11.749	11.531	11.71	13.139	14.367	16.783	20.238	21.98	23.001	25.847	26.292	18.891	17.531	23.127	27.054	30.965	35.195	40.279	45.691	49.849	61.139	60.095	68.151	78.987	87.735	96.57	102.718	97.21	97.671	104.467	107.479	107.596	95.865	107.179	116.133	121.147	121.728	125.677	130.31	135.35	140.863	146.638	152.588	2023
248	ECU	NGDPRPC	Ecuador	Gross domestic product per capita, constant prices	GDP is expressed in constant national currency per person. Data are derived by dividing constant price GDP by total population.	National currency	Units	See notes for:  Gross domestic product, constant prices (National currency) Population (Persons).	4,241.50	4,283.97	4,215.72	3,986.22	4,043.16	4,111.31	4,130.84	3,787.82	4,078.70	3,991.73	4,016.82	4,126.78	4,181.43	4,174.22	4,264.06	4,278.14	4,278.23	4,393.32	4,469.23	4,195.68	4,179.14	4,285.97	4,420.74	4,468.22	4,689.64	4,856.43	4,976.53	4,979.74	5,213.41	5,177.52	5,289.41	5,633.21	5,850.95	6,162.34	6,311.59	6,212.41	6,071.48	6,334.15	6,293.46	6,202.54	5,574.65	6,069.43	6,389.01	6,472.37	6,299.03	6,359.26	6,443.97	6,540.91	6,652.50	6,768.04	6,883.33	2022
248	ECU	NGDPDPC	Ecuador	Gross domestic product per capita, current prices	GDP is expressed in current U.S. dollars per person. Data are derived by first converting GDP in national currency to U.S. dollars and then dividing it by total population.	U.S. dollars	Units	See notes for:  Gross domestic product, current prices (National currency) Population (Persons).	2,015.08	2,005.71	1,947.09	1,664.71	1,724.51	1,964.32	1,404.72	1,280.02	1,186.36	1,136.26	1,127.22	1,236.27	1,321.88	1,511.30	1,785.61	1,902.88	1,957.42	2,165.07	2,169.51	1,536.21	1,404.64	1,823.70	2,097.12	2,358.04	2,633.05	2,960.73	3,298.41	3,533.67	4,257.89	4,111.48	4,578.94	5,210.00	5,682.12	6,144.12	6,422.12	5,975.08	5,907.93	6,220.97	6,293.46	6,199.03	5,469.76	6,084.74	6,555.53	6,792.72	6,775.26	6,942.10	7,142.69	7,361.58	7,602.24	7,853.16	8,109.68	2022
248	ECU	PCPIPCH	Ecuador	Inflation, average consumer prices	Annual percentages of average consumer prices are year-on-year changes.	Percent change	Units	See notes for:  Inflation, average consumer prices (Index).	13.049	16.387	16.258	48.434	31.23	27.983	23.03	29.504	58.216	75.648	48.519	48.804	54.341	45	27.443	22.886	24.4	30.6	36.1	52.2	96.1	37.674	12.485	7.929	2.741	2.17	3.299	2.276	8.4	5.16	3.554	4.475	5.102	2.722	3.589	3.966	1.728	0.417	-0.224	0.266	-0.339	0.133	3.466	2.216	1.547	1.337	1.461	1.536	1.536	1.536	1.536	2024
248	ECU	LUR	Ecuador	Unemployment rate	Unemployment rate can be defined by either the national definition, the ILO harmonized definition, or the OECD harmonized definition. The OECD harmonized unemployment rate gives the number of unemployed persons as a percentage of the labor force (the total number of people employed plus unemployed). [OECD Main Economic Indicators, OECD, monthly] As defined by the International Labour Organization, unemployed workers are those who are currently not working but are willing and able to work for pay, currently available to work, and have actively searched for work. [ILO, http://www.ilo.org/public/english/bureau/stat/res/index.htm]	Percent of total labor force	Units	Source: National Statistics Office. Source: INEC and Central Bank Latest actual data: 2024 Employment type: National definition Primary domestic currency: US dollar Data last updated: 04/10/2025	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	7	7.9	6.1	8.5	8.9	8.3	5.696	5.493	9.046	7.828	10.163	13.107	7.625	9.554	7.828	10.163	7.219	7.095	6.687	6.923	5.95	6.47	5.02	4.21	4.12	4.15	3.8	4.77	5.21	4.62	3.69	3.84	5.346	4.68	3.8	3.57	3.38	4	3.8	3.6	3.5	3.5	3.5	2024
248	ECU	BCA_NGDPD	Ecuador	Current account balance	Current account is all transactions other than those in financial and capital items. The major classifications are goods and services, income and current transfers. The focus of the BOP is on transactions (between an economy and the rest of the world) in goods, services, and income.	Percent of GDP	Units	See notes for:  Gross domestic product, current prices (National currency) Current account balance (U.S. dollars).	-3.981	-6.048	-7.175	-0.794	-1.772	0.422	-4.402	-9.608	-5.788	-6.201	-3.074	-5.388	-0.849	-5.058	-4.439	-4.55	-0.238	-1.767	-7.982	4.86	6.347	-2.383	-4.506	-1.249	-1.362	1.177	3.808	3.784	2.894	0.521	-2.322	-0.507	-0.167	-0.966	-0.651	-2.285	0.922	-0.388	-1.534	-0.507	2.091	2.741	1.84	1.83	5.818	3.423	2.641	2.52	2.514	2.512	2.482	2023
248	ECU	GGXWDG_NGDP	Ecuador	General government gross debt	Gross debt consists of all liabilities that require payment or payments of interest and/or principal by the debtor to the creditor at a date or dates in the future. This includes debt liabilities in the form of SDRs, currency and deposits, debt securities, loans, insurance, pensions and standardized guarantee schemes, and other accounts payable. Thus, all liabilities in the GFSM 2001 system are debt, except for equity and investment fund shares and financial derivatives and employee stock options. Debt can be valued at current market, nominal, or face values (GFSM 2001, paragraph 7.110).	Percent of GDP	Units	See notes for:  General government gross debt (National currency).	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	63.803	55.043	47.198	40.2	35.758	33.094	29.648	24.873	19.667	18.436	18.607	19.341	23.426	28.163	36.438	46.066	47.391	49.505	52.064	63.551	61.756	57.203	54.332	55.039	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGXCNL_NGDP	Ecuador	General government net lending/borrowing	Net lending (+)/ borrowing (-) is calculated as revenue minus total expenditure. This is a core GFS balance that measures the extent to which general government is either putting financial resources at the disposal of other sectors in the economy and nonresidents (net lending), or utilizing the financial resources generated by other sectors and nonresidents (net borrowing). This balance may be viewed as an indicator of the financial impact of general government activity on the rest of the economy and nonresidents (GFSM 2001, paragraph 4.17). Note: Net lending (+)/borrowing (-) is also equal to net acquisition of financial assets minus net incurrence of liabilities.	Percent of GDP	Units	See notes for:  General government net lending/borrowing (National currency).	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	-2.024	-3.44	-2.825	-5.099	-4.825	-0.32	0.033	0.738	1.045	1.942	0.661	2.921	2.658	0.568	-3.714	-1.385	-0.127	-2.835	-8.165	-8.106	-6.866	-10.292	-5.772	-2.803	-3.468	-7.376	-1.588	0.045	-3.484	-1.332	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	TX_RPCH	Ecuador	Volume of exports of goods and services	Percent change of volume of exports refers to the aggregate change in the quantities of total exports whose characteristics are unchanged. The goods and services and their prices are held constant, therefore changes are due to changes in quantities only. [Export and Import Price Index Manual: Theory and Practice, Glossary]	Percent change	Units	Source: Central Bank Latest actual data: 2024 Base year: 2014 Methodology used to derive volumes: Deflation by unit value indexes (from customs data) Formula used to derive volumes: Laspeyres-type Chain-weighted: No. Last updated in 2014 Trade System: General trade Oil coverage: Primary or unrefined products; Secondary or refined products Valuation of exports: Free on board (FOB) Valuation of imports: Free on board (FOB) Primary domestic currency: US dollar Data last updated: 04/10/2025	-1.855	6.362	-3.783	10.062	3.346	13.813	3.963	-15.791	22.953	-3.83	3.104	10.5	9.6	4.2	11.684	11.26	-2.123	6.986	-4.737	7.631	2.536	-1.587	0.624	7.21	17.178	7.521	4.992	-1.958	2.99	-1.762	-0.413	3.891	4.815	5.109	6.525	2.867	-0.142	3.207	0.951	6.915	1.736	7.44	5.521	6.74	4.817	-1.457	4.695	4.17	4.978	5.251	4.999	2024
248	ECU	TM_RPCH	Ecuador	Volume of imports of goods and services	Percent change of volume of imports refers to the aggregate change in the quantities of total imports whose characteristics are unchanged. The goods and services and their prices are held constant, therefore changes are due to changes in quantities only. [Export and Import Price Index Manual: Theory and Practice, Glossary]	Percent change	Units	Source: Central Bank Latest actual data: 2024 Base year: 2014 Methodology used to derive volumes: Deflation by unit value indexes (from customs data) Formula used to derive volumes: Laspeyres-type Chain-weighted: No. Last updated in 2014 Trade System: General trade Oil coverage: Primary or unrefined products; Secondary or refined products Valuation of exports: Free on board (FOB) Valuation of imports: Free on board (FOB) Primary domestic currency: US dollar Data last updated: 04/10/2025	-1.061	5.244	-4.988	-33.125	9.195	5.857	-7.484	9.719	-23.134	3.39	-0.839	16	1	0.8	14.636	7.949	-12.597	20.513	6.532	-31.595	12.822	25.722	19.015	-4.06	10.877	13.162	7.038	6.175	13.009	-6.852	12.483	2.598	0.214	8.16	4.687	-4.79	-11.405	16.627	3.978	0.359	-17.08	18.984	10.016	2.555	-3.279	5.166	3.974	3.885	4.538	5.816	5.466	2024
248	ECU	LP	Ecuador	Population	For census purposes, the total population of the country consists of all persons falling within the scope of the census. In the broadest sense, the total may comprise either all usual residents of the country or all persons present in the country at the time of the census. [Principles and Recommendations for Population and Housing Censuses, Revision 1, paragraph 2.42]	Persons	Millions	Source: National Statistics Office Latest actual data: 2022 Primary domestic currency: US dollar Data last updated: 04/10/2025	7.998	8.227	8.461	8.697	8.935	9.173	9.413	9.652	9.903	10.148	10.388	10.628	10.868	11.105	11.334	11.551	11.751	11.938	12.119	12.297	12.481	12.681	12.901	13.132	13.367	13.604	13.852	14.107	14.359	14.616	14.884	15.161	15.441	15.718	15.994	16.269	16.532	16.793	17.078	17.357	17.526	17.614	17.715	17.835	17.967	18.104	18.244	18.386	18.529	18.672	18.815	2022"""
    
    return weo_raw_data

class EcuadorWEOProcessor:
    """Procesador mejorado de datos WEO de Ecuador del FMI"""
    
    def __init__(self, weo_data_text: str):
        self.raw_data = weo_data_text
        self.df = None
        self.processed_data = {}
        self.indicators_info = {}
        self.year_columns = []
        self.process_data()
    
    def process_data(self):
        """Procesar datos del WEO desde texto"""
        try:
            # Convertir texto a DataFrame
            lines = [line for line in self.raw_data.split('\n') if line.strip()]
            
            # Usar el primer line como headers
            headers = lines[0].split('\t')
            
            # Procesar cada línea de datos
            data_rows = []
            for line in lines[1:]:  # Skip header
                row = line.split('\t')
                # Asegurar que tenga el mismo número de columnas
                while len(row) < len(headers):
                    row.append('')
                data_rows.append(row[:len(headers)])  # Truncar si es muy largo
            
            # Crear DataFrame
            self.df = pd.DataFrame(data_rows, columns=headers)
            
            # Identificar columnas de años - RANGO COMPLETO
            self.year_columns = [col for col in self.df.columns 
                               if col.isdigit() and 1980 <= int(col) <= 2030]
            
            # Procesar cada indicador
            for _, row in self.df.iterrows():
                indicator_code = row['WEO Subject Code']
                if pd.notna(indicator_code) and indicator_code.strip():
                    self.process_indicator(row)
            
            st.success(f"✅ Procesados {len(self.processed_data)} indicadores macroeconómicos con {len(self.year_columns)} años de datos (1980-2030)")
            
        except Exception as e:
            st.error(f"Error procesando datos: {e}")
    
    def process_indicator(self, row):
        """Procesar un indicador individual"""
        indicator_code = row['WEO Subject Code']
        
        # Extraer información del indicador
        indicator_info = {
            'code': indicator_code,
            'name': row['Subject Descriptor'],
            'description': row.get('Subject Notes', ''),
            'units': row['Units'],
            'scale': row['Scale'],
            'notes': row.get('Country/Series-specific Notes', '')
        }
        
        # Extraer datos temporales - TODOS LOS AÑOS
        yearly_data = {}
        for year in self.year_columns:
            value_str = str(row[year]).strip()
            if value_str and value_str.lower() not in ['n/a', 'nan', '', 'none']:
                try:
                    value = float(value_str)
                    yearly_data[int(year)] = value
                except ValueError:
                    continue
        
        # Solo guardar si tiene datos
        if yearly_data:
            # Calcular estadísticas
            values = list(yearly_data.values())
            stats = {
                'data_points': len(yearly_data),
                'first_year': min(yearly_data.keys()),
                'last_year': max(yearly_data.keys()),
                'latest_value': yearly_data[max(yearly_data.keys())],
                'min_value': min(values),
                'max_value': max(values),
                'mean_value': np.mean(values),
                'std_value': np.std(values)
            }
            
            self.processed_data[indicator_code] = {
                'info': indicator_info,
                'data': yearly_data,
                'stats': stats
            }
            
            self.indicators_info[indicator_code] = indicator_info
    
    def get_indicator_data(self, indicator_code: str, start_year: int = None, end_year: int = None):
        """Obtener datos de un indicador específico"""
        if indicator_code not in self.processed_data:
            return None
        
        indicator = self.processed_data[indicator_code]
        data = indicator['data'].copy()
        
        # Filtrar por años si se especifica
        if start_year:
            data = {year: value for year, value in data.items() if year >= start_year}
        if end_year:
            data = {year: value for year, value in data.items() if year <= end_year}
        
        return {
            'info': indicator['info'],
            'data': data,
            'stats': indicator['stats']
        }
    
    def get_all_years_data(self, indicator_code: str):
        """Obtener TODOS los datos históricos de un indicador"""
        if indicator_code not in self.processed_data:
            return None
        
        return self.processed_data[indicator_code]

class EcuadorAdvancedAssistant:
    """Asistente avanzado para datos económicos de Ecuador usando Claude"""
    
    def __init__(self, weo_processor: EcuadorWEOProcessor):
        self.weo_processor = weo_processor
        self.claude_client = None
        self.setup_claude()
    
    def setup_claude(self):
        """Configurar Claude AI"""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY') or st.secrets.get('ANTHROPIC_API_KEY')
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
            else:
                st.warning("⚠️ Claude API key no encontrada. Funcionará con respuestas básicas.")
        except Exception as e:
            st.error(f"Error configurando Claude: {e}")
    
    def generate_response(self, query: str, selected_indicator: str = None) -> str:
        """Generar respuesta usando Claude con TODOS los datos históricos"""
        
        # Determinar indicadores relevantes
        if selected_indicator:
            indicators_to_analyze = [selected_indicator]
        else:
            indicators_to_analyze = self.find_relevant_indicators(query)
        
        # Obtener datos COMPLETOS
        context_data = []
        for indicator_code in indicators_to_analyze:
            full_data = self.weo_processor.get_all_years_data(indicator_code)
            if full_data:
                context_data.append(full_data)
        
        if self.claude_client and context_data:
            return self.generate_claude_response_full(query, context_data)
        else:
            return self.generate_fallback_response(query, context_data)
    
    def find_relevant_indicators(self, query: str) -> List[str]:
        """Encontrar indicadores relevantes para la consulta"""
        query_lower = query.lower()
        
        # Mapeo mejorado de palabras clave
        keyword_mapping = {
            'pib': ['NGDP_RPCH', 'NGDP', 'NGDPD'],
            'gdp': ['NGDP_RPCH', 'NGDP', 'NGDPD'],
            'crecimiento': ['NGDP_RPCH'],
            'inflacion': ['PCPIPCH'],
            'desempleo': ['LUR'],
            'deuda': ['GGXWDG_NGDP'],
            'deficit': ['GGXCNL_NGDP'],
            'balanza': ['BCA_NGDPD'],
            'comercio': ['TX_RPCH', 'TM_RPCH'],
            'exportaciones': ['TX_RPCH'],
            'importaciones': ['TM_RPCH'],
            'poblacion': ['LP'],
            'per capita': ['NGDPRPC', 'NGDPDPC'],
            'dolarizacion': ['NGDP_RPCH', 'PCPIPCH']  # Indicadores clave para análisis de dolarización
        }
        
        relevant_codes = set()
        for keyword, codes in keyword_mapping.items():
            if keyword in query_lower:
                relevant_codes.update(codes)
        
        # Si no hay coincidencias específicas, usar indicadores principales
        if not relevant_codes:
            relevant_codes = ['NGDP_RPCH', 'PCPIPCH', 'LUR']
        
        return list(relevant_codes)[:3]  # Máximo 3 indicadores
    
    def generate_claude_response_full(self, query: str, context_data: List[Dict]) -> str:
        """Generar respuesta usando Claude con datos históricos COMPLETOS"""
        try:
            # Construir contexto con TODOS los datos históricos
            context = "DATOS ECONÓMICOS COMPLETOS DE ECUADOR (FMI - 1980-2030):\n\n"
            
            for indicator_data in context_data:
                info = indicator_data['info']
                stats = indicator_data['stats']
                data = indicator_data['data']
                
                # Incluir TODOS los datos por décadas para análisis histórico
                decades_summary = self.create_decades_summary(data)
                
                # Datos recientes y tendencias
                recent_years = sorted(data.keys(), reverse=True)[:10]
                recent_data = {year: data[year] for year in recent_years if year in data}
                
                # Datos históricos clave (dolarización, crisis, etc.)
                historical_periods = {
                    'Pre-dolarización (1995-1999)': {year: data[year] for year in range(1995, 2000) if year in data},
                    'Post-dolarización (2000-2005)': {year: data[year] for year in range(2000, 2006) if year in data},
                    'Boom commodities (2006-2014)': {year: data[year] for year in range(2006, 2015) if year in data},
                    'Crisis/Ajuste (2015-2020)': {year: data[year] for year in range(2015, 2021) if year in data},
                    'Recuperación (2021-2024)': {year: data[year] for year in range(2021, 2025) if year in data}
                }
                
                context += f"""
=== INDICADOR: {info['name']} ({indicator_data['info']['code']}) ===
Descripción: {info['description'][:300]}...
Unidades: {info['units']}

PERÍODO COMPLETO: {stats['first_year']}-{stats['last_year']} ({stats['data_points']} observaciones)

RESUMEN POR DÉCADAS:
{decades_summary}

PERÍODOS HISTÓRICOS CLAVE:
"""
                for period, period_data in historical_periods.items():
                    if period_data:
                        avg_value = np.mean(list(period_data.values()))
                        context += f"- {period}: Promedio {avg_value:.2f}\n"
                
                context += f"""
DATOS RECIENTES (últimos 10 años): {recent_data}

ESTADÍSTICAS GENERALES:
- Valor actual: {stats['latest_value']:.2f} ({stats['last_year']})
- Promedio histórico: {stats['mean_value']:.2f}
- Máximo histórico: {stats['max_value']:.2f} 
- Mínimo histórico: {stats['min_value']:.2f}

========================

"""
            
            prompt = f"""Eres un economista senior especializado en Ecuador con acceso COMPLETO a 45 años de datos históricos (1980-2030). 

CONTEXTO HISTÓRICO DISPONIBLE:
{context}

PREGUNTA DEL USUARIO: {query}

INSTRUCCIONES ESPECIALIZADAS:
1. Analiza TODA la serie histórica disponible (1980-2030)
2. Identifica períodos económicos clave (crisis 1999, dolarización 2000, boom commodities, etc.)
3. Proporciona datos específicos con años y cifras exactas
4. Compara diferentes períodos históricos cuando sea relevante
5. Explica causas económicas y contexto institucional
6. Usa terminología económica apropiada pero accesible
7. Incluye implicaciones para política económica cuando corresponda

FORMATO DE RESPUESTA:
📊 **Análisis Histórico Completo**
- Resumen ejecutivo con datos clave
- Tendencias históricas por períodos
- Comparaciones temporales específicas
- Contexto económico e interpretación
- Implicaciones y outlook

RESPUESTA:"""

            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            st.warning(f"Error con Claude API: {e}")
            return self.generate_fallback_response(query, context_data)
    
    def create_decades_summary(self, data: Dict[int, float]) -> str:
        """Crear resumen por décadas"""
        decades_data = {}
        for year, value in data.items():
            decade = (year // 10) * 10
            if decade not in decades_data:
                decades_data[decade] = []
            decades_data[decade].append(value)
        
        summary = ""
        for decade in sorted(decades_data.keys()):
            values = decades_data[decade]
            if len(values) >= 3:  # Solo décadas con datos suficientes
                avg_value = np.mean(values)
                summary += f"- {decade}s: {avg_value:.2f} promedio\n"
        
        return summary
    
    def generate_fallback_response(self, query: str, context_data: List[Dict]) -> str:
        """Respuesta de fallback mejorada"""
        if not context_data:
            return """📊 **Información no encontrada**

Para obtener análisis específicos, puedes preguntar sobre:
- **PIB y crecimiento económico** (incluye análisis pre/post dolarización)
- **Inflación y estabilidad de precios** 
- **Mercado laboral y desempleo**
- **Finanzas públicas y deuda**
- **Sector externo y balanza comercial**

*Datos disponibles: 1980-2030 | Fuente: FMI World Economic Outlook*"""
        
        # Análisis básico con datos completos
        indicator = context_data[0]
        info = indicator['info']
        stats = indicator['stats']
        data = indicator['data']
        
        # Períodos clave para análisis
        pre_dolar = {year: value for year, value in data.items() if 1995 <= year <= 1999}
        post_dolar = {year: value for year, value in data.items() if 2000 <= year <= 2005}
        recent = {year: value for year, value in data.items() if 2020 <= year <= 2024}
        
        response = f"""📊 **{info['name']}** 

**📈 Análisis Histórico Completo (1980-2030)**

**Valor actual ({stats['last_year']}):** {stats['latest_value']:.2f} {info['units']}

**🔍 Períodos clave:**"""
        
        if pre_dolar:
            avg_pre = np.mean(list(pre_dolar.values()))
            response += f"\n- **Pre-dolarización (1995-1999):** {avg_pre:.2f} promedio"
        
        if post_dolar:
            avg_post = np.mean(list(post_dolar.values()))
            response += f"\n- **Post-dolarización (2000-2005):** {avg_post:.2f} promedio"
        
        if recent:
            avg_recent = np.mean(list(recent.values()))
            response += f"\n- **Período reciente (2020-2024):** {avg_recent:.2f} promedio"
        
        response += f"""

**📊 Estadísticas históricas:**
- Período completo: {stats['first_year']}-{stats['last_year']} ({stats['data_points']} años)
- Promedio histórico: {stats['mean_value']:.2f}
- Máximo: {stats['max_value']:.2f} | Mínimo: {stats['min_value']:.2f}

**📝 Definición:** {info['description'][:200]}...

*Fuente: FMI World Economic Outlook | Sistema con acceso a datos históricos completos*"""
        
        return response

# Indicadores macroeconómicos principales
MACRO_INDICATORS = {
    'NGDP_RPCH': {
        'name': 'Crecimiento del PIB Real',
        'category': 'Actividad Económica',
        'icon': '📈'
    },
    'NGDP': {
        'name': 'PIB Nominal (Miles de millones USD)',
        'category': 'Actividad Económica', 
        'icon': '💰'
    },
    'NGDPDPC': {
        'name': 'PIB per cápita (USD)',
        'category': 'Actividad Económica',
        'icon': '👤'
    },
    'PCPIPCH': {
        'name': 'Inflación (Variación % anual)',
        'category': 'Precios y Estabilidad',
        'icon': '📊'
    },
    'LUR': {
        'name': 'Tasa de Desempleo (%)',
        'category': 'Mercado Laboral',
        'icon': '👥'
    },
    'BCA_NGDPD': {
        'name': 'Cuenta Corriente (% del PIB)',
        'category': 'Sector Externo',
        'icon': '🌍'
    },
    'GGXWDG_NGDP': {
        'name': 'Deuda Pública (% del PIB)',
        'category': 'Finanzas Públicas',
        'icon': '🏛️'
    },
    'GGXCNL_NGDP': {
        'name': 'Balance Fiscal (% del PIB)',
        'category': 'Finanzas Públicas',
        'icon': '⚖️'
    },
    'TX_RPCH': {
        'name': 'Crecimiento Exportaciones (%)',
        'category': 'Comercio Exterior',
        'icon': '📤'
    },
    'TM_RPCH': {
        'name': 'Crecimiento Importaciones (%)',
        'category': 'Comercio Exterior',
        'icon': '📥'
    },
    'LP': {
        'name': 'Población (Millones)',
        'category': 'Demografía',
        'icon': '🏘️'
    }
}

@st.cache_resource
def load_system():
    """Cargar sistema mejorado"""
    try:
        # Cargar datos WEO
        weo_data = load_weo_data()
        
        # Procesar datos
        weo_processor = EcuadorWEOProcessor(weo_data)
        
        # Crear asistente
        assistant = EcuadorAdvancedAssistant(weo_processor)
        
        return assistant, weo_processor
        
    except Exception as e:
        st.error(f"Error cargando sistema: {e}")
        return None, None

def create_enhanced_visualization(indicator_code: str, weo_processor: EcuadorWEOProcessor, start_year: int = 1980, end_year: int = 2030):
    """Crear visualización mejorada estilo CEPALSTAT"""
    try:
        data = weo_processor.get_indicator_data(indicator_code, start_year, end_year)
        if not data or not data['data']:
            return None, None
        
        years = list(data['data'].keys())
        values = list(data['data'].values())
        
        # Crear gráfico principal
        fig = go.Figure()
        
        # Línea principal
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            line=dict(color='#2a5298', width=3),
            marker=dict(size=6, color='#2a5298'),
            name=data['info']['name'],
            hovertemplate='<b>%{x}</b><br>%{y:.2f}<br><extra></extra>'
        ))
        
        # Marcar evento de dolarización si está en el período
        if 2000 in years:
            fig.add_vline(
                x=2000, 
                line_dash="dash", 
                line_color="red",
                annotation_text="Dolarización",
                annotation_position="top"
            )
        
        # Marcar crisis 2020 si está en el período
        if 2020 in years:
            fig.add_vline(
                x=2020, 
                line_dash="dash", 
                line_color="orange",
                annotation_text="COVID-19",
                annotation_position="top"
            )
        
        # Configuración del gráfico
        fig.update_layout(
            title={
                'text': f"{data['info']['name']}",
                'x': 0.02,
                'font': {'size': 16, 'color': '#2a5298'}
            },
            xaxis_title='Año',
            yaxis_title=f"{data['info']['units']}",
            template='plotly_white',
            height=500,
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        # Mejorar grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        return fig, data
        
    except Exception as e:
        st.error(f"Error creando visualización: {e}")
        return None, None

def create_excel_download(indicator_code: str, weo_processor: EcuadorWEOProcessor, start_year: int, end_year: int):
    """Crear archivo Excel para descarga"""
    try:
        data = weo_processor.get_indicator_data(indicator_code, start_year, end_year)
        if not data:
            return None
        
        # Crear DataFrame para Excel
        df = pd.DataFrame(list(data['data'].items()), columns=['Año', 'Valor'])
        df['Indicador'] = data['info']['name']
        df['Código'] = indicator_code
        df['Unidades'] = data['info']['units']
        
        # Convertir a Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Datos', index=False)
            
            # Agregar información adicional
            info_df = pd.DataFrame([
                ['Indicador', data['info']['name']],
                ['Código WEO', indicator_code],
                ['Descripción', data['info']['description'][:200] + '...'],
                ['Unidades', data['info']['units']],
                ['Período', f"{start_year}-{end_year}"],
                ['Fuente', 'FMI World Economic Outlook'],
                ['Fecha de descarga', datetime.now().strftime('%Y-%m-%d %H:%M')]
            ], columns=['Campo', 'Valor'])
            
            info_df.to_excel(writer, sheet_name='Metadatos', index=False)
        
        return output.getvalue()
        
    except Exception as e:
        st.error(f"Error generando Excel: {e}")
        return None

# Interfaz principal estilo CEPALSTAT
def main():
    """Función principal de la aplicación"""
    
    # Header principal estilo CEPALSTAT
    st.markdown("""
    <div class="main-header">
        <h1>🇪🇨 Ecuador Economic Data Assistant</h1>
        <p>Plataforma de análisis macroeconómico con datos oficiales del FMI | Powered by Claude AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar sistema
    assistant, weo_processor = load_system()
    
    if not assistant or not weo_processor:
        st.error("No se pudo cargar el sistema. Por favor, recarga la página.")
        return
    
    # Layout principal estilo CEPALSTAT
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        # Selector de indicadores
        st.markdown("""
        <div class="indicator-selector">
            <h3>📊 Indicadores Macroeconómicos</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Indicador principal
        indicator_options = list(MACRO_INDICATORS.keys())
        indicator_labels = [f"{MACRO_INDICATORS[code]['icon']} {MACRO_INDICATORS[code]['name']}" 
                          for code in indicator_options]
        
        selected_idx = st.selectbox(
            "Seleccionar indicador:",
            range(len(indicator_options)),
            format_func=lambda x: indicator_labels[x],
            key="main_indicator"
        )
        selected_indicator = indicator_options[selected_idx]
        
        # Control de período
        st.markdown("### 📅 Período de análisis")
        year_range = st.slider(
            "Seleccionar años:",
            min_value=1980,
            max_value=2030,
            value=(1995, 2024),
            step=1
        )
        
        # Mostrar información del indicador
        indicator_info = MACRO_INDICATORS[selected_indicator]
        st.markdown(f"""
        <div class="indicator-definition">
            <h4>{indicator_info['icon']} {indicator_info['name']}</h4>
            <p><strong>Categoría:</strong> {indicator_info['category']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Estadísticas rápidas
        if selected_indicator:
            data = weo_processor.get_indicator_data(selected_indicator, year_range[0], year_range[1])
            if data:
                stats = data['stats']
                st.markdown("### 📈 Estadísticas del período")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Valor actual", f"{stats['latest_value']:.2f}", 
                             delta=f"{stats['latest_value'] - stats['mean_value']:.2f}")
                with col_b:
                    st.metric("Promedio", f"{stats['mean_value']:.2f}")
                
                col_c, col_d = st.columns(2)
                with col_c:
                    st.metric("Máximo", f"{stats['max_value']:.2f}")
                with col_d:
                    st.metric("Mínimo", f"{stats['min_value']:.2f}")
    
    with col_right:
        # Gráfico principal
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if selected_indicator:
            fig, chart_data = create_enhanced_visualization(
                selected_indicator, 
                weo_processor, 
                year_range[0], 
                year_range[1]
            )
            
            if fig and chart_data:
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # Definición detallada del indicador
                info = chart_data['info']
                st.markdown(f"""
                <div class="indicator-definition">
                    <h4>📋 Definición técnica</h4>
                    <p><strong>Descripción:</strong> {info['description'][:300]}...</p>
                    <p><strong>Unidades:</strong> {info['units']} | <strong>Escala:</strong> {info['scale']}</p>
                    <p><strong>Fuente:</strong> FMI World Economic Outlook Database</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Sección de descarga
                st.markdown('<div class="download-section">', unsafe_allow_html=True)
                st.markdown("### 📥 Descargar datos")
                
                excel_data = create_excel_download(selected_indicator, weo_processor, year_range[0], year_range[1])
                if excel_data:
                    st.download_button(
                        label="📊 Descargar Excel",
                        data=excel_data,
                        file_name=f"ecuador_{selected_indicator}_{year_range[0]}_{year_range[1]}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección de chat con IA (ancho completo)
    st.markdown('<div class="chat-section">', unsafe_allow_html=True)
    st.markdown("## 🤖 Consultas al Asistente Económico")
    st.markdown("*Pregunta sobre cualquier aspecto de la economía ecuatoriana. Tengo acceso a 45 años de datos históricos (1980-2030).*")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mostrar mensajes del chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("Ejemplo: ¿Cómo afectó la dolarización al crecimiento del PIB?"):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner("Analizando datos históricos completos..."):
                # Generar respuesta con contexto del indicador actual
                response = assistant.generate_response(prompt, selected_indicator)
                st.markdown(response)
                
                # Agregar respuesta al historial
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p><strong>Ecuador Economic Data Assistant</strong> | FMI World Economic Outlook Database | Powered by Claude AI</p>
        <p>Datos históricos completos: 1980-2030 | Última actualización: Octubre 2024</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()