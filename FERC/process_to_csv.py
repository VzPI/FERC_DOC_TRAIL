import pandas as pd
import os

file_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'FERC/download_folder/log.json')
csv_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'FERC/download_folder/log.csv')
# print(file_dir)
test_df = pd.read_json(file_dir, orient = "index")
test_df.to_csv(csv_dir)
