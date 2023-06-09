# **arima-ercot-2021-opendss**

This repository contains the source code for generating the [`arima-ercot-2021`](https://www.kaggle.com/datasets/msk5sdata/arima-ercot-2021) data suite.

The data suite contains voltage magnitude datasets from the following test feeders:
- [Electric Power Research Institute's (EPRI)](https://www.epri.com/) `ckt5` test feeder circuit. `ckt5` is a radial network with 1379 single-phase wye-connected loads.
- [Electric Power Research Institute's (EPRI)](https://www.epri.com/) Low-Voltage North American (LVNA) test feeder circuit. This is EPRI's implementation of the IEEE 342-Node test feeder. `lvna` is a meshed network with 624 single-phase wye and delta-connected loads.

The [Electric Reliability Council of Texas (ERCOT) 2021 backcasted load profiles](https://www.ercot.com/mktinfo/loadprofile/alp) are used to generated the voltage magnitude data for each of the circuits. However, these load profiles have missing values and have been imputed in the [arima-ercot-2021-profile](https://github.com/msk-5s/arima-ercot-2021-profile) repository. Each dataset will have a total of 35040 voltage magnitude measurements over the year (15-minute samples).

The generated dataset will be in the [Apache Arrow Feather](https://arrow.apache.org/docs/python/feather.html) format.

## Requirements
    - Windows
    - Python 3.8+ (64-bit)
    - OpenDSS 9.6.1.1+ (64-bit)
    - See requirements.txt file for the required python packages.
    
## Folders
`data/`
: This folder will contain the generated data sets.

`profiles/`
: The ERCOT 2021 load profiles that are generated by the [arima-ercot-2021-profile](https://github.com/msk-5s/arima-ercot-2021-profile) repository should be placed in this folder.

`src/`
: The `.dss` files aren't included in this repository. The folders containing the `ckt5` and `lvna` files can be found in the OpenDSS installation folder and should be placed in this folder.

## Running
The dataset can be generated by simply running `run.py`.

> NOTE: During the `Running simulation...` step, the OpenDSS progress bar that pops up may stop responding (as of OpenDSS 9.6.1.1). You can safely ignore this (you just won't see how far along the simulation is) as the simulation is still running. Once the simulation is done, you will have to manually close the OpenDSS progress bar.

## Converting to `.csv` (if desired)
Pandas can be used to convert a `.feather` file to a `.csv` file using the below code:
```
import pyarrow.feather

# A pandas dataframe is returned.
# We are assuming that we are in the repository's root directory.
data_df = pyarrow.feather.read_feather("data/lvna-load-voltage_magnitudes-raw.feather")

data_df.to_csv("data/lvna-load-voltage_magnitudes-raw.csv")
```
