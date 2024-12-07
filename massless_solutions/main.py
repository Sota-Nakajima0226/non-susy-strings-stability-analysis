# import numpy as np
# import logging
from datetime import datetime
import os
import sys
current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(root_dir)
from common.lattice_vectors import generate_e8_root_vectors
from common.utils import load_json, save_json, get_logger
from massless_solutions.module import read_moduli_from_json, solve_massless_conditions, count_nonzero_roots

# input json file path
input_dir_path = os.path.join(root_dir, 'input')
input_file_path = os.path.join(input_dir_path, 'untwisted_moduli.json')
fund_weight_file_path = os.path.join(input_dir_path, 'fund_weight.json')
# result json file directory path
output_dir_path = os.path.join(root_dir, 'output')
result_dir_path = os.path.join(output_dir_path, 'massless_solutions')
# log file directory path
today = datetime.today().strftime('%Y%m%d')
log_dir_path = os.path.join(root_dir, 'logs')
today_log_dir = os.path.join(log_dir_path, today)

def main():
  # Generate E8 root vectors
  e8_root_vectors = generate_e8_root_vectors()
  # Read moduli data from input.json
  input_data = load_json(input_file_path)
  input_moduli_num = len(input_data["moduli"])
  fund_weight_data = load_json(fund_weight_file_path)
  # Make dir for log and set log config
  os.makedirs(today_log_dir, exist_ok=True)
#   logging.basicConfig(level=logging.INFO, format='%(message)s')

  for i in range(input_moduli_num):
      moduli_data = read_moduli_from_json(fund_weight_data, input_data, i)
      A2_1 = moduli_data["A2_1"]
      A2_2 = moduli_data["A2_2"]
      G2 = moduli_data["G2"]
      # Set log file
      log_file_name = f'{moduli_data["A2_labels"][0]}_{moduli_data["A2_labels"][1]}.log'
      log_file_path = os.path.join(today_log_dir, log_file_name)
      logger = get_logger(log_file=log_file_path)
      now = datetime.now()
      logger.info(f"Starting the calculation...: {now}")
      logger.info(f"Wilson lines: {A2_1} {A2_2}, metric: {G2}")
      solutions = solve_massless_conditions(A2_1, A2_2, G2, e8_root_vectors, logger)
      # Check if the number of solutions matches that of nonzero roots
      is_matched = False
      roots_num = count_nonzero_roots(moduli_data["L"])
      if len(solutions) == roots_num:
          is_matched = True
      result_file_path = os.path.join(result_dir_path, f'result_{moduli_data["A2_labels"][0]}-{moduli_data["A2_labels"][1]}.json')
      result_json = {
          "moduli": {
              "A2_1": {
                  "vector": A2_1["vector"].tolist(),
                  "k": A2_1["k"],
              },
              "A2_2": {
                  "vector": A2_2["vector"].tolist(),
                  "k": A2_2["k"],
              },
              "G2": G2
          },
          "L": moduli_data["L"],
          "roots_num": roots_num,
          "solutions_num": len(solutions),
          "is_valid_solutions": is_matched,
          "solutions": solutions
      }
      save_json(result_json, result_file_path)

if __name__ == '__main__':
    main()