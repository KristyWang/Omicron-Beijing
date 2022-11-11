# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime
from chinese_calendar import is_workday
import Function as Func
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)

pd.set_option('display.max_columns', 1000000)
pd.set_option('display.max_rows', 1000000)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 180)  # 设置打印宽度(**重要**)
pd.set_option('expand_frame_repr', False)  # 数据超过总宽度后，是否折叠显示

age_structure = "../1. data/age_structure.xlsx"
age_structure = pd.DataFrame(pd.read_excel(age_structure))

VE = "../1. data/VE.xlsx"
VE_table = pd.DataFrame(pd.read_excel(VE))


def branching_tree(seed0, Num_ini, end_date, Up_limit, R_no_vax, vax_stra, output):
    np.random.seed(seed=seed0)
    ref_date = datetime.datetime.strptime('2020-05-31 00:00:00', '%Y-%m-%d %H:%M:%S')
    col_name = ["g", "infector", "id", "age", "sex", "inf", "vax_status", "whe_symp", "Onset", "R0", "Workday",
                "Setting", "Activity1", "in_cm1", "Occupation", "Activity2", "in_cm2",
                "hh_id", "hh_size", "cm", "loc_resid", "loc_work", "loc_social_wkd",
                "loc_social_hld", "loc_trans_site", "Remove"]

    # initial case #
    ini_case = pd.DataFrame(index=range(1, Num_ini + 1), columns=col_name)
    ini_case["g"] = 1
    ini_case["infector"] = "ini"
    ini_case["id"] = range(1, Num_ini + 1)
    ini_case["sex"] = np.random.choice([1, 2], size=Num_ini)
    ini_case["inf"] = np.random.choice(range(-3, 1), size=Num_ini)
    ini_case["hh_id"] = ini_case["id"]
    ini_case["cm"] = ini_case["id"]
    ini_case["loc_resid"] = np.random.choice(Func.Beijing_street["ASCRIPTION"], size=Num_ini,
                                             p=Func.Beijing_street["Prob"])
    ini_case["Remove"] = 0
    for i in range(1, Num_ini + 1):
        age_l = np.random.choice(age_structure["age_l"], size=1, p=age_structure["Prob"])[0]
        ini_case.at[i, "age"] = np.random.choice(range(age_l, age_l + 5), size=1)[0]
        ini_case.at[i, "vax_status"] = Func.vax_func(vax_stra, ini_case.at[i, "age"])
        if ini_case.at[i, "vax_status"] == 0:
            VET = VE_table.loc[0, ]["VET"]
            VE_symp = VE_table.loc[0, ]["VES"]
        if ini_case.at[i, "vax_status"] == 2:
            VET = VE_table.loc[1, ]["VET"]
            VE_symp = VE_table.loc[1, ]["VES"]
        if (ini_case.at[i, "vax_status"] == 3) & (vax_stra == "hom"):
            VET = VE_table.loc[2, ]["VET"]
            VE_symp = VE_table.loc[2, ]["VES"]
        if (ini_case.at[i, "vax_status"] == 3) & (vax_stra == "het"):
            VET = VE_table.loc[3, ]["VET"]
            VE_symp = VE_table.loc[3, ]["VES"]
        ini_case.at[i, "R0"] = np.random.negative_binomial(R_no_vax * (1 - VET) * (1 - 0.43) / 0.43,
                                                           (1 - 0.43), size=1)[0]
        ini_case.at[i, "whe_symp"] = Func.symp_func(ini_case.at[i, "age"], VE_symp)
        if ini_case.at[i, "whe_symp"] == 1:
            ini_case.at[i, "Onset"] = ini_case.at[i, "inf"] + \
                                      int(np.random.gamma(shape=3.65, scale=1/0.63, size=1)[0])
        ini_case.at[i, "Workday"] = is_workday(datetime.timedelta(days=int(ini_case.at[i, "inf"])) + ref_date)
        ini_case.at[i, "hh_size"] = Func.hh_size_func(ini_case.at[i, "age"])
        ini_case.at[i, "Occupation"] = Func.Occupation_func("", "", ini_case.at[i, "age"], ini_case.at[i, "sex"])
        int_mat = Func.interaction_mat[Func.interaction_mat["start_place"] == ini_case.at[i, "loc_resid"]]
        if ini_case.at[i, "Occupation"] == "general_worker":
            ini_case.at[i, "loc_work"] = np.random.choice(int_mat["end_place"], 1,
                                                          p=int_mat["wk"] / int_mat["wk"].sum())[0]
        if ini_case.at[i, "Occupation"] == "service_worker":
            ini_case.at[i, "loc_work"] = np.random.choice(int_mat["end_place"], 1,
                                                          p=int_mat["serv"] / int_mat["serv"].sum())[0]
    hh_data = pd.DataFrame(ini_case[["hh_id", "hh_size"]])
    hh_data["No_inf"] = 1
    hh_data["hh_suscept"] = hh_data["hh_size"] - 1

    # Branching tree #
    simu_data = ini_case
    if simu_data["R0"].max() > 0:
        M = simu_data["inf"].min()
        data_M = simu_data[(simu_data["R0"] > 0) & (simu_data["inf"] == M)].reset_index(drop=True)
        while data_M.shape[0] == 0:
            M += 1
            data_M = simu_data[(simu_data["R0"] > 0) & (simu_data["inf"] == M)].reset_index(drop=True)

        while (M <= end_date) & (simu_data.loc[simu_data["inf"] == M].shape[0] < Up_limit):
            print(M, simu_data.loc[simu_data["inf"] == M].shape[0], simu_data.loc[simu_data["inf"] <= M].shape[0])
            for i in range(0, data_M.shape[0]):
                data_i = data_M.loc[i, ]
                for j in range(0, data_i["R0"]):
                    g = data_i["g"] + 1
                    infector = data_i["id"]
                    id = str(infector) + "_" + str(j + 1)
                    inf = data_i["inf"] + round(np.random.gamma(13.8556, 1 / 2.948, 1)[0])
                    Workday = is_workday(datetime.timedelta(days=int(inf)) + ref_date)
                    hh_suscept = int(hh_data.loc[hh_data["hh_id"] == data_i["hh_id"], "hh_suscept"])
                    Setting = Func.Setting_func(hh_suscept, data_i["Occupation"], Workday)
                    age = Func.age_func(data_i["age"], Setting)
                    vax_status = Func.vax_func(vax_stra, age)
                    if vax_status == 0:
                        VET = VE_table.loc[0, ]["VET"]
                        VEI = VE_table.loc[0, ]["VEI"]
                        VE_symp = VE_table.loc[0, ]["VES"]
                    if vax_status == 2:
                        VET = VE_table.loc[1, ]["VET"]
                        VEI = VE_table.loc[1, ]["VEI"]
                        VE_symp = VE_table.loc[1, ]["VES"]
                    if (vax_status == 3) & (vax_stra == "hom"):
                        VET = VE_table.loc[2, ]["VET"]
                        VEI = VE_table.loc[2, ]["VEI"]
                        VE_symp = VE_table.loc[2, ]["VES"]
                    if (vax_status == 3) & (vax_stra == "het"):
                        VET = VE_table.loc[3, ]["VET"]
                        VEI = VE_table.loc[3, ]["VEI"]
                        VE_symp = VE_table.loc[3, ]["VES"]
                    Remove = np.random.choice([1, 0], 1, p=[VEI, 1 - VEI])[0]
                    if Remove == 0:
                        R0 = np.random.negative_binomial(R_no_vax * (1 - VET) * (1 - 0.43) / 0.43, (1 - 0.43), 1)[0]
                        sex = np.random.choice([1, 2], 1, p=[0.5, 0.5])[0]
                        if (age >= 55) & (age < 60) & (Setting == "Workplace"):
                            sex = 1

                        if Setting == "Household":
                            hh_id = data_i["hh_id"]
                            hh_size = data_i["hh_size"]
                            hh_data["No_inf"] = np.where(hh_data["hh_id"] == data_i["hh_id"], hh_data["No_inf"] + 1,
                                                         hh_data["No_inf"])
                            hh_data["hh_suscept"] = np.where(hh_data["hh_id"] == data_i["hh_id"],
                                                             hh_data["hh_suscept"] - 1, hh_data["hh_suscept"])
                        else:
                            hh_id = id
                            hh_size = Func.hh_size_func(age)
                            hh_data.loc[hh_data.shape[0] + 1] = [hh_id, hh_size, 1, hh_size - 1]

                        whe_symp = Func.symp_func(age, VE_symp)
                        if whe_symp == 1:
                            onset = inf + int(np.random.gamma(shape=3.65, scale=1/0.63, size=1)[0])
                        else:
                            onset = np.nan

                        Activity1 = Func.activity_func(Setting, data_i["Occupation"])
                        Occupation = Func.Occupation_func(data_i["Occupation"], Activity1, age, sex)
                        Activity2 = Func.activity_func(Setting, Occupation)

                        if Setting == "Community":
                            in_cm1 = np.random.choice([0, 1], 1, p=[0.4, 0.6])[0]
                            in_cm2 = np.random.choice([0, 1], 1, p=[0.4, 0.6])[0]
                        else:
                            in_cm1 = np.nan
                            in_cm2 = np.nan

                        if (Setting == "Household") | ((in_cm1 == 1) & (in_cm2 == 1)):
                            cm = data_i["cm"]
                        else:
                            cm = hh_id

                        # network interaction model
                        if Activity1 == "Social":
                            if in_cm1 == 1:
                                data_i["loc_social_wkd"] = data_i["loc_resid"]
                                data_i["loc_social_hld"] = data_i["loc_resid"]
                            if in_cm1 == 0:
                                int_mat1 = Func.interaction_mat[Func.interaction_mat["start_place"] == data_i["loc_resid"]]
                                data_i["loc_social_wkd"] = np.random.choice(int_mat1["end_place"], 1,
                                                                            p=int_mat1["soc_wkd"] / int_mat1["soc_wkd"].sum())[0]
                                data_i["loc_social_hld"] = np.random.choice(int_mat1["end_place"], 1,
                                                                            p=int_mat1["soc_hld"] / int_mat1["soc_hld"].sum())[0]

                        location = Func.location_func(data_i["loc_resid"], data_i["loc_work"], data_i["loc_social_wkd"],
                                                      data_i["loc_social_hld"], Setting, Activity1, Activity2,
                                                      in_cm2, Workday, Occupation)

                        data1 = [g, infector, id, age, sex, inf, vax_status, whe_symp, onset, R0, Workday, Setting,
                                 Activity1, in_cm1, Occupation, Activity2, in_cm2, hh_id, hh_size, cm, location[0],
                                 location[1], "", "", location[2], Remove]

                        if inf > 0:
                            simu_data.loc[simu_data.shape[0] + 1] = data1
            if simu_data[(simu_data["R0"] > 0) & (simu_data["inf"] > M) & (simu_data["Remove"] == 0)].shape[0] > 0:
                M += 1
                data_M = simu_data[(simu_data["R0"] > 0) & (simu_data["inf"] == M) &
                                   (simu_data["Remove"] == 0)].reset_index(drop=True)
                while data_M.shape[0] == 0:
                    M += 1
                    data_M = simu_data[(simu_data["R0"] > 0) & (simu_data["inf"] == M) &
                                       (simu_data["Remove"] == 0)].reset_index(drop=True)
            else:
                break
    simu_data.to_excel(output, index=False)


Num_ini_x = 3
end_date_x = 30
Up_limit_x = 10000

R_no_vax_x = 7.5
vax_stra_x = "prm"

prefix2 = "_"
prefix1 = "../4. output/R1/"
prefix3 = "_seed_"
suffix = ".xlsx"

for seed0_x in range(1, 2):
    output_x = f"{prefix1}{vax_stra_x}{prefix2}{np.floor(R_no_vax_x)}{prefix3}{seed0_x}{suffix}"
    branching_tree(seed0_x, Num_ini_x, end_date_x, Up_limit_x, R_no_vax_x, vax_stra_x, output_x)
    print(output_x)
