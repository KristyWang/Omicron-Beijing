# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)

pd.set_option('display.max_columns', 1000000)
pd.set_option('display.max_rows', 1000000)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 180)  # 设置打印宽度(**重要**)
pd.set_option('expand_frame_repr', False)   # 数据超过总宽度后，是否折叠显示

prefix2 = "hom_9.0"

for seed0 in range(1, 101):
    print(seed0)
    # baseline intervention
    input_data = f"{'../4. output/R1/'}{prefix2}{'_seed_'}{seed0}{'.xlsx'}"
    No_NPI = pd.read_excel(input_data)
    temp = No_NPI[["id", "inf"]]
    temp.columns = ["infector", "inf1"]
    No_NPI = pd.merge(No_NPI, temp, on="infector", how="left")
    End_date = No_NPI["inf1"].max()

    input_data = f"{'../5. NPI_output/R1/Level_0_'}{prefix2}{'_seed_'}{seed0}{'.xlsx'}"
    simu_data = pd.read_excel(input_data)

    cut_off = simu_data["diag_tmp"].min()

    temp = simu_data[["id", "inf"]]
    temp.columns = ["infector", "inf1"]

    if temp.shape[0] > 3:
        simu_data = pd.merge(simu_data, temp, on="infector", how="left")
        case_after_NPIs = simu_data.loc[(simu_data["inf"] >= cut_off) & (simu_data["inf"] <= End_date)][["id", "inf"]]
        case_after_NPIs = case_after_NPIs.reset_index(drop=True)

        after_NPIs = simu_data[simu_data["infector"].isin(case_after_NPIs["id"])]
        R_eff = pd.DataFrame(after_NPIs.groupby(by=["infector"]).size())
        R_eff.columns = ["R_eff"]
        R_eff["id"] = R_eff.index
        R_eff = R_eff.reset_index(drop=True)
        case_after_NPIs = pd.merge(case_after_NPIs, R_eff, on="id", how="left")
        case_after_NPIs["R_eff"] = np.where(np.isnan(case_after_NPIs["R_eff"]), 0, case_after_NPIs["R_eff"])
        if case_after_NPIs.shape[0] == 0:
            R_eff = 0
        else:
            R_eff = case_after_NPIs["R_eff"].mean()
    else:
        End_date = 0
        R_eff = 0

    data1 = pd.DataFrame({"seed0": seed0, "R_eff": R_eff, "Date_detection": cut_off, "End_date": End_date}, index=[0])

    # Enhanced symptom surveillance
    input_data = f"{'../5. NPI_output/R1/Level_1_'}{prefix2}{'_seed_'}{seed0}{'.xlsx'}"
    simu_data = pd.read_excel(input_data)

    cut_off = simu_data["diag_tmp"].min()

    temp = simu_data[["id", "inf"]]
    temp.columns = ["infector", "inf1"]

    if temp.shape[0] > 3:
        simu_data = pd.merge(simu_data, temp, on="infector", how="left")
        case_after_NPIs = simu_data.loc[(simu_data["inf"] >= cut_off) & (simu_data["inf"] <= End_date)][["id", "inf"]]
        case_after_NPIs = case_after_NPIs.reset_index(drop=True)

        after_NPIs = simu_data[simu_data["infector"].isin(case_after_NPIs["id"])]
        R_eff = pd.DataFrame(after_NPIs.groupby(by=["infector"]).size())
        R_eff.columns = ["R_eff"]
        R_eff["id"] = R_eff.index
        R_eff = R_eff.reset_index(drop=True)
        case_after_NPIs = pd.merge(case_after_NPIs, R_eff, on="id", how="left")
        case_after_NPIs["R_eff"] = np.where(np.isnan(case_after_NPIs["R_eff"]), 0, case_after_NPIs["R_eff"])
        if case_after_NPIs.shape[0] == 0:
            R_eff = 0
        else:
            R_eff = case_after_NPIs["R_eff"].mean()
    else:
        R_eff = 0

    data2 = pd.DataFrame({"seed0": seed0, "R_eff": R_eff, "Date_detection": cut_off, "End_date": End_date}, index=[0])

    # Enhanced mask wearing
    input_data = f"{'../5. NPI_output/R1/Level_2_'}{prefix2}{'_seed_'}{seed0}{'.xlsx'}"
    simu_data = pd.read_excel(input_data)

    cut_off = simu_data["diag_tmp"].min()

    temp = simu_data[["id", "inf"]]
    temp.columns = ["infector", "inf1"]

    if temp.shape[0] > 3:
        simu_data = pd.merge(simu_data, temp, on="infector", how="left")
        case_after_NPIs = simu_data.loc[(simu_data["inf"] >= cut_off) & (simu_data["inf"] <= End_date)][["id", "inf"]]
        case_after_NPIs = case_after_NPIs.reset_index(drop=True)

        after_NPIs = simu_data[simu_data["infector"].isin(case_after_NPIs["id"])]
        R_eff = pd.DataFrame(after_NPIs.groupby(by=["infector"]).size())
        R_eff.columns = ["R_eff"]
        R_eff["id"] = R_eff.index
        R_eff = R_eff.reset_index(drop=True)
        case_after_NPIs = pd.merge(case_after_NPIs, R_eff, on="id", how="left")
        case_after_NPIs["R_eff"] = np.where(np.isnan(case_after_NPIs["R_eff"]), 0, case_after_NPIs["R_eff"])
        if case_after_NPIs.shape[0] == 0:
            R_eff = 0
        else:
            R_eff = case_after_NPIs["R_eff"].mean()
    else:
        R_eff = 0

    data3 = pd.DataFrame({"seed0": seed0, "R_eff": R_eff, "Date_detection": cut_off, "End_date": End_date}, index=[0])

    # Enhanced occupation surveillance
    input_data = f"{'../5. NPI_output/R1/Level_3_'}{prefix2}{'_seed_'}{seed0}{'.xlsx'}"
    simu_data = pd.read_excel(input_data)

    cut_off = simu_data["diag_tmp"].min()

    temp = simu_data[["id", "inf"]]
    temp.columns = ["infector", "inf1"]

    if temp.shape[0] > 3:
        simu_data = pd.merge(simu_data, temp, on="infector", how="left")
        case_after_NPIs = simu_data.loc[(simu_data["inf"] >= cut_off) & (simu_data["inf"] <= End_date)][["id", "inf"]]
        case_after_NPIs = case_after_NPIs.reset_index(drop=True)

        after_NPIs = simu_data[simu_data["infector"].isin(case_after_NPIs["id"])]
        R_eff = pd.DataFrame(after_NPIs.groupby(by=["infector"]).size())
        R_eff.columns = ["R_eff"]
        R_eff["id"] = R_eff.index
        R_eff = R_eff.reset_index(drop=True)
        case_after_NPIs = pd.merge(case_after_NPIs, R_eff, on="id", how="left")
        case_after_NPIs["R_eff"] = np.where(np.isnan(case_after_NPIs["R_eff"]), 0, case_after_NPIs["R_eff"])
        if case_after_NPIs.shape[0] == 0:
            R_eff = 0
        else:
            R_eff = case_after_NPIs["R_eff"].mean()
    else:
        R_eff = 0

    data4 = pd.DataFrame({"seed0": seed0, "R_eff": R_eff, "Date_detection": cut_off, "End_date": End_date}, index=[0])

    # Enhanced mass screening
    input_data = f"{'../5. NPI_output/R1/Level_4_'}{prefix2}{'_seed_'}{seed0}{'.xlsx'}"
    simu_data = pd.read_excel(input_data)

    cut_off = simu_data["diag_tmp"].min()

    temp = simu_data[["id", "inf"]]
    temp.columns = ["infector", "inf1"]

    if temp.shape[0] > 3:
        simu_data = pd.merge(simu_data, temp, on="infector", how="left")
        case_after_NPIs = simu_data.loc[(simu_data["inf"] >= cut_off) & (simu_data["inf"] <= End_date)][["id", "inf"]]
        case_after_NPIs = case_after_NPIs.reset_index(drop=True)

        after_NPIs = simu_data[simu_data["infector"].isin(case_after_NPIs["id"])]
        R_eff = pd.DataFrame(after_NPIs.groupby(by=["infector"]).size())
        R_eff.columns = ["R_eff"]
        R_eff["id"] = R_eff.index
        R_eff = R_eff.reset_index(drop=True)
        case_after_NPIs = pd.merge(case_after_NPIs, R_eff, on="id", how="left")
        case_after_NPIs["R_eff"] = np.where(np.isnan(case_after_NPIs["R_eff"]), 0, case_after_NPIs["R_eff"])
        if case_after_NPIs.shape[0] == 0:
            R_eff = 0
        else:
            R_eff = case_after_NPIs["R_eff"].mean()
    else:
        R_eff = 0

    data5 = pd.DataFrame({"seed0": seed0, "R_eff": R_eff, "Date_detection": cut_off, "End_date": End_date}, index=[0])

    # Enhanced mobility restriction
    input_data = f"{'../5. NPI_output/R1/Level_5_'}{prefix2}{'_seed_'}{seed0}{'.xlsx'}"
    simu_data = pd.read_excel(input_data)

    cut_off = simu_data["diag_tmp"].min()

    temp = simu_data[["id", "inf"]]
    temp.columns = ["infector", "inf1"]

    if temp.shape[0] > 3:
        simu_data = pd.merge(simu_data, temp, on="infector", how="left")
        case_after_NPIs = simu_data.loc[(simu_data["inf"] >= cut_off) & (simu_data["inf"] <= End_date)][["id", "inf"]]
        case_after_NPIs = case_after_NPIs.reset_index(drop=True)

        after_NPIs = simu_data[simu_data["infector"].isin(case_after_NPIs["id"])]
        R_eff = pd.DataFrame(after_NPIs.groupby(by=["infector"]).size())
        R_eff.columns = ["R_eff"]
        R_eff["id"] = R_eff.index
        R_eff = R_eff.reset_index(drop=True)
        case_after_NPIs = pd.merge(case_after_NPIs, R_eff, on="id", how="left")
        case_after_NPIs["R_eff"] = np.where(np.isnan(case_after_NPIs["R_eff"]), 0, case_after_NPIs["R_eff"])
        if case_after_NPIs.shape[0] == 0:
            R_eff = 0
        else:
            R_eff = case_after_NPIs["R_eff"].mean()
    else:
        R_eff = 0

    data6 = pd.DataFrame({"seed0": seed0, "R_eff": R_eff, "Date_detection": cut_off, "End_date": End_date}, index=[0])

    if seed0 == 1:
        output_data1 = data1
        output_data2 = data2
        output_data3 = data3
        output_data4 = data4
        output_data5 = data5
        output_data6 = data6

    else:
        output_data1 = output_data1.append(data1, ignore_index=True)
        output_data2 = output_data2.append(data2, ignore_index=True)
        output_data3 = output_data3.append(data3, ignore_index=True)
        output_data4 = output_data4.append(data4, ignore_index=True)
        output_data5 = output_data5.append(data5, ignore_index=True)
        output_data6 = output_data6.append(data6, ignore_index=True)


output1 = f"{'../3. result/R1/Level_0_'}{prefix2}{'.xlsx'}"
output_data1.to_excel(output1, index=False)
output2 = f"{'../3. result/R1/Level_1_'}{prefix2}{'.xlsx'}"
output_data2.to_excel(output2, index=False)
output3 = f"{'../3. result/R1/Level_2_'}{prefix2}{'.xlsx'}"
output_data3.to_excel(output3, index=False)
output4 = f"{'../3. result/R1/Level_3_'}{prefix2}{'.xlsx'}"
output_data4.to_excel(output4, index=False)
output5 = f"{'../3. result/R1/Level_4_'}{prefix2}{'.xlsx'}"
output_data5.to_excel(output5, index=False)
output6 = f"{'../3. result/R1/Level_5_'}{prefix2}{'.xlsx'}"
output_data6.to_excel(output6, index=False)

