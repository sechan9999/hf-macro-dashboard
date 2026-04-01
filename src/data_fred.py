import os
import pandas as pd
from fredapi import Fred
import pandas_datareader as pdr

SERIES = {
  "dgs10":"DGS10",
  "tb3ms":"TB3MS",
  "cpi":"CPIAUCSL",
  "unrate":"UNRATE",
  "indpro":"INDPRO",
  "t10y2y":"T10Y2Y",
  "baa":"BAA",
  "aaa":"AAA",
  "nfci":"NFCI"
}

def load_fred(start="1990-01-01"):
    key = os.getenv("FRED_API_KEY")
    
    if key:
        print("FRED_API_KEY found, using official fredapi...")
        fred = Fred(api_key=key)
        frames=[]
        for col,sid in SERIES.items():
            print(f"Loading {sid}...")
            s = fred.get_series(sid)
            s = pd.Series(s, name=col)
            s.index = pd.to_datetime(s.index)
            frames.append(s.to_frame())
        df = pd.concat(frames, axis=1).sort_index()
    else:
        print("FRED_API_KEY not found. Using pandas_datareader fallback (No API key needed)...")
        frames = []
        for col, sid in SERIES.items():
            print(f"Loading {sid}...")
            try:
                s = pdr.get_data_fred(sid, start=start)
                s.columns = [col]
                frames.append(s)
            except Exception as e:
                print(f"Failed to load {sid}: {e}")
                
        df = pd.concat(frames, axis=1).sort_index()
        
    df = df[df.index >= pd.to_datetime(start)]
    # month-end
    m = df.resample("M").last().ffill()
    return m
