import os
from typing import List, Any

import pandas as pd
import numpy as np

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
csv = os.path.join(os.getcwd(), ("Complete_evidence_Instances_test"+ file_name_suffix + ".csv"))
complete_evidence_Instances = pd.read_csv(csv, encoding="latin1")

