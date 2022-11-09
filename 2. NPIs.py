# -*- coding: utf-8 -*-
import pandas as pd
import datetime
import NPI_Functions as NPI_Func
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)

pd.set_option('display.max_columns', 1000000)
pd.set_option('display.max_rows', 1000000)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 180)  # 设置打印宽度(**重要**)
pd.set_option('expand_frame_repr', False)  # 数据超过总宽度后，是否折叠显示
ref_date = datetime.datetime.strptime('2020-05-31 00:00:00', '%Y-%m-%d %H:%M:%S')


prefix0 = "Level_1_"
prefix2 = "hom_9.0"

hosp_prop = 2 / 3
# hosp_speed1 = 2.375
# hosp_speed2 = 4.173
hosp_speed1 = 0.689
hosp_speed2 = 0.258

Prob_mask_wk = 0.1
Prob_mask_cm = 0.3
# Prob_mask_wk = 0.5
# Prob_mask_cm = 0.8

Prob_test_h = 0.16
Prob_test_m = 0.12
# Prob_test_h = 0.25
# Prob_test_m = 0.25

rnd_scr = 1
Freq_scr = 3

prob_out = [0.8, 0.5, 0.3, 0.5, 0.3, 0.1, 0.3, 0.1, 0, 0.9, 0.6, 0.3]
# prob_out = [0.5, 0.3, 0.1, 0.3, 0.1, 0, 0, 0, 0, 0.6, 0.3, 0]

# Level 0 (Note: onset to hospital: weibull distribution)
# Level 1 - 3 (Note: change distribution of onset to hospital to gamma distribution)
for seed0 in range(1, 21):
    bs = NPI_Func.bs_NPI(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2, Prob_test_h, Prob_test_m,
                         Prob_mask_wk, Prob_mask_cm, rnd_scr, Freq_scr, prob_out)
    output_bs = f"{'../5. NPI_output/R1/'}{prefix0}{prefix2}{'_seed_'}{seed0}{'.xlsx'}"
    print(output_bs)
    bs.to_excel(output_bs, index=False)

# # Level 4 - 5 (Note: use Enhance_mass_scr function)
# for seed0 in range(1, 21):
#     bs = NPI_Func.Enhance_mass_scr(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2, Prob_test_h, Prob_test_m,
#                                    Prob_mask_wk, Prob_mask_cm, rnd_scr, Freq_scr, prob_out)
#     output_bs = f"{'../5. NPI_output/'}{prefix0}{prefix2}{'_seed_'}{seed0}{'.xlsx'}"
#     print(output_bs)
#     bs.to_excel(output_bs, index=False)
