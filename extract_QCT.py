##############################################################################
# Usage: python extract_QCT.py Proj_path Demo_path Proj
# ex) python extract_QCT.py
#       data/sample_Proj/Proj_Subj
#       data/sample_demo.csv
#       ENV18PM
#
# Run Time: ~1 min
# Ref: ENV18PM.drawio
# ##############################################################################
# extract_QCT.py (No version suffix): 20220118, In Kyu Lee
# Use git to maintain different versions.
# ##############################################################################
# v2h: 20211031, In Kyu Lee
# - Minor error fixed: Airtrap -> AirT.
# v2g: 20211031, Jiwoong Choi
# - AirT is added.
# v2f: 20211020, Jiwoong Choi
# - TF.average instead of TF.total
# v2d: 20211015, In Kyu Lee
# - CFG class is defined to get config.
# v2c: 20211015, Jiwoong Choi, In Kyu Lee
# - changed ("string") to (str) for number only subject ID (Subj) for version independency.
# -
# v2b: 20211008b, In Kyu Lee
# - Changed FU to T0
# v2a: 20211007a, Jiwoong Choi
# - corrected WT_pred & Dh_pred for KOR.
# - made minor edits in comments for hard-coded parameters.
# v2: 20211007, In Kyu Lee
# - Proj is the third argument
# - Korean predicted value is available
# - Manual work is minimized
# ##############################################################################
# v1: 20210501, In Kyu Lee
# Desc: Extract QCT variables
# ##############################################################################
# Input:
#  - Path of the project folder, ex) /data4/common/IR/IR_ENV18PM_SN12
#  - Path of the demographics csv file, ex) /data1/common/IR/ENV18PM_Demo_20210304.csv
#  - Proj, ex) ENV18PM
# Output:
#  - QCT varialbes csv file for each subject
#  - combined QCT variables csv file
# ##############################################################################
import pandas as pd
import numpy as np
import os
import sys
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


class CFG:
    path = str(sys.argv[1])
    demo_path = str(sys.argv[2])
    Proj = str(sys.argv[3])
    # --------------------
    # Proj = 'ENV18PM'
    # Proj = 'CBDPI'
    # Proj = "SARP"
    # Img0: Fixed Image
    # Img1: Floating Image
    Img0 = "IN0"
    Img1 = "EX0"
    # Img0 = 'IND0'
    # Img0 = 'TLC0'
    # Img1 = 'FRC0'
    # FU = '{FU}' # 20211008IK
    FU = "T0"
    # For Korean, set True
    KOR = False
    # --------------------


def Circularity(branch):
    if branch.empty:
        return np.nan
    A = branch.avgInnerArea.values[0]
    P = branch.avgInnerPerimeter.values[0]
    return (4 * np.pi * A) / P ** 2

def Eccentricity(branch):
    if branch.empty:
        return np.nan
    minor_inner_D = branch.avgMinorInnerDiam.values[0]
    major_inner_D = branch.avgMajorInnerDiam.values[0]
    return minor_inner_D/major_inner_D


def LADIVBYCL(branch):
    if branch.empty:
        return np.nan
    inner_A = branch.avgInnerArea.values[0]
    center_line_l = branch.centerLineLength.values[0]
    return inner_A/center_line_l

def D_inner(branch):
    if branch.empty:
        return np.nan, np.nan
    minor_inner_D = branch.avgMinorInnerDiam.values[0]
    major_inner_D = branch.avgMajorInnerDiam.values[0]
    return minor_inner_D, major_inner_D

def Area_lumen(branch):
    if branch.empty:
        return np.nan, np.nan
    inner_A = branch.avgInnerArea.values[0]
    outer_A = branch.avgOuterArea.values[0]
    return inner_A, outer_A

def Peri_lumen(branch):
    if branch.empty:
        return np.nan, np.nan
    inner_P = branch.avgInnerPerimeter.values[0]
    outer_P = branch.avgOuterPerimeter.values[0]
    return inner_P, outer_P

    #     WALLAREA
    #     WALLAREAPCT

def Area_wall(branch):
    if branch.empty:
        return np.nan, np.nan
    wall_frac = branch.avgWallAreaFraction.values[0]
    inner_A = branch.avgInnerArea.values[0]
    outer_A = branch.avgOuterArea.values[0]
    wall_A = outer_A - inner_A
    wall_A_p = wall_frac *100
    return wall_A, wall_A_p

    #     avgavgwallthickness
    #     WALLTHICKNESSPCT
# avgAvgWallThickness
# avgAvgWallThickness/(avgInnerEquivalentCircleDiameter + avgAvgWallThickness)*100%
def Thickness_wall(branch):
    if branch.empty:
        return np.nan, np.nan
    wall_th = branch.avgAvgWallThickness.values[0]
    inner_CD = branch.avgInnerEquivalentCircleDiameter.values[0]
    wall_th_p = 100 * wall_th / (inner_CD + wall_th)
    return wall_th, wall_th_p

def WT_pred(row, KOR=False):
    if KOR:
        return np.log10(
            9.11
            - 1.02 * np.log10(row["Age_yr"])
            - 0.98 * row["Height_m"] * row["Height_m"] * row["Gender_m0f1"]
            + 1.01
            * row["Height_m"]
            * row["Height_m"]
            * np.log10(row["Age_yr"])  # 20211007jc
            #           + 1.01*row["Height_yr"]*row["Height_yr"]*row["Age_yr"]
        )
    else:
        return (
            4.5493
            - 0.5007 * row["Gender_m0f1"]
            + 0.3007 * np.log10(row["Age_yr"]) * row["Height_m"]
        )


def WT_norm(branch, row, KOR=False):
    if branch.empty or row.empty:
        return np.nan
    WT = branch.avgAvgWallThickness.values[0]
    WT_predicted = WT_pred(row, KOR)
    return WT / WT_predicted


# Ref: [QCT-based structural Alterations of Asthma]
def Dh_pred(row, KOR=False):
    if KOR:
        return (
            12.79
            - 0.13 * np.log10(row["Age_yr"])
            - 5.82 * np.log10(row["Height_m"]) * row["Gender_m0f1"]  # 20211007jc
            #       - 5.82 * np.log10(row["Height_yr"]) * row["Gender_m0f1"]
            + 3.01 * np.log10(row["Age_yr"]) * row["Height_m"]
        )
    else:
        return (
            16.446
            - 2.4019 * row["Gender_m0f1"]
            - 0.298809 * row["Gender_m0f1"] * row["Age_yr"]
            + 0.0284836 * row["Age_yr"] * row["Height_m"]
            + 0.1786604 * row["Gender_m0f1"] * row["Age_yr"] * row["Height_m"]
        )


def Dh_norm(branch, row, KOR=False):
    if branch.empty or row.empty:
        return np.nan
    A = branch.avgInnerArea.values[0]
    P = branch.avgInnerPerimeter.values[0]
    Dh = 4 * A / P
    Dh_predicted = Dh_pred(row, KOR)
    return Dh / Dh_predicted


# Angle between two vectors: arccos(np.dot(v1,v2))
def Angle_vectors(v1, v2):
    return np.arccos(np.dot(v1, v2)) * (180 / np.pi)


def main():
    Config = CFG()
    path = Config.path
    demo_path = Config.demo_path
    Proj = Config.Proj
    Img0 = Config.Img0
    Img1 = Config.Img1
    FU = Config.FU
    KOR = Config.KOR

    Subjs = [
        f.split("_")[1]
        for f in os.listdir(path)
        if os.path.isdir(os.path.join(path, f)) and f.split("_")[0] == Proj
    ]
    if os.path.exists(demo_path):
        demo_available = True
        demo_df = pd.read_csv(demo_path)
        demo_df["Subj"] = demo_df["Subj"].astype(str)
    else:
        demo_available = False
        print(f"{demo_path} cant be found.")
        print("Extracting QCTs without demo.")

    for i, Subj in enumerate(Subjs):
        subj_path = os.path.join(path, f"{Proj}_{Subj}")
        df = pd.DataFrame({"Proj": [Proj], "Subj": [Subj]})
        # variable_ : path of the variable
        # lobe0: lu | lobe1: ll | lobe2: ru | lobe3: rm | lobe4: rl

        # Demographics
        if demo_available:
            row = demo_df[demo_df.Subj == Subj].reset_index(drop=True)
            if len(row) > 0:
                row = row.loc[0, :]
            df["Age_yr"] = row.Age_yr
            df["Gender_m0f1"] = row.Gender_m0f1
            df["Height_m"] = row.Height_m
            df["Weight_kg"] = row.Weight_kg

        else:
            df["Age_yr"] = "na"
            df["Gender_m0f1"] = "na"
            df["Height_m"] = "na"
            df["Weight_kg"] = "na"

        # Vent
        Vent_ = os.path.join(
            subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_airDiff_Lobe.dat"
        )
        if os.path.exists(Vent_):
            Vent = pd.read_csv(Vent_, sep=" ")
            # Upper/(Middle+Lower)
            df[f"dAV_U_ML_{FU}"] = (Vent.total[0] + Vent.total[2]) / (
                Vent.total[1] + Vent.total[3] + Vent.total[4]
            )
            # (Upper+Middle)/Lower
            df[f"dAV_UM_L_{FU}"] = (Vent.total[0] + Vent.total[2] + Vent.total[3]) / (
                Vent.total[1] + Vent.total[4]
            )

            df[f"dAV_xLUL_{FU}"] = Vent.total[0] / Vent.total[5]
            df[f"dAV_xLLL_{FU}"] = Vent.total[1] / Vent.total[5]
            df[f"dAV_xRUL_{FU}"] = Vent.total[2] / Vent.total[5]
            df[f"dAV_xRML_{FU}"] = Vent.total[3] / Vent.total[5]
            df[f"dAV_xRLL_{FU}"] = Vent.total[4] / Vent.total[5]

        # Tissue fraction @ TLC
        TLC_tiss_ = os.path.join(
            subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_fixed_tissue_Lobe.dat"
        )
        if os.path.exists(TLC_tiss_):
            TLC_tiss = pd.read_csv(TLC_tiss_, sep=" ")
            df[f"TF_All_{Img0}"] = TLC_tiss.average[5]
            df[f"TF_LUL_{Img0}"] = TLC_tiss.average[0]
            df[f"TF_LLL_{Img0}"] = TLC_tiss.average[1]
            df[f"TF_RUL_{Img0}"] = TLC_tiss.average[2]
            df[f"TF_RML_{Img0}"] = TLC_tiss.average[3]
            df[f"TF_RLL_{Img0}"] = TLC_tiss.average[4]

        # Emphysema & fSAD
        # Emph_ = os.path.join(subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_lobar_Emphy.txt")
        Emph_ = os.path.join(
            subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_lobar_Emph_fSAD.txt"
        )
        if not os.path.exists(Emph_):
            Emph_ = os.path.join(
                subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_lobar_Emphys.txt"
            )

        if os.path.exists(Emph_):
            Emph = pd.read_csv(Emph_, sep=" ")
            df[f"Emph_All_{FU}"] = Emph.Emphysratio[5]
            df[f"Emph_LUL_{FU}"] = Emph.Emphysratio[0]
            df[f"Emph_LLL_{FU}"] = Emph.Emphysratio[1]
            df[f"Emph_RUL_{FU}"] = Emph.Emphysratio[2]
            df[f"Emph_RML_{FU}"] = Emph.Emphysratio[3]
            df[f"Emph_RLL_{FU}"] = Emph.Emphysratio[4]

            df[f"fSAD_All_{FU}"] = Emph.fSADratio[5]
            df[f"fSAD_LUL_{FU}"] = Emph.fSADratio[0]
            df[f"fSAD_LLL_{FU}"] = Emph.fSADratio[1]
            df[f"fSAD_RUL_{FU}"] = Emph.fSADratio[2]
            df[f"fSAD_RML_{FU}"] = Emph.fSADratio[3]
            df[f"fSAD_RLL_{FU}"] = Emph.fSADratio[4]

        # Airtrap
        # AirT_ = os.path.join(subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_lobar_Airtrap.txt")
        AirT_ = os.path.join(
#            subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_lobar_Airtrap.txt"
             subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_lobar_AirT.txt" #20211031 IKL
        )
        if os.path.exists(AirT_):
            AirT = pd.read_csv(AirT_, sep=" ")
            df[f"AirT_All_{FU}"] = AirT.airtrapratio[5]
            df[f"AirT_LUL_{FU}"] = AirT.airtrapratio[0]
            df[f"AirT_LLL_{FU}"] = AirT.airtrapratio[1]
            df[f"AirT_RUL_{FU}"] = AirT.airtrapratio[2]
            df[f"AirT_RML_{FU}"] = AirT.airtrapratio[3]
            df[f"AirT_RLL_{FU}"] = AirT.airtrapratio[4]

        # RRAVC
        RRAVC_ = os.path.join(
            subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_lobar_RRAVC.txt"
        )
        if os.path.exists(RRAVC_):
            RRAVC = pd.read_csv(RRAVC_, sep=" ")
            df[f"RRAVC_All_{FU}"] = RRAVC.RRAVC_m[5]
            df[f"RRAVC_LUL_{FU}"] = RRAVC.RRAVC_m[0]
            df[f"RRAVC_LLL_{FU}"] = RRAVC.RRAVC_m[1]
            df[f"RRAVC_RUL_{FU}"] = RRAVC.RRAVC_m[2]
            df[f"RRAVC_RML_{FU}"] = RRAVC.RRAVC_m[3]
            df[f"RRAVC_RLL_{FU}"] = RRAVC.RRAVC_m[4]

        # s_norm
        s_norm_ = os.path.join(
            subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_lobar_s_norm.txt"
        )
        if os.path.exists(s_norm_):
            s_norm = pd.read_csv(s_norm_, sep=" ")
            df[f"sStar_All_{FU}"] = s_norm.sStar_m[5]
            df[f"sStar_LUL_{FU}"] = s_norm.sStar_m[0]
            df[f"sStar_LLL_{FU}"] = s_norm.sStar_m[1]
            df[f"sStar_RUL_{FU}"] = s_norm.sStar_m[2]
            df[f"sStar_RML_{FU}"] = s_norm.sStar_m[3]
            df[f"sStar_RLL_{FU}"] = s_norm.sStar_m[4]

        # HAA
        HAA_ = os.path.join(
            subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_lobar_HAA-700to0.txt"
        )
        if os.path.exists(HAA_):
            HAA = pd.read_csv(HAA_, sep=" ")
            df[f"HAA_All_{FU}"] = HAA.HAAratio[5]
            df[f"HAA_LUL_{FU}"] = HAA.HAAratio[0]
            df[f"HAA_LLL_{FU}"] = HAA.HAAratio[1]
            df[f"HAA_RUL_{FU}"] = HAA.HAAratio[2]
            df[f"HAA_RML_{FU}"] = HAA.HAAratio[3]
            df[f"HAA_RLL_{FU}"] = HAA.HAAratio[4]

        # Jacob
        J_ = os.path.join(
            subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_jacob_Lobe.dat"
        )
        if os.path.exists(J_):
            J = pd.read_csv(J_, sep=" ")
            df[f"J_All_{FU}"] = J.average[5]
            df[f"J_LUL_{FU}"] = J.average[0]
            df[f"J_LLL_{FU}"] = J.average[1]
            df[f"J_RUL_{FU}"] = J.average[2]
            df[f"J_RML_{FU}"] = J.average[3]
            df[f"J_RLL_{FU}"] = J.average[4]

        # ADI
        ADI_ = os.path.join(
            subj_path, f"{Subj}_{Img1}-TO-{Subj}_{Img0}-SSTVD_ADI_Lobe.dat"
        )
        if os.path.exists(ADI_):
            ADI = pd.read_csv(ADI_, sep=" ")
            df[f"ADI_All_{FU}"] = ADI.average[5]
            df[f"ADI_LUL_{FU}"] = ADI.average[0]
            df[f"ADI_LLL_{FU}"] = ADI.average[1]
            df[f"ADI_RUL_{FU}"] = ADI.average[2]
            df[f"ADI_RML_{FU}"] = ADI.average[3]
            df[f"ADI_RLL_{FU}"] = ADI.average[4]


        # pi10
        pi10_ = os.path.join(subj_path, f"{Subj}_{Img0}_vida-Pi10.csv")
        if os.path.exists(pi10_):
            pi10 = pd.read_csv(pi10_)
            df[f"whole_tree_all_INSP"] = pi10['pi10_whole_tree_all'].values[0]
            df[f"whole_tree_leq20_INSP"] = pi10['pi10_whole_tree_leq20'].values[0]

        # histo
        histo_ = os.path.join(subj_path, f"{Subj}_{Img0}_vida-histo.csv")
        if os.path.exists(histo_):
            histo = pd.read_csv(histo_)
            Lung = histo[histo.location == "both"]

            df[f"both_mean_hu_INSP"] = Lung['mean'].values[0]
            df[f"both_pct_be_950_INSP"] = Lung['percent-below_-950'].values[0]
            df[f"both_tissue_volume_cm3_INSP"] = Lung['tissue-volume-cm3'].values[0]
            df[f"both_air_volume_cm3_INSP"] = Lung['air-volume-cm3'].values[0]
            df[f"both_total_volume_cm3_INSP"] = Lung['total-volume-cm3'].values[0]


        # Air meas
        air_meas_ = os.path.join(subj_path, f"{Subj}_{Img0}_vida-airmeas.csv")
        if os.path.exists(air_meas_):
            air_meas = pd.read_csv(air_meas_)
            Trachea = air_meas[air_meas.anatomicalName == "Trachea"]
            RMB = air_meas[air_meas.anatomicalName == "RMB"]
            LMB = air_meas[air_meas.anatomicalName == "LMB"]
            LLB = air_meas[air_meas.anatomicalName == "LLB"]
            BronInt = air_meas[air_meas.anatomicalName == "BronInt"]
            LUL = air_meas[air_meas.anatomicalName == "LUL"]
            RUL = air_meas[air_meas.anatomicalName == "RUL"]
            RLL = air_meas[air_meas.anatomicalName == "RLL"]
            
            # segmental branches
            # Left Upper Lobe (LUL)
            LB1 = air_meas[air_meas.anatomicalName == "LB1"]
            LB2 = air_meas[air_meas.anatomicalName == "LB2"]
            LB3 = air_meas[air_meas.anatomicalName == "LB3"]
            LB4 = air_meas[air_meas.anatomicalName == "LB4"]
            LB5 = air_meas[air_meas.anatomicalName == "LB5"]
            # Left Lower Lobe (LLL)
            LB6 = air_meas[air_meas.anatomicalName == "LB6"]
            LB8 = air_meas[air_meas.anatomicalName == "LB8"]
            LB9 = air_meas[air_meas.anatomicalName == "LB9"]
            LB10 = air_meas[air_meas.anatomicalName == "LB10"]
            # Right Upper Lobe (RUL)
            RB1 = air_meas[air_meas.anatomicalName == "RB1"]
            RB2 = air_meas[air_meas.anatomicalName == "RB2"]
            RB3 = air_meas[air_meas.anatomicalName == "RB3"]
            # Right Middle Lobe (RML)
            RB4 = air_meas[air_meas.anatomicalName == "RB4"]
            RB5 = air_meas[air_meas.anatomicalName == "RB5"]
            # Right Lower Lobe (RLL)
            RB6 = air_meas[air_meas.anatomicalName == "RB6"]
            RB7 = air_meas[air_meas.anatomicalName == "RB7"]
            RB8 = air_meas[air_meas.anatomicalName == "RB8"]
            RB9 = air_meas[air_meas.anatomicalName == "RB9"]
            RB10 = air_meas[air_meas.anatomicalName == "RB10"]

            # Angle_Trachea
            RMB_vector = np.array(
                (RMB.dirCosX.values[0], RMB.dirCosY.values[0], RMB.dirCosZ.values[0])
            )
            LMB_vector = np.array(
                (LMB.dirCosX.values[0], LMB.dirCosY.values[0], LMB.dirCosZ.values[0])
            )
            RUL_vector = np.array(
                (RUL.dirCosX.values[0], RUL.dirCosY.values[0], RUL.dirCosZ.values[0])
            )
            BronInt_vector = np.array(
                (
                    BronInt.dirCosX.values[0],
                    BronInt.dirCosY.values[0],
                    BronInt.dirCosZ.values[0],
                )
            )
            df[f"Angle_eTrachea_{Img0}"] = Angle_vectors(RMB_vector, LMB_vector)
            # Angle between RUL and BronInt:
            df[f"Angle_eRMB_{Img0}"] = Angle_vectors(RUL_vector, BronInt_vector)

            # Circularity: C = 4*pi*A/P^2; P: perimeter
            df[f"Cr_Trachea_{Img0}"] = Circularity(Trachea)
            df[f"Cr_RMB_{Img0}"] = Circularity(RMB)
            df[f"Cr_LMB_{Img0}"] = Circularity(LMB)
            df[f"Cr_LLB_{Img0}"] = Circularity(LLB)
            df[f"Cr_BI_{Img0}"] = Circularity(BronInt)
            cr_LB1  = Circularity(LB1)
            cr_LB2  = Circularity(LB2)
            cr_LB3  = Circularity(LB3)
            cr_LB4  = Circularity(LB4)
            cr_LB5  = Circularity(LB5)
            cr_LB6  = Circularity(LB6)
            cr_LB8  = Circularity(LB8)
            cr_LB9  = Circularity(LB9)
            cr_LB10 = Circularity(LB10)
            cr_RB1  = Circularity(RB1)
            cr_RB2  = Circularity(RB2)
            cr_RB3  = Circularity(RB3)
            cr_RB4  = Circularity(RB4)
            cr_RB5  = Circularity(RB5)
            cr_RB6  = Circularity(RB6)
            cr_RB7  = Circularity(RB7)
            cr_RB8  = Circularity(RB8)
            cr_RB9  = Circularity(RB9)
            cr_RB10 = Circularity(RB10)

            df[f"Cr_sLUL_{Img0}"] = np.mean([cr_LB1,cr_LB2,cr_LB3,cr_LB4,cr_LB5])
            df[f"Cr_sLLL_{Img0}"] = np.mean([cr_LB6,cr_LB8,cr_LB9,cr_LB10])
            df[f"Cr_sRUL_{Img0}"] = np.mean([cr_RB1,cr_RB2,cr_RB3])
            df[f"Cr_sRML_{Img0}"] = np.mean([cr_RB4,cr_RB5])
            df[f"Cr_sRLL_{Img0}"] = np.mean([cr_RB6,cr_RB7,cr_RB8,cr_RB9,cr_RB10])

            # Eccentircity
            ecc_lb1 = Eccentricity(LB1)
            ecc_lb10 = Eccentricity(LB10)
            ecc_rb1 = Eccentricity(RB1)
            ecc_rb4 = Eccentricity(RB4)
            ecc_rb10 = Eccentricity(RB10)
            df[f"ECCENTRICITY"] = (ecc_lb1 + ecc_lb10 + ecc_rb1 + ecc_rb4 + ecc_rb10)/5

            # LADIVBYCL
            l_cl_lb1 = LADIVBYCL(LB1)
            l_cl_lb10 = LADIVBYCL(LB10)
            l_cl_rb1 = LADIVBYCL(RB1)
            l_cl_rb4 = LADIVBYCL(RB4)
            l_cl_rb10 = LADIVBYCL(RB10)
            df[f"LADIVBYCL"] = (l_cl_lb1 + l_cl_lb10 + l_cl_rb1 + l_cl_rb4 + l_cl_rb10)/5

            # avgminorinnerdiam, avgmajorinnerdiam
            minor_in_d_lb1, major_in_d_lb1 = D_inner(LB1)
            minor_in_d_lb10, major_in_d_lb10 = D_inner(LB10)
            minor_in_d_rb1, major_in_d_rb1 = D_inner(RB1)
            minor_in_d_rb4, major_in_d_rb4 = D_inner(RB4)
            minor_in_d_rb10, major_in_d_rb10 = D_inner(RB10)
            df[f"Dminor"] = (minor_in_d_lb1 + minor_in_d_lb10 + minor_in_d_rb1 + minor_in_d_rb4 + minor_in_d_rb10)/5
            df[f"Dmajor"] = (major_in_d_lb1 + major_in_d_lb10 + major_in_d_rb1 + major_in_d_rb4 + major_in_d_rb10)/5

            # avginnerarea, avgouterarea
            in_A_lb1, out_A_lb1 = Area_lumen(LB1)
            in_A_lb10, out_A_lb10 = Area_lumen(LB10)
            in_A_rb1, out_A_rb1 = Area_lumen(RB1)
            in_A_rb4, out_A_rb4 = Area_lumen(RB4)
            in_A_rb10, out_A_rb10 = Area_lumen(RB10)
            LA = (in_A_lb1 + in_A_lb10 + in_A_rb1 + in_A_rb4 + in_A_rb10)/5
            df[f"LA"] = LA
            OA = (out_A_lb1 + out_A_lb10 + out_A_rb1 + out_A_rb4 + out_A_rb10)/5
            df[f"OA"] = OA

            df[f"Dout"] = np.sqrt((4*OA)/np.pi)

            # avginnerperimeter, avgouterperimeter
            in_P_lb1, out_P_lb1 = Peri_lumen(LB1)
            in_P_lb10, out_P_lb10 = Peri_lumen(LB10)
            in_P_rb1, out_P_rb1 = Peri_lumen(RB1)
            in_P_rb4, out_P_rb4 = Peri_lumen(RB4)
            in_P_rb10, out_P_rb10 = Peri_lumen(RB10)
            df[f"Peri"] = (in_P_lb1 + in_P_lb10 + in_P_rb1 + in_P_rb4 + in_P_rb10)/5
            df[f"Peri_o"] = (out_P_lb1 + out_P_lb10 + out_P_rb1 + out_P_rb4 + out_P_rb10)/5

            # WALLAREA, WALLAREAPCT
            wall_A_lb1, wall_A_p_lb1 = Area_wall(LB1)
            wall_A_lb10, wall_A_p_lb10 = Area_wall(LB10)
            wall_A_rb1, wall_A_p_rb1 = Area_wall(RB1)
            wall_A_rb4, wall_A_p_rb4 = Area_wall(RB4)
            wall_A_rb10, wall_A_p_rb10 = Area_wall(RB10)
            df[f"WA"] = (wall_A_lb1 + wall_A_lb10 + wall_A_rb1 + wall_A_rb4 + wall_A_rb10)/5
            df[f"WA_pct"] = (wall_A_p_lb1 + wall_A_p_lb10 + wall_A_p_rb1 + wall_A_p_rb4 + wall_A_p_rb10)/5

            # avgavgwallthickness, WALLTHICKNESSPCT
            wall_th_lb1, wall_th_p_lb1 = Thickness_wall(LB1)
            wall_th_lb10, wall_th_p_lb10 = Thickness_wall(LB10)
            wall_th_rb1, wall_th_p_rb1 = Thickness_wall(RB1)
            wall_th_rb4, wall_th_p_rb4 = Thickness_wall(RB4)
            wall_th_rb10, wall_th_p_rb10 = Thickness_wall(RB10)
            df[f"WT"] = (wall_th_lb1 + wall_th_lb10 + wall_th_rb1 + wall_th_rb4 + wall_th_rb10)/5
            df[f"WT_pct"] = (wall_th_p_lb1 + wall_th_p_lb10 + wall_th_p_rb1 + wall_th_p_rb4 + wall_th_p_rb10)/5

            if demo_available:
                # Normalized Wall thickness
                df[f"WTn_Trachea_{Img0}"] = WT_norm(Trachea, row, KOR)
                df[f"WTn_RMB_{Img0}"] = WT_norm(RMB, row, KOR)
                df[f"WTn_LMB_{Img0}"] = WT_norm(LMB, row, KOR)
                df[f"WTn_LLB_{Img0}"] = WT_norm(LLB, row, KOR)
                df[f"WTn_BI_{Img0}"] = WT_norm(BronInt, row, KOR)
                wTn_LB1  = WT_norm(LB1,row,KOR)
                wTn_LB2  = WT_norm(LB2,row,KOR)
                wTn_LB3  = WT_norm(LB3,row,KOR)
                wTn_LB4  = WT_norm(LB4,row,KOR)
                wTn_LB5  = WT_norm(LB5,row,KOR)
                wTn_LB6  = WT_norm(LB6,row,KOR)
                wTn_LB8  = WT_norm(LB8,row,KOR)
                wTn_LB9  = WT_norm(LB9,row,KOR)
                wTn_LB10 = WT_norm(LB10,row,KOR)
                wTn_RB1  = WT_norm(RB1,row,KOR)
                wTn_RB2  = WT_norm(RB2,row,KOR)
                wTn_RB3  = WT_norm(RB3,row,KOR)
                wTn_RB4  = WT_norm(RB4,row,KOR)
                wTn_RB5  = WT_norm(RB5,row,KOR)
                wTn_RB6  = WT_norm(RB6,row,KOR)
                wTn_RB7  = WT_norm(RB7,row,KOR)
                wTn_RB8  = WT_norm(RB8,row,KOR)
                wTn_RB9  = WT_norm(RB9,row,KOR)
                wTn_RB10 = WT_norm(RB10,row,KOR)

                df[f"WTn_sLUL_{Img0}"] = np.mean([wTn_LB1,wTn_LB2,wTn_LB3,wTn_LB4,wTn_LB5])
                df[f"WTn_sLLL_{Img0}"] = np.mean([wTn_LB6,wTn_LB8,wTn_LB9,wTn_LB10])
                df[f"WTn_sRUL_{Img0}"] = np.mean([wTn_RB1,wTn_RB2,wTn_RB3])
                df[f"WTn_sRML_{Img0}"] = np.mean([wTn_RB4,wTn_RB5])
                df[f"WTn_sRLL_{Img0}"] = np.mean([wTn_RB6,wTn_RB7,wTn_RB8,wTn_RB9,wTn_RB10])

                # Normalized hydraulic diameter: 4A/P
                df[f"Dhn_Trachea_{Img0}"] = Dh_norm(Trachea, row, KOR)
                df[f"Dhn_RMB_{Img0}"] = Dh_norm(RMB, row, KOR)
                df[f"Dhn_LMB_{Img0}"] = Dh_norm(LMB, row, KOR)
                df[f"Dhn_LLB_{Img0}"] = Dh_norm(LLB, row, KOR)
                df[f"Dhn_BI_{Img0}"] = Dh_norm(BronInt, row, KOR)

                dhn_LB1  = Dh_norm(LB1,row,KOR)
                dhn_LB2  = Dh_norm(LB2,row,KOR)
                dhn_LB3  = Dh_norm(LB3,row,KOR)
                dhn_LB4  = Dh_norm(LB4,row,KOR)
                dhn_LB5  = Dh_norm(LB5,row,KOR)
                dhn_LB6  = Dh_norm(LB6,row,KOR)
                dhn_LB8  = Dh_norm(LB8,row,KOR)
                dhn_LB9  = Dh_norm(LB9,row,KOR)
                dhn_LB10 = Dh_norm(LB10,row,KOR)
                dhn_RB1  = Dh_norm(RB1,row,KOR)
                dhn_RB2  = Dh_norm(RB2,row,KOR)
                dhn_RB3  = Dh_norm(RB3,row,KOR)
                dhn_RB4  = Dh_norm(RB4,row,KOR)
                dhn_RB5  = Dh_norm(RB5,row,KOR)
                dhn_RB6  = Dh_norm(RB6,row,KOR)
                dhn_RB7  = Dh_norm(RB7,row,KOR)
                dhn_RB8  = Dh_norm(RB8,row,KOR)
                dhn_RB9  = Dh_norm(RB9,row,KOR)
                dhn_RB10 = Dh_norm(RB10,row,KOR)

                df[f"Dhn_sLUL_{Img0}"] = np.mean([dhn_LB1,dhn_LB2,dhn_LB3,dhn_LB4,dhn_LB5])
                df[f"Dhn_sLLL_{Img0}"] = np.mean([dhn_LB6,dhn_LB8,dhn_LB9,dhn_LB10])
                df[f"Dhn_sRUL_{Img0}"] = np.mean([dhn_RB1,dhn_RB2,dhn_RB3])
                df[f"Dhn_sRML_{Img0}"] = np.mean([dhn_RB4,dhn_RB5])
                df[f"Dhn_sRLL_{Img0}"] = np.mean([dhn_RB6,dhn_RB7,dhn_RB8,dhn_RB9,dhn_RB10])


            else:
                df[f"WTn_Trachea_{Img0}"] = "na"
                df[f"WTn_RMB_{Img0}"] = "na"
                df[f"WTn_LMB_{Img0}"] = "na"
                df[f"WTn_LLB_{Img0}"] = "na"
                df[f"WTn_BI_{Img0}"] = "na"
                df[f"WTn_sLUL_{Img0}"] = "na"
                df[f"WTn_sLLL_{Img0}"] = "na"
                df[f"WTn_sRUL_{Img0}"] = "na"
                df[f"WTn_sRML_{Img0}"] = "na"
                df[f"WTn_sRLL_{Img0}"] = "na"

                df[f"Dhn_Trachea_{Img0}"] = "na"
                df[f"Dhn_RMB_{Img0}"] = "na"
                df[f"Dhn_LMB_{Img0}"] = "na"
                df[f"Dhn_LLB_{Img0}"] = "na"
                df[f"Dhn_BI_{Img0}"] = "na"
                df[f"Dhn_sLUL_{Img0}"] = "na"
                df[f"Dhn_sLLL_{Img0}"] = "na"
                df[f"Dhn_sRUL_{Img0}"] = "na"
                df[f"Dhn_sRML_{Img0}"] = "na"
                df[f"Dhn_sRLL_{Img0}"] = "na"

            # Save per subject
            df.to_csv(
                os.path.join(subj_path, f"{Proj}_{Subj}_{Img0}_{Img1}_QCT.csv"),
                index=False,
            )
        if i == 0:
            final_df = df
        else:
            final_df = pd.concat([final_df, df], ignore_index=True)
    # Save all subjects
    final_df.to_csv(
        os.path.join(path, f"{Proj}_{Img0}_{Img1}_QCT_all.csv"), index=False
    )


if __name__ == "__main__":
    main()
