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

        # Air meas
        air_meas_ = os.path.join(subj_path, f"{Subj}_{Img0}_vida-airmeas.csv")
        if os.path.exists(air_meas_):
            air_meas = pd.read_csv(air_meas_)
            Trachea = air_meas[air_meas.anatomicalName == "Trachea"]
            RMB = air_meas[air_meas.anatomicalName == "RMB"]
            LMB = air_meas[air_meas.anatomicalName == "LMB"]
            LLB = air_meas[air_meas.anatomicalName == "LLB"]
            BronInt = air_meas[air_meas.anatomicalName == "BronInt"]
            sLUL = air_meas[air_meas.anatomicalName == "LUL"]
            sRUL = air_meas[air_meas.anatomicalName == "RUL"]
            sRLL = air_meas[air_meas.anatomicalName == "RLL"]

            # Angle_Trachea
            RMB_vector = np.array(
                (RMB.dirCosX.values[0], RMB.dirCosY.values[0], RMB.dirCosZ.values[0])
            )
            LMB_vector = np.array(
                (LMB.dirCosX.values[0], LMB.dirCosY.values[0], LMB.dirCosZ.values[0])
            )
            sRUL_vector = np.array(
                (sRUL.dirCosX.values[0], sRUL.dirCosY.values[0], sRUL.dirCosZ.values[0])
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
            df[f"Angle_eRMB_{Img0}"] = Angle_vectors(sRUL_vector, BronInt_vector)

            # Circularity: C = 4*pi*A/P^2; P: perimeter
            df[f"Cr_Trachea_{Img0}"] = Circularity(Trachea)
            df[f"Cr_RMB_{Img0}"] = Circularity(RMB)
            df[f"Cr_LMB_{Img0}"] = Circularity(LMB)
            df[f"Cr_LLB_{Img0}"] = Circularity(LLB)
            df[f"Cr_BI_{Img0}"] = Circularity(BronInt)
            df[f"Cr_sLUL_{Img0}"] = Circularity(sLUL)
            df[f"Cr_sRUL_{Img0}"] = Circularity(sRUL)
            df[f"Cr_sRLL_{Img0}"] = Circularity(sRLL)

            if demo_available:
                # Normalized Wall thickness
                df[f"WTn_Trachea_{Img0}"] = WT_norm(Trachea, row, KOR)
                df[f"WTn_RMB_{Img0}"] = WT_norm(RMB, row, KOR)
                df[f"WTn_LMB_{Img0}"] = WT_norm(LMB, row, KOR)
                df[f"WTn_LLB_{Img0}"] = WT_norm(LLB, row, KOR)
                df[f"WTn_BI_{Img0}"] = WT_norm(BronInt, row, KOR)
                df[f"WTn_sLUL_{Img0}"] = WT_norm(sLUL, row, KOR)
                df[f"WTn_sRUL_{Img0}"] = WT_norm(sRUL, row, KOR)
                df[f"WTn_sRLL_{Img0}"] = WT_norm(sRLL, row, KOR)

                # Normalized hydraulic diameter: 4A/P
                df[f"Dhn_Trachea_{Img0}"] = Dh_norm(Trachea, row, KOR)
                df[f"Dhn_RMB_{Img0}"] = Dh_norm(RMB, row, KOR)
                df[f"Dhn_LMB_{Img0}"] = Dh_norm(LMB, row, KOR)
                df[f"Dhn_LLB_{Img0}"] = Dh_norm(LLB, row, KOR)
                df[f"Dhn_BI_{Img0}"] = Dh_norm(BronInt, row, KOR)
                df[f"Dhn_sLUL_{Img0}"] = Dh_norm(sLUL, row, KOR)
                df[f"Dhn_sRUL_{Img0}"] = Dh_norm(sRUL, row, KOR)
                df[f"Dhn_sRLL_{Img0}"] = Dh_norm(sRLL, row, KOR)

            else:
                df[f"WTn_Trachea_{Img0}"] = "na"
                df[f"WTn_RMB_{Img0}"] = "na"
                df[f"WTn_LMB_{Img0}"] = "na"
                df[f"WTn_LLB_{Img0}"] = "na"
                df[f"WTn_BI_{Img0}"] = "na"
                df[f"WTn_sLUL_{Img0}"] = "na"
                df[f"WTn_sRUL_{Img0}"] = "na"
                df[f"WTn_sRLL_{Img0}"] = "na"

                df[f"Dhn_Trachea_{Img0}"] = "na"
                df[f"Dhn_RMB_{Img0}"] = "na"
                df[f"Dhn_LMB_{Img0}"] = "na"
                df[f"Dhn_LLB_{Img0}"] = "na"
                df[f"Dhn_BI_{Img0}"] = "na"
                df[f"Dhn_sLUL_{Img0}"] = "na"
                df[f"Dhn_sRUL_{Img0}"] = "na"
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
