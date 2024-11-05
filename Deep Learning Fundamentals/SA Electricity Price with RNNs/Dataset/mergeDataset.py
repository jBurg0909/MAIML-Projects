"""
This script serves to merge the total spot market electricity price for SA for the past 25 years. This merge will be completed in 2 Steps:
1. 30-minute interval data will be merged together, and linear interpolated to 5-minute intervals (1999 to Sept-21).
2. 5-minte interval data will be appended to the original dataframe (Oct-21 to present)
"""
# Libraries
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



direc = "Raw Data/"

norm_dfs = list()
interp_dfs = list()

# Identify .csv files requiring Interpolation
for filename in os.listdir(direc):
   if filename.endswith(".csv"):
      if int(filename[17:23]) < 202110:
         df = pd.read_csv(os.path.join(direc,filename),parse_dates=["SETTLEMENTDATE"])
         interp_dfs.append(df)
      else:
        df = pd.read_csv(os.path.join(direc,filename),parse_dates=["SETTLEMENTDATE"])
        norm_dfs.append(df)

# Concatenate DataFrame Lists
combined_interp_dfs = pd.concat(interp_dfs,ignore_index=True)
combined_dfs = pd.concat(norm_dfs, ignore_index = True)

# Convert 30-minute data to 5-minute interval
combined_interp_dfs.set_index("SETTLEMENTDATE", inplace = True)
df_resampled = combined_interp_dfs.resample("5min").asfreq()
df_interped = df_resampled.interpolate(method = "linear")
df_interped.reset_index(inplace=True)
df_interped["REGION"] = df_interped["REGION"].fillna("SA1")
df_interped["PERIODTYPE"] = df_interped["PERIODTYPE"].fillna("TRADE")

# Combine into Final DF
combined_df = pd.concat([df_interped,combined_dfs],ignore_index = True)

# Creating Smaller RNN Dataset
rnn_df = combined_df.copy()
rnn_df.drop(columns=["REGION","PERIODTYPE","TOTALDEMAND"],inplace=True)

# .csv Export
combined_df.to_csv("sa_electricity_market_operational_dataset.csv",index=False)
rnn_df.to_csv("sa_electricity_price_25y.csv",index=False)

# Plot
plt.figure(figsize=(10,6))

plt.subplot(2,1,1)
plt.title("SA1 - Spot Market Electricity Price")
plt.plot(combined_df["SETTLEMENTDATE"],combined_df["RRP"])
plt.ylabel("Price ($/MWh)")
plt.xlabel("Time")
plt.grid(True)

plt.subplot(2,1,2)
plt.title("SA1 - Operational Demand")
plt.plot(combined_df["SETTLEMENTDATE"],combined_df["TOTALDEMAND"])
plt.ylabel("Demand (MW)")
plt.xlabel("Time")
plt.grid(True)

plt.tight_layout()
plt.show()