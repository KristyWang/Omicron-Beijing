# Assessing the feasibility of sustaining SARS-CoV-2 local containment in China in the era of highly transmissible variants 
Yan Wang, Kaiyuan Sun, Zhaomin Feng, Lan Yi, Yanpeng Wu, Hengcong Liu, Quanyi Wang, Marco Ajelli, Cécile Viboud, Hongjie Yu
# 

## Getting started
### Software and packages
This is the instruction for readers to repeat and understand the construction for the agent-based model simulating the transmission of SARS-CoV-2 Omicron in Beijing, China. The codes were written in Python (version 3.10). The following packages are needed to run the scripts:
* pandas
* numpy
* datetime
* chinese_calendar
* scipy.stats
### Folder structure
The Python scripts are written assuming you have the following folder structure:
```
variant model
│    0. Readme.pdf
└─── 1. data
└─── 2. code
└─── 3. result
└─── 4. output
└─── 5. NPI_output
```
Where
- All data (except for the mobility data) needed to run the model is reported in folder ‘1. data’. The mobility network, which contains commercial data provided by China Unicom, is available from the corresponding author ( yhj@fudan.edu.cn ) upon reasonable request;
- The codes are reported in folder ‘2. code’;
- The aggregated results produced by the codes will be stored in folder ‘3. result’;
- The unmitigated transmission chains will be stored in folder ‘4. output’;
- The transmission chains under different vaccination and intervention scenarios will be stored in ‘5. NPI_output’.
## Linelist for the data and code
### 1. Data

* age_structure.xlsx
  - Description: The population structure by five-year age group in Beijing, China, in 2020	
  - Source: Beijing Municipal Bureau of Statistics [1]
* Beijing_street.xlsx	
  - Description: The population structure by street/town in Beijing, China, in 2020	
  - Source: WorldPop [2]
* SH_bs_hh.xlsx	
  - Description: The age-specific population contact matrix in the household in Shanghai, China, in 2017-2018	
  - Source: Previous study [3]
* SH_bs_wk.xlsx	
  - Description: The age-specific population contact matrix in the workplace in Shanghai, China, in 2017-2018	
  - Source: Previous study [3]
* SH_bs_cm.xlsx	
  - Description: The age-specific population contact matrix in the community in Shanghai, China, in 2017-2018	
  - Source: Previous study [3]
* hh_size_freq.xlsx
  - Description: The age-specific household size distribution in Shanghai, China, in 2017-2018	
  - Source: Previous study [3]
* interaction matrix.xlsx
  - Description: The mobility patterns in Beijing, China (available from the corresponding author upon reasonable request)	
  - Source: China Unicom (one of the leading mobile phone service providers in China)
* sen_PCR.xlsx
  - Description: The time-varied sensitivity of RT-PCR testing	
  - Source: Previous study [4]
* VE.xlsx
  - Description: The effectiveness of inactivated vaccines	
  - Source: Previous study [5, 6]
* NZ_vax_cov_0920.xlsx
  - Description: Population immunity levels in the baseline immunization scenario and the enhanced immunization scenarios, assumed based on the vaccine coverage of New Zealand (as of September 20, 2022)	
  - Source: Ministry of Health, New Zealand [7]
 
### 2. Code

* Function.py	
  - Description: Pre-defined functions to run the branching process model.
* NPI_Function.py	
  - Description: Pre-defined functions to simulate different intervention scenarios.
* 1.branching tree.py
  - Description: The script of branching process model to generate unmitigated transmission chains.
* 2.NPIs.py
  - Description: The script to simulate the effect of NPIs through pruning the unmitigated chains of transmission. 
* 3.R_eff.py
  - Description: The script to aggregate the simulation results of different scenarios.

## Simulation
We evaluate an exhaustive combinatory of hypothetical scenarios (two Omicron sublineages, three population immunity levels, and six NPI intensity levels, for a total of 36 scenarios):
* Variant type: we consider both the Omicron BA.1 (R_0=7.5) and BA.2 (R_0=9.5) sublineages.
* Level of population immunity: We consider a baseline immunization scenario and two enhanced immunization scenarios (a homologous booster scenario and a heterologous booster scenario).
* Intervention strategy: We consider a baseline intervention scenario with moderate intervention intensity and five enhanced intervention scenarios with NPI intensity gradually increased.

We first simulate the transmission chain in the absence of NPIs (stored in folder ‘4. output’), based on a branching process described in ‘1. branching tree.py’ and then simulate the effect of NPIs through pruning the unmitigated chains of transmission by removing branches that would otherwise be interrupted by the corresponding NPIs of the scenario of interest (coded in ‘2. NPIs.py’ and stored in folder ‘5. NPI_output’). We run 100 simulations for each scenario to capture the stochasticity of the transmission process and aggregate the simulation results (stored in folder ‘3. result’) of different scenarios using ‘3. R_eff.py’.
 
## References
1.	Beijing Municipal Bureau of Statistics. Beijing 2020 annual statistics. 2020. http://tjj.beijing.gov.cn/tjsj_31433/tjbmfbjh/ndtjzl_31437/2021ndtjzl/202012/t20201231_2191210.html. Accessed 27 May 2022.
2.	WorldPop. The spatial distribution of population in 2020, China. 2020. https://doi.org/10.5258/SOTON/WP00645. Accessed 27 May 2022.
3.	Zhang J, Klepac P, Read JM, Rosello A, Wang X, Lai S, et al. Patterns of human social contact and contact with animals in Shanghai, China. Sci Rep. 2019; 9:15141. https://doi.org/10.1038/s41598-019-51609-8.
4.	Kucirka LM, Lauer SA, Laeyendecker O, Boon D, Lessler J. Variation in False-Negative Rate of Reverse Transcriptase Polymerase Chain Reaction-Based SARS-CoV-2 Tests by Time Since Exposure. Ann Intern Med. 2020; 173:262-267. https://doi.org/10.7326/m20-1495.
5.	Cai J, Deng X, Yang J, Sun K, Liu H, Chen Z, et al. Modeling transmission of SARS-CoV-2 Omicron in China. Nat Med. 2022; 28:1468–1475. https://doi.org/10.1038/s41591-022-01855-7.
6.	Wei Z, Ma W, Wang Z, Li J, Fu X, Chang H, et al. Household transmission of SARS-CoV-2 during the Omicron wave in Shanghai, China:a case-ascertained study. medRxiv. 2022:22280362. https://doi.org/10.1101/2022.09.26.22280362.
7.	Ministry of Health, New Zealand Government. Data and statistics about the rollout of COVID-19 vaccines in New Zealand.  2022. https://www.health.govt.nz/covid-19-novel-coronavirus/covid-19-data-and-statistics/covid-19-vaccine-data#uptake. Accessed 27 May 2022.
