 # -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

NZ_vax_cov = "../1. data/NZ_vax_cov_0920.xlsx"
NZ_vax_cov = pd.read_excel(NZ_vax_cov)

sh_bs_hh = "../1. data/cnt_matrix/Shanghai_baseline/SH_bs_hh.xlsx"
sh_bs_wk = "../1. data/cnt_matrix/Shanghai_baseline/SH_bs_wk.xlsx"
sh_bs_cm = "../1. data/cnt_matrix/Shanghai_baseline/SH_bs_cm.xlsx"

sh_bs_hh = pd.read_excel(sh_bs_hh)
sh_bs_wk = pd.read_excel(sh_bs_wk)
sh_bs_cm = pd.read_excel(sh_bs_cm)

hh_size = "../1. data/hh_size_freq.xlsx"
hh_size = pd.DataFrame(pd.read_excel(hh_size))

Beijing_street = "../1. data/Beijing_street.xlsx"
Beijing_street = pd.DataFrame(pd.read_excel(Beijing_street))

interaction_mat = "../1. data/interaction matrix.xlsx"
interaction_mat = pd.DataFrame(pd.read_excel(interaction_mat))

filename = "../1. data/sen_PCR.xlsx"
sen_PCR = pd.read_excel(filename)


def vax_func(vax_stra, age):
    temp = pd.DataFrame(NZ_vax_cov[(NZ_vax_cov["age_l"] <= age) & (NZ_vax_cov["age_u"] >= age)])
    whe_prm = np.random.choice([1, 0], 1, p=[temp["prm_vax"].values[0]/100, 1 - temp["prm_vax"].values[0]/100])[0]
    if vax_stra == "prm":
        if whe_prm == 1:
            vax_status = 2
        if whe_prm == 0:
            vax_status = 0
    if (vax_stra == "hom") | (vax_stra == "het"):
        if whe_prm == 1:
            p1 = temp["boost_vax"].values[0]/temp["prm_vax"].values[0]
            whe_bst = np.random.choice([1, 0], 1, p=[p1, 1 - p1])[0]
            if whe_bst == 1:
                vax_status = 3
            if whe_bst == 0:
                vax_status = 2
        if whe_prm == 0:
            vax_status = 0
    return vax_status


def Setting_func(hh_suscept, Occupation1, Workday):
    if hh_suscept > 0:
        if Occupation1 == "service_worker":
            Setting = np.random.choice(['Household', 'Community'], 1, p=[0.5, 0.5])[0]
        if (Occupation1 == "general_worker") & (Workday == True):
            Setting = np.random.choice(['Household', 'Workplace', 'Community'], 1, p=[0.5, 0.3, 0.2])[0]
        if (Occupation1 == "general_worker") & (Workday == False):
            Setting = np.random.choice(['Household', 'Community'], 1, p=[0.7, 0.3])[0]
        if Occupation1 == "Non-worker":
            Setting = np.random.choice(["Household", "Community"], 1, p=[0.7, 0.3])[0]
    if hh_suscept == 0:
        if Occupation1 == "service_worker":
            Setting = "Community"
        if (Occupation1 == "general_worker") & (Workday == True):
            Setting = np.random.choice(['Workplace', 'Community'], 1, p=[0.6, 0.4])[0]
        if (Occupation1 == "general_worker") & (Workday == False):
            Setting = "Community"
        if Occupation1 == "Non-worker":
            Setting = "Community"
    return Setting


def age_func(age1, Setting):
    if Setting == "Household":
        temp = pd.DataFrame(sh_bs_hh[(sh_bs_hh["age1_lower"] <= age1) & (sh_bs_hh["age1_upper"] > age1)])
    if Setting == "Workplace":
        temp = pd.DataFrame(sh_bs_wk[(sh_bs_wk["age1_lower"] <= age1) & (sh_bs_wk["age1_upper"] > age1)])
    if Setting == "Community":
        temp = pd.DataFrame(sh_bs_cm[(sh_bs_cm["age1_lower"] <= age1) & (sh_bs_cm["age1_upper"] > age1)])

    temp["prob"] = temp['mean'] / temp['mean'].sum()
    age = np.random.choice(range(1, 17, 1), 1, p=np.array(temp["prob"]))[0]
    temp = temp[temp["x2"] == age]
    age = np.random.choice(range(temp[["age2_lower"]].values[0][0], temp[["age2_upper"]].values[0][0], 1), 1)[0]
    return age


def hh_size_func(age):
    if age <= 18:
        hh = hh_size[hh_size["Group"] == "Other 0-18"]
    if (age > 18) & (age < 65):
        hh = hh_size[hh_size["Group"] == "Other 19-64"]
    if age >= 65:
        hh = hh_size[hh_size["Group"] == "Other ≥65"]
    return np.random.choice(hh["hh_size"], 1, p=hh["probability"])[0]


def symp_func(age, VE_symp):
    if age < 20:
        whe_symp = np.random.choice([0, 1], 1, p=[1 - 0.1809 * (1 - VE_symp), 0.1809 * (1 - VE_symp)])[0]
    if (age >= 20) & (age < 40):
        whe_symp = np.random.choice([0, 1], 1, p=[1 - 0.2241 * (1 - VE_symp), 0.2241 * (1 - VE_symp)])[0]
    if (age >= 40) & (age < 60):
        whe_symp = np.random.choice([0, 1], 1, p=[1 - 0.3054 * (1 - VE_symp), 0.3054 * (1 - VE_symp)])[0]
    if (age >= 60) & (age < 80):
        whe_symp = np.random.choice([0, 1], 1, p=[1 - 0.3546 * (1 - VE_symp), 0.3546 * (1 - VE_symp)])[0]
    if age >= 80:
        whe_symp = np.random.choice([0, 1], 1, p=[1 - 0.6456 * (1 - VE_symp), 0.6456 * (1 - VE_symp)])[0]
    return whe_symp


def activity_func(Setting, Occupation):
    if Setting == "Household":
        Activity = "Household"
    if Setting == "Workplace":
        Activity = "Work"
    if Setting == "Community":
        if Occupation == "service_worker":
            Activity = np.random.choice(['Work', 'Social'], 1, p=[0.6, 0.4])[0]
        if (Occupation == "general_worker") | (Occupation == "Non-worker"):
            Activity = "Social"
    return Activity


def Occupation_func(Occupation1, Activity1, age2, sex2):
    if (age2 < 18) | ((sex2 == 1) & (age2 >= 60)) | ((sex2 == 2) & (age2 >= 55)):
        Occupation2 = "Non-worker"
    if (age2 >= 18) & (((sex2 == 1) & (age2 < 60)) | ((sex2 == 2) & (age2 < 55))):
        if Occupation1 == "service_worker":
            if Activity1 == "Work":
                Occupation2 = np.random.choice(['service_worker', 'general_worker'], 1, p=[0.2, 0.8])[0]
            else:
                Occupation2 = np.random.choice(['service_worker', 'general_worker'], 1, p=[0.097, 0.903])[0]

        if Occupation1 == "general_worker":
            if Activity1 == "Work":
                Occupation2 = "general_worker"
            else:
                Occupation2 = np.random.choice(['service_worker', 'general_worker'], 1, p=[0.097, 0.903])[0]

        if (Occupation1 == "Non-worker") | (Occupation1 == ""):
            Occupation2 = np.random.choice(['service_worker', 'general_worker'], 1, p=[0.097, 0.903])[0]
    return Occupation2


def location_func(loc_resid1, loc_work1, loc_social_wkd1, loc_social_hld1,
                  Setting, Activity1, Activity2, in_cm2, Workday, Occupation2):
    # Household
    if Setting == "Household":
        loc_resid2 = loc_resid1
        loc_trans_site = loc_resid1
        int_mat2 = interaction_mat[interaction_mat["start_place"] == loc_resid2]
        if Occupation2 == "service_worker":
            loc_work2 = np.random.choice(int_mat2["end_place"], 1, p=int_mat2["serv"] / int_mat2["serv"].sum())[0]
        if Occupation2 == "general_worker":
            loc_work2 = np.random.choice(int_mat2["end_place"], 1, p=int_mat2["wk"] / int_mat2["wk"].sum())[0]
        if Occupation2 == "Non-worker":
            loc_work2 = ""

    # Workplace
    if Setting == "Workplace":
        loc_work2 = loc_work1
        loc_trans_site = loc_work1
        int_mat2 = interaction_mat[interaction_mat["end_place"] == loc_work2]
        loc_resid2 = np.random.choice(int_mat2["start_place"], 1, p=int_mat2["wk"] / int_mat2["wk"].sum())[0]

    # Community
    if Setting == "Community":
        if (Activity1 == "Work") & (Activity2 == "Work"):
            loc_work2 = loc_work1
            loc_trans_site = loc_work1
            if in_cm2 == 1:
                loc_resid2 = loc_work2
            if in_cm2 == 0:
                int_mat2 = interaction_mat[interaction_mat["end_place"] == loc_work2]
                loc_resid2 = np.random.choice(int_mat2["start_place"], 1,
                                              p=int_mat2["serv"] / int_mat2["serv"].sum())[0]

        if (Activity1 == "Work") & (Activity2 == "Social"):
            loc_soc = loc_work1
            loc_trans_site = loc_work1
            if in_cm2 == 1:
                loc_resid2 = loc_soc
            if in_cm2 == 0:
                int_mat2 = interaction_mat[interaction_mat["end_place"] == loc_soc]
                if Workday is True:
                    loc_resid2 = np.random.choice(int_mat2["start_place"], 1,
                                                  p=int_mat2["soc_wkd"] / int_mat2["soc_wkd"].sum())[0]
                if Workday is False:
                    loc_resid2 = np.random.choice(int_mat2["start_place"], 1,
                                                  p=int_mat2["soc_hld"] / int_mat2["soc_hld"].sum())[0]
            int_mat2 = interaction_mat[interaction_mat["start_place"] == loc_resid2]
            if Occupation2 == "service_worker":
                loc_work2 = np.random.choice(int_mat2["end_place"], 1, p=int_mat2["serv"] / int_mat2["serv"].sum())[0]
            if Occupation2 == "general_worker":
                loc_work2 = np.random.choice(int_mat2["end_place"], 1, p=int_mat2["wk"] / int_mat2["wk"].sum())[0]
            if Occupation2 == "Non-worker":
                loc_work2 = ""

        if (Activity1 == "Social") & (Activity2 == "Work"):
            if Workday is True:
                loc_work2 = loc_social_wkd1
            if Workday is False:
                loc_work2 = loc_social_hld1
            loc_trans_site = loc_work2
            if in_cm2 == 1:
                loc_resid2 = loc_work2
            if in_cm2 == 0:
                int_mat2 = interaction_mat[interaction_mat["end_place"] == loc_work2]
                loc_resid2 = np.random.choice(int_mat2["start_place"], 1,
                                              p=int_mat2["serv"] / int_mat2["serv"].sum())[0]

        if (Activity1 == "Social") & (Activity2 == "Social"):
            if Workday is True:
                loc_soc = loc_social_wkd1
            if Workday is False:
                loc_soc = loc_social_hld1
            loc_trans_site = loc_soc
            if in_cm2 == 1:
                loc_resid2 = loc_soc
            if in_cm2 == 0:
                int_mat2 = interaction_mat[interaction_mat["end_place"] == loc_soc]
                if Workday is True:
                    loc_resid2 = np.random.choice(int_mat2["start_place"], 1,
                                                  p=int_mat2["soc_wkd"] / int_mat2["soc_wkd"].sum())[0]
                if Workday is False:
                    loc_resid2 = np.random.choice(int_mat2["start_place"], 1,
                                                  p=int_mat2["soc_hld"] / int_mat2["soc_hld"].sum())[0]

            int_mat2 = interaction_mat[interaction_mat["start_place"] == loc_resid2]
            if Occupation2 == "service_worker":
                loc_work2 = np.random.choice(int_mat2["end_place"], 1, p=int_mat2["serv"] / int_mat2["serv"].sum())[0]
            if Occupation2 == "general_worker":
                loc_work2 = np.random.choice(int_mat2["end_place"], 1, p=int_mat2["wk"] / int_mat2["wk"].sum())[0]
            if Occupation2 == "Non-worker":
                loc_work2 = ""

    return [loc_resid2, loc_work2, loc_trans_site]


def test_proc(whe_symp, onset_date, iso_date):
    onset_date = np.floor(onset_date)
    iso_date = np.floor(iso_date)
    if ((whe_symp == 1) & (onset_date + 6 < iso_date)) | ((whe_symp == 1) & (onset_date > iso_date + 20)) | \
            (whe_symp == 0):
        test_date = iso_date + [0, 3, 6, 13, 15, 20]
    if (whe_symp == 1) & (onset_date < iso_date) & (onset_date + 6 >= iso_date):
        test_date1 = [iso_date, iso_date + 2, iso_date + 6]
        test_date2 = iso_date + [0, 3, 6, 13, 15, 20]
        test_date = np.sort(np.unique(np.hstack((test_date1, test_date2))))
    if (whe_symp == 1) & (onset_date >= iso_date) & (onset_date <= iso_date + 20):
        test_date1 = [onset_date, onset_date + 2, onset_date + 6]
        test_date2 = iso_date + [0, 3, 6, 13, 15, 20]
        test_date = np.sort(np.unique(np.hstack((test_date1, test_date2))))
    return test_date


def diag_func(inf_date, test_date):
    whe_diag = 0
    diag_date = np.nan
    m = 0
    while (whe_diag == 0) & (m < len(test_date)):
        smp_diff = test_date[m] - inf_date
        if (smp_diff > 30) | (smp_diff < 0):
            pos = 0
        else:
            pos = sen_PCR.loc[sen_PCR["smp_diff"] == smp_diff, "Positive"].reset_index(drop=True)[0]
        whe_diag = np.random.choice([0, 1], 1, p=[(1 - pos), pos])[0]
        if whe_diag == 1:
            diag_date = test_date[m] + np.random.choice([0, 1], 1, p=[0.75, 0.25])[0]
        if whe_diag == 0:
            m += 1
    return diag_date
