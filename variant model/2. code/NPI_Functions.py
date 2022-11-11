# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import scipy.stats as st
import datetime
import Function as Func


pd.set_option('display.max_columns', 1000000)
pd.set_option('display.max_rows', 1000000)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 180)  # 设置打印宽度(**重要**)
pd.set_option('expand_frame_repr', False)   # 数据超过总宽度后，是否折叠显示
ref_date = datetime.datetime.strptime('2020-05-31 00:00:00', '%Y-%m-%d %H:%M:%S')


def pass_surv(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2):

    np.random.seed(seed=seed0)
    col_name = ["g", "infector", "id", "age", "sex", "inf", "vax_status", "whe_symp", "Onset", "R0", "Workday",
                "Setting", "Activity1", "in_cm1", "Occupation", "Activity2", "in_cm2",
                "hh_id", "hh_size", "iso_tmp", "diag_tmp", "found_way", "loc_resid", "cm", "loc_work",
                "loc_social_wkd", "loc_social_hld", "loc_trans_site", "Remove"]

    prefix1 = "../4. output/R1/"
    prefix4 = "_seed_"
    suffix = ".xlsx"
    input_data = f"{prefix1}{prefix2}{prefix4}{seed0}{suffix}"
    simu_data = pd.read_excel(input_data)

    # Passive hospital surveillance #
    simu_data["Random"] = np.random.choice([0, 1], simu_data.shape[0], p=[1 - hosp_prop, hosp_prop])
    simu_data["whe_hosp"] = np.where((simu_data["whe_symp"] == 1), simu_data["Random"], np.nan)
    # simu_data["Random"] = st.weibull_min.rvs(c=hosp_speed1, loc=0, scale=hosp_speed2, size=simu_data.shape[0])
    simu_data["Random"] = np.random.gamma(hosp_speed1, 1 / hosp_speed2, 1)[0]
    simu_data["iso_a"] = np.where((simu_data["whe_hosp"] == 1),
                                  simu_data["Onset"] + np.round(simu_data["Random"]), np.nan)

    for i in range(0, simu_data.shape[0]):
        if simu_data.at[i, "whe_hosp"] == 1:
            test_date = [int(simu_data.at[i, "iso_a"]), int(simu_data.at[i, "iso_a"]) + 2,
                         int(simu_data.at[i, "iso_a"]) + 6]
            simu_data.at[i, "diag_a"] = Func.diag_func(simu_data.at[i, "inf"], test_date)
        else:
            simu_data.at[i, "diag_a"] = np.nan

    temp = simu_data[["id", "iso_a"]]
    temp.columns = ["infector", "iso_a1"]

    simu_data = pd.merge(simu_data, temp, on="infector", how="left")
    simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso_a1"], 1, np.nan)

    id_ex = []
    for i in range(2, simu_data["g"].max() + 1):
        simu_data["Remove"] = np.where((simu_data["g"] == i) & (simu_data["infector"].isin(id_ex)),
                                       1, simu_data["Remove"])
        id_ex = simu_data[(simu_data["g"] == i) & (simu_data["Remove"] == 1)]["id"].values

    simu_data = simu_data[simu_data["Remove"] != 1].reset_index(drop=True)

    simu_data["iso_tmp"] = simu_data["iso_a"]
    simu_data["diag_tmp"] = simu_data["diag_a"]
    simu_data["found_way"] = np.where(~np.isnan(simu_data["diag_a"]), 1, np.nan)
    simu_data = simu_data[col_name]
    return simu_data


def act_surv(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2, Prob_test_h, Prob_test_m):

    np.random.seed(seed=seed0)
    col_name = ["g", "infector", "id", "age", "sex", "inf", "vax_status", "whe_symp", "Onset", "R0", "Workday",
                "Setting", "Activity1", "in_cm1", "Occupation", "Activity2", "in_cm2", "hh_id", "hh_size",
                "iso_tmp", "diag_tmp", "found_way",
                "loc_resid", "cm", "loc_work", "loc_social_wkd", "loc_social_hld", "loc_trans_site", "Remove"]

    simu_data = pass_surv(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2)
    simu_data["diag_c"] = np.nan

    # PCR-based surveillance
    # High-risk occupations: (2.5% RR=8  every 3 days) | (5% RR=7.5  every 3 days)
    simu_data["Random"] = np.random.choice([0, 1], simu_data.shape[0], p=[1 - Prob_test_h, Prob_test_h])
    simu_data["risk"] = np.where((simu_data["Occupation"] != "Non-worker") & (simu_data["Random"] == 1), 2, np.nan)
    # Middle-risk occupations: (7.5% RR=2 every 7 days) | (20% RR=1.875 every 7 days)
    simu_data["Random"] = np.random.choice([0, 1], simu_data.shape[0], p=[1 - Prob_test_m, Prob_test_m])
    simu_data["risk"] = np.where((simu_data["Occupation"] != "Non-worker") & (simu_data["Random"] == 1) &
                                 (simu_data["risk"] != 2), 1, simu_data["risk"])

    for i in range(0, simu_data.shape[0]):
        if simu_data.at[i, "risk"] >= 1:
            if simu_data.at[i, "risk"] == 2:
                Freq_test = 3
            if simu_data.at[i, "risk"] == 1:
                Freq_test = 7
            random = np.random.choice(range(0, Freq_test), 1)[0]
            times = int((30 - random) / Freq_test) + 1
            test_date = simu_data.at[i, "inf"] + np.linspace(random, random + Freq_test * (times - 1), times)
            simu_data.at[i, "diag_c"] = Func.diag_func(simu_data.at[i, "inf"], test_date)

    simu_data["iso_c"] = np.where(~np.isnan(simu_data["diag_c"]), simu_data["diag_c"], np.nan)

    simu_data["found_way"] = np.where((np.isnan(simu_data["iso_tmp"])) & (~np.isnan(simu_data["iso_c"])),
                                      3,  simu_data["found_way"])
    simu_data["diag_tmp"] = np.where((np.isnan(simu_data["iso_tmp"])) & (~np.isnan(simu_data["iso_c"])),
                                     simu_data["diag_c"], simu_data["diag_tmp"])
    simu_data["iso_tmp"] = np.where((np.isnan(simu_data["iso_tmp"])) & (~np.isnan(simu_data["iso_c"])),
                                    simu_data["iso_c"], simu_data["iso_tmp"])

    simu_data["found_way"] = np.where(simu_data["iso_tmp"] > simu_data["iso_c"],
                                      3, simu_data["found_way"])
    simu_data["diag_tmp"] = np.where(simu_data["iso_tmp"] > simu_data["iso_c"],
                                     simu_data["diag_c"], simu_data["diag_tmp"])
    simu_data["iso_tmp"] = np.where(simu_data["iso_tmp"] > simu_data["iso_c"],
                                    simu_data["iso_c"], simu_data["iso_tmp"])

    temp = simu_data[["id", "iso_tmp"]]
    temp.columns = ["infector", "iso_tmp1"]

    simu_data = pd.merge(simu_data, temp, on="infector", how="left")
    simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso_tmp1"], 1, np.nan)

    id_ex = []
    for i in range(2, simu_data["g"].max() + 1):
        simu_data["Remove"] = np.where((simu_data["g"] == i) & (simu_data["infector"].isin(id_ex)),
                                       1, simu_data["Remove"])
        id_ex = simu_data[(simu_data["g"] == i) & (simu_data["Remove"] == 1)]["id"].values

    simu_data = simu_data[simu_data["Remove"] != 1].reset_index(drop=True)

    simu_data = simu_data[col_name]
    return simu_data


def mask_wearing(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2, Prob_test_h, Prob_test_m,
                 Prob_mask_wk, Prob_mask_cm):

    np.random.seed(seed=seed0)
    col_name = ["g", "infector", "id", "age", "sex", "inf", "vax_status", "whe_symp", "Onset", "R0", "Workday",
                "Setting", "Activity1", "in_cm1", "Occupation", "Activity2", "in_cm2", "hh_id", "hh_size",
                "iso_tmp", "diag_tmp", "found_way",
                "loc_resid", "cm", "loc_work", "loc_social_wkd", "loc_social_hld", "loc_trans_site", "Remove"]

    simu_data = act_surv(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2, Prob_test_h, Prob_test_m)
    simu_data["whe_mask1"] = np.where(simu_data["Setting"] == "Household", 0, np.nan)
    simu_data["whe_mask2"] = np.where(simu_data["Setting"] == "Household", 0, np.nan)
    simu_data["Random"] = np.random.choice([0, 1], size=simu_data.shape[0], p=[1 - Prob_mask_wk, Prob_mask_wk])
    simu_data["whe_mask1"] = np.where(simu_data["Setting"] == "Workplace", simu_data["Random"], simu_data["whe_mask1"])
    simu_data["Random"] = np.random.choice([0, 1], size=simu_data.shape[0], p=[1 - Prob_mask_wk, Prob_mask_wk])
    simu_data["whe_mask2"] = np.where(simu_data["Setting"] == "Workplace", simu_data["Random"], simu_data["whe_mask2"])
    simu_data["Random"] = np.random.choice([0, 1], size=simu_data.shape[0], p=[1 - Prob_mask_cm, Prob_mask_cm])
    simu_data["whe_mask1"] = np.where(simu_data["Setting"] == "Community", simu_data["Random"], simu_data["whe_mask1"])
    simu_data["Random"] = np.random.choice([0, 1], size=simu_data.shape[0], p=[1 - Prob_mask_cm, Prob_mask_cm])
    simu_data["whe_mask2"] = np.where(simu_data["Setting"] == "Community", simu_data["Random"], simu_data["whe_mask2"])

    simu_data["Prob"] = np.where((simu_data["whe_mask1"] == 1) & (simu_data["whe_mask2"] == 1), 0.905 * 0.82, 1)
    simu_data["Prob"] = np.where((simu_data["whe_mask1"] == 0) & (simu_data["whe_mask2"] == 1), 0.82, simu_data["Prob"])
    simu_data["Prob"] = np.where((simu_data["whe_mask1"] == 1) & (simu_data["whe_mask2"] == 0), 0.905,
                                 simu_data["Prob"])

    for i in range(0, simu_data.shape[0]):
        simu_data.at[i, "Remove"] = np.random.choice([np.nan, 1], 1,
                                                     p=[simu_data.at[i, "Prob"], 1 - simu_data.at[i, "Prob"]])
    id_ex = []
    for i in range(2, simu_data["g"].max() + 1):
        simu_data["Remove"] = np.where((simu_data["g"] == i) & (simu_data["infector"].isin(id_ex)),
                                       1, simu_data["Remove"])
        id_ex = simu_data[(simu_data["g"] == i) & (simu_data["Remove"] == 1)]["id"].values

    simu_data = simu_data[simu_data["Remove"] != 1].reset_index(drop=True)
    simu_data = simu_data[col_name]
    return simu_data


def bs_NPI(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2, Prob_test_h, Prob_test_m,
           Prob_mask_wk, Prob_mask_cm, rnd_scr, Freq_scr, prob_out):

    Prob_travel = pd.DataFrame({
        "Within":    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        "Risk_Home": [0, 0, 0, 1, 1, 1, 2, 2, 2, 0, 1, 2],
        "Risk_Site": [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2],
        "Prob_out":  prob_out})

    np.random.seed(seed=seed0)
    col_name = ["g", "infector", "id", "age", "sex", "inf", "vax_status", "whe_symp", "Onset", "R0", "Workday",
                "Setting", "Activity1", "in_cm1", "Occupation", "Activity2", "in_cm2", "hh_id", "hh_size",
                "whe_trace", "index_case", "iso_b", "diag_b",
                "cm_test", "case_test", "iso_d", "diag_d", "cm_closed_first", "cm_closed_last", "Prob",
                "loc_scr", "case_scr", "iso_e", "diag_e",
                "iso_tmp", "diag_tmp", "found_way",
                "loc_resid", "cm", "loc_work", "loc_social_wkd", "loc_social_hld", "loc_trans_site", "Remove"]

    simu_data = mask_wearing(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2, Prob_test_h, Prob_test_m,
                             Prob_mask_wk, Prob_mask_cm)

    simu_data["whe_trace"] = np.nan
    simu_data["index_case"] = np.nan
    simu_data["iso_b"] = np.nan
    simu_data["diag_b"] = np.nan

    simu_data["cm_test"] = 0
    simu_data["case_test"] = np.nan
    simu_data["iso_d"] = np.nan
    simu_data["diag_d"] = np.nan
    simu_data["cm_closed_first"] = 0
    simu_data["cm_closed_last"] = 0
    simu_data["Prob"] = 1

    simu_data["loc_scr"] = 0
    simu_data["case_scr"] = np.nan
    simu_data["iso_e"] = np.nan
    simu_data["diag_e"] = np.nan

    simu_data = simu_data.sort_values(by="diag_tmp", ascending=True)

    i = np.floor(simu_data["diag_tmp"].min())
    index_case = simu_data[(simu_data["diag_tmp"] == i) & (simu_data["Remove"] != 1)].reset_index(drop=True)
    while i <= (np.floor(simu_data["diag_tmp"].max()) + 1):
        print(i)
        simu_data["index_case"] = np.where(simu_data["id"].isin(index_case["id"]), 1, simu_data["index_case"])

        # Household contact
        index0 = pd.DataFrame(index_case)
        # print(index0)
        index0 = index0[["hh_id", "iso_tmp", "diag_tmp"]].sort_values(by="iso_tmp", ascending=True).reset_index(drop=True)
        index0 = index0.drop_duplicates("hh_id").reset_index(drop=True)
        index0.columns = ["hh_id", "iso1", "diag1"]
        hh_cnt = simu_data[(simu_data["hh_id"].isin(index_case["hh_id"])) & (pd.isna(simu_data["index_case"])) &
                           (pd.isna(simu_data["whe_trace"])) & (simu_data["Remove"] != 1)]
        hh_cnt = pd.merge(hh_cnt, index0, on="hh_id", how="left")
        hh_cnt["whe_trace"] = 1
        hh_cnt["iso_b"] = hh_cnt["diag1"]
        hh_cnt = hh_cnt[["id", "inf", "whe_symp", "Onset", "whe_trace", "iso_b"]]

        # Forward
        index1 = pd.DataFrame(index_case)
        index1["trace_start"] = np.where((index1["whe_symp"] == 1) & (index1["Onset"] <= index1["diag_tmp"]),
                                         index1["Onset"] - 4, index1["diag_tmp"] - 4)
        index1 = index1[["id", "diag_tmp", "trace_start"]]
        # print(index1)
        index1.columns = ["infector", "diag1", "trace_start"]

        pros = simu_data[(simu_data["infector"].isin(index_case["id"]))
                         & (~simu_data["hh_id"].isin(index_case["hh_id"]))
                         & (pd.isna(simu_data["index_case"])) & (pd.isna(simu_data["whe_trace"]))
                         & (simu_data["Remove"] != 1)].reset_index(drop=True)
        pros = pd.merge(pros, index1, on="infector", how="left")

        pros["whe_trace"] = np.where((pros["Setting"] == "Workplace") & (pros["inf"] >= pros["trace_start"]),
                                     1, pros["whe_trace"])

        pros["whe_trace"] = np.where((pros["Setting"] == "Community") & (pros["Activity1"] == "Work") &
                                     (pros["Activity2"] == "Work") & (pros["inf"] >= pros["trace_start"]),
                                     1, pros["whe_trace"])

        pros["Random"] = np.random.choice([0, 1], pros.shape[0], p=[0.3, 0.7])
        pros["whe_trace"] = np.where((pros["Setting"] == "Community") & (pros["inf"] >= pros["trace_start"]) &
                                     (~((pros["Activity1"] == "Work") & (pros["Activity2"] == "Work"))),
                                     pros["Random"], pros["whe_trace"])

        # pros["Random"] = np.round(np.random.gamma(1.7914883, 1 / 0.6001156, pros.shape[0]))
        pros["Random"] = np.random.choice([0, 1, 2], pros.shape[0], p=[0.5, 0.3, 0.2])
        pros["iso_b"] = np.where(pros["whe_trace"] == 1, pros["diag1"] + pros["Random"], pros["iso_b"])

        # print(pros[["infector", "id", "index_case", "inf", "trace_start", "Setting", "Activity1", "Activity2",
        #             "whe_trace", "diag1", "iso_b"]])
        pros = pros[["id", "inf", "whe_symp", "Onset", "whe_trace", "iso_b"]]

        # Backward
        index2 = index_case
        index2 = index2[index2["infector"] != "ini"].reset_index(drop=True)
        index2 = index2.sort_values(by="Onset", ascending=True).reset_index(drop=True)
        index2 = index2.drop_duplicates(subset='infector').reset_index(drop=True)
        index2["trace_start"] = np.where((index2["whe_symp"] == 1) & (index2["Onset"] <= index2["diag_tmp"]),
                                         index2["Onset"] - 4, index2["diag_tmp"] - 4)

        index2["whe_trace"] = np.where((index2["Setting"] == "Workplace") & (index2["inf"] >= index2["trace_start"]),
                                       1, index2["whe_trace"])

        index2["whe_trace"] = np.where((index2["Setting"] == "Community") & (index2["Activity1"] == "Work") &
                                       (index2["Activity2"] == "Work") & (index2["inf"] >= index2["trace_start"]),
                                       1, index2["whe_trace"])

        index2["Random"] = np.random.choice([0, 1], index2.shape[0], p=[0.3, 0.7])
        index2["whe_trace"] = np.where((index2["Setting"] == "Community") & (index2["inf"] >= index2["trace_start"]) &
                                       (~((index2["Activity1"] == "Work") & (index2["Activity2"] == "Work"))),
                                       index2["Random"], index2["whe_trace"])

        # index2["Random"] = np.round(np.random.gamma(1.7914883, 1 / 0.6001156, index2.shape[0]))
        index2["Random"] = np.random.choice([0, 1, 2], index2.shape[0], p=[0.5, 0.3, 0.2])
        index2["iso_b"] = np.where(index2["whe_trace"] == 1, index2["diag_tmp"] + index2["Random"], index2["iso_b"])

        # print(index2[["infector", "id", "index_case", "Setting", "Activity1", "Activity2",
        #               "inf", "trace_start", "whe_trace", "iso_b"]])

        index2 = index2[["infector", "whe_trace", "iso_b"]]
        index2.columns = ["id", "whe_trace", "iso_b"]
        retros = simu_data[["id", "index_case", "whe_trace", "Remove", "inf", "whe_symp", "Onset"]]
        retros.columns = ["id", "index_case", "whe_trace1", "Remove", "inf", "whe_symp", "Onset"]
        retros = pd.DataFrame(pd.merge(index2, retros, on="id", how="left"))
        retros = retros[(pd.isna(retros["index_case"])) & (retros["whe_trace1"] != 1) & (~retros["id"].isin(pros["id"]))
                        & (~retros["id"].isin(hh_cnt["id"])) & (retros["Remove"] != 1)].reset_index(drop=True)
        retros = retros[["id", "inf", "whe_symp", "Onset", "whe_trace", "iso_b"]]
        # print(retros)

        # All contacts
        cnt_data = hh_cnt.append(pros, ignore_index=True).append(retros, ignore_index=True)
        cnt_data = cnt_data[(cnt_data["whe_trace"] == 1)].reset_index(drop=True)
        cnt_data["diag_b"] = np.nan
        for j in range(0, cnt_data.shape[0]):
            if ~np.isnan(cnt_data.at[j, "iso_b"]):
                smp_test = Func.test_proc(cnt_data.at[j, "whe_symp"], cnt_data.at[j, "Onset"], cnt_data.at[j, "iso_b"])
                cnt_data.at[j, "diag_b"] = Func.diag_func(cnt_data.at[j, "inf"], smp_test)
        cnt_data = cnt_data[["id", "whe_trace", "iso_b", "diag_b"]]
        cnt_data.columns = ["id", "whe_trace1", "iso_b1", "diag_b1"]
        # print(cnt_data)
        simu_data = pd.merge(simu_data, cnt_data, on="id", how="left")
        simu_data["whe_trace"] = np.where(simu_data["id"].isin(cnt_data["id"]),
                                          simu_data["whe_trace1"], simu_data["whe_trace"])
        simu_data["iso_b"] = np.where(simu_data["id"].isin(cnt_data["id"]), simu_data["iso_b1"], simu_data["iso_b"])
        simu_data["diag_b"] = np.where(simu_data["id"].isin(cnt_data["id"]), simu_data["diag_b1"], simu_data["diag_b"])

        simu_data["diag_tmp"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (np.isnan(simu_data["iso_tmp"])),
                                         simu_data["diag_b"], simu_data["diag_tmp"])
        simu_data["found_way"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (np.isnan(simu_data["iso_tmp"])) &
                                          (~np.isnan(simu_data["diag_b"])), 2, simu_data["found_way"])
        simu_data["iso_tmp"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (np.isnan(simu_data["iso_tmp"])),
                                        simu_data["iso_b"], simu_data["iso_tmp"])

        simu_data["diag_tmp"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (~np.isnan(simu_data["iso_tmp"])) &
                                         (simu_data["iso_tmp"] > simu_data["iso_b"]), simu_data["diag_b"],
                                         simu_data["diag_tmp"])
        simu_data["found_way"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (~np.isnan(simu_data["iso_tmp"])) &
                                          (simu_data["iso_tmp"] > simu_data["iso_b"]) &
                                          (~np.isnan(simu_data["diag_b"])), 2, simu_data["found_way"])
        simu_data["iso_tmp"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (~np.isnan(simu_data["iso_tmp"])) &
                                        (simu_data["iso_tmp"] > simu_data["iso_b"]), simu_data["iso_b"],
                                        simu_data["iso_tmp"])

        temp = simu_data[["id", "iso_tmp", "diag_tmp"]]
        temp.columns = ["infector", "iso1", "diag1"]
        simu_data = pd.DataFrame(pd.merge(simu_data, temp, on="infector", how="left"))
        simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso1"], 1, simu_data["Remove"])
        simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso_tmp"], 1, simu_data["Remove"])

        id_ex = simu_data[(simu_data["Remove"] == 1) & (simu_data["g"] == 1)]["id"].values
        for k in range(2, simu_data["g"].max() + 1):
            simu_data["Remove"] = np.where((simu_data["g"] == k) & (simu_data["infector"].isin(id_ex)), 1,
                                           simu_data["Remove"])
            id_ex = simu_data[(simu_data["g"] == k) & (simu_data["Remove"] == 1)]["id"].values

        simu_data = simu_data.loc[simu_data["Remove"] != 1, col_name]
        simu_data = simu_data.reset_index(drop=True)
        # print(simu_data[(simu_data["id"].isin(cnt_data["id"])) | (simu_data["id"].isin(index_case["id"]))])

        index3 = simu_data[(simu_data["diag_tmp"] == i) & (simu_data["Remove"] != 1) &
                           (simu_data["id"].isin(cnt_data["id"]))]

        if index3.shape[0] != 0:
            index_case = index3.reset_index(drop=True)
        if index3.shape[0] == 0:
            # Closed management of community
            index_cm = simu_data[(simu_data["diag_tmp"] == i)].reset_index(drop=True)
            simu_data["case_test"] = np.where(((simu_data["iso_tmp"] > i + 1) | (np.isnan(simu_data["iso_tmp"]))) &
                                              (simu_data["cm"].isin(index_cm["cm"])) & (simu_data["cm_test"] == 0),
                                              i + 1, simu_data["case_test"])

            simu_data["cm_test"] = np.where((simu_data["cm"].isin(index_cm["cm"])) & (simu_data["cm_test"] == 0),
                                            i + 1, simu_data["cm_test"])

            simu_data["cm_closed_first"] = np.where((simu_data["cm"].isin(index_cm["cm"])) &
                                                    (simu_data["cm_closed_first"] == 0),
                                                    i, simu_data["cm_closed_first"])
            simu_data["cm_closed_last"] = np.where((simu_data["cm"].isin(index_cm["cm"])) &
                                                   (simu_data["cm_closed_last"] < i + 13),
                                                   i + 13, simu_data["cm_closed_last"])
            cm_test_case = simu_data.loc[simu_data["case_test"] == i + 1].reset_index(drop=True)
            if cm_test_case.shape[0] != 0:
                for j in range(0, cm_test_case.shape[0]):
                    cm_test_case.at[j, "diag_d"] = Func.diag_func(cm_test_case.at[j, "inf"], [i + 1, i + 7, i + 12])

            cm_test_case["iso_d"] = np.where(~np.isnan(cm_test_case["diag_d"]),
                                             cm_test_case["diag_d"], cm_test_case["iso_d"])
            cm_test_case = cm_test_case[["id", "iso_d", "diag_d"]]
            cm_test_case.columns = ["id", "iso_d1", "diag_d1"]
            simu_data = pd.merge(simu_data, cm_test_case, on="id", how="left")
            simu_data["iso_d"] = np.where(simu_data["id"].isin(cm_test_case["id"]),
                                          simu_data["iso_d1"], simu_data["iso_d"])
            simu_data["diag_d"] = np.where(simu_data["id"].isin(cm_test_case["id"]),
                                           simu_data["diag_d1"], simu_data["diag_d"])

            simu_data["diag_tmp"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                             (np.isnan(simu_data["iso_tmp"])),
                                             simu_data["diag_d"], simu_data["diag_tmp"])
            simu_data["found_way"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                              (np.isnan(simu_data["iso_tmp"])) & (~np.isnan(simu_data["diag_d"])),
                                              4, simu_data["found_way"])
            simu_data["iso_tmp"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                            (np.isnan(simu_data["iso_tmp"])),
                                            simu_data["iso_d"], simu_data["iso_tmp"])

            simu_data["diag_tmp"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                             (~np.isnan(simu_data["iso_tmp"])) &
                                             (simu_data["iso_tmp"] > simu_data["iso_d"]),
                                             simu_data["diag_d"], simu_data["diag_tmp"])
            simu_data["found_way"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                              (~np.isnan(simu_data["iso_tmp"])) &
                                              (simu_data["iso_tmp"] > simu_data["iso_d"]) &
                                              (~np.isnan(simu_data["diag_d"])), 4, simu_data["found_way"])
            simu_data["iso_tmp"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                            (~np.isnan(simu_data["iso_tmp"])) &
                                            (simu_data["iso_tmp"] > simu_data["iso_d"]),
                                            simu_data["iso_d"], simu_data["iso_tmp"])

            temp = simu_data[["id", "iso_tmp", "diag_tmp", "cm_closed_first", "cm_closed_last"]]
            temp.columns = ["infector", "iso1", "diag1", "cm_closed_first1", "cm_closed_last1"]
            simu_data = pd.DataFrame(pd.merge(simu_data, temp, on="infector", how="left"))
            simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso1"], 1, simu_data["Remove"])

            simu_data["Prob"] = np.where((simu_data["Setting"] == "Workplace") &
                                         (((simu_data["cm_closed_first1"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last1"] >= simu_data["inf"])) |
                                          ((simu_data["cm_closed_first"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last"] >= simu_data["inf"]))),
                                         0, simu_data["Prob"])

            simu_data["Prob"] = np.where((simu_data["Setting"] == "Community") &
                                         (~((simu_data["in_cm1"] == 1) & (simu_data["in_cm2"] == 1))) &
                                         (((simu_data["cm_closed_first1"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last1"] >= simu_data["inf"])) |
                                          ((simu_data["cm_closed_first"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last"] >= simu_data["inf"]))),
                                         0, simu_data["Prob"])

            simu_data["Prob"] = np.where((simu_data["Setting"] == "Community") &
                                         ((simu_data["in_cm1"] == 1) & (simu_data["in_cm2"] == 1)) &
                                         (((simu_data["cm_closed_first1"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last1"] >= simu_data["inf"])) |
                                          ((simu_data["cm_closed_first"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last"] >= simu_data["inf"]))),
                                         0.1, simu_data["Prob"])

            simu_data["Remove"] = np.where(simu_data["Prob"] == 0, 1, simu_data["Remove"])
            simu_data["Remove"] = np.where((simu_data["Prob"] == 0.1) & (simu_data["Remove"] != 1),
                                           np.random.choice([0, 1], 1, p=[0.1, 0.9])[0], simu_data["Remove"])

            # Remove later generations
            id_ex = simu_data[(simu_data["Remove"] == 1) & (simu_data["g"] == 1)]["id"].values
            for k in range(2, simu_data["g"].max() + 1):
                simu_data["Remove"] = np.where((simu_data["g"] == k) & (simu_data["infector"].isin(id_ex)), 1,
                                               simu_data["Remove"])
                id_ex = simu_data[(simu_data["g"] == k) & (simu_data["Remove"] == 1)]["id"].values

            simu_data = simu_data.loc[simu_data["Remove"] != 1, col_name]
            simu_data = simu_data.reset_index(drop=True)

            # Mass screening
            # Diagnosed cases at date i : who trigger mass screening
            index_scr = simu_data[(simu_data["diag_tmp"] == i)].reset_index(drop=True)

            simu_data["case_scr"] = np.where((simu_data["loc_resid"].isin(index_scr["loc_resid"])) &
                                             (simu_data["loc_scr"] == 0) & (simu_data["Remove"] != 1) &
                                             ((np.floor(simu_data["iso_tmp"]) > i + 1) |
                                              (np.isnan(simu_data["iso_tmp"]))) &
                                             ((simu_data["cm_test"] > i + 1) | (simu_data["cm_test"] == 0)),
                                             i + 1, simu_data["case_scr"])

            simu_data["loc_scr"] = np.where((simu_data["loc_resid"].isin(index_scr["loc_resid"])) &
                                            (simu_data["loc_scr"] == 0), i + 1, simu_data["loc_scr"])

            scr_case = simu_data[simu_data["case_scr"] == i + 1].reset_index(drop=True)
            if scr_case.shape[0] != 0:
                for j in range(0, scr_case.shape[0]):
                    scr_date = i + np.random.choice(range(1, Freq_scr + 1), 1)[0]
                    scr_date = np.linspace(scr_date, scr_date + Freq_scr * (rnd_scr - 1), rnd_scr)
                    scr_case.at[j, "diag_e"] = Func.diag_func(scr_case.at[j, "inf"], scr_date)

                scr_case["iso_e"] = scr_case["diag_e"]
                scr_case = scr_case.loc[~np.isnan(scr_case["diag_e"])][["id", "iso_e", "diag_e"]]
                # print(scr_case)
                scr_case.columns = ["id", "iso_e1", "diag_e1"]
                simu_data = pd.merge(simu_data, scr_case, on="id", how="left")
                simu_data["iso_e"] = np.where(simu_data["id"].isin(scr_case["id"]),
                                              simu_data["iso_e1"], simu_data["iso_e"])
                simu_data["diag_e"] = np.where(simu_data["id"].isin(scr_case["id"]),
                                               simu_data["diag_e1"], simu_data["diag_e"])

                simu_data["diag_tmp"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                 (np.isnan(simu_data["iso_tmp"])),
                                                 simu_data["diag_e"], simu_data["diag_tmp"])
                simu_data["found_way"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                  (np.isnan(simu_data["iso_tmp"])) & (~np.isnan(simu_data["diag_e"])),
                                                  5, simu_data["found_way"])
                simu_data["iso_tmp"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                (np.isnan(simu_data["iso_tmp"])),
                                                simu_data["iso_e"], simu_data["iso_tmp"])

                simu_data["diag_tmp"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                 (~np.isnan(simu_data["iso_tmp"])) &
                                                 (simu_data["iso_tmp"] > simu_data["iso_e"]),
                                                 simu_data["diag_e"], simu_data["diag_tmp"])
                simu_data["found_way"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                  (~np.isnan(simu_data["iso_tmp"])) &
                                                  (simu_data["iso_tmp"] > simu_data["iso_e"]) &
                                                  (~np.isnan(simu_data["diag_e"])), 5, simu_data["found_way"])
                simu_data["iso_tmp"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                (~np.isnan(simu_data["iso_tmp"])) &
                                                (simu_data["iso_tmp"] > simu_data["iso_e"]),
                                                simu_data["iso_e"], simu_data["iso_tmp"])

                temp = simu_data[["id", "iso_tmp", "diag_tmp"]]
                temp.columns = ["infector", "iso1", "diag1"]
                simu_data = pd.DataFrame(pd.merge(simu_data, temp, on="infector", how="left"))
                simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso1"], 1, simu_data["Remove"])

                # Remove later generation
                id_ex = simu_data[(simu_data["Remove"] == 1) & (simu_data["g"] == 1)]["id"].values
                for k in range(2, simu_data["g"].max() + 1):
                    simu_data["Remove"] = np.where((simu_data["g"] == k) & (simu_data["infector"].isin(id_ex)), 1,
                                                   simu_data["Remove"])
                    id_ex = simu_data[(simu_data["g"] == k) & (simu_data["Remove"] == 1)]["id"].values

                simu_data = simu_data.loc[simu_data["Remove"] != 1, col_name]
                simu_data = simu_data.reset_index(drop=True)

            # Risk regions
            # Diagnosed cases in the past 14 days
            case_14d = simu_data[(simu_data["Remove"] != 1) & (simu_data["diag_tmp"] >= i - 13) &
                                 (simu_data["diag_tmp"] <= i)].reset_index(drop=True)
            # if case_14d.shape[0] == 0:
            #     print(i, "clear")
            if case_14d.shape[0] != 0:
                case_freq = pd.DataFrame(case_14d.groupby(by=["loc_resid"]).size())
                case_freq["inf"] = i + 1
                case_freq["loc_resid"] = case_freq.index
                case_freq = case_freq.reset_index(drop=True)
                case_freq.columns = ["Num", "inf", "loc_resid"]
                # Risk level of each street
                # 1. Number of diagnosed cases 2 - 5: Middle risk areas
                # 2. Number of diagnosed cases more than 5: High risk areas
                case_freq["Risk"] = np.where(case_freq["Num"] <= 5, 1, 2)
                case_freq["Risk"] = np.where(case_freq["Num"] == 1, 0, case_freq["Risk"])
                case_freq = case_freq[["inf", "loc_resid", "Num", "Risk"]]
                # print(case_freq)

                temp = simu_data[["id", "loc_resid"]]
                temp.columns = ["infector", "loc_resid1"]
                simu_data = pd.DataFrame(pd.merge(simu_data, temp, on="infector", how="left"))

                # New infections in the (i + 1)th day
                case_inf = simu_data[(simu_data["inf"] == i + 1) & (simu_data["Remove"] != 1)]
                # Risk level of each street
                case_inf = pd.merge(case_inf, case_freq, on=["inf", "loc_resid"], how="left")

                case_freq.columns = ["inf", "loc_resid1", "Num1", "Risk1"]
                case_inf = pd.DataFrame(pd.merge(case_inf, case_freq, on=["inf", "loc_resid1"], how="left"))

                case_freq.columns = ["inf", "loc_trans_site", "Num_Site", "Risk_Site"]
                case_inf = pd.DataFrame(pd.merge(case_inf, case_freq, on=["inf", "loc_trans_site"], how="left"))

                # Low risk: No new infections detected in the past 14 days
                # Low risk streets not included in the case_freq dataset, thus the risk level is empty
                case_inf["Risk1"] = np.where((case_inf["infector"] != "ini") & (np.isnan(case_inf["Risk1"])),
                                             0, case_inf["Risk1"])
                case_inf["Risk"] = np.where(np.isnan(case_inf["Risk"]), 0, case_inf["Risk"])
                case_inf["Risk_Site"] = np.where(np.isnan(case_inf["Risk_Site"]), 0, case_inf["Risk_Site"])
                case_inf = case_inf.reset_index(drop=True)
                # print(case_inf)

                # Prob_a: probability that the infector move out of home given the risk level of their residential areas
                # Prob_b: Probability that the infectee move out of home given the risk level of their residential areas
                case_inf["Prob_a"] = 1.0
                case_inf["Prob_b"] = 1.0
                for r in range(0, case_inf.shape[0]):

                    # Move out of the street (infector)
                    if (case_inf.at[r, "infector"] != "ini") & \
                            (case_inf.at[r, "loc_resid1"] != case_inf.at[r, "loc_trans_site"]):
                        case_inf.at[r, "Prob_a"] = Prob_travel.loc[(Prob_travel["Within"] == 0) &
                                                                   (Prob_travel["Risk_Home"] == case_inf.at[r, "Risk1"])
                                                                   & (Prob_travel["Risk_Site"] ==
                                                                      case_inf.at[r, "Risk_Site"]), "Prob_out"]

                    # Move out of the street (infectee)
                    if case_inf.at[r, "loc_resid"] != case_inf.at[r, "loc_trans_site"]:
                        case_inf.at[r, "Prob_b"] = Prob_travel.loc[(Prob_travel["Within"] == 0) &
                                                                   (Prob_travel["Risk_Home"] == case_inf.at[r, "Risk"])
                                                                   & (Prob_travel["Risk_Site"] ==
                                                                      case_inf.at[r, "Risk_Site"]), "Prob_out"]

                    # Move within the street (infector)
                    if (case_inf.at[r, "loc_resid1"] == case_inf.at[r, "loc_trans_site"]) & \
                            (case_inf.at[r, "Setting"] != "Household"):
                        case_inf.at[r, "Prob_a"] = Prob_travel.loc[(Prob_travel["Risk_Home"] == case_inf.at[r, "Risk1"])
                                                                   & (Prob_travel["Within"] == 1), "Prob_out"]

                    # Move within the street (infectee)
                    if (case_inf.at[r, "loc_resid"] == case_inf.at[r, "loc_trans_site"]) & \
                            (case_inf.at[r, "Setting"] != "Household"):
                        case_inf.at[r, "Prob_b"] = Prob_travel.loc[(Prob_travel["Risk_Home"] == case_inf.at[r, "Risk"])
                                                                   & (Prob_travel["Within"] == 1), "Prob_out"]
                # Prob that the transmission event occur
                case_inf["Prob"] = np.where(case_inf["Prob_a"] * case_inf["Prob_b"] < case_inf["Prob"],
                                            case_inf["Prob_a"] * case_inf["Prob_b"], case_inf["Prob"])

                for k in range(0, case_inf.shape[0]):
                    Random = np.random.choice([0, 1], 1, p=[case_inf.at[k, "Prob"], (1 - case_inf.at[k, "Prob"])])[0]
                    if (Random == 1) & (case_inf.at[k, "Setting"] != "Household"):
                        case_inf.at[k, "Remove"] = 1

                # print(case_inf[["g", "inf", "Setting", "in_cm1", "in_cm2",
                #                 "Risk1", "Risk", "Risk_Site", "cm_closed_first", "cm_closed_last",
                #                 "loc_resid1", "loc_resid", "loc_trans_site",
                #                 "Prob_a", "Prob_b", "Prob", "Remove"]])

                # remove later generation
                id_ex = case_inf.loc[case_inf["Remove"] == 1, "id"]
                simu_data["Remove"] = np.where(simu_data["id"].isin(id_ex), 1, simu_data["Remove"])
                while len(id_ex) != 0:
                    simu_data["Remove"] = np.where(simu_data["infector"].isin(id_ex), 1, simu_data["Remove"])
                    id_ex = simu_data.loc[simu_data["infector"].isin(id_ex), "id"]

                simu_data = simu_data.loc[simu_data["Remove"] != 1, col_name]
                simu_data = simu_data.reset_index(drop=True)

            i += 1
            index_case = simu_data[(simu_data["diag_tmp"] == i) & (simu_data["Remove"] != 1)].reset_index(drop=True)
    return simu_data


def Enhance_mass_scr(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2, Prob_test_h, Prob_test_m,
                     Prob_mask_wk, Prob_mask_cm, rnd_scr, Freq_scr, prob_out):

    Prob_travel = pd.DataFrame({
        "Within": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        "Risk_Home": [0, 0, 0, 1, 1, 1, 2, 2, 2, 0, 1, 2],
        "Risk_Site": [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2],
        "Prob_out": prob_out})

    np.random.seed(seed=seed0)
    col_name = ["g", "infector", "id", "age", "sex", "inf", "vax_status", "whe_symp", "Onset", "R0", "Workday",
                "Setting", "Activity1", "in_cm1", "Occupation", "Activity2", "in_cm2", "hh_id", "hh_size",
                "whe_trace", "index_case", "iso_b", "diag_b",
                "cm_test", "case_test", "iso_d", "diag_d", "cm_closed_first", "cm_closed_last", "Prob",
                "loc_scr", "case_scr", "iso_e", "diag_e",
                "iso_tmp", "diag_tmp", "found_way",
                "loc_resid", "cm", "loc_work", "loc_social_wkd", "loc_social_hld", "loc_trans_site", "Remove"]

    simu_data = mask_wearing(prefix2, seed0, hosp_prop, hosp_speed1, hosp_speed2, Prob_test_h, Prob_test_m,
                             Prob_mask_wk, Prob_mask_cm)

    simu_data["whe_trace"] = np.nan
    simu_data["index_case"] = np.nan
    simu_data["iso_b"] = np.nan
    simu_data["diag_b"] = np.nan

    simu_data["cm_test"] = 0
    simu_data["case_test"] = np.nan
    simu_data["iso_d"] = np.nan
    simu_data["diag_d"] = np.nan
    simu_data["cm_closed_first"] = 0
    simu_data["cm_closed_last"] = 0
    simu_data["Prob"] = 1

    simu_data["loc_scr"] = 0
    simu_data["case_scr"] = np.nan
    simu_data["iso_e"] = np.nan
    simu_data["diag_e"] = np.nan

    simu_data = simu_data.sort_values(by="diag_tmp", ascending=True)

    i = np.floor(simu_data["diag_tmp"].min())
    index_case = simu_data[(simu_data["diag_tmp"] == i) & (simu_data["Remove"] != 1)].reset_index(drop=True)
    while i <= (np.floor(simu_data["diag_tmp"].max()) + 1):
        print(i)
        simu_data["index_case"] = np.where(simu_data["id"].isin(index_case["id"]), 1, simu_data["index_case"])

        # Household contact
        index0 = pd.DataFrame(index_case)
        # print(index0)
        index0 = index0[["hh_id", "iso_tmp", "diag_tmp"]].sort_values(by="iso_tmp", ascending=True).reset_index(drop=True)
        index0 = index0.drop_duplicates("hh_id").reset_index(drop=True)
        index0.columns = ["hh_id", "iso1", "diag1"]
        hh_cnt = simu_data[(simu_data["hh_id"].isin(index_case["hh_id"])) & (pd.isna(simu_data["index_case"])) &
                           (pd.isna(simu_data["whe_trace"])) & (simu_data["Remove"] != 1)]
        hh_cnt = pd.merge(hh_cnt, index0, on="hh_id", how="left")
        hh_cnt["whe_trace"] = 1
        hh_cnt["iso_b"] = hh_cnt["diag1"]
        hh_cnt = hh_cnt[["id", "inf", "whe_symp", "Onset", "whe_trace", "iso_b"]]

        # Forward
        index1 = pd.DataFrame(index_case)
        index1["trace_start"] = np.where((index1["whe_symp"] == 1) & (index1["Onset"] <= index1["diag_tmp"]),
                                         index1["Onset"] - 4, index1["diag_tmp"] - 4)
        index1 = index1[["id", "diag_tmp", "trace_start"]]
        # print(index1)
        index1.columns = ["infector", "diag1", "trace_start"]

        pros = simu_data[(simu_data["infector"].isin(index_case["id"]))
                         & (~simu_data["hh_id"].isin(index_case["hh_id"]))
                         & (pd.isna(simu_data["index_case"])) & (pd.isna(simu_data["whe_trace"]))
                         & (simu_data["Remove"] != 1)].reset_index(drop=True)
        pros = pd.merge(pros, index1, on="infector", how="left")

        pros["whe_trace"] = np.where((pros["Setting"] == "Workplace") & (pros["inf"] >= pros["trace_start"]),
                                     1, pros["whe_trace"])

        pros["whe_trace"] = np.where((pros["Setting"] == "Community") & (pros["Activity1"] == "Work") &
                                     (pros["Activity2"] == "Work") & (pros["inf"] >= pros["trace_start"]),
                                     1, pros["whe_trace"])

        pros["Random"] = np.random.choice([0, 1], pros.shape[0], p=[0.3, 0.7])
        pros["whe_trace"] = np.where((pros["Setting"] == "Community") & (pros["inf"] >= pros["trace_start"]) &
                                     (~((pros["Activity1"] == "Work") & (pros["Activity2"] == "Work"))),
                                     pros["Random"], pros["whe_trace"])

        # pros["Random"] = np.round(np.random.gamma(1.7914883, 1 / 0.6001156, pros.shape[0]))
        pros["Random"] = np.random.choice([0, 1, 2], pros.shape[0], p=[0.5, 0.3, 0.2])
        pros["iso_b"] = np.where(pros["whe_trace"] == 1, pros["diag1"] + pros["Random"], pros["iso_b"])

        # print(pros[["infector", "id", "index_case", "inf", "trace_start", "Setting", "Activity1", "Activity2",
        #             "whe_trace", "diag1", "iso_b"]])
        pros = pros[["id", "inf", "whe_symp", "Onset", "whe_trace", "iso_b"]]

        # Backward
        index2 = index_case
        index2 = index2[index2["infector"] != "ini"].reset_index(drop=True)
        index2 = index2.sort_values(by="Onset", ascending=True).reset_index(drop=True)
        index2 = index2.drop_duplicates(subset='infector').reset_index(drop=True)
        index2["trace_start"] = np.where((index2["whe_symp"] == 1) & (index2["Onset"] <= index2["diag_tmp"]),
                                         index2["Onset"] - 4, index2["diag_tmp"] - 4)

        index2["whe_trace"] = np.where((index2["Setting"] == "Workplace") & (index2["inf"] >= index2["trace_start"]),
                                       1, index2["whe_trace"])

        index2["whe_trace"] = np.where((index2["Setting"] == "Community") & (index2["Activity1"] == "Work") &
                                       (index2["Activity2"] == "Work") & (index2["inf"] >= index2["trace_start"]),
                                       1, index2["whe_trace"])

        index2["Random"] = np.random.choice([0, 1], index2.shape[0], p=[0.3, 0.7])
        index2["whe_trace"] = np.where((index2["Setting"] == "Community") & (index2["inf"] >= index2["trace_start"]) &
                                       (~((index2["Activity1"] == "Work") & (index2["Activity2"] == "Work"))),
                                       index2["Random"], index2["whe_trace"])

        # index2["Random"] = np.round(np.random.gamma(1.7914883, 1 / 0.6001156, index2.shape[0]))
        index2["Random"] = np.random.choice([0, 1, 2], index2.shape[0], p=[0.5, 0.3, 0.2])
        index2["iso_b"] = np.where(index2["whe_trace"] == 1, index2["diag_tmp"] + index2["Random"], index2["iso_b"])

        # print(index2[["infector", "id", "index_case", "Setting", "Activity1", "Activity2",
        #               "inf", "trace_start", "whe_trace", "iso_b"]])

        index2 = index2[["infector", "whe_trace", "iso_b"]]
        index2.columns = ["id", "whe_trace", "iso_b"]
        retros = simu_data[["id", "index_case", "whe_trace", "Remove", "inf", "whe_symp", "Onset"]]
        retros.columns = ["id", "index_case", "whe_trace1", "Remove", "inf", "whe_symp", "Onset"]
        retros = pd.DataFrame(pd.merge(index2, retros, on="id", how="left"))
        retros = retros[(pd.isna(retros["index_case"])) & (retros["whe_trace1"] != 1) & (~retros["id"].isin(pros["id"]))
                        & (~retros["id"].isin(hh_cnt["id"])) & (retros["Remove"] != 1)].reset_index(drop=True)
        retros = retros[["id", "inf", "whe_symp", "Onset", "whe_trace", "iso_b"]]
        # print(retros)

        # All contacts
        cnt_data = hh_cnt.append(pros, ignore_index=True).append(retros, ignore_index=True)
        cnt_data = cnt_data[(cnt_data["whe_trace"] == 1)].reset_index(drop=True)
        cnt_data["diag_b"] = np.nan
        for j in range(0, cnt_data.shape[0]):
            if ~np.isnan(cnt_data.at[j, "iso_b"]):
                smp_test = Func.test_proc(cnt_data.at[j, "whe_symp"], cnt_data.at[j, "Onset"], cnt_data.at[j, "iso_b"])
                cnt_data.at[j, "diag_b"] = Func.diag_func(cnt_data.at[j, "inf"], smp_test)
        cnt_data = cnt_data[["id", "whe_trace", "iso_b", "diag_b"]]
        cnt_data.columns = ["id", "whe_trace1", "iso_b1", "diag_b1"]
        # print(cnt_data)
        simu_data = pd.merge(simu_data, cnt_data, on="id", how="left")
        simu_data["whe_trace"] = np.where(simu_data["id"].isin(cnt_data["id"]),
                                          simu_data["whe_trace1"], simu_data["whe_trace"])
        simu_data["iso_b"] = np.where(simu_data["id"].isin(cnt_data["id"]), simu_data["iso_b1"], simu_data["iso_b"])
        simu_data["diag_b"] = np.where(simu_data["id"].isin(cnt_data["id"]), simu_data["diag_b1"], simu_data["diag_b"])

        simu_data["diag_tmp"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (np.isnan(simu_data["iso_tmp"])),
                                         simu_data["diag_b"], simu_data["diag_tmp"])
        simu_data["found_way"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (np.isnan(simu_data["iso_tmp"])) &
                                          (~np.isnan(simu_data["diag_b"])), 2, simu_data["found_way"])
        simu_data["iso_tmp"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (np.isnan(simu_data["iso_tmp"])),
                                        simu_data["iso_b"], simu_data["iso_tmp"])

        simu_data["diag_tmp"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (~np.isnan(simu_data["iso_tmp"])) &
                                         (simu_data["iso_tmp"] > simu_data["iso_b"]), simu_data["diag_b"],
                                         simu_data["diag_tmp"])
        simu_data["found_way"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (~np.isnan(simu_data["iso_tmp"])) &
                                          (simu_data["iso_tmp"] > simu_data["iso_b"]) &
                                          (~np.isnan(simu_data["diag_b"])), 2, simu_data["found_way"])
        simu_data["iso_tmp"] = np.where((simu_data["id"].isin(cnt_data["id"])) & (~np.isnan(simu_data["iso_tmp"])) &
                                        (simu_data["iso_tmp"] > simu_data["iso_b"]), simu_data["iso_b"],
                                        simu_data["iso_tmp"])

        temp = simu_data[["id", "iso_tmp", "diag_tmp"]]
        temp.columns = ["infector", "iso1", "diag1"]
        simu_data = pd.DataFrame(pd.merge(simu_data, temp, on="infector", how="left"))
        simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso1"], 1, simu_data["Remove"])
        simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso_tmp"], 1, simu_data["Remove"])

        id_ex = simu_data[(simu_data["Remove"] == 1) & (simu_data["g"] == 1)]["id"].values
        for k in range(2, simu_data["g"].max() + 1):
            simu_data["Remove"] = np.where((simu_data["g"] == k) & (simu_data["infector"].isin(id_ex)), 1,
                                           simu_data["Remove"])
            id_ex = simu_data[(simu_data["g"] == k) & (simu_data["Remove"] == 1)]["id"].values

        simu_data = simu_data.loc[simu_data["Remove"] != 1, col_name]
        simu_data = simu_data.reset_index(drop=True)
        # print(simu_data[(simu_data["id"].isin(cnt_data["id"])) | (simu_data["id"].isin(index_case["id"]))])

        index3 = simu_data[(simu_data["diag_tmp"] == i) & (simu_data["Remove"] != 1) &
                           (simu_data["id"].isin(cnt_data["id"]))]

        if index3.shape[0] != 0:
            index_case = index3.reset_index(drop=True)
        if index3.shape[0] == 0:
            # Closed management of community
            index_cm = simu_data[(simu_data["diag_tmp"] == i)].reset_index(drop=True)
            simu_data["case_test"] = np.where(((simu_data["iso_tmp"] > i + 1) | (np.isnan(simu_data["iso_tmp"]))) &
                                              (simu_data["cm"].isin(index_cm["cm"])) & (simu_data["cm_test"] == 0),
                                              i + 1, simu_data["case_test"])

            simu_data["cm_test"] = np.where((simu_data["cm"].isin(index_cm["cm"])) & (simu_data["cm_test"] == 0),
                                            i + 1, simu_data["cm_test"])

            simu_data["cm_closed_first"] = np.where((simu_data["cm"].isin(index_cm["cm"])) &
                                                    (simu_data["cm_closed_first"] == 0),
                                                    i, simu_data["cm_closed_first"])
            simu_data["cm_closed_last"] = np.where((simu_data["cm"].isin(index_cm["cm"])) &
                                                   (simu_data["cm_closed_last"] < i + 13),
                                                   i + 13, simu_data["cm_closed_last"])
            cm_test_case = simu_data.loc[simu_data["case_test"] == i + 1].reset_index(drop=True)
            if cm_test_case.shape[0] != 0:
                for j in range(0, cm_test_case.shape[0]):
                    cm_test_case.at[j, "diag_d"] = Func.diag_func(cm_test_case.at[j, "inf"], [i + 1, i + 7, i + 12])

            cm_test_case["iso_d"] = np.where(~np.isnan(cm_test_case["diag_d"]),
                                             cm_test_case["diag_d"], cm_test_case["iso_d"])
            cm_test_case = cm_test_case[["id", "iso_d", "diag_d"]]
            cm_test_case.columns = ["id", "iso_d1", "diag_d1"]
            simu_data = pd.merge(simu_data, cm_test_case, on="id", how="left")
            simu_data["iso_d"] = np.where(simu_data["id"].isin(cm_test_case["id"]),
                                          simu_data["iso_d1"], simu_data["iso_d"])
            simu_data["diag_d"] = np.where(simu_data["id"].isin(cm_test_case["id"]),
                                           simu_data["diag_d1"], simu_data["diag_d"])

            simu_data["diag_tmp"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                             (np.isnan(simu_data["iso_tmp"])),
                                             simu_data["diag_d"], simu_data["diag_tmp"])
            simu_data["found_way"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                              (np.isnan(simu_data["iso_tmp"])) & (~np.isnan(simu_data["diag_d"])),
                                              4, simu_data["found_way"])
            simu_data["iso_tmp"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                            (np.isnan(simu_data["iso_tmp"])),
                                            simu_data["iso_d"], simu_data["iso_tmp"])

            simu_data["diag_tmp"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                             (~np.isnan(simu_data["iso_tmp"])) &
                                             (simu_data["iso_tmp"] > simu_data["iso_d"]),
                                             simu_data["diag_d"], simu_data["diag_tmp"])
            simu_data["found_way"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                              (~np.isnan(simu_data["iso_tmp"])) &
                                              (simu_data["iso_tmp"] > simu_data["iso_d"]) &
                                              (~np.isnan(simu_data["diag_d"])), 4, simu_data["found_way"])
            simu_data["iso_tmp"] = np.where((simu_data["id"].isin(cm_test_case["id"])) &
                                            (~np.isnan(simu_data["iso_tmp"])) &
                                            (simu_data["iso_tmp"] > simu_data["iso_d"]),
                                            simu_data["iso_d"], simu_data["iso_tmp"])

            temp = simu_data[["id", "iso_tmp", "diag_tmp", "cm_closed_first", "cm_closed_last"]]
            temp.columns = ["infector", "iso1", "diag1", "cm_closed_first1", "cm_closed_last1"]
            simu_data = pd.DataFrame(pd.merge(simu_data, temp, on="infector", how="left"))
            simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso1"], 1, simu_data["Remove"])

            simu_data["Prob"] = np.where((simu_data["Setting"] == "Workplace") &
                                         (((simu_data["cm_closed_first1"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last1"] >= simu_data["inf"])) |
                                          ((simu_data["cm_closed_first"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last"] >= simu_data["inf"]))),
                                         0, simu_data["Prob"])

            simu_data["Prob"] = np.where((simu_data["Setting"] == "Community") &
                                         (~((simu_data["in_cm1"] == 1) & (simu_data["in_cm2"] == 1))) &
                                         (((simu_data["cm_closed_first1"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last1"] >= simu_data["inf"])) |
                                          ((simu_data["cm_closed_first"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last"] >= simu_data["inf"]))),
                                         0, simu_data["Prob"])

            simu_data["Prob"] = np.where((simu_data["Setting"] == "Community") &
                                         ((simu_data["in_cm1"] == 1) & (simu_data["in_cm2"] == 1)) &
                                         (((simu_data["cm_closed_first1"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last1"] >= simu_data["inf"])) |
                                          ((simu_data["cm_closed_first"] <= simu_data["inf"]) &
                                           (simu_data["cm_closed_last"] >= simu_data["inf"]))),
                                         0.1, simu_data["Prob"])

            simu_data["Remove"] = np.where(simu_data["Prob"] == 0, 1, simu_data["Remove"])
            simu_data["Remove"] = np.where((simu_data["Prob"] == 0.1) & (simu_data["Remove"] != 1),
                                           np.random.choice([0, 1], 1, p=[0.1, 0.9])[0], simu_data["Remove"])

            # Remove later generations
            id_ex = simu_data[(simu_data["Remove"] == 1) & (simu_data["g"] == 1)]["id"].values
            for k in range(2, simu_data["g"].max() + 1):
                simu_data["Remove"] = np.where((simu_data["g"] == k) & (simu_data["infector"].isin(id_ex)), 1,
                                               simu_data["Remove"])
                id_ex = simu_data[(simu_data["g"] == k) & (simu_data["Remove"] == 1)]["id"].values

            simu_data = simu_data.loc[simu_data["Remove"] != 1, col_name]
            simu_data = simu_data.reset_index(drop=True)

            # Mass screening
            # Diagnosed cases at date i : who trigger mass screening

            simu_data["loc_dist"] = simu_data["loc_resid"].str[3:6]
            index_scr = simu_data[(simu_data["diag_tmp"] == i)].reset_index(drop=True)

            simu_data["case_scr"] = np.where((simu_data["loc_dist"].isin(index_scr["loc_dist"])) &
                                             (simu_data["loc_scr"] == 0) & (simu_data["Remove"] != 1) &
                                             ((np.floor(simu_data["iso_tmp"]) > i + 1) |
                                              (np.isnan(simu_data["iso_tmp"]))) &
                                             ((simu_data["cm_test"] > i + 1) | (simu_data["cm_test"] == 0)),
                                             i + 1, simu_data["case_scr"])

            simu_data["loc_scr"] = np.where((simu_data["loc_dist"].isin(index_scr["loc_dist"])) &
                                            (simu_data["loc_scr"] == 0), i + 1, simu_data["loc_scr"])

            scr_case = simu_data[simu_data["case_scr"] == i + 1].reset_index(drop=True)

            if scr_case.shape[0] != 0:
                for j in range(0, scr_case.shape[0]):
                    scr_date = i + np.random.choice(range(1, Freq_scr + 1), 1)[0]
                    scr_date = np.linspace(scr_date, scr_date + Freq_scr * (rnd_scr - 1), rnd_scr)
                    scr_case.at[j, "diag_e"] = Func.diag_func(scr_case.at[j, "inf"], scr_date)

                scr_case["iso_e"] = scr_case["diag_e"]
                scr_case = scr_case.loc[~np.isnan(scr_case["diag_e"])][["id", "iso_e", "diag_e"]]
                # print(scr_case)
                scr_case.columns = ["id", "iso_e1", "diag_e1"]
                simu_data = pd.merge(simu_data, scr_case, on="id", how="left")
                simu_data["iso_e"] = np.where(simu_data["id"].isin(scr_case["id"]),
                                              simu_data["iso_e1"], simu_data["iso_e"])
                simu_data["diag_e"] = np.where(simu_data["id"].isin(scr_case["id"]),
                                               simu_data["diag_e1"], simu_data["diag_e"])

                simu_data["diag_tmp"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                 (np.isnan(simu_data["iso_tmp"])),
                                                 simu_data["diag_e"], simu_data["diag_tmp"])
                simu_data["found_way"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                  (np.isnan(simu_data["iso_tmp"])) & (~np.isnan(simu_data["diag_e"])),
                                                  5, simu_data["found_way"])
                simu_data["iso_tmp"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                (np.isnan(simu_data["iso_tmp"])),
                                                simu_data["iso_e"], simu_data["iso_tmp"])

                simu_data["diag_tmp"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                 (~np.isnan(simu_data["iso_tmp"])) &
                                                 (simu_data["iso_tmp"] > simu_data["iso_e"]),
                                                 simu_data["diag_e"], simu_data["diag_tmp"])
                simu_data["found_way"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                  (~np.isnan(simu_data["iso_tmp"])) &
                                                  (simu_data["iso_tmp"] > simu_data["iso_e"]) &
                                                  (~np.isnan(simu_data["diag_e"])), 5, simu_data["found_way"])
                simu_data["iso_tmp"] = np.where((simu_data["id"].isin(scr_case["id"])) &
                                                (~np.isnan(simu_data["iso_tmp"])) &
                                                (simu_data["iso_tmp"] > simu_data["iso_e"]),
                                                simu_data["iso_e"], simu_data["iso_tmp"])

                temp = simu_data[["id", "iso_tmp", "diag_tmp"]]
                temp.columns = ["infector", "iso1", "diag1"]
                simu_data = pd.DataFrame(pd.merge(simu_data, temp, on="infector", how="left"))
                simu_data["Remove"] = np.where(simu_data["inf"] > simu_data["iso1"], 1, simu_data["Remove"])

                # Remove later generation
                id_ex = simu_data[(simu_data["Remove"] == 1) & (simu_data["g"] == 1)]["id"].values
                for k in range(2, simu_data["g"].max() + 1):
                    simu_data["Remove"] = np.where((simu_data["g"] == k) & (simu_data["infector"].isin(id_ex)), 1,
                                                   simu_data["Remove"])
                    id_ex = simu_data[(simu_data["g"] == k) & (simu_data["Remove"] == 1)]["id"].values

                simu_data = simu_data.loc[simu_data["Remove"] != 1, col_name]
                simu_data = simu_data.reset_index(drop=True)

            # Risk regions
            # Diagnosed cases in the past 14 days
            case_14d = simu_data[(simu_data["Remove"] != 1) & (simu_data["diag_tmp"] >= i - 13) &
                                 (simu_data["diag_tmp"] <= i)].reset_index(drop=True)
            # if case_14d.shape[0] == 0:
            #     print(i, "clear")
            if case_14d.shape[0] != 0:
                case_freq = pd.DataFrame(case_14d.groupby(by=["loc_resid"]).size())
                case_freq["inf"] = i + 1
                case_freq["loc_resid"] = case_freq.index
                case_freq = case_freq.reset_index(drop=True)
                case_freq.columns = ["Num", "inf", "loc_resid"]
                # Risk level of each street
                # 1. Number of diagnosed cases 2 - 5: Middle risk areas
                # 2. Number of diagnosed cases more than 5: High risk areas
                case_freq["Risk"] = np.where(case_freq["Num"] <= 5, 1, 2)
                case_freq["Risk"] = np.where(case_freq["Num"] == 1, 0, case_freq["Risk"])
                case_freq = case_freq[["inf", "loc_resid", "Num", "Risk"]]
                # print(case_freq)

                temp = simu_data[["id", "loc_resid"]]
                temp.columns = ["infector", "loc_resid1"]
                simu_data = pd.DataFrame(pd.merge(simu_data, temp, on="infector", how="left"))

                # New infections in the (i + 1)th day
                case_inf = simu_data[(simu_data["inf"] == i + 1) & (simu_data["Remove"] != 1)]
                # Risk level of each street
                case_inf = pd.merge(case_inf, case_freq, on=["inf", "loc_resid"], how="left")

                case_freq.columns = ["inf", "loc_resid1", "Num1", "Risk1"]
                case_inf = pd.DataFrame(pd.merge(case_inf, case_freq, on=["inf", "loc_resid1"], how="left"))

                case_freq.columns = ["inf", "loc_trans_site", "Num_Site", "Risk_Site"]
                case_inf = pd.DataFrame(pd.merge(case_inf, case_freq, on=["inf", "loc_trans_site"], how="left"))

                # Low risk: No new infections detected in the past 14 days
                # Low risk streets not included in the case_freq dataset, thus the risk level is empty
                case_inf["Risk1"] = np.where((case_inf["infector"] != "ini") & (np.isnan(case_inf["Risk1"])),
                                             0, case_inf["Risk1"])
                case_inf["Risk"] = np.where(np.isnan(case_inf["Risk"]), 0, case_inf["Risk"])
                case_inf["Risk_Site"] = np.where(np.isnan(case_inf["Risk_Site"]), 0, case_inf["Risk_Site"])
                case_inf = case_inf.reset_index(drop=True)
                # print(case_inf)

                # Prob_a: probability that the infector move out of home given the risk level of their residential areas
                # Prob_b: Probability that the infectee move out of home given the risk level of their residential areas
                case_inf["Prob_a"] = 1.0
                case_inf["Prob_b"] = 1.0
                for r in range(0, case_inf.shape[0]):

                    # Move out of the street (infector)
                    if (case_inf.at[r, "infector"] != "ini") & \
                            (case_inf.at[r, "loc_resid1"] != case_inf.at[r, "loc_trans_site"]):
                        case_inf.at[r, "Prob_a"] = Prob_travel.loc[(Prob_travel["Within"] == 0) &
                                                                   (Prob_travel["Risk_Home"] == case_inf.at[r, "Risk1"])
                                                                   & (Prob_travel["Risk_Site"] ==
                                                                      case_inf.at[r, "Risk_Site"]), "Prob_out"]

                    # Move out of the street (infectee)
                    if case_inf.at[r, "loc_resid"] != case_inf.at[r, "loc_trans_site"]:
                        case_inf.at[r, "Prob_b"] = Prob_travel.loc[(Prob_travel["Within"] == 0) &
                                                                   (Prob_travel["Risk_Home"] == case_inf.at[r, "Risk"])
                                                                   & (Prob_travel["Risk_Site"] ==
                                                                      case_inf.at[r, "Risk_Site"]), "Prob_out"]

                    # Move within the street (infector)
                    if (case_inf.at[r, "loc_resid1"] == case_inf.at[r, "loc_trans_site"]) & \
                            (case_inf.at[r, "Setting"] != "Household"):
                        case_inf.at[r, "Prob_a"] = Prob_travel.loc[(Prob_travel["Risk_Home"] == case_inf.at[r, "Risk1"])
                                                                   & (Prob_travel["Within"] == 1), "Prob_out"]

                    # Move within the street (infectee)
                    if (case_inf.at[r, "loc_resid"] == case_inf.at[r, "loc_trans_site"]) & \
                            (case_inf.at[r, "Setting"] != "Household"):
                        case_inf.at[r, "Prob_b"] = Prob_travel.loc[(Prob_travel["Risk_Home"] == case_inf.at[r, "Risk"])
                                                                   & (Prob_travel["Within"] == 1), "Prob_out"]
                # Prob that the transmission event occur
                case_inf["Prob"] = np.where(case_inf["Prob_a"] * case_inf["Prob_b"] < case_inf["Prob"],
                                            case_inf["Prob_a"] * case_inf["Prob_b"], case_inf["Prob"])

                for k in range(0, case_inf.shape[0]):
                    Random = np.random.choice([0, 1], 1, p=[case_inf.at[k, "Prob"], (1 - case_inf.at[k, "Prob"])])[0]
                    if (Random == 1) & (case_inf.at[k, "Setting"] != "Household"):
                        case_inf.at[k, "Remove"] = 1

                # print(case_inf[["g", "inf", "Setting", "in_cm1", "in_cm2",
                #                 "Risk1", "Risk", "Risk_Site", "cm_closed_first", "cm_closed_last",
                #                 "loc_resid1", "loc_resid", "loc_trans_site",
                #                 "Prob_a", "Prob_b", "Prob", "Remove"]])

                # remove later generation
                id_ex = case_inf.loc[case_inf["Remove"] == 1, "id"]
                simu_data["Remove"] = np.where(simu_data["id"].isin(id_ex), 1, simu_data["Remove"])
                while len(id_ex) != 0:
                    simu_data["Remove"] = np.where(simu_data["infector"].isin(id_ex), 1, simu_data["Remove"])
                    id_ex = simu_data.loc[simu_data["infector"].isin(id_ex), "id"]

                simu_data = simu_data.loc[simu_data["Remove"] != 1, col_name]
                simu_data = simu_data.reset_index(drop=True)

            i += 1
            simu_data = simu_data[col_name]
            index_case = simu_data[(simu_data["diag_tmp"] == i) & (simu_data["Remove"] != 1)].reset_index(drop=True)
    return simu_data
