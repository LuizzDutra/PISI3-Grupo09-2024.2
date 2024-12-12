import pandas as pd
import io
import os



path = "data/"
arquivos = os.listdir(path)

for csv in arquivos:
    opened = pd.read_csv(path+csv)
    opened.to_parquet(path+os.path.splitext(csv)[0]+'.parquet')
    
    