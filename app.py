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

# CSS personalizado para mejor apariencia
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    
    .assistant-message {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        margin-right: 20%;
    }
    
    .sidebar-info {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #2a5298;
        margin: 1rem 0;
    }
    
    .indicator-chip {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        border: 1px solid #bbdefb;
    }
    
    .highlight-stat {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_weo_data():
    """Cargar datos WEO desde el documento"""
    
    # Datos WEO completos de Ecuador (tu paste)
    weo_raw_data = """WEO Country Code	ISO	WEO Subject Code	Country	Subject Descriptor	Subject Notes	Units	Scale	Country/Series-specific Notes	1980	1981	1982	1983	1984	1985	1986	1987	1988	1989	1990	1991	1992	1993	1994	1995	1996	1997	1998	1999	2000	2001	2002	2003	2004	2005	2006	2007	2008	2009	2010	2011	2012	2013	2014	2015	2016	2017	2018	2019	2020	2021	2022	2023	2024	2025	2026	2027	2028	2029	2030	Estimates Start After
248	ECU	NGDP_R	Ecuador	Gross domestic product, constant prices	Expressed in billions of national currency units; the base year is country-specific. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]	National currency	Billions	Source: Central Bank Latest actual data: 2023 Notes: The national accounts have been updated from 2002 onwards. Prior to 2002 the data are adjusted to produce smooth series with the use of splicing technique. These estimates continue to serve as proxies for historical series when complete information is una National accounts manual used: System of National Accounts (SNA) 2008 GDP valuation: Market prices Reporting in calendar year: Yes Start/end months of reporting year: January/December Base year: 2018 Chain-weighted: Yes, from 2018 Primary domestic currency: US dollar Data last updated: 04/10/2025	33.922	35.245	35.668	34.669	36.125	37.715	38.882	36.56	40.393	40.508	41.727	43.86	45.445	46.354	48.328	49.417	50.273	52.448	54.162	51.595	52.158	54.352	57.03	58.676	62.684	66.069	68.937	70.248	74.86	75.677	78.726	85.403	90.342	96.857	100.95	101.071	100.375	106.368	107.479	107.657	97.704	106.909	113.183	115.434	113.172	115.126	117.563	120.261	123.265	126.376	129.513	2023
248	ECU	NGDP_RPCH	Ecuador	Gross domestic product, constant prices	Annual percentages of constant price GDP are year-on-year changes; the base year is country-specific. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]	Percent change	Units	See notes for:  Gross domestic product, constant prices (National currency).	4.9	3.9	1.2	-2.8	4.2	4.4	3.094	-5.972	10.486	0.285	3.008	5.113	3.614	2	4.258	2.253	1.732	4.328	3.267	-4.739	1.092	4.206	4.928	2.885	6.832	5.399	4.341	1.902	6.565	1.091	4.029	8.481	5.783	7.211	4.226	0.12	-0.688	5.97	1.044	0.165	-9.245	9.422	5.868	1.988	-1.959	1.727	2.117	2.295	2.498	2.524	2.482	2023
248	ECU	NGDP	Ecuador	Gross domestic product, current prices	Expressed in billions of national currency units. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]	National currency	Billions	Source: Central Bank Latest actual data: 2023 Notes: The national accounts have been updated from 2002 onwards. Prior to 2002 the data are adjusted to produce smooth series with the use of splicing technique. These estimates continue to serve as proxies for historical series when complete information is una National accounts manual used: System of National Accounts (SNA) 2008 GDP valuation: Market prices Reporting in calendar year: Yes Start/end months of reporting year: January/December Base year: 2018 Chain-weighted: Yes, from 2018 Primary domestic currency: US dollar Data last updated: 04/10/2025	16.116	16.501	16.474	14.478	15.408	18.02	13.222	12.355	11.749	11.531	11.71	13.139	14.367	16.783	20.238	21.98	23.001	25.847	26.292	18.891	17.531	23.127	27.054	30.965	35.195	40.279	45.691	49.849	61.139	60.095	68.151	78.987	87.735	96.57	102.718	97.21	97.671	104.467	107.479	107.596	95.865	107.179	116.133	121.147	121.728	125.677	130.31	135.35	140.863	146.638	152.588	2023
248	ECU	NGDPD	Ecuador	Gross domestic product, current prices	Values are based upon GDP in national currency converted to U.S. dollars using market exchange rates (yearly average). Exchange rate projections are provided by country economists for the group of other emerging market and developing countries. Exchanges rates for advanced economies are established in the WEO assumptions for each WEO exercise. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]	U.S. dollars	Billions	See notes for:  Gross domestic product, current prices (National currency).	16.116	16.501	16.474	14.478	15.408	18.02	13.222	12.355	11.749	11.531	11.71	13.139	14.367	16.783	20.238	21.98	23.001	25.847	26.292	18.891	17.531	23.127	27.054	30.965	35.195	40.279	45.691	49.849	61.139	60.095	68.151	78.987	87.735	96.57	102.718	97.21	97.671	104.467	107.479	107.596	95.865	107.179	116.133	121.147	121.728	125.677	130.31	135.35	140.863	146.638	152.588	2023
248	ECU	PPPGDP	Ecuador	Gross domestic product, current prices	These data form the basis for the country weights used to generate the World Economic Outlook country group composites for the domestic economy.   The IMF is not a primary source for purchasing power parity (PPP) data. WEO weights have been created from primary sources and are used solely for purposes of generating country group composites. For primary source information, please refer to one of the following sources: the Organization for Economic Cooperation and Development, the World Bank, or the Penn World Tables.  For further information see Box A2 in the Statistical Appendix of the October 2024 WEO, Box 1.1 in the October 2020 World Economic Outlook, "Revised Purchasing Power Parity Weights" in the July 2014 WEO Update, Box A2 in the April 2004 World Economic Outlook, Box A1 in the May 2000 World Economic Outlook, and Annex IV in the May 1993 World Economic Outlook for summaries of the revised PPP-based weights; and Box 1.2 in the September 2003 World Economic Outlook for a discussion on the measurement of global growth. See also Anne Marie Gulde and Marianne Schulze-Ghattas, Purchasing Power Parity Based Weights for the World Economic Outlook, in Staff Studies for the World Economic Outlook (Washington: IMF, December 1993), pp. 106-23.	Purchasing power parity; international dollars	Billions	See notes for:  Gross domestic product, current prices (National currency).	24.818	28.225	30.329	30.634	33.073	35.62	37.461	36.097	41.288	43.029	45.982	49.968	52.954	55.294	58.879	61.468	63.677	67.578	70.57	68.177	70.482	75.101	80.026	83.96	92.109	100.126	107.694	112.716	122.43	124.529	131.12	145.176	156.431	170.567	180.871	182.768	183.236	197.653	207.781	217.496	202.25	238.845	270.889	286.217	287.394	300.122	313.172	326.256	341.379	356.403	372.087	2023
248	ECU	NGDP_D	Ecuador	Gross domestic product, deflator	The GDP deflator is derived by dividing current price GDP by constant price GDP and is considered to be an alternate measure of inflation. Data are expressed in the base year of each country's national accounts.	Index	Units	See notes for:  Gross domestic product, constant prices (National currency) Gross domestic product, current prices (National currency).	47.509	46.819	46.186	41.762	42.652	47.778	34.006	33.793	29.087	28.465	28.063	29.957	31.613	36.206	41.876	44.479	45.753	49.281	48.543	36.614	33.611	42.551	47.438	52.774	56.146	60.965	66.279	70.961	81.672	79.41	86.568	92.487	97.115	99.704	101.751	96.18	97.306	98.213	100	99.943	98.119	100.252	102.606	104.95	107.56	109.165	110.843	112.547	114.276	116.033	117.816	2023
248	ECU	NGDPRPC	Ecuador	Gross domestic product per capita, constant prices	GDP is expressed in constant national currency per person. Data are derived by dividing constant price GDP by total population.	National currency	Units	See notes for:  Gross domestic product, constant prices (National currency) Population (Persons).	4,241.50	4,283.97	4,215.72	3,986.22	4,043.16	4,111.31	4,130.84	3,787.82	4,078.70	3,991.73	4,016.82	4,126.78	4,181.43	4,174.22	4,264.06	4,278.14	4,278.23	4,393.32	4,469.23	4,195.68	4,179.14	4,285.97	4,420.74	4,468.22	4,689.64	4,856.43	4,976.53	4,979.74	5,213.41	5,177.52	5,289.41	5,633.21	5,850.95	6,162.34	6,311.59	6,212.41	6,071.48	6,334.15	6,293.46	6,202.54	5,574.65	6,069.43	6,389.01	6,472.37	6,299.03	6,359.26	6,443.97	6,540.91	6,652.50	6,768.04	6,883.33	2022
248	ECU	NGDPRPPPPC	Ecuador	Gross domestic product per capita, constant prices	GDP is expressed in constant international dollars per person. Data are derived by dividing constant price purchasing-power parity (PPP) GDP by total population.	Purchasing power parity; 2021 international dollar	Units	See notes for:  Gross domestic product, constant prices (National currency) Population (Persons).	9,475.89	9,570.76	9,418.29	8,905.57	9,032.77	9,185.02	9,228.65	8,462.32	9,112.18	8,917.88	8,973.93	9,219.58	9,341.69	9,325.57	9,526.27	9,557.73	9,557.95	9,815.05	9,984.64	9,373.52	9,336.56	9,575.23	9,876.32	9,982.39	10,477.06	10,849.69	11,118.00	11,125.18	11,647.22	11,567.02	11,817.00	12,585.09	13,071.53	13,767.20	14,100.64	13,879.06	13,564.22	14,151.05	14,060.14	13,857.02	12,454.25	13,559.63	14,273.60	14,459.83	14,072.58	14,207.15	14,396.40	14,612.98	14,862.27	15,120.40	15,377.96	2022
248	ECU	NGDPPC	Ecuador	Gross domestic product per capita, current prices	GDP is expressed in current national currency per person. Data are derived by dividing current price GDP by total population.	National currency	Units	See notes for:  Gross domestic product, current prices (National currency) Population (Persons).	2,015.08	2,005.71	1,947.09	1,664.71	1,724.51	1,964.32	1,404.72	1,280.02	1,186.36	1,136.26	1,127.22	1,236.27	1,321.88	1,511.30	1,785.61	1,902.88	1,957.42	2,165.07	2,169.51	1,536.21	1,404.64	1,823.70	2,097.12	2,358.04	2,633.05	2,960.73	3,298.41	3,533.67	4,257.89	4,111.48	4,578.94	5,210.00	5,682.12	6,144.12	6,422.12	5,975.08	5,907.93	6,220.97	6,293.46	6,199.03	5,469.76	6,084.74	6,555.53	6,792.72	6,775.26	6,942.10	7,142.69	7,361.58	7,602.24	7,853.16	8,109.68	2022
248	ECU	NGDPDPC	Ecuador	Gross domestic product per capita, current prices	GDP is expressed in current U.S. dollars per person. Data are derived by first converting GDP in national currency to U.S. dollars and then dividing it by total population.	U.S. dollars	Units	See notes for:  Gross domestic product, current prices (National currency) Population (Persons).	2,015.08	2,005.71	1,947.09	1,664.71	1,724.51	1,964.32	1,404.72	1,280.02	1,186.36	1,136.26	1,127.22	1,236.27	1,321.88	1,511.30	1,785.61	1,902.88	1,957.42	2,165.07	2,169.51	1,536.21	1,404.64	1,823.70	2,097.12	2,358.04	2,633.05	2,960.73	3,298.41	3,533.67	4,257.89	4,111.48	4,578.94	5,210.00	5,682.12	6,144.12	6,422.12	5,975.08	5,907.93	6,220.97	6,293.46	6,199.03	5,469.76	6,084.74	6,555.53	6,792.72	6,775.26	6,942.10	7,142.69	7,361.58	7,602.24	7,853.16	8,109.68	2022
248	ECU	PPPPC	Ecuador	Gross domestic product per capita, current prices	Expressed in GDP in PPP dollars per person. Data are derived by dividing GDP in PPP dollars by total population. These data form the basis for the country weights used to generate the World Economic Outlook country group composites for the domestic economy.   The IMF is not a primary source for purchasing power parity (PPP) data. WEO weights have been created from primary sources and are used solely for purposes of generating country group composites. For primary source information, please refer to one of the following sources: the Organization for Economic Cooperation and Development, the World Bank, or the Penn World Tables.  For further information see Box A2 in the Statistical Appendix of the October 2024 WEO, Box 1.1 in the October 2020 World Economic Outlook, "Revised Purchasing Power Parity Weights" in the July 2014 WEO Update, Box A2 in the April 2004 World Economic Outlook, Box A1 in the May 2000 World Economic Outlook, and Annex IV in the May 1993 World Economic Outlook for summaries of the revised PPP-based weights; and Box 1.2 in the September 2003 World Economic Outlook for a discussion on the measurement of global growth. See also Anne Marie Gulde and Marianne Schulze-Ghattas, Purchasing Power Parity Based Weights for the World Economic Outlook, in Staff Studies for the World Economic Outlook (Washington: IMF, December 1993), pp. 106-23.	Purchasing power parity; international dollars	Units	See notes for:  Gross domestic product, current prices (National currency) Population (Persons).	3,103.09	3,430.69	3,584.65	3,522.24	3,701.49	3,882.90	3,979.89	3,739.84	4,169.06	4,240.16	4,426.49	4,701.48	4,872.32	4,979.18	5,194.97	5,321.39	5,418.94	5,660.66	5,823.20	5,544.13	5,647.37	5,922.14	6,203.28	6,393.69	6,890.96	7,359.82	7,774.40	7,990.19	8,526.28	8,519.79	8,809.69	9,575.90	10,131.21	10,852.01	11,308.43	11,234.03	11,083.52	11,770.11	12,166.66	12,530.83	11,539.70	13,559.63	15,291.23	16,048.18	15,996.06	16,577.99	17,165.95	17,744.83	18,423.92	19,087.09	19,775.55	2022
248	ECU	NGAP_NPGDP	Ecuador	Output gap in percent of potential GDP	Output gaps for advanced economies are calculated as actual GDP less potential GDP as a percent of potential GDP. Estimates of output gaps are subject to a significant margin of uncertainty. For a discussion of approaches to calculating potential output, see Paula R. De Masi, IMF Estimates of Potential Output: Theory and Practice, in Staff Studies for the World Economic Outlook (Washington: IMF, December 1997), pp. 40-46.	Percent of potential GDP	Units																																																					
248	ECU	PPPSH	Ecuador	Gross domestic product based on purchasing-power-parity (PPP) share of world total	Expressed in percent of world GDP in PPP dollars. These data form the basis for the country weights used to generate the World Economic Outlook country group composites for the domestic economy.   The IMF is not a primary source for purchasing power parity (PPP) data. WEO weights have been created from primary sources and are used solely for purposes of generating country group composites. For primary source information, please refer to one of the following sources: the Organization for Economic Cooperation and Development, the World Bank, or the Penn World Tables.  For further information see Box A2 in the Statistical Appendix of the October 2024 WEO, Box 1.1 in the October 2020 World Economic Outlook, "Revised Purchasing Power Parity Weights" in the July 2014 WEO Update, Box A2 in the April 2004 World Economic Outlook, Box A1 in the May 2000 World Economic Outlook, and Annex IV in the May 1993 World Economic Outlook for summaries of the revised PPP-based weights; and Box 1.2 in the September 2003 World Economic Outlook for a discussion on the measurement of global growth. See also Anne Marie Gulde and Marianne Schulze-Ghattas, Purchasing Power Parity Based Weights for the World Economic Outlook, in Staff Studies for the World Economic Outlook (Washington: IMF, December 1993), pp. 106-23.	Percent	Units	See notes for:  Gross domestic product, current prices (National currency).	0.188	0.191	0.192	0.182	0.182	0.183	0.183	0.165	0.175	0.17	0.168	0.173	0.161	0.161	0.163	0.161	0.158	0.158	0.159	0.146	0.141	0.143	0.146	0.145	0.148	0.149	0.147	0.143	0.148	0.151	0.149	0.156	0.16	0.166	0.167	0.162	0.156	0.159	0.157	0.155	0.145	0.153	0.156	0.154	0.147	0.145	0.144	0.143	0.142	0.141	0.14	2023
248	ECU	PPPEX	Ecuador	Implied PPP conversion rate	Expressed in national currency per current international dollar. These data form the basis for the country weights used to generate the World Economic Outlook country group composites for the domestic economy.   The IMF is not a primary source for purchasing power parity (PPP) data. WEO weights have been created from primary sources and are used solely for purposes of generating country group composites. For primary source information, please refer to one of the following sources: the Organization for Economic Cooperation and Development, the World Bank, or the Penn World Tables.  For further information see Box A2 in the Statistical Appendix of the October 2024 WEO, Box 1.1 in the October 2020 World Economic Outlook, "Revised Purchasing Power Parity Weights" in the July 2014 WEO Update, Box A2 in the April 2004 World Economic Outlook, Box A1 in the May 2000 World Economic Outlook, and Annex IV in the May 1993 World Economic Outlook for summaries of the revised PPP-based weights; and Box 1.2 in the September 2003 World Economic Outlook for a discussion on the measurement of global growth. See also Anne Marie Gulde and Marianne Schulze-Ghattas, Purchasing Power Parity Based Weights for the World Economic Outlook, in Staff Studies for the World Economic Outlook (Washington: IMF, December 1993), pp. 106-23.	National currency per current international dollar	Units	See notes for:  Gross domestic product, current prices (National currency).	0.649	0.585	0.543	0.473	0.466	0.506	0.353	0.342	0.285	0.268	0.255	0.263	0.271	0.304	0.344	0.358	0.361	0.382	0.373	0.277	0.249	0.308	0.338	0.369	0.382	0.402	0.424	0.442	0.499	0.483	0.52	0.544	0.561	0.566	0.568	0.532	0.533	0.529	0.517	0.495	0.474	0.449	0.429	0.423	0.424	0.419	0.416	0.415	0.413	0.411	0.41	2023
248	ECU	NID_NGDP	Ecuador	Total investment	Expressed as a ratio of total investment in current local currency and GDP in current local currency. Investment or gross capital formation is measured by the total value of the gross fixed capital formation and changes in inventories and acquisitions less disposals of valuables for a unit or sector. [SNA 1993]	Percent of GDP	Units	Source: Central Bank Latest actual data: 2023 Notes: The national accounts have been updated from 2002 onwards. Prior to 2002 the data are adjusted to produce smooth series with the use of splicing technique. These estimates continue to serve as proxies for historical series when complete information is una National accounts manual used: System of National Accounts (SNA) 2008 GDP valuation: Market prices Reporting in calendar year: Yes Start/end months of reporting year: January/December Base year: 2018 Chain-weighted: Yes, from 2018 Primary domestic currency: US dollar Data last updated: 04/10/2025	16.428	15.81	18.279	11.613	11.912	13.119	14.084	14.465	13.941	13.398	11.389	15.107	14.393	15.714	15.098	13.938	12.498	14.726	18.489	12.779	17.167	18.491	19.656	15.773	16.25	17.465	18.118	18.318	21.566	21.173	23.49	23.532	23.013	24.883	24.706	22.686	20.246	22.48	22.54	21.049	17.585	20.748	22.406	20.651	18.165	20.606	21.69	22.126	22.533	22.847	23.192	2023
248	ECU	NGSD_NGDP	Ecuador	Gross national savings	Expressed as a ratio of gross national savings in current local currency and GDP in current local currency. Gross national saving is gross disposable income less final consumption expenditure after taking account of an adjustment for pension funds. [SNA 1993] For many countries, the estimates of national saving are built up from national accounts data on gross domestic investment and from balance of payments-based data on net foreign investment.	Percent of GDP	Units	Source: Central Bank Latest actual data: 2023 Notes: The national accounts have been updated from 2002 onwards. Prior to 2002 the data are adjusted to produce smooth series with the use of splicing technique. These estimates continue to serve as proxies for historical series when complete information is una National accounts manual used: System of National Accounts (SNA) 2008 GDP valuation: Market prices Reporting in calendar year: Yes Start/end months of reporting year: January/December Base year: 2018 Chain-weighted: Yes, from 2018 Primary domestic currency: US dollar Data last updated: 04/10/2025	17.947	15.407	17.254	14.726	14.05	17.977	14.629	10.954	14.389	13.369	12.742	14.496	17.703	16.109	15.731	13.467	16.537	16.242	14.012	20.86	23.514	16.108	15.15	14.524	14.888	18.641	21.926	22.102	24.46	21.694	21.168	23.026	22.846	23.917	24.055	20.402	21.168	22.092	21.006	20.542	19.676	23.489	24.245	22.481	23.983	24.029	24.321	24.619	25.049	25.386	25.687	2023
248	ECU	PCPI	Ecuador	Inflation, average consumer prices	Expressed in averages for the year, not end-of-period data. A consumer price index (CPI) measures changes in the prices of goods and services that households consume. Such changes affect the real purchasing power of consumers' incomes and their welfare. As the prices of different goods and services do not all change at the same rate, a price index can only reflect their average movement. A price index is typically assigned a value of unity, or 100, in some reference period and the values of the index for other periods of time are intended to indicate the average proportionate, or percentage, change in prices from this price reference period. Price indices can also be used to measure differences in price levels between different cities, regions or countries at the same point in time. [CPI Manual 2004, Introduction] For euro countries, consumer prices are calculated based on harmonized prices. For more information see http://epp.eurostat.ec.europa.eu/cache/ITY_OFFPUB/KS-BE-04-001/EN/KS-BE-04-001-EN.PDF.]	Index	Units	Source: National Statistics Office. Source: INEC and Central Bank Latest actual data: 2024 Notes: The price Ecuador receives for its oil exports is subject to effects of marketing and discounts for the quality of the Ecuadorian mix. These effects are variable over time. Therefore, while the price of Ecuadorian oil moves in tandem with world prices, de Harmonized prices: No Base year: 2014. The authorities introduced the series with base in 2014 in 2015 and presents data for this year onwards. Prior years are obtained by splicing the series backwards with the old CPI series. As a result, the base year is different from 100. Primary domestic currency: US dollar Data last updated: 04/10/2025	0.051	0.059	0.069	0.102	0.134	0.172	0.211	0.273	0.432	0.76	1.128	1.679	2.591	3.757	4.788	5.884	7.32	9.56	13.011	19.803	38.833	53.463	60.138	64.907	66.686	68.133	70.38	71.982	78.029	82.055	84.972	88.774	93.303	95.842	99.282	103.22	105.004	105.442	105.206	105.486	105.129	105.269	108.917	111.331	113.053	114.564	116.237	118.022	119.834	121.675	123.543	2024
248	ECU	PCPIPCH	Ecuador	Inflation, average consumer prices	Annual percentages of average consumer prices are year-on-year changes.	Percent change	Units	See notes for:  Inflation, average consumer prices (Index).	13.049	16.387	16.258	48.434	31.23	27.983	23.03	29.504	58.216	75.648	48.519	48.804	54.341	45	27.443	22.886	24.4	30.6	36.1	52.2	96.1	37.674	12.485	7.929	2.741	2.17	3.299	2.276	8.4	5.16	3.554	4.475	5.102	2.722	3.589	3.966	1.728	0.417	-0.224	0.266	-0.339	0.133	3.466	2.216	1.547	1.337	1.461	1.536	1.536	1.536	1.536	2024
248	ECU	PCPIE	Ecuador	Inflation, end of period consumer prices	Expressed in end of the period, not annual average data. A consumer price index (CPI) measures changes in the prices of goods and services that households consume. Such changes affect the real purchasing power of consumers' incomes and their welfare. As the prices of different goods and services do not all change at the same rate, a price index can only reflect their average movement. A price index is typically assigned a value of unity, or 100, in some reference period and the values of the index for other periods of time are intended to indicate the average proportionate, or percentage, change in prices from this price reference period. Price indices can also be used to measure differences in price levels between different cities, regions or countries at the same point in time. [CPI Manual 2004, Introduction] For euro countries, consumer prices are calculated based on harmonized prices. For more information see http://epp.eurostat.ec.europa.eu/cache/ITY_OFFPUB/KS-BE-04-001/EN/KS-BE-04-001-EN.PDF.	Index	Units	Source: National Statistics Office. Source: INEC and Central Bank Latest actual data: 2024 Notes: The price Ecuador receives for its oil exports is subject to effects of marketing and discounts for the quality of the Ecuadorian mix. These effects are variable over time. Therefore, while the price of Ecuadorian oil moves in tandem with world prices, de Harmonized prices: No Base year: 2014. The authorities introduced the series with base in 2014 in 2015 and presents data for this year onwards. Prior years are obtained by splicing the series backwards with the old CPI series. As a result, the base year is different from 100. Primary domestic currency: US dollar Data last updated: 04/10/2025	0.053	0.062	0.077	0.118	0.147	0.183	0.233	0.308	0.573	0.883	1.32	1.967	3.152	4.16	5.217	6.405	8.039	10.508	15.068	24.214	46.25	56.62	61.92	65.68	66.96	69.057	71.038	73.396	79.878	83.322	86.095	90.752	94.531	97.084	100.644	104.046	105.211	105.004	105.283	105.215	104.233	106.256	110.227	111.715	112.306	116.092	117.825	119.54	121.281	123.047	124.838	2024
248	ECU	PCPIEPCH	Ecuador	Inflation, end of period consumer prices	Annual percentages of end of period consumer prices are year-on-year changes.	Percent change	Units	See notes for:  Inflation, end of period consumer prices (Index).	13.53	17.3	24.4	52.5	25.1	24.4	27.3	32.5	85.7	54.2	49.5	49	60.2	32	25.383	22.774	25.527	30.7	43.4	60.7	91.005	22.422	9.361	6.072	1.949	3.132	2.869	3.319	8.832	4.312	3.328	5.409	4.164	2.701	3.667	3.38	1.12	-0.197	0.266	-0.065	-0.933	1.941	3.737	1.35	0.529	3.371	1.493	1.456	1.456	1.456	1.456	2024
248	ECU	TM_RPCH	Ecuador	Volume of imports of goods and services	Percent change of volume of imports refers to the aggregate change in the quantities of total imports whose characteristics are unchanged. The goods and services and their prices are held constant, therefore changes are due to changes in quantities only. [Export and Import Price Index Manual: Theory and Practice, Glossary]	Percent change	Units	Source: Central Bank Latest actual data: 2024 Base year: 2014 Methodology used to derive volumes: Deflation by unit value indexes (from customs data) Formula used to derive volumes: Laspeyres-type Chain-weighted: No. Last updated in 2014 Trade System: General trade Oil coverage: Primary or unrefined products; Secondary or refined products Valuation of exports: Free on board (FOB) Valuation of imports: Free on board (FOB) Primary domestic currency: US dollar Data last updated: 04/10/2025	-1.061	5.244	-4.988	-33.125	9.195	5.857	-7.484	9.719	-23.134	3.39	-0.839	16	1	0.8	14.636	7.949	-12.597	20.513	6.532	-31.595	12.822	25.722	19.015	-4.06	10.877	13.162	7.038	6.175	13.009	-6.852	12.483	2.598	0.214	8.16	4.687	-4.79	-11.405	16.627	3.978	0.359	-17.08	18.984	10.016	2.555	-3.279	5.166	3.974	3.885	4.538	5.816	5.466	2024
248	ECU	TMG_RPCH	Ecuador	Volume of Imports of goods	Percent change of volume of imports of goods refers to the aggregate change in the quantities of imports of goods whose characteristics are unchanged. The goods and their prices are held constant, therefore changes are due to changes in quantities only. [Export and Import Price Index Manual: Theory and Practice, Glossary]	Percent change	Units	Source: Central Bank Latest actual data: 2024 Base year: 2014 Methodology used to derive volumes: Deflation by unit value indexes (from customs data) Formula used to derive volumes: Laspeyres-type Chain-weighted: No. Last updated in 2014 Trade System: General trade Oil coverage: Primary or unrefined products; Secondary or refined products Valuation of exports: Free on board (FOB) Valuation of imports: Free on board (FOB) Primary domestic currency: US dollar Data last updated: 04/10/2025	-6.343	6.202	-4.486	-33.245	11.225	5.889	-9.235	20.703	-27.399	5.141	-1.442	28.659	-7.932	20.722	29.253	16.223	5.454	-13.509	-8.869	-13.172	19.133	21.488	-2.691	-3.714	8.988	14.18	6.976	6.003	12.734	-5.821	12.374	2.437	0.208	8.351	5.306	-4.076	-15.27	19.652	3.289	-0.093	-14.862	16.628	7.081	3.777	-3.215	4.939	4.368	4.144	4.831	5.976	5.595	2024
248	ECU	TX_RPCH	Ecuador	Volume of exports of goods and services	Percent change of volume of exports refers to the aggregate change in the quantities of total exports whose characteristics are unchanged. The goods and services and their prices are held constant, therefore changes are due to changes in quantities only. [Export and Import Price Index Manual: Theory and Practice, Glossary]	Percent change	Units	Source: Central Bank Latest actual data: 2024 Base year: 2014 Methodology used to derive volumes: Deflation by unit value indexes (from customs data) Formula used to derive volumes: Laspeyres-type Chain-weighted: No. Last updated in 2014 Trade System: General trade Oil coverage: Primary or unrefined products; Secondary or refined products Valuation of exports: Free on board (FOB) Valuation of imports: Free on board (FOB) Primary domestic currency: US dollar Data last updated: 04/10/2025	-1.855	6.362	-3.783	10.062	3.346	13.813	3.963	-15.791	22.953	-3.83	3.104	10.5	9.6	4.2	11.684	11.26	-2.123	6.986	-4.737	7.631	2.536	-1.587	0.624	7.21	17.178	7.521	4.992	-1.958	2.99	-1.762	-0.413	3.891	4.815	5.109	6.525	2.867	-0.142	3.207	0.951	6.915	1.736	7.44	5.521	6.74	4.817	-1.457	4.695	4.17	4.978	5.251	4.999	2024
248	ECU	TXG_RPCH	Ecuador	Volume of exports of goods	Percent change of volume of exports of goods refers to the aggregate change in the quantities of exports of goods whose characteristics are unchanged. The goods and their prices are held constant, therefore changes are due to changes in quantities only. [Export and Import Price Index Manual: Theory and Practice, Glossary]	Percent change	Units	Source: Central Bank Latest actual data: 2024 Base year: 2014 Methodology used to derive volumes: Deflation by unit value indexes (from customs data) Formula used to derive volumes: Laspeyres-type Chain-weighted: No. Last updated in 2014 Trade System: General trade Oil coverage: Primary or unrefined products; Secondary or refined products Valuation of exports: Free on board (FOB) Valuation of imports: Free on board (FOB) Primary domestic currency: US dollar Data last updated: 04/10/2025	-5.449	6.82	-1.63	15.8	7.066	10.309	2.817	-17.48	27.88	-6.546	4.189	14.298	6.342	13.371	13.783	11.357	-0.783	4.546	-5.339	1.295	2.923	1.052	-1.939	10.174	15.364	8.27	5.355	-2.94	2.402	-0.937	-0.906	3.946	4.56	4.706	6.153	3.295	-1.273	2.783	-0.146	7.596	6.108	7.05	2.774	5.91	6.489	-1.454	4.952	4.298	5.134	5.613	5.33	2024
248	ECU	LUR	Ecuador	Unemployment rate	Unemployment rate can be defined by either the national definition, the ILO harmonized definition, or the OECD harmonized definition. The OECD harmonized unemployment rate gives the number of unemployed persons as a percentage of the labor force (the total number of people employed plus unemployed). [OECD Main Economic Indicators, OECD, monthly] As defined by the International Labour Organization, unemployed workers are those who are currently not working but are willing and able to work for pay, currently available to work, and have actively searched for work. [ILO, http://www.ilo.org/public/english/bureau/stat/res/index.htm]	Percent of total labor force	Units	Source: National Statistics Office. Source: INEC and Central Bank Latest actual data: 2024 Employment type: National definition Primary domestic currency: US dollar Data last updated: 04/10/2025	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	7	7.9	6.1	8.5	8.9	8.3	5.696	5.493	9.046	7.828	10.163	13.107	7.625	9.554	7.828	10.163	7.219	7.095	6.687	6.923	5.95	6.47	5.02	4.21	4.12	4.15	3.8	4.77	5.21	4.62	3.69	3.84	5.346	4.68	3.8	3.57	3.38	4	3.8	3.6	3.5	3.5	3.5	2024
248	ECU	LE	Ecuador	Employment	Employment can be defined by either the national definition, the ILO harmonized definition, or the OECD harmonized definition. Persons who during a specified brief period such as one week or one day, (a) performed some work for wage or salary in cash or in kind, (b) had a formal attachment to their job but were temporarily not at work during the reference period, (c) performed some work for profit or family gain in cash or in kind, (d) were with an enterprise such as a business, farm or service but who were temporarily not at work during the reference period for any specific reason. [Current International Recommendations on Labour Statistics, 1988 Edition, ILO, Geneva, page 47]	Persons	Millions																																																					
248	ECU	LP	Ecuador	Population	For census purposes, the total population of the country consists of all persons falling within the scope of the census. In the broadest sense, the total may comprise either all usual residents of the country or all persons present in the country at the time of the census. [Principles and Recommendations for Population and Housing Censuses, Revision 1, paragraph 2.42]	Persons	Millions	Source: National Statistics Office Latest actual data: 2022 Primary domestic currency: US dollar Data last updated: 04/10/2025	7.998	8.227	8.461	8.697	8.935	9.173	9.413	9.652	9.903	10.148	10.388	10.628	10.868	11.105	11.334	11.551	11.751	11.938	12.119	12.297	12.481	12.681	12.901	13.132	13.367	13.604	13.852	14.107	14.359	14.616	14.884	15.161	15.441	15.718	15.994	16.269	16.532	16.793	17.078	17.357	17.526	17.614	17.715	17.835	17.967	18.104	18.244	18.386	18.529	18.672	18.815	2022
248	ECU	GGR	Ecuador	General government revenue	Revenue consists of taxes, social contributions, grants receivable, and other revenue. Revenue increases government's net worth, which is the difference between its assets and liabilities (GFSM 2001, paragraph 4.20). Note: Transactions that merely change the composition of the balance sheet do not change the net worth position, for example, proceeds from sales of nonfinancial and financial assets or incurrence of liabilities.	National currency	Billions	Source: Ministry of Finance or Treasury Latest actual data: 2024 Reporting in calendar year: Yes Start/end months of reporting year: January/December GFS Manual used: Government Finance Statistics Manual (GFSM) 2014. Fiscal series are compiled according to GFSM2014 starting in 2012. Data up to 2011 are estimates based on available information. Basis of recording: Mixed. As per source data. General government includes: Central Government; State Government; Local Government; Social Security Funds Valuation of public debt: Face value Instruments included in gross and net debt: Currency and Deposits; Loans; Securities Other than Shares Primary domestic currency: US dollar Data last updated: 04/10/2025	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	4.38	4.438	4.947	4.32	3.647	4.197	4.955	6.361	6.91	8.176	9.146	11.263	13.631	22.108	18.378	23.178	31.19	35.387	37.242	38.855	36.183	33.048	36.265	40.973	39.042	31.468	38.443	45.172	43.576	45.789	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGR_NGDP	Ecuador	General government revenue	Revenue consists of taxes, social contributions, grants receivable, and other revenue. Revenue increases government's net worth, which is the difference between its assets and liabilities (GFSM 2001, paragraph 4.20). Note: Transactions that merely change the composition of the balance sheet do not change the net worth position, for example, proceeds from sales of nonfinancial and financial assets or incurrence of liabilities.	Percent of GDP	Units	See notes for:  General government revenue (National currency).	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	19.928	19.295	19.138	16.432	19.304	23.939	21.423	23.512	22.316	23.232	22.706	24.65	27.344	36.161	30.582	34.01	39.487	40.334	38.565	37.827	37.222	33.836	34.714	38.122	36.286	32.825	35.868	38.896	35.969	37.616	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGX	Ecuador	General government total expenditure	Total expenditure consists of total expense and the net acquisition of nonfinancial assets. Note: Apart from being on an accrual basis, total expenditure differs from the GFSM 1986 definition of total expenditure in the sense that it also takes the disposals of nonfinancial assets into account.	National currency	Billions	Source: Ministry of Finance or Treasury Latest actual data: 2024 Reporting in calendar year: Yes Start/end months of reporting year: January/December GFS Manual used: Government Finance Statistics Manual (GFSM) 2014. Fiscal series are compiled according to GFSM2014 starting in 2012. Data up to 2011 are estimates based on available information. Basis of recording: Mixed. As per source data. General government includes: Central Government; State Government; Local Government; Social Security Funds Valuation of public debt: Face value Instruments included in gross and net debt: Currency and Deposits; Loans; Securities Other than Shares Primary domestic currency: US dollar Data last updated: 04/10/2025	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	4.825	5.229	5.677	5.661	4.558	4.253	4.947	6.161	6.587	7.493	8.88	9.928	12.305	21.761	20.61	24.123	31.29	37.874	45.128	47.182	42.858	43.101	42.295	43.985	42.773	38.538	40.145	45.12	47.796	47.41	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGX_NGDP	Ecuador	General government total expenditure	Total expenditure consists of total expense and the net acquisition of nonfinancial assets. Note: Apart from being on an accrual basis, total expenditure differs from the GFSM 1986 definition of total expenditure in the sense that it also takes the disposals of nonfinancial assets into account.	Percent of GDP	Units	See notes for:  General government total expenditure (National currency).	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	21.952	22.735	21.963	21.532	24.129	24.259	21.391	22.774	21.271	21.29	22.045	21.729	24.686	35.593	34.296	35.396	39.615	43.169	46.73	45.934	44.088	44.128	40.486	40.925	39.753	40.2	37.456	38.852	39.453	38.947	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGXCNL	Ecuador	General government net lending/borrowing	Net lending (+)/ borrowing (-) is calculated as revenue minus total expenditure. This is a core GFS balance that measures the extent to which general government is either putting financial resources at the disposal of other sectors in the economy and nonresidents (net lending), or utilizing the financial resources generated by other sectors and nonresidents (net borrowing). This balance may be viewed as an indicator of the financial impact of general government activity on the rest of the economy and nonresidents (GFSM 2001, paragraph 4.17). Note: Net lending (+)/borrowing (-) is also equal to net acquisition of financial assets minus net incurrence of liabilities.	National currency	Billions	Source: Ministry of Finance or Treasury Latest actual data: 2024 Reporting in calendar year: Yes Start/end months of reporting year: January/December GFS Manual used: Government Finance Statistics Manual (GFSM) 2014. Fiscal series are compiled according to GFSM2014 starting in 2012. Data up to 2011 are estimates based on available information. Basis of recording: Mixed. As per source data. General government includes: Central Government; State Government; Local Government; Social Security Funds Valuation of public debt: Face value Instruments included in gross and net debt: Currency and Deposits; Loans; Securities Other than Shares Primary domestic currency: US dollar Data last updated: 04/10/2025	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	-0.445	-0.791	-0.73	-1.341	-0.911	-0.056	0.008	0.2	0.324	0.683	0.266	1.335	1.325	0.347	-2.232	-0.944	-0.1	-2.487	-7.885	-8.327	-6.675	-10.053	-6.03	-3.012	-3.731	-7.071	-1.701	0.052	-4.22	-1.621	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGXCNL_NGDP	Ecuador	General government net lending/borrowing	Net lending (+)/ borrowing (-) is calculated as revenue minus total expenditure. This is a core GFS balance that measures the extent to which general government is either putting financial resources at the disposal of other sectors in the economy and nonresidents (net lending), or utilizing the financial resources generated by other sectors and nonresidents (net borrowing). This balance may be viewed as an indicator of the financial impact of general government activity on the rest of the economy and nonresidents (GFSM 2001, paragraph 4.17). Note: Net lending (+)/borrowing (-) is also equal to net acquisition of financial assets minus net incurrence of liabilities.	Percent of GDP	Units	See notes for:  General government net lending/borrowing (National currency).	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	-2.024	-3.44	-2.825	-5.099	-4.825	-0.32	0.033	0.738	1.045	1.942	0.661	2.921	2.658	0.568	-3.714	-1.385	-0.127	-2.835	-8.165	-8.106	-6.866	-10.292	-5.772	-2.803	-3.468	-7.376	-1.588	0.045	-3.484	-1.332	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGSB	Ecuador	General government structural balance	The structural budget balance refers to the general government cyclically adjusted balance adjusted for nonstructural elements beyond the economic cycle. These include temporary financial sector and asset price movements as well as one-off, or temporary, revenue or expenditure items. The cyclically adjusted balance is the fiscal balance adjusted for the effects of the economic cycle; see, for example, A. Fedelino. A. Ivanova and M. Horton "Computing Cyclically Adjusted Balances and Automatic Stabilizers" IMF Technical Guidance Note No. 5, http://www.imf.org/external/pubs/ft/tnm/2009/tnm0905.pdf.	National currency	Billions	Source: Ministry of Finance or Treasury Latest actual data: 2024 Reporting in calendar year: Yes Start/end months of reporting year: January/December GFS Manual used: Government Finance Statistics Manual (GFSM) 2014. Fiscal series are compiled according to GFSM2014 starting in 2012. Data up to 2011 are estimates based on available information. Basis of recording: Mixed. As per source data. General government includes: Central Government; State Government; Local Government; Social Security Funds Valuation of public debt: Face value Instruments included in gross and net debt: Currency and Deposits; Loans; Securities Other than Shares Primary domestic currency: US dollar Data last updated: 04/10/2025	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	0.002	0.223	0.454	0.641	0.179	1.234	0.852	-1.327	-0.846	-0.244	-1.168	-3.633	-8.947	-9.191	-8.317	-10.819	-6.035	-3.887	-3.879	-5.446	-1.326	-1.057	-4.32	-1.033	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGSB_NPGDP	Ecuador	General government structural balance	The structural budget balance refers to the general government cyclically adjusted balance adjusted for nonstructural elements beyond the economic cycle. These include temporary financial sector and asset price movements as well as one-off, or temporary, revenue or expenditure items. The cyclically adjusted balance is the fiscal balance adjusted for the effects of the economic cycle; see, for example, A. Fedelino. A. Ivanova and M. Horton "Computing Cyclically Adjusted Balances and Automatic Stabilizers" IMF Technical Guidance Note No. 5, http://www.imf.org/external/pubs/ft/tnm/2009/tnm0905.pdf.	Percent of potential GDP	Units	See notes for:  General government structural balance (National currency).	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	0.009	0.802	1.423	1.798	0.442	2.695	1.688	-2.172	-1.391	-0.354	-1.494	-4.222	-9.589	-9.283	-8.747	-11.146	-5.893	-3.658	-3.605	-5.404	-1.212	-0.905	-3.546	-0.821	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGXONLB	Ecuador	General government primary net lending/borrowing	Primary net lending/borrowing is net lending (+)/borrowing (-) plus net interest payable/paid (interest expense minus interest revenue).	National currency	Billions	Source: Ministry of Finance or Treasury Latest actual data: 2024 Reporting in calendar year: Yes Start/end months of reporting year: January/December GFS Manual used: Government Finance Statistics Manual (GFSM) 2014. Fiscal series are compiled according to GFSM2014 starting in 2012. Data up to 2011 are estimates based on available information. Basis of recording: Mixed. As per source data. General government includes: Central Government; State Government; Local Government; Social Security Funds Valuation of public debt: Face value Instruments included in gross and net debt: Currency and Deposits; Loans; Securities Other than Shares Primary domestic currency: US dollar Data last updated: 04/10/2025	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	0.375	0.059	0.284	-0.361	0.437	1.001	1.004	1.041	1.143	1.48	1.073	2.231	2.187	1.052	-1.883	-0.531	0.402	-2.029	-7.659	-8.083	-6.222	-9.453	-4.893	-1.5	-2.07	-5.523	-1.522	0.551	-3.17	-0.223	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGXONLB_NGDP	Ecuador	General government primary net lending/borrowing	Primary net lending/borrowing is net lending (+)/borrowing (-) plus net interest payable/paid (interest expense minus interest revenue).	Percent of GDP	Units	See notes for:  General government primary net lending/borrowing (National currency).	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	1.707	0.255	1.098	-1.372	2.311	5.709	4.34	3.849	3.692	4.205	2.664	4.883	4.387	1.72	-3.133	-0.78	0.508	-2.313	-7.931	-7.869	-6.401	-9.678	-4.684	-1.396	-1.924	-5.761	-1.42	0.475	-2.617	-0.183	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGXWDN	Ecuador	General government net debt	Net debt is calculated as gross debt minus financial assets corresponding to debt instruments. These financial assets are: monetary gold and SDRs, currency and deposits, debt securities, loans, insurance, pension, and standardized guarantee schemes, and other accounts receivable.	National currency	Billions																																																					
248	ECU	GGXWDN_NGDP	Ecuador	General government net debt	Net debt is calculated as gross debt minus financial assets corresponding to debt instruments. These financial assets are: monetary gold and SDRs, currency and deposits, debt securities, loans, insurance, pension, and standardized guarantee schemes, and other accounts receivable.	Percent of GDP	Units																																																					
248	ECU	GGXWDG	Ecuador	General government gross debt	Gross debt consists of all liabilities that require payment or payments of interest and/or principal by the debtor to the creditor at a date or dates in the future. This includes debt liabilities in the form of SDRs, currency and deposits, debt securities, loans, insurance, pensions and standardized guarantee schemes, and other accounts payable. Thus, all liabilities in the GFSM 2001 system are debt, except for equity and investment fund shares and financial derivatives and employee stock options. Debt can be valued at current market, nominal, or face values (GFSM 2001, paragraph 7.110).	National currency	Billions	Source: Ministry of Finance or Treasury Latest actual data: 2024 Reporting in calendar year: Yes Start/end months of reporting year: January/December GFS Manual used: Government Finance Statistics Manual (GFSM) 2014. Fiscal series are compiled according to GFSM2014 starting in 2012. Data up to 2011 are estimates based on available information. Basis of recording: Mixed. As per source data. General government includes: Central Government; State Government; Local Government; Social Security Funds Valuation of public debt: Face value Instruments included in gross and net debt: Currency and Deposits; Loans; Securities Other than Shares Primary domestic currency: US dollar Data last updated: 04/10/2025	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	14.756	14.891	14.615	14.148	14.403	15.121	14.779	15.207	11.819	12.564	14.697	16.969	22.622	28.928	35.421	44.993	49.509	53.208	56.019	60.923	66.19	66.431	65.821	66.998	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	GGXWDG_NGDP	Ecuador	General government gross debt	Gross debt consists of all liabilities that require payment or payments of interest and/or principal by the debtor to the creditor at a date or dates in the future. This includes debt liabilities in the form of SDRs, currency and deposits, debt securities, loans, insurance, pensions and standardized guarantee schemes, and other accounts payable. Thus, all liabilities in the GFSM 2001 system are debt, except for equity and investment fund shares and financial derivatives and employee stock options. Debt can be valued at current market, nominal, or face values (GFSM 2001, paragraph 7.110).	Percent of GDP	Units	See notes for:  General government gross debt (National currency).	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	n/a	63.803	55.043	47.198	40.2	35.758	33.094	29.648	24.873	19.667	18.436	18.607	19.341	23.426	28.163	36.438	46.066	47.391	49.505	52.064	63.551	61.756	57.203	54.332	55.039	n/a	n/a	n/a	n/a	n/a	n/a	2024
248	ECU	NGDP_FY	Ecuador	Gross domestic product corresponding to fiscal year, current prices	Gross domestic product corresponding to fiscal year is the country's GDP based on the same period during the year as their fiscal data. In the case of countries whose fiscal data are based on a fiscal calendar (e.g., July to June), this series would be the country's GDP over that same period. For countries whose fiscal data are based on a calendar year (i.e., January to December), this series will be the same as their GDP in current prices.	National currency	Billions	Source: Ministry of Finance or Treasury Latest actual data: 2024 Reporting in calendar year: Yes Start/end months of reporting year: January/December GFS Manual used: Government Finance Statistics Manual (GFSM) 2014. Fiscal series are compiled according to GFSM2014 starting in 2012. Data up to 2011 are estimates based on available information. Basis of recording: Mixed. As per source data. General government includes: Central Government; State Government; Local Government; Social Security Funds Valuation of public debt: Face value Instruments included in gross and net debt: Currency and Deposits; Loans; Securities Other than Shares Primary domestic currency: US dollar Data last updated: 04/10/2025	16.116	16.501	16.474	14.478	15.408	18.02	13.222	12.355	11.749	11.531	11.71	13.139	14.367	16.783	20.238	21.98	23.001	25.847	26.292	18.891	17.531	23.127	27.054	30.965	35.195	40.279	45.691	49.849	61.139	60.095	68.151	78.987	87.735	96.57	102.718	97.21	97.671	104.467	107.479	107.596	95.865	107.179	116.133	121.147	121.728	125.677	130.31	135.35	140.863	146.638	152.588	2024
248	ECU	BCA	Ecuador	Current account balance	Current account is all transactions other than those in financial and capital items. The major classifications are goods and services, income and current transfers. The focus of the BOP is on transactions (between an economy and the rest of the world) in goods, services, and income.	U.S. dollars	Billions	Source: Central Bank Latest actual data: 2024 BOP Manual used: Balance of Payments and International Investment Position Manual, sixth edition (BPM6) Primary domestic currency: US dollar Data last updated: 04/10/2025	-0.642	-0.998	-1.182	-0.115	-0.273	0.076	-0.582	-1.187	-0.68	-0.715	-0.36	-0.708	-0.122	-0.849	-0.898	-1	-0.055	-0.457	-2.099	0.918	1.113	-0.551	-1.219	-0.387	-0.479	0.474	1.74	1.886	1.769	0.313	-1.582	-0.4	-0.146	-0.933	-0.669	-2.221	0.9	-0.406	-1.649	-0.546	2.005	2.938	2.136	2.217	7.082	4.302	3.442	3.411	3.541	3.683	3.788	2024
248	ECU	BCA_NGDPD	Ecuador	Current account balance	Current account is all transactions other than those in financial and capital items. The major classifications are goods and services, income and current transfers. The focus of the BOP is on transactions (between an economy and the rest of the world) in goods, services, and income.	Percent of GDP	Units	See notes for:  Gross domestic product, current prices (National currency) Current account balance (U.S. dollars).	-3.981	-6.048	-7.175	-0.794	-1.772	0.422	-4.402	-9.608	-5.788	-6.201	-3.074	-5.388	-0.849	-5.058	-4.439	-4.55	-0.238	-1.767	-7.982	4.86	6.347	-2.383	-4.506	-1.249	-1.362	1.177	3.808	3.784	2.894	0.521	-2.322	-0.507	-0.167	-0.966	-0.651	-2.285	0.922	-0.388	-1.534	-0.507	2.091	2.741	1.84	1.83	5.818	3.423	2.641	2.52	2.514	2.512	2.482	2023"""
    
    return weo_raw_data

class EcuadorWEOProcessor:
    """Procesador simplificado de datos WEO de Ecuador del FMI"""
    
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
            
            # Identificar columnas de años
            self.year_columns = [col for col in self.df.columns 
                               if col.isdigit() and 1980 <= int(col) <= 2030]
            
            # Procesar cada indicador
            for _, row in self.df.iterrows():
                indicator_code = row['WEO Subject Code']
                if pd.notna(indicator_code) and indicator_code.strip():
                    self.process_indicator(row)
            
            st.success(f"✅ Procesados {len(self.processed_data)} indicadores con {len(self.year_columns)} años de datos")
            
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
        
        # Extraer datos temporales
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
    
    def search_indicators(self, query: str):
        """Buscar indicadores por término"""
        query_lower = query.lower()
        results = []
        
        for code, info in self.indicators_info.items():
            if (query_lower in info['name'].lower() or 
                query_lower in info['description'].lower() or
                query_lower in code.lower()):
                results.append({
                    'code': code,
                    'name': info['name'],
                    'units': info['units'],
                    'relevance_score': 1.0  # Simple relevance
                })
        
        return results

class EcuadorSimpleAssistant:
    """Asistente simplificado para datos económicos de Ecuador usando Claude"""
    
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
    
    def search_relevant_indicators(self, query: str, max_results: int = 3) -> List[Dict]:
        """Buscar indicadores relevantes basado en palabras clave"""
        query_lower = query.lower()
        
        # Mapeo de palabras clave a códigos de indicadores
        keyword_mapping = {
            'pib': ['NGDP_RPCH', 'NGDP', 'NGDPD', 'NGDPRPC'],
            'gdp': ['NGDP_RPCH', 'NGDP', 'NGDPD', 'NGDPRPC'],
            'crecimiento': ['NGDP_RPCH'],
            'inflacion': ['PCPIPCH', 'PCPI'],
            'inflation': ['PCPIPCH', 'PCPI'],
            'desempleo': ['LUR'],
            'unemployment': ['LUR'],
            'deuda': ['GGXWDG_NGDP', 'GGXWDG'],
            'debt': ['GGXWDG_NGDP', 'GGXWDG'],
            'fiscal': ['GGR_NGDP', 'GGX_NGDP', 'GGXCNL_NGDP'],
            'government': ['GGR_NGDP', 'GGX_NGDP', 'GGXCNL_NGDP'],
            'cuenta corriente': ['BCA_NGDPD', 'BCA'],
            'current account': ['BCA_NGDPD', 'BCA'],
            'comercio': ['TX_RPCH', 'TM_RPCH'],
            'trade': ['TX_RPCH', 'TM_RPCH'],
            'exportaciones': ['TX_RPCH'],
            'exports': ['TX_RPCH'],
            'importaciones': ['TM_RPCH'],
            'imports': ['TM_RPCH'],
            'poblacion': ['LP'],
            'population': ['LP'],
            'per capita': ['NGDPRPC', 'NGDPDPC'],
            'per cápita': ['NGDPRPC', 'NGDPDPC']
        }
        
        # Encontrar códigos relevantes
        relevant_codes = set()
        for keyword, codes in keyword_mapping.items():
            if keyword in query_lower:
                relevant_codes.update(codes)
        
        # Si no hay coincidencias específicas, buscar en nombres de indicadores
        if not relevant_codes:
            search_results = self.weo_processor.search_indicators(query)
            relevant_codes = [r['code'] for r in search_results[:max_results]]
        
        # Obtener datos de los indicadores relevantes
        relevant_data = []
        for code in list(relevant_codes)[:max_results]:
            if code in self.weo_processor.processed_data:
                indicator_data = self.weo_processor.processed_data[code]
                relevant_data.append({
                    'code': code,
                    'info': indicator_data['info'],
                    'stats': indicator_data['stats'],
                    'data': indicator_data['data']
                })
        
        return relevant_data
    
    def generate_response(self, query: str) -> str:
        """Generar respuesta usando Claude o fallback"""
        # Buscar indicadores relevantes
        relevant_indicators = self.search_relevant_indicators(query)
        
        if self.claude_client and relevant_indicators:
            return self.generate_claude_response(query, relevant_indicators)
        else:
            return self.generate_fallback_response(query, relevant_indicators)
    
    def generate_claude_response(self, query: str, relevant_indicators: List[Dict]) -> str:
        """Generar respuesta usando Claude API"""
        try:
            # Construir contexto con indicadores relevantes
            context = "DATOS ECONÓMICOS DE ECUADOR (FMI World Economic Outlook):\n\n"
            
            for indicator in relevant_indicators:
                info = indicator['info']
                stats = indicator['stats']
                data = indicator['data']
                
                # Obtener datos recientes
                recent_years = sorted(data.keys(), reverse=True)[:5]
                recent_data = {year: data[year] for year in recent_years}
                
                context += f"""
INDICADOR: {info['name']} ({indicator['code']})
- Descripción: {info['description'][:200]}...
- Unidades: {info['units']}
- Valor actual ({stats['last_year']}): {stats['latest_value']:.2f}
- Promedio histórico: {stats['mean_value']:.2f}
- Datos recientes: {recent_data}

"""
            
            prompt = f"""Eres un economista experto especializado en Ecuador. Responde la siguiente pregunta usando únicamente los datos proporcionados.

CONTEXTO:
{context}

PREGUNTA: {query}

INSTRUCCIONES:
1. Responde de manera profesional y precisa
2. Usa datos específicos con cifras y años
3. Explica tendencias cuando sea relevante
4. Mantén un tono informativo pero accesible
5. Si no tienes información suficiente, indícalo claramente

RESPUESTA:"""

            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            st.warning(f"Error con Claude API: {e}")
            return self.generate_fallback_response(query, relevant_indicators)
    
    def generate_fallback_response(self, query: str, relevant_indicators: List[Dict]) -> str:
        """Respuesta de fallback cuando Claude no está disponible"""
        if not relevant_indicators:
            return """🔍 **No encontré información específica para tu consulta.**

Puedes preguntarme sobre:
- **PIB y crecimiento económico**
- **Inflación y precios**
- **Desempleo y mercado laboral**
- **Deuda pública y finanzas fiscales**
- **Comercio exterior**
- **Población y demografía**

*Datos fuente: FMI World Economic Outlook*"""
        
        # Usar el primer indicador más relevante
        indicator = relevant_indicators[0]
        info = indicator['info']
        stats = indicator['stats']
        data = indicator['data']
        
        # Generar respuesta básica
        recent_years = sorted(data.keys(), reverse=True)[:3]
        recent_data_text = ", ".join([f"{year}: {data[year]:.2f}" for year in recent_years])
        
        # Análisis de tendencia simple
        if len(recent_years) >= 2:
            change = data[recent_years[0]] - data[recent_years[1]]
            trend = "📈 creciente" if change > 0 else "📉 decreciente" if change < 0 else "→ estable"
        else:
            trend = "datos limitados"
        
        return f"""📊 **{info['name']}** (`{indicator['code']}`)

**Valor actual ({stats['last_year']}):** {stats['latest_value']:.2f} {info['units']}

**Datos recientes:** {recent_data_text}
**Tendencia:** {trend}

**Estadísticas históricas:**
- Período: {stats['first_year']}-{stats['last_year']} ({stats['data_points']} observaciones)
- Promedio histórico: {stats['mean_value']:.2f}
- Máximo histórico: {stats['max_value']:.2f}
- Mínimo histórico: {stats['min_value']:.2f}

**Descripción:** {info['description'][:300]}...

*Fuente: FMI World Economic Outlook*"""

@st.cache_resource
def load_system():
    """Cargar sistema simplificado"""
    try:
        # Cargar datos WEO
        weo_data = load_weo_data()
        
        # Procesar datos
        weo_processor = EcuadorWEOProcessor(weo_data)
        
        # Crear asistente
        assistant = EcuadorSimpleAssistant(weo_processor)
        
        return assistant, weo_processor
        
    except Exception as e:
        st.error(f"Error cargando sistema: {e}")
        return None, None

def create_visualization(indicator_code: str, weo_processor: EcuadorWEOProcessor, start_year: int = 2015, end_year: int = 2024):
    """Crear visualización con datos reales"""
    try:
        data = weo_processor.get_indicator_data(indicator_code, start_year, end_year)
        if not data or not data['data']:
            return None, None
        
        years = list(data['data'].keys())
        values = list(data['data'].values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            line=dict(color='#2a5298', width=3),
            marker=dict(size=8, color='#2a5298'),
            name=data['info']['name'],
            hovertemplate='<b>Año:</b> %{x}<br><b>Valor:</b> %{y:.2f}<br><extra></extra>'
        ))
        
        fig.update_layout(
            title=f"{data['info']['name']} ({indicator_code})",
            xaxis_title='Año',
            yaxis_title=f"{data['info']['units']}",
            template='plotly_white',
            height=400,
            showlegend=False
        )
        
        return fig, data
        
    except Exception as e:
        st.error(f"Error creando visualización: {e}")
        return None, None

# Interfaz principal de Streamlit
def main():
    """Función principal de la aplicación"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🇪🇨 Ecuador Economic Data Assistant</h1>
        <p>Asistente inteligente con datos oficiales del FMI usando Claude AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar sistema
    assistant, weo_processor = load_system()
    
    if not assistant or not weo_processor:
        st.error("No se pudo cargar el sistema. Por favor, recarga la página.")
        return
    
    # Layout con sidebar y main
    with st.sidebar:
        st.markdown("## 📊 Explorador de Datos")
        
        # Búsqueda de indicadores
        search_query = st.text_input("🔍 Buscar indicadores:", placeholder="PIB, inflación, desempleo...")
        
        if search_query:
            search_results = weo_processor.search_indicators(search_query)
            if search_results:
                st.markdown("### Resultados:")
                for result in search_results[:5]:
                    st.markdown(f"""
                    <div class="indicator-chip">
                        <strong>{result['code']}</strong><br>
                        {result['name'][:50]}...
                    </div>
                    """, unsafe_allow_html=True)
        
        # Selector de indicadores principales
        st.markdown("### 📈 Indicadores Principales")
        key_indicators = {
            'NGDP_RPCH': 'Crecimiento PIB',
            'PCPIPCH': 'Inflación',
            'LUR': 'Desempleo',
            'GGXWDG_NGDP': 'Deuda Pública',
            'BCA_NGDPD': 'Cuenta Corriente'
        }
        
        selected_indicator = st.selectbox(
            "Seleccionar indicador:",
            options=list(key_indicators.keys()),
            format_func=lambda x: key_indicators[x]
        )
        
        # Selector de años
        year_range = st.slider(
            "Rango de años:",
            min_value=2000,
            max_value=2024,
            value=(2015, 2024)
        )
        
        # Información del sistema
        st.markdown("""
        <div class="sidebar-info">
            <h4>📋 Información</h4>
            <p><strong>Fuente:</strong> FMI World Economic Outlook</p>
            <p><strong>Última actualización:</strong> Octubre 2024</p>
            <p><strong>Total indicadores:</strong> 40+</p>
            <p><strong>Sistema:</strong> Simplificado</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🤖 Asistente Económico")
        
        # Chat interface
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Mostrar mensajes del chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input del usuario
        if prompt := st.chat_input("Pregúntame sobre la economía de Ecuador..."):
            # Agregar mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generar respuesta
            with st.chat_message("assistant"):
                with st.spinner("Analizando datos económicos..."):
                    # Generar respuesta
                    response = assistant.generate_response(prompt)
                    st.markdown(response)
                    
                    # Agregar respuesta al historial
                    st.session_state.messages.append({"role": "assistant", "content": response})
    
    with col2:
        st.markdown("## 📊 Visualización")
        
        # Crear visualización del indicador seleccionado
        if selected_indicator:
            fig, data = create_visualization(
                selected_indicator, 
                weo_processor, 
                year_range[0], 
                year_range[1]
            )
            
            if fig and data:
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar estadísticas
                st.markdown("### 📋 Estadísticas")
                latest_value = data['stats']['latest_value']
                latest_year = data['stats']['last_year']
                
                st.markdown(f"""
                <div class="highlight-stat">
                    <h4>Valor Actual</h4>
                    <h2>{latest_value:.2f}</h2>
                    <p>{data['info']['units']} ({latest_year})</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Métricas adicionales
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(
                        "Promedio Histórico",
                        f"{data['stats']['mean_value']:.2f}",
                        delta=f"{latest_value - data['stats']['mean_value']:.2f}"
                    )
                
                with col_b:
                    st.metric(
                        "Máximo Histórico",
                        f"{data['stats']['max_value']:.2f}",
                        delta=f"{latest_value - data['stats']['max_value']:.2f}"
                    )
        
        # Ejemplos de consultas
        st.markdown("### 💡 Ejemplos de Consultas")
        example_queries = [
            "¿Cuál es la tendencia del PIB?",
            "¿Cómo ha evolucionado la inflación?",
            "¿Cuál es el nivel de deuda pública?",
            "Compara el desempleo antes y después de 2020",
            "¿Cómo está la balanza comercial?"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query[:10]}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🇪🇨 <strong>Ecuador Economic Data Assistant</strong> | Datos oficiales del FMI | Powered by Claude AI</p>
        <p><small>Última actualización: Octubre 2024 | Versión simplificada para máxima compatibilidad</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    

