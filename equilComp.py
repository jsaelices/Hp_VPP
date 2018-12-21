__author__ = 'Jaime Saelices'
__copyright__ = 'Copyright 2016, Jaime Saelices'
__license__ = 'GPL'
__version__ = '0.1.0'
__email__ = 'jsaelices@gmail.com'
__status__ = 'dev'

import numpy as np
import scipy as sp
import pandas as pd
from scipy.interpolate import interp1d
import math
import os
from datetime import datetime
import shutil
import sys
import csv
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("projectname", action='store', help="project name")
parser.add_argument("-p", action='store', type=float, nargs=1, dest='p', help="P rig dimension")
parser.add_argument("-e", action='store', type=float, nargs=1, dest='e', help="E rig dimension")
parser.add_argument("-j", action='store', type=float, nargs=1, dest='j', help="J rig dimension")
parser.add_argument("-ig", action='store', type=float, nargs=1, dest='ig', help="IG rig dimension")
parser.add_argument("-sl", action='store', type=float, nargs=1, dest='sl', help="SL rig dimension")
parser.add_argument("-bad", action='store', type=float, nargs=1, dest='bad', help="BAD rig dimension")
parser.add_argument("-ehm", action='store', type=float, nargs=1, dest='ehm', help="EHM rig dimension")
parser.add_argument("-fam", action='store', type=float, nargs=1, dest='fam', help="FAM boat dimension")
parser.add_argument("-b", action='store', type=float, nargs=1, dest='b', help="B boat dimension")
parser.add_argument("-emdc", action='store', type=float, nargs=1, dest='emdc', help="EMDC rig dimension")
parser.add_argument("-ketch", action='store_true', default=False, dest='ketch', help="indicates that boat is a ketch type")
parser.add_argument("-yawl", action='store_true', default=False, dest='yawl', help="indicates that boat is a yawl type")

parser.add_argument("-cm", action='store', type=float, nargs=1, dest='cm', help="Midship coefficient")
parser.add_argument("-cp", action='store', type=float, nargs=1, dest='cp', help="Prismatic coefficient")
parser.add_argument("-nablac", action='store', type=float, nargs=1, dest='nablac', help="Displacement volume of canoe body")
parser.add_argument("-lwl", action='store', type=float, nargs=1, dest='lwl', help="Length in the waterline")
parser.add_argument("-bwl", action='store', type=float, nargs=1, dest='bwl', help="Beam in the waterline")
parser.add_argument("-aw", action='store', type=float, nargs=1, dest='aw', help="Area of the waterplane")
parser.add_argument("-tc", action='store', type=float, nargs=1, dest='tc', help="Draft of canoe body")
parser.add_argument("-lcb", action='store', type=float, nargs=1, dest='lcb', help="Longitudinal center of buoyancy (from forward perpendicular)")
parser.add_argument("-lcf", action='store', type=float, nargs=1, dest='lcf', help="Longitudinal center of flotation (from forward perpendicular)")
parser.add_argument("-kc", action='store_true', default=False, dest='kc', help="Keel mean chord")
parser.add_argument("-kt", action='store_true', default=False, dest='kt', help="Keel thickness")
parser.add_argument("-rc", action='store_true', default=False, dest='rc', help="Rudder mean chord")
parser.add_argument("-rt", action='store_true', default=False, dest='rt', help="Rudder thickness")
parser.add_argument("-nablak", action='store_true', default=False, dest='nablak', help="Displacement volume of keel")
parser.add_argument("-z", action='store_true', default=False, dest='z', help="Vertical position of center of buoyancy of keel")
parser.add_argument("-t", action='store_true', default=False, dest='t', help="Draft of the boat")
parser.add_argument("-rt", action='store_true', default=False, dest='rt', help="Rudder thickness")
parser.add_argument("-alat", action='store_true', default=False, dest='alat', help="Projected area of hull and keel")

args = parser.parse_args()

########################################################################################################################
########################################################################################################################
#
# Variables definitions
#
# TWA--> True Wind Angle
# TWS--> True Wind Speed
# AWA--> Apparent Wind Angle
# AWS--> Apparent Wind Speed
# AWAe--> Effective AWA
# AWSe--> Effective AWS
# Bs--> Boat speed
# FAM--> Freeboard aft
# FDM--> Freeboard midships
# FBI--> Freeboard at fore side mast location
# FFM--> Freeboard forward
# MB--> Maximum beam
# DMT--> Vertical distance from the deepest point of keel or bulb to the sheer point at the same section
# SFFP--> Horizontal distance from the forward end of LOA to the forward freeboard station
# SAFP--> Horizontal distance from the forward end of LOA to the aft freeboard station
# SDM--> Horizontal distance from the bow to the maximum draft section
# SMB--> Horizontal distance from the forward end of LOA to the maximum beam section
# LOA--> Length Over All
# LWL--> Length in the waterline
# BWL--> Beam in the waterline
# Cp--> Longitudinal prismatic coefficient
# Cb--> Block coefficient
# Awp--> Area of the waterplane
# LCB--> Longitudinal position of center of buoyancy
# LCF--> Longitudinal position of center of flotation
# GZ--> Arm of righting moment
# GM--> Metacentric height
# KN--> Distance from keel to direction of application of buoyancy
# KM--> Height of metacenter
# KC--> Height of center of buoyancy
# KG--> Height of CoG
# CM--> Metacentric radius
# TC--> Draft of canoe body
# T--> Draft of boat
# Nablac--> Volume of displacement of canoe body
# Nablak--> Volume of displacement of keel
# Ws--> Wetted surface
# Wsh--> Heeled wetted surface
# Wsk--> Keel wetted surface
# Wsr--> Rudder wetted surface
# ff--> Form factor
# t--> Thickness of appendage (k-keel, r-rudder, f-forward foil, dss-dynamic stability system, d-daggerboards)
# c--> chord of appendage
# Zcbk--> Height of center of buoyancy of keel
# AR--> Aspect Ratio of appendage
# ARe--> Effective AR
# Rn--> Reynolds number
# Fn--> Froude number based on length
# Cf--> Friction resistance coefficient
# Cdo--> Windage resistance coefficient
# Cdp--> Parasitic drag coefficient
# Cdi--> Induced resistance coefficient
# Clm--> Mainsail lift coefficient
# Cdm--> Mainsail drag coefficient
# Clj--> Jibsail lift coefficient
# Cdj--> Jibsail drag coefficient
# Cls--> Spinnaker lift coefficient
# Cds--> Spinnaker drag coefficient
# Cr--> Residuary drag coefficient
# Clk--> Keel lift coefficient
# Cdk--> Keel drag coefficient
# Clr--> Rudder lift coefficient
# Cdr--> Rudder drag coefficient
# Cld--> Daggerboard lift coefficient
# Cdd--> Daggerboard drag coefficient
# Clf--> Forward foil lift coefficient
# Cdf--> Forward foil drag coefficient
# Cldss--> Dynamic Stability System lift coefficient
# Cddss--> DSS drag coefficient
# Lm--> Lift of mainsail
# Dm--> Drag of mainsail
# Lj--> Lift of jibsail
# Dj--> Drag of jibsail
# Ls--> Lift of spinnaker
# Ds--> Drag of spinnaker
# Lk--> Lift of keel
# Dk--> Drag of keel
# Lr--> Lift of rudder
# Dr--> Drag of rudder
# Ld--> Lift of daggerboards
# Dd--> Drag of daggerboards
# Lf--> Lift of forward foil
# Df--> Drag of forward foil
# Ldss--> Lift of DSS
# Ddss--> Drag of DSS
# Fy--> Heeling force due to sails
# Fx--> Driving force due to sails
# R--> Total resistance of the boat
# Fside--> Lateral force due to hydrodynamic forces
# Dprop--> Resistance due to propeller presence
# Mx--> Heeling moment due to aero-hydro forces
# My--> Bow down moment due to aero-hydro forces
# Mz--> Yaw moment due to aero-hydro forces
# RMt--> Transversal righting moment
# RMl--> Longitudinal righting moment
# RMz--> Yaw moment due to hydrodynamic forces (rudder)
#
# For propeller values see IMS Documentation from www.orc.org
# For rig and sails measurement values see also ORC web page
#
########################################################################################################################
#
# AERO model variables declaration
#
########################################################################################################################
#
# Wind and state variables
#
global TWA, TWS, AWA, AWS, AWAe, AWSe, leeway, heel, Bs, rho
#
# Adimensional coefficients
#
global Cf, Cl, Cd, Cdo, Cdp, Cdi, Clm, Clj, Cdm, Cdj, Cls, Cds, Cly, Cdy, Clys, Cdys
#
# Forces
#
global L, Lm, Dm, Lj, Dj, Ls, Ds, Ly, Lys, D, Dy, Dys, Fy, Fx
#
# Moments
#
global Mx, My, Mz, RMt, RMl, RMz
#
# Boolean variables for boat type
#
global sloop, ketch, yawl, catamaran, trimaran
#
# Boolean variables for sails inventory
#
global main, jib, spi, code0, j1, j2, j3, j4, j5, a1, a1_5, a2, a3, a4, a5, s1, s1_5, s2, s3, s4, s5, c1, c2, g0, g1, g2, g3, battens
#
# Rig and sails measurement values
#
global MDT1, MDL1, MDT2, MDL2, TL, MW, GO, GOA, BD, BAL, BWT, J, IG, ISP, SPS, BAD, EHM, EMDC, E, P, SFJ, CPW, CPD, FSP, \
    SPL, TPS, MWT, MCG, LPG, PY, MDT1Y, MDL1Y, MDT2Y, MDL2Y, TLY, BADY, EY, BDY, BALY, IY, EB, HB, MGT, MGU, MGM, MGL, \
    HBY, MGLY, MGMY, MGUY, MGTY, JH, JGT, JGU, JGM, JGL, JL, YSD, YSMG, YSF, SL, SMG, SF, SLU, SLE, AMG, ASF
#
# Sails parameters for aero model
#
global reef, flat, twist
#
# Center of Efforts and Areas
#
global CEm, CEj, CEs, CEy, CEys, CE, Am, Aj, Ag, As, Ay, Ays, areas, ARa

########################################################################################################################
#
# HYDRO model variables declaration
#
#######################################################################################################################
#
# Water properties
#
global rhow, nu, mu
#
# Hull measurement values
#
global FAM, FDM, FBI, FFM, MB, DMT, SFFP, SAFP, SDM, SMB, Loa, Lwl, Bwl, B
#
# Appendages measurement values
#
global KTHU, KTHM, KTHL, KBW, KBL, KBH, KBWT, KW, KWC, KCG, ECM, KCDA, WCBA, CBDA, CBDB, CBRC, CBMC, CBTC, RCG, RSP, RC1, \
    RT1, RC2, RT2, RY, RAN, BS, BC, BT, BX, BY, BA, BF, DSS, DSC, DST, DSA, DSD
#
# Hull and appendages parameters
#
global Cp, Cb, Cm, Aw, LCB, LCF, GZ, GM, KN, KM, KC, KG, CM, Tc, T, Nablac, Nablak, Ws, Wsh, Wsk, Wsr, Wsd, tk, ck, tr, \
    cr, td, cd, tff, cff, tdss, cdss, Zcbk, ARk, ARr
#
# Adimensional numbers
#
global Rn, Fn
#
# Forces generated on underwater hull
#
global Rfh, Rrh, Rvk, Rrk, Rvr, dRft, dRrt, dRrkt, dRtp, dRrtrim, Raw
#
# Propeller measurement values
#
global PIPA, PHD, ST1, ST2, ST3, ST4, ST5, PRD, PHL, PSA, ESL, APT, APB, APH, EDL

########################################################################################################################
########################################################################################################################
#
# Variables needed when CFD or experimental data is imported
#
########################################################################################################################
#
# Adimensional coefficients
#
global Cr, Clk, Cdk, Clr, Cdr, Cld, Cdd, Clf, Cdf, Cldss, Cddss
#
# Forces on the underwater elements
#
global Lk, Dk, Lr, Dr, Ld, Dd, Lf, Df, Ldss, Ddss, Rf, Rp, Fside, Dprop
########################################################################################################################
########################################################################################################################
#
# AERO MODELS:
#
# SIMPLIFIED (according to Principles of Yacht Design and Ship Resistance and Propulsion books)
#           Aero follows Hazen model although the twist of sails can be chosen
# ORC MODEL (according to ORC VPP DOCUMENTATION 2015/2016)
#           This model is enhanced with a bigger sails inventory and a more accurate sail area calculation
# CFD DATA
#           Direct computation of forces and moments using any CFD solver available. The equilibrium state search is a task performed by VPP solver.
# WIND TUNNEL DATA
#           Forces and moments obtained on wind tunnel and extrapolated to full scale using some method
#
########################################################################################################################
########################################################################################################################

########################################################################################################################
########################################################################################################################
#
# Wind and water properties
#
TWS = range(2, 30, 2)
TWA = range(40, 180, 10)
rho = 1.225
rhow = 1025
nu = 1.139e-6

Boatname = args.projectname

J = args.j[0]
IG = args.ig[0]
E = args.e[0]
P = args.p[0]
SL = args.sl[0]
BAD = args.bad[0]
EHM = args.ehm[0]
FAM = args.fam[0]
B = args.b[0]
EMDC = args.emdc[0]
PY = args.py[0]
EY = args.ey[0]
YSD = args.ysd[0]
YSMG = args.ysmg[0]
YSF = args.ysf[0]
BADY = args.bady[0]

Bwl = args.bwl[0]
Lwl = args.lwl[0]
Nablac = args.nablac[0]
Cm = args.cm[0]
Tc = args.tc[0]
LCB = args.lcb[0]
LCF = args.lcf[0]
Aw = args.aw[0]

########################################################################################################################
#
# Functions to do unit systems conversions
#
########################################################################################################################
def siSConv(x):
    sival = x * 0.5144
    return sival

def knConv(x):
    knval = x / 0.5144
    return knval

########################################################################################################################
#
# Functions to compute AWA, AWS, AWAe and AWSe
#
########################################################################################################################
def awaComp(TWA, TWS, Bs):
    global AWA
    TWSsi = siSConv(TWS)
    Bssi = siSConv(Bs)
    TWArad = math.radians(TWA)
    value = math.sin(TWArad) / (math.cos(TWArad) + (Bssi / TWSsi))
    value2 = math.atan(value)
    AWA = math.degrees(value2)
    return AWA


def awsComp(TWA, AWA, TWS):
    global AWS
    TWSsi = siSConv(TWS)
    TWArad = math.radians(TWA)
    AWArad = math.radians(AWA)
    value = TWSsi * (math.sin(TWArad) / math.sin(AWArad))
    AWS = value
    return AWS


def awseComp(TWS, Bs, TWA, heel):
    global AWSe
    TWSsi = siSConv(TWS)
    Bssi = siSConv(Bs)
    TWArad = math.radians(TWA)
    heelrad = math.radians(heel)
    V1 = Bssi + TWSsi * math.cos(TWArad)
    V2 = TWSsi * math.sin(TWArad) * math.cos(heelrad)
    AWSe = math.sqrt(math.pow(V1, 2) + math.pow(V2, 2))
    return AWSe


def awaeComp(TWS, Bs, TWA, heel):
    global AWAe
    TWSsi = siSConv(TWS)
    Bssi = siSConv(Bs)
    TWArad = math.radians(TWA)
    heelrad = math.radians(heel)
    V1 = Bssi + TWSsi * math.cos(TWArad)
    value1 = awseComp(TWS, Bs, TWA, heel)
    value2 = math.acos(V1 / value1)
    AWAe = math.degrees(value2)
    return AWAe


########################################################################################################################
########################################################################################################################
#
# Tabulated Cl and Cd values from Principles of Yacht Design used in simplified aero method
#
########################################################################################################################
simpl_angle = [0, 10, 27, 50, 80, 100, 180]
main_cl_simpl = [0, 1, 1.5, 1.5, 0.95, 0.85, 0]
main_cd_simpl = [0, 0, 0.02, 0.15, 0.8, 1, 0.9]
jib_cl_simpl = [0, 1, 1.5, 0.5, 0.3, 0, 0]
jib_cd_simpl = [0, 0, 0.02, 0.25, 0.15, 0, 0]
spi_cl_simpl = [0, 0, 0.6, 1.5, 1, 0.85, 0]
spi_cd_simpl = [0, 0, 0, 0.25, 0.9, 1.2, 0.66]
mizzen_cl_simpl = [0, 1, 1.3, 1.4, 1, 0.8, 0]
mizzen_cd_simpl = [0, 0, 0.02, 0.15, 0.75, 1, 0.8]
mizz_stays_cl_simpl = [0, 0, 0.4, 0.75, 1, 0.8, 0]
mizz_stays_cd_simpl = [0, 0, 0, 0.1, 0.75, 1, 0]

#
# We do cubic interpolation using tabulated values
#
main_cl_funcs = interp1d(simpl_angle, main_cl_simpl, 3)
main_cd_funcs = interp1d(simpl_angle, main_cd_simpl, 3)
jib_cl_funcs = interp1d(simpl_angle, jib_cl_simpl, 3)
jib_cd_funcs = interp1d(simpl_angle, jib_cd_simpl, 3)
spi_cl_funcs = interp1d(simpl_angle, spi_cl_simpl, 3)
spi_cd_funcs = interp1d(simpl_angle, spi_cd_simpl, 3)
mizzen_cl_funcs = interp1d(simpl_angle, mizzen_cl_simpl, 3)
mizzen_cd_funcs = interp1d(simpl_angle, mizzen_cd_simpl, 3)
mizz_stays_cl_funcs = interp1d(simpl_angle, mizz_stays_cl_simpl, 3)
mizz_stays_cd_funcs = interp1d(simpl_angle, mizz_stays_cd_simpl, 3)

val = main_cl_funcs(170)

########################################################################################################################
########################################################################################################################
#
# Tabulated Cl and Cd values from ORC documentation used in ORC method
#
########################################################################################################################
main_angle = [0, 7, 9, 12, 28, 60, 90, 120, 150, 180]
main_cl_low = [0, 0.862, 1.052, 1.164, 1.347, 1.239, 1.125, 0.838, 0.296, -0.112]
main_cd_low = [0.043, 0.026, 0.023, 0.023, 0.033, 0.113, 0.383, 0.969, 1.316, 1.345]
main_cl_high = [0, 0.948, 1.138, 1.25, 1.427, 1.269, 1.125, 0.838, 0.296, -0.112]
main_cd_high = [0.034, 0.017, 0.015, 0.015, 0.026, 0.113, 0.383, 0.969, 1.316, 1.345]

jib_angle = [7, 15, 20, 27, 50, 60, 100, 150, 180]
jib_cl_low = [0, 1, 1.375, 1.450, 1.430, 1.250, 0.400, 0, -0.100]
jib_cd_low = [0.05, 0.032, 0.031, 0.037, 0.250, 0.350, 0.730, 0.950, 0.900]
jib_cl_high = [0, 1.100, 1.475, 1.500, 1.430, 1.250, 0.400, 0, -0.100]
jib_cd_high = [0.050, 0.032, 0.031, 0.037, 0.250, 0.350, 0.730, 0.950, 0.900]

spi_angle = [28, 41, 50, 60, 67, 75, 100, 115, 130, 150, 180]
sym_spi_cl = [0, 0.978, 1.241, 1.454, 1.456, 1.437, 1.190, 0.951, 0.706, 0.425, 0]
sym_spi_cd = [0.213, 0.321, 0.425, 0.587, 0.598, 0.619, 0.850, 0.911, 0.935, 0.935, 0.935]
asym_spi_cl = [0.026, 1.018, 1.277, 1.471, 1.513, 1.444, 1.137, 0.829, 0.560, 0.250, 0.120]
asym_spi_cd = [0.191, 0.280, 0.366, 0.523, 0.448, 0.556, 0.757, 0.790, 0.776, 0.620, 0.400]
asym_spi_cl_pole = [0.085, 1.114, 1.360, 1.513, 1.548, 1.479, 1.207, 0.956, 0.706, 0.425, 0]
asym_spi_cd_pole = [0.170, 0.238, 0.306, 0.459, 0.392, 0.493, 0.791, 0.894, 0.936, 0.936, 0.936]

c0_angle = [7, 19, 26, 35, 42, 53, 70, 100, 120, 150, 180]
c0_cl = [0, 0.766, 1.367, 1.647, 1.685, 1.455, 1.111, 0.613, 0.345, 0.115, -0.054]
c0_cd = [0.05, 0.034, 0.05, 0.061, 0.107, 0.214, 0.360, 0.567, 0.651, 0.628, 0.551]
c0_cl_batt = [0, 0.797, 1.442, 1.746, 1.786, 1.535, 1.172, 0.633, 0.353, 0.115, 0.054]
c0_cd_batt = [0.041, 0.029, 0.041, 0.051, 0.094, 0.189, 0.353, 0.567, 0.651, 0.628, 0.551]

main_cll_func = interp1d(main_angle, main_cl_low, 3)
main_cdl_func = interp1d(main_angle, main_cd_low, 3)
main_clh_func = interp1d(main_angle, main_cl_high, 3)
main_cdh_func = interp1d(main_angle, main_cd_high, 3)
jib_cll_func = interp1d(jib_angle, jib_cl_low, 3)
jib_cdl_func = interp1d(jib_angle, jib_cd_low, 3)
jib_clh_func = interp1d(jib_angle, jib_cl_high, 3)
jib_cdh_func = interp1d(jib_angle, jib_cd_high, 3)
spi_sym_cl_func = interp1d(spi_angle, sym_spi_cl, 3)
spi_sym_cd_func = interp1d(spi_angle, sym_spi_cd, 3)
spi_asym_cl_func = interp1d(spi_angle, asym_spi_cl, 3)
spi_asym_cd_func = interp1d(spi_angle, asym_spi_cd, 3)
spi_asym_cl_pole_func = interp1d(spi_angle, asym_spi_cl_pole, 3)
spi_asym_cd_pole_func = interp1d(spi_angle, asym_spi_cd_pole, 3)
c0_cl_func = interp1d(c0_angle, c0_cl, 3)
c0_cd_func = interp1d(c0_angle, c0_cd, 3)
c0_cl_batt_func = interp1d(c0_angle, c0_cl_batt, 3)
c0_cd_batt_func = interp1d(c0_angle, c0_cd_batt, 3)

########################################################################################################################
########################################################################################################################
#
# Sails areas calculation and centers of effort using simplified method
#
########################################################################################################################
def areasComp(P, E, IG, J, SL, PY, EY, YSD, YSMG, YSF, BAS, BASY):
    global Am, Ag, Aj, As, Ay, Ays, CEm, CEj, CEs, CEy, CEys, areas
    Am = 0.5 * P * E
    #Ag = 0.5 * math.sqrt(math.pow(I, 2) + math.pow(J, 2)) * LPG
    Ag = 0
    Aj = 0.5 * IG * J
    As = 1.15 * SL * J
    Ay = 0.5 * PY * EY
    Ays = 0.5 * YSD * (YSMG + YSF)
    CEm = 0.39 * P + BAS
    CEj = 0.39 * IG
    CEs = 0.59 * IG
    CEy = 0.39 * PY + BASY
    CEys = 0.39 * PY + BASY
    areas = [Am, Ag, Aj, As, Ay, Ays, CEm, CEj, CEs, CEy, CEys]
    return areas

#header = ["Wind conditions", "Sailing condition", "Rig dimensions", "Sails areas", "Center of Efforts", \
# "Lift coefficients per sail", "Parasitic Drag coefficients per sail", "Induced Drag per sail", "Windage", \
# "Total Lift and Drag", "Total Driving and Heeling forces"]
header_det = ["Project name", "TWS", "TWA", "AWS", "AWA", "AWSe", "AWAe", "Boat speed", "Heel", "J", "IG", "P", "E", "SL",
              "BAD", "EHM", "FAM", "B", "EMDC", "Am", "Aj", "As", "Ay", "Ays", "Atot", "CEm", "CEj", "CEs", "CEy", "CEys",
              "CE", "Clm", "Clj", "Cls", "Cly", "Clys", "Cl", "Cdm", "Cdj", "Cds", "Cdy", "Cdys", "Cdp", "Cdo", "Cdi", "Cd", "L", "D", "Fx", "Fy"]

file_suffix = "aero_output"
file_extension = ".csv"
model = "simpl"
csv_file = os.path.join(Boatname + "_" + file_suffix + "_" + model + file_extension)
if os.path.isfile(csv_file):
    os.rename(csv_file, csv_file + datetime.now().strftime("%Y%m%d-%H%M%S"))
file = open(csv_file, "ab")
write = csv.writer(file)
#write.writerow(header)
write.writerow(header_det)

for speed in TWS:
    for angle in TWA:
        for Bs in range(1, speed+1, 1):
            for heel in range(0, 26, 1):
                awaComp(angle, speed, Bs)
                awsComp(angle, AWA, speed)
                awseComp(speed, Bs, angle, heel)
                awaeComp(speed, Bs, angle, heel)
                tocsv = [Boatname, speed, angle, AWS, AWA, AWSe, AWAe, Bs, heel, J, IG, P,
                         E, SL, BAD, EHM, FAM, B, EMDC]
                if args.ketch == True or args.yawl == True:
                    areasComp(P, E, IG, J, SL, PY, EY, YSD,
                              YSMG, YSF, BAD, BADY)
                    tocsv.extend([areas[0], areas[2], areas[3], areas[4], areas[5], areas[6], areas[7], areas[8], areas[9], areas[10]])
                    if AWAe <= 90:
                        Atot = areas[0] + areas[2] + areas[4]

                        Clm = main_cl_funcs(AWAe)
                        Clj = jib_cl_funcs(AWAe)
                        Cly = mizzen_cl_funcs(AWAe)
                        Clys = mizz_stays_cl_funcs(AWAe)
                        Cl = (Clm * areas[0] + Clj * areas[2] + Cly * areas[4]) / Atot
                        L = 0.5 * rho * Atot * math.pow(AWSe, 2) * Cl

                        Cdm = main_cd_funcs(AWAe)
                        Cdj = jib_cd_funcs(AWAe)
                        Cdy = mizzen_cd_funcs(AWAe)
                        Cdys = mizz_stays_cd_funcs(AWAe)
                        Cdp = (Cdm * areas[0] + Cdj * areas[2] + Cdys * areas[4]) / Atot
                        Cdo = 1.13 * (((FAM * B) + (EHM * EMDC)) / Atot)
                        if AWAe < 70:
                            ARa = math.pow((1.1 * (EHM + FAM)), 2) / Atot
                        else:
                            ARa = math.pow((1.1 * EHM), 2) / Atot
                        Cdi = math.pow(Cl, 2) * ((1 / (math.pi * ARa) )+ 0.005)
                        Cd = Cdp + Cdo + Cdi
                        D = 0.5 * rho * Atot * math.pow(AWSe, 2) * Cd
                        tocsv.insert(24, Atot)
                        tocsv.insert(30, 0)
                        tocsv.extend([Clm, Clj, 0, Cly, 0, Cl, Cdm, Cdj, 0, Cdy, 0, Cdp, Cdo, Cdi, L, D])
                        write.writerow(tocsv)
                    else:
                        Atot = areas[0] + areas[3] + areas[4]
                        ARa = math.pow((1.1 * EHM), 2) / Atot

                        Clm = main_cl_funcs(AWAe)
                        Cls = spi_cl_funcs(AWAe)
                        Cly = mizzen_cl_funcs(AWAe)
                        Cl = (Clm * areas[0] + Cls * areas[3] + Cly * areas[4]) / Atot
                        L = 0.5 * rho * Atot * math.pow(AWSe, 2) * Cl

                        Cdm = main_cd_funcs(AWAe)
                        Cds = spi_cd_funcs(AWAe)
                        Cdy = mizzen_cd_funcs(AWAe)
                        Cdp = (Cdm * areas[0] + Cdj * areas[2] + Cdy * areas[4]) / Atot
                        Cdo = 1.13 * (((FAM * B) + (EHM * EMDC)) / Atot)
                        Cdi = (Cl ** 2) * ((1/(math.pi * ARa)) + 0.005)
                        Cd = Cdp + Cdo + Cdi
                        D = 0.5 * rho * Atot * math.pow(AWSe, 2) * Cd
                        tocsv.insert(24, Atot)
                        tocsv.insert(30, 0)
                        tocsv.extend([Clm, 0, Cls, Cly, 0, Cl, Cdm, 0, Cds, Cdy, 0, Cd, Cdo, Cdi, L, D])
                        write.writerow(tocsv)
                else:
                    areasComp(P, E, IG, J, SL, 0, 0, 0, 0, 0, BAD, 0)
                    tocsv.extend([areas[0], areas[2], areas[3], areas[4], areas[5], areas[6], areas[7], areas[8], areas[9], areas[10]])
                    if AWAe <= 90:
                        Atot = areas[0] + areas[2]

                        Clm = main_cl_funcs(AWAe)
                        Clj = jib_cl_funcs(AWAe)
                        Cl = (Clm * areas[0] + Clj * areas[2]) / Atot
                        L = 0.5 * rho * Atot * math.pow(AWSe, 2) * Cl

                        Cdm = main_cd_funcs(AWAe)
                        Cdj = jib_cd_funcs(AWAe)
                        Cdp = (Cdm * areas[0] + Cdj * areas[2])/Atot
                        Cdo = 1.13 * (((FAM * B) + (EHM * EMDC)) / Atot)
                        if AWAe < 70:
                            ARa = math.pow((1.1 * (EHM + FAM)), 2) / Atot
                        else:
                            ARa = math.pow((1.1 * EHM), 2) / Atot
                        Cdi = math.pow(Cl,2) * ((1 / (math.pi * ARa)) + 0.005)
                        Cd = Cdp + Cdo + Cdi
                        D = 0.5 * rho * Atot * math.pow(AWSe, 2) * Cd

                        Fx = L * math.sin(math.radians(AWAe)) -D * math.cos(math.radians(AWAe))
                        Fy = L * math.cos(math.radians(AWAe)) + D * math.sin(math.radians(AWAe))

                        Fm = math.sqrt((math.pow(Clm, 2) + math.pow(Cdm, 2))) / (math.sqrt((math.pow(Clm, 2) + math.pow(Cdm, 2)))
                                                                                 + math.sqrt((math.pow(Clj, 2) + math.pow(Cdj, 2))))
                        Fj = math.sqrt((math.pow(Clj, 2) + math.pow(Cdj, 2))) / (math.sqrt((math.pow(Clm, 2) + math.pow(Cdm, 2)))
                                                                                 + math.sqrt((math.pow(Clj, 2) + math.pow(Cdj, 2))))
                        CE = ((Am * Fm * CEm) + (Aj * Fj * CEj)) / ((Am * Fm) + (Aj * Fj))

                        tocsv.insert(24, Atot)
                        tocsv.insert(30, CE)
                        tocsv.extend([Clm, Clj, 0, 0, 0, Cl, Cdm, Cdj, 0, 0, 0, Cd, Cdo, Cdi, Cd, L, D, Fx, Fy])
                        write.writerow(tocsv)
                    else:
                        Atot = areas[0] + areas[3]
                        ARa = math.pow((1.1 * args.ehm[0]), 2) / Atot

                        Clm = main_cl_funcs(AWAe)
                        Cls = spi_cl_funcs(AWAe)
                        Cl = (Clm * areas[0] + Cls * areas[3]) / Atot
                        L = 0.5 * rho * Atot * math.pow(AWSe, 2) * Cl

                        Cdm = main_cd_funcs(AWAe)
                        Cds = spi_cd_funcs(AWAe)
                        Cdp = (Cdm * areas[0] + Cds * areas[3]) / Atot
                        Cdo = 1.13 * (((FAM * B) + (EHM * EMDC)) / Atot)
                        Cdi = (Cl ** 2) * ((1 / (math.pi * ARa)) + 0.005)
                        Cd = Cdp + Cdo + Cdi
                        D = 0.5 * rho * Atot * math.pow(AWSe, 2) * Cd

                        Fx = L * math.sin(math.radians(AWAe)) -D * math.cos(math.radians(AWAe))
                        Fy = L * math.cos(math.radians(AWAe)) + D * math.sin(math.radians(AWAe))

                        Fm = math.sqrt((math.pow(Clm, 2) + math.pow(Cdm, 2))) / (math.sqrt((math.pow(Clm, 2) + math.pow(Cdm, 2)))
                                                                                 + math.sqrt((math.pow(Cls, 2) + math.pow(Cds, 2))))
                        Fs = math.sqrt((math.pow(Cls, 2) + math.pow(Cds, 2))) / (math.sqrt((math.pow(Clm, 2) + math.pow(Cdm, 2)))
                                                                                 + math.sqrt((math.pow(Cls, 2) + math.pow(Cds, 2))))
                        CE = ((Am * Fm * CEm) + (As * Fs * CEs)) / ((Am * Fm) + (As * Fs))

                        tocsv.insert(24, Atot)
                        tocsv.insert(30, CE)
                        tocsv.extend([Clm, 0, Cls, 0, 0, Cl, Cdm, 0, Cds, 0, 0, Cd, Cdo, Cdi, Cd, L, D, Fx, Fy])
                        write.writerow(tocsv)
file.close()

########################################################################################################################
########################################################################################################################
#
# HYDRO MODELS:
#
# SIMPLIFIED (according to DSYHS papers and database)
#           Aero follows Hazen model although the twist of sails can be chosen
# ORC MODEL (according to ORC VPP DOCUMENTATION 2015/2016)
#           Enhanced model with several refinements from experiments
# CFD DATA
#           Direct computation of forces and moments using any CFD solver available. The equilibrium state search is a task performed by VPP solver.
# TOWING TANK DATA
#           Forces and moments obtained on towing tank and extrapolated to full scale using some method
#
########################################################################################################################
########################################################################################################################
########################################################################################################################
#
# Resistance calculation using DSYHS formulation
#
#
# Rttp = Rfh (C1) + Rrh (C2) + Rvk (C3) + Rrk (C4) + Rvr (C5) + dRft (C6) + dRrt (C7) + dRrkt (C8) + dRtp (C9) + dRrtrim (C10) + Raw (C11)
#
########################################################################################################################
########################################################################################################################
#
# Wetted area computation
#
########################################################################################################################
def wettedA(Bwl, Tc, Nablac, Lwl):
    global Ws, Bwl, Tc, Nablac, Lwl
    Ws = (1.97 + 0.171 * (Bwl / Tc) * math.pow((0.65 / Cm), 1 / 3) * math.pow((Nablac * Lwl), 0.5)
    return Ws

########################################################################################################################
#
# Heeled hull wetted surface computation
#
########################################################################################################################
def wettedAh(Bwl, Tc, Cm, Ws, heel):
    global Bwl, Tc, Cm, Ws, Wsh, heel

    angle = [ 5, 10, 15, 20, 25, 30, 35]
    s0i = [-4.112, -4.522, -3.291, 1.850, 6.510, 12.334, 14.648]
    s1i = [0.054, -0.132, -0.389, -1.2, -2.305, -3.911, -5.182]
    s2i = [-0.027, -0.077, -0.118, -0.109, -0.066, 0.024, 0.102]
    s3i = [6.329, 8.738, 8.949, 5.364, 3.443, 1.767, 3.497]
    s0_func = interp1d(angle, s0i, 3)
    s1_func = interp1d(angle, s1i, 3)
    s2_func = interp1d(angle, s2i, 3)
    s3_func = interp1d(angle, s3i, 3)

    Wsh = Ws * (1 + (0.01 *(s0_func(heel) + (s1_func(heel) * (Bwl / Tc)) + s2_func(heel) * (math.pow((Bwl / Tc), 2)) + s3_func(heel) * Cm)))
    return Wsh

########################################################################################################################
#
# Reynolds and Froude numbers
#
########################################################################################################################
def reynolds(Bs, Lwl):
    global Bs, Lwl, nu
    Rn = (Bs * 0.7 * Lwl) / nu
    return Rn

def froude(Bs, Lwl):
    global Bs, Lwl
    Fn = Bs / math.sqrt((9.81 * Lwl))
    return Fn

########################################################################################################################
#
# Rfh (Component 1) Friction resistance of canoe body
#
########################################################################################################################
def resistC1(Rn, Bwl, Tc, Nablac, Lwl, Bs):
    global Rn, Rfh, Bwl, Tc, Nablac, Lwl, Bs
    Cf = 0.075 / math.pow((math.log10(Rn) - 2), 2)
    Rfh = 0.5 * rhow * wettedA(Bwl, Tc, Nablac, Lwl) * math.pow(Bs, 2) * Cf
    return Rfh

########################################################################################################################
#
# Rrh (Component 2) Rsiduary resistance of canoe body
#
########################################################################################################################
def resistC2(Bs, Nablac, rhow, LCB, LCF, Lwl, Bwl, Tc, Cm, Cp, Aw):
    global Bs, Nablac, rhow, LCB, LCF, Lwl, Bwl, Tc, Cm, Cp, Aw, Rrh

    frouden = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
    a0i = [-0.0005, -0.0003, -0.0002, -0.0009, -0.0026, -0.0064, -0.0218, -0.0388, -0.0347, -0.0361, 0.0008, 0.0108, 0.1023]
    a1i = [0.0023, 0.0059, -0.0156, 0.0016, -0.0567, -0.4034, -0.5261, -0.5986, -0.4764, 0.0037, 0.3728, -0.1238, 0.7726]
    a2i = [-0.0086, -0.0064, 0.0031, 0.0337, 0.0446, -0.1250, -0.2945, -0.3038, -0.2361, -0.2960, -0.3667, -0.2026, 0.5040]
    a3i = [-0.0015, 0.0070, -0.0021, -0.0285, -0.1091, 0.0273, 0.2485, 0.6033, 0.8726, 0.9661, 1.3957, 1.1282, 1.7867]
    a4i = [0.0061, 0.0014, -0.0070, -0.0367, -0.0707, -0.1341, -0.2428, -0.0430, 0.4219, 0.6132, 1.0343, 1.1836, 2.1934]
    a5i = [0.0010, 0.0013, 0.0148, 0.0218, 0.0914, 0.3578, 0.6293, 0.8332, 0.8990, 0.7534, 0.3230, 0.4973, -1.5479]
    a6i = [0.0001, 0.0005, 0.0010, 0.0015, 0.0021, 0.0045, 0.0081, 0.0106, 0.0096, 0.0100, 0.0072, 0.0038, -0.0115]
    a7i = [0.0052, -0.0020, -0.0043, -0.0172, -0.0078, 0.1115, 0.2086, 0.1336, -0.2272, -0.3352, -0.4632, -0.4477, -0.0977]
    a0_func = interp1d(frouden, a0i, 3)
    a1_func = interp1d(frouden, a1i, 3)
    a2_func = interp1d(frouden, a2i, 3)
    a3_func = interp1d(frouden, a3i, 3)
    a4_func = interp1d(frouden, a4i, 3)
    a5_func = interp1d(frouden, a5i, 3)
    a6_func = interp1d(frouden, a6i, 3)
    a7_func = interp1d(frouden, a7i, 3)

    Fn = froude(Bs, Lwl)

    Rrh = Nablac * rhow * 9.81 * (a0_func(Fn) + ((math.pow(Nablac, 1/3) / Lwl) * (a1_func(Fn) * (LCB / Lwl) + a2_func(Fn)
                                                                                  * Cp + a3_func(Fn) * (math.pow(Nablac, 2/3) / Aw)
                                                                                  + a4_func(Fn) * (Bwl / Lwl) + a5_func(Fn)
                                                                                  * (LCB / LCF)) + a6_func(Fn) * (Bwl / Tc)) + a7_func(Fn) *Cm)
    return Rrh

########################################################################################################################
#
# Rvk (Component 3) Viscous resistance of keel
#
########################################################################################################################
def resistC3(Bs, Wsk, tk, ck):
    global Bs, Wsk, tk, ck, Rvk

    Rn = reynolds(Bs, ck)
    Cf = 0.075 / math.pow((math.log10(Rn) - 2), 2)
    ff = 1 + 2 * tk / ck + 60 * math.pow((tk / ck), 4)
    Rf = 0.5 * rhow * Wsk * math.pow(Bs, 2) * Cf
    Rvk = ff * Rf
    return Rvk

########################################################################################################################
#
# Rrk (Component 4) Keel residuary resistance
#
########################################################################################################################
def resistC4(Nablak, Bs, T, Lwl, Bwl, Tc, Zcbk, Nablac):
    global Nablak, Bs, T, Lwl, Bwl, Tc, Zcbk, Nablac, Rrk

    Fn = froude(Bs, Lwl)
    frouden = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
    A0i = [-0.00104, -0.00550, -0.01110, -0.00713, -0.03581, -0.00470, 0.00553, 0.04822, 0.01021]
    A1i = [0.00172, 0.00597, 0.01421, 0.02632, 0.08649, 0.11592, 0.07371, 0.00660, 0.14173]
    A2i = [0.00117, 0.00390, 0.00069, -0.00232, 0.00999, -0.00064, 0.05991, 0.07048, 0.06409]
    A3i = [-0.00008, -0.00009, 0.00021, 0.00039, 0.00017, 0.00035, -0.00114, -0.00035, -0.00192]
    A0_func = interp1d(frouden, A0i, 3)
    A1_func = interp1d(frouden, A1i, 3)
    A2_func = interp1d(frouden, A2i, 3)
    A3_func = interp1d(frouden, A3i, 3)

    Rrk = A0_func(Fn) + (A1_func(Fn) * (T / Bwl)) + (A2_func(Fn) * math.pow((Tc + Zcbk), 3) / Nablak) + (A3_func(Fn) * Nablac / Nablak)
    return Rrk

########################################################################################################################
#
# Rvr (Component 5) Viscous resistance of rudder
#
########################################################################################################################
def resistC5(Bs, Wsr, tr, cr):
    global Bs, Wsr, tr, cr, Rvr, rhow

    Rn = reynolds(Bs, cr)
    Cf = 0.075 / math.pow((math.log10(Rn) - 2), 2)
    ff = 1 + 2 * tr / cr + 60 * math.pow((tr / cr), 4)
    Rf = 0.5 * rhow * Wsr * math.pow(Bs, 2) * Cf
    Rvr = ff * Rf
    return Rvr

########################################################################################################################
#
# dRft (Component 6) Increment of friction resistance of canoe body due to heel
#
########################################################################################################################
def resistC6(Rn, Bwl, Tc, Nablac, Lwl, Cm, Bs):
    global Rn, Rfht, dRft, Bwl, Tc, Nablac, Lwl, Cm, Bs, rhow
    Cft = 0.075 / math.pow((math.log10(Rn) - 2), 2)
    value1 = wettedA(Bwl, Tc, Nablac, Lwl)
    value2 = resistC1(Rn, Bwl, Tc, Nablac, Lwl, Bs)
    Rfht = 0.5 * rhow * wettedAh(Bwl, Tc, Cm, value1, heel) * math.pow(Bs, 2) * Cft
    dRft = value2 - Rfht
    return dRft

########################################################################################################################
#
# dRrt (Component 7) Increment of residuary resistance of canoe body due to heel
#
########################################################################################################################
def resistC7(Bs, Lwl, Nablac, rhow, LCB, Bwl, Tc, heel):
    global Bs, Lwl, Nablac, rhow, LCB, Bwl, Tc, heel, dRrt, rhow

    frouden = [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55]
    u0i = [-0.0268e-3, 0.6628e-3, 1.6433e-3, -0.8659e-3, -3.2715e-3, -0.1976e-3, 1.5873e-3]
    u1i = [-0.0014e-3, -0.0632e-3, -0.2144e-3, -0.0354e-3, 0.1372e-3, -0.148e-3, -0.3749e-3]
    u2i = [-0.0057e-3, -0.0699e-3, -0.164e-3, 0.2226e-3, 0.5547e-3, -0.6593e-3, -0.7105e-3]
    u3i = [0.0016e-3, 0.0069e-3, 0.0199e-3, 0.0188e-3, 0.0268e-3, 0.1862e-3, 0.2146e-3]
    u4i = [-0.007e-3, 0.0459e-3, -0.054e-3, -0.58e-3, -1.0064e-3, -0.7489e-3, -0.4818e-3]
    u5i = [-0.0017e-3, -0.0004e-3, -0.0268e-3, -0.1133e-3, -0.2026e-3, -0.1648e-3, -0.1174e-3]
    u0_func = interp1d(frouden, u0i, 3)
    u1_func = interp1d(frouden, u1i, 3)
    u2_func = interp1d(frouden, u2i, 3)
    u3_func = interp1d(frouden, u3i, 3)
    u4_func = interp1d(frouden, u4i, 3)
    u5_func = interp1d(frouden, u5i, 3)

    Fn = froude(Bs, Lwl)

    dRr20 = Nablac * rhow * 9.81 * (u0_func(Fn) + (u1_func(Fn) * (Lwl / Bwl)) + (u2_func(Fn) * (Bwl / Tc)) + ((u3_func(Fn))
                                                                                                              * math.pow((Bwl / Tc), 2))
                                    + (u4_func(Fn) * LCB) + (u5_func(Fn) * math.pow(LCB, 2)))
    dRrt = dRr20 * 6 * math.pow(heel, 1.7)
    return dRrt

########################################################################################################################
#
# dRrkt (Component 8) Increment of residuary resistance of the keel due to heel
#
########################################################################################################################
def resistC8(Nablak, Bwl, Lwl, T, Tc, Nablac, heel, Bs):
    global Nablak, Bwl, Lwl, T, Tc, Nablac, heel, Bs, dRrkt, rhow

    Fn = froude(Bs, Lwl)
    Ch = (-3.5837 * Tc / T) - (0.0518 * Bwl / Tc) + 0.5958 * (Tc * Bwl) / (T * Tc) + (0.2055 * Lwl / math.pow(Nablac, 1/3))
    dRrkt = Nablak * rhow * 9.81 * Ch * math.pow(Fn, 2) * heel
    return dRrkt

########################################################################################################################
#
# dRtp (Component 9) Increment of resistance due to sideforce on appendages (Induced resistance)
#
########################################################################################################################
def resistC9():
    pass

########################################################################################################################
#
# dRtrim (Component 10) Increment of resistance due to trimming
#
########################################################################################################################
def resistC10():
    pass

########################################################################################################################
#
# Raw (Component 11) Added resistance due to waves
#
########################################################################################################################
def resistC11():
    pass




