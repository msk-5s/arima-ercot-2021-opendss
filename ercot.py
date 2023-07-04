# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains dictionaries for the valid ERCOT load profile classes. See 'Appendix D: Profile
Decision Tree' of ERCOT's Load Profile Guide.

These are here for reference and should not me modified. To get the column name of a profile class
in the `data/ercot-2021-load_profiles.feather` data frame, join the valid class name with the
desired weather zone using an underscore (e.g. "BUSLOLF_COAST").
"""

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
valid_profile_classes = {
    # Business Group
    0: "BUSNODEM",  # Non-Demand
    1: "BUSLOLF",   # Low Load Factor (average LF < 0.40)
    2: "BUSMEDLF",  # Medium Load Factor (0.4 <= average LF <= 0.6)
    3: "BUSHILF",   # High Load Factor (average LF > 0.6)
    4: "BUSIDRRQ",  # 4-CP tariff - TDSP no support 4-CP billing rate with AMS profile.
    5: "BUSOGFLT",  # Oil and Gas Flat (no sales tax for transporting oil from site of production).
    6: "BUSNODPV",  # Non-Demand for premises with PV generation.
    7: "BUSLOPV",   # Low Winter Ratio / Low Load Factor for premises with PV generation.
    8: "BUSMEDPV",  # Medium Load Factor for premises with PV generation.
    9: "BUSHIPV",   # High Winter Ratio / High Load Factor with premises with PV generation.
    10: "BUSOGFPV", # PV generation present (meet's DG criteria).
    11: "BUSNODWD", # Non-Demand for premises with wind generation.
    12: "BUSLOWD",  # Low Winter Ratio / Low Load Factor for premises with non-PV DG.
    13: "BUSMEDWD", # Medium Load Factor for premises with wind generation.
    14: "BUSHIWD",  # High Winter Ratio / High Load Factor for premises with wind generation.
    15: "BUSOGFWD", # Wind generation present (meet's DG criteria).
    16: "BUSNODDG", # Non-Demand for premises with DG (no PV or wind).
    17: "BUSLODG",  # Low Winter Ratio / Low Load Factor for premises with DG (no PV or wind).
    18: "BUSMEDDG", # Medium Load Factor for premises with DG (no PV or wind).
    19: "BUSHIDG",  # High Winter Ratio / High Load Factor for premises with DG (no PV or wind).
    20: "BUSOGFDG", # Oil and Gas Flat for premises with DG (no PV or wind).

    # Non-Metered Group
    21: "NMLIGHT",  # Lighting load (city street lights, etc.).
    22: "NMFLAT",   # Non-lighting loads.

    # Residential Group
    23: "RESLOWR",  # Low Winter Ratio (default, if no segment defined).
    24: "RESHIWR",  # High Winter Ratio
    25: "RESLOPV",  # Low Winter Ratio / Low Load Factor for premises with PV generation.
    26: "RESHIPV",  # High Winter Ratio / High Load Factor for premises with PV generation.
    27: "RESLOWD",  # Low Winter Ratio / Low Load Factor for premises with DG (no PV).
    28: "RESHIWD",  # High Winter Ratio / High Load Factor for premises with wind generation.
    29: "RESLODG",  # Low Winter Ratio / Low Load Factor for premises with DG (no PV or wind).
    30: "RESHIDG"   # High Winter Ratio / High Load Factor for premises with DG (no PV or wind).
}

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
# Texas weather zones defined by ERCOT.
valid_weather_zones = {
    0: "COAST", 1: "EAST", 2: "FWEST", 3: "NCENT", 4: "NORTH", 5: "SCENT", 6: "SOUTH", 7: "WEST"
}
