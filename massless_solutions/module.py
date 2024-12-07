import numpy as np
import math
import itertools
import math
from common.calculator import is_integer, compare_float_num, is_equal_float_num

def read_moduli_from_json(fund_weight_data, input_json, index):
    input_moduli = input_json["moduli"][index]
    G2 = input_moduli["G2"]["top"] / input_moduli["G2"]["bottom"]
    fund_weights1 = fund_weight_data["W_1"]
    fund_weights2 = fund_weight_data["W_2"]
    fund_weight1 = next((item for item in fund_weights1 if item.get('label') == input_moduli["A2"][0]), None)
    fund_weight2 = next((item for item in fund_weights2 if item.get('label') == input_moduli["A2"][1]), None)
    # A2_1_vector = np.array(fund_weight1["value"]) / fund_weight1["k"]
    A2_1_vector = {
        "vector": np.array(fund_weight1["value"]),
        "k": fund_weight1["k"]
    }
    # A2_2_vector = np.array(fund_weight2["value"]) / fund_weight2["k"]
    A2_2_vector = {
        "vector": np.array(fund_weight2["value"]),
        "k": fund_weight2["k"]
    }
    return {
        "A2_1": A2_1_vector,
        "A2_2": A2_2_vector,
        "G2": G2,
        "A2_labels": input_moduli["A2"],
        "L": input_moduli["L"]
    }

def count_nonzero_roots(algebra):
    """
    Args:
      {
        "A": [1,2,3,..]
        "D": [2,3,4,...]
        "E": [6,7,8]
      }
    Return:
      the number of nonzero roots of ADE algebra
    """
    A_list = algebra["A"]
    D_list = algebra["D"]
    E_list = algebra["E"]
    num = 0
    if len(A_list) != 0:
        for n in A_list:
            num += n*(n+1)
    if len(D_list) != 0:
        for n in D_list:
            num += 2*n*(n-1)
    if len(E_list) != 0:
        for n in E_list:
            if n == 6:
                num += 72
            elif n == 7:
                num += 126
            elif n == 8:
                num += 240
    return num

def calculate_rho(A2, w2, Pi):
    rho = Pi - (w2/2) * A2
    return rho.tolist()

def solve_massless_conditions(A2_1, A2_2, G2, rootVectors, logger):
    """
    Massless conditions
    (Pi - w2*A2)^2 == 2 - 2*(w2**2)*G2
    n2 := w2 - np.dot(Pi, A2) is an integer
    """
    solutions = []
    R2 = math.sqrt(G2)
    A2_1Vec = A2_1["vector"]
    A2_2Vec = A2_2["vector"]
    k1 = A2_1["k"]
    k2 = A2_2["k"]
    A2_1_value = A2_1Vec / k1
    A2_2_value = A2_2Vec / k2
    A2 = np.concatenate((A2_1_value, A2_2_value))
    for w2 in range(-math.floor(1/R2), math.floor(1/R2)+1):

        logger.info(f"w2={w2}")
        w2 = float(w2)
        if w2 == 0:
            # Root vectors used for w2=0
            numOfSol = len(solutions)
            for pi in rootVectors:
                n2_1 = -np.dot(pi, A2_1Vec) / k1
                if is_integer(n2_1):
                    Pi = np.concatenate((np.array(pi), np.zeros(8)))
                    solution = {'w2': w2, 'n2': n2_1, 'Pi': Pi.tolist(), "rho": calculate_rho(A2, w2, Pi)}
                    solutions.append(solution)
                n2_2 = -np.dot(pi, A2_2Vec) / k2
                if is_integer(n2_2):
                    Pi = np.concatenate((np.zeros(8), np.array(pi)))
                    solution = {'w2': w2, 'n2': n2_2, 'Pi': Pi.tolist(), "rho": calculate_rho(A2, w2, Pi)}
                    solutions.append(solution)
            numOfUnwindingSol = len(solutions) - numOfSol
            logger.info(f"The number of unwinding solutions: {numOfUnwindingSol}")
        else:
            rhs = 2 - 2*(w2**2)*G2
            logger.info(f"the R.H.S: {rhs}")
            rangesO1 = []
            rangesS1 = []
            rangesO2 = []
            rangesS2 = []
            # Determine the bounds of each component of lattice elements
            for i in range(16):
                upperBound = math.sqrt(rhs) + w2*A2[i]
                lowerBound = -math.sqrt(rhs) + w2*A2[i]
                logger.info(f"{i+1}-th component: upper bound: {upperBound}, lowerBound: {lowerBound}")
                rangeO = range(math.ceil(lowerBound), math.floor(upperBound)+1)
                rangeS = range(math.ceil(lowerBound - 1/2), math.floor(upperBound - 1/2)+1)
                logger.info(f"{i+1}-th rangeO: {rangeO}")
                logger.info(f"{i+1}-th rangeS: {rangeS}")
                if i < 8:
                    rangesO1.append(rangeO)
                    rangesS1.append(rangeS)
                else:
                    rangesO2.append(rangeO)
                    rangesS2.append(rangeS)
            solutionsOO = get_winding_massless_solutions(rhs, A2_1_value, A2_2_value, A2, w2, rangesO1, rangesO2, False, False, logger)
            solutionsOS = get_winding_massless_solutions(rhs, A2_1_value, A2_2_value, A2, w2, rangesO1, rangesS2, False, True, logger)
            solutionsSO = get_winding_massless_solutions(rhs, A2_1_value, A2_2_value, A2, w2, rangesS1, rangesO2, True, False, logger)
            solutionsSS = get_winding_massless_solutions(rhs, A2_1_value, A2_2_value, A2, w2, rangesS1, rangesS2, True, True, logger)
            if len(solutionsOO) > 0:
                solutions.extend(solutionsOO)
            if len(solutionsOS) > 0:
                solutions.extend(solutionsOS)
            if len(solutionsSO) > 0:
                solutions.extend(solutionsSO)
            if len(solutionsSS) > 0:
                solutions.extend(solutionsSS)
    return solutions

def get_winding_massless_solutions(rhs, A2_1_value, A2_2_value, A2, w2, ranges1, ranges2, is_spin1, is_spin2, logger):
    solutions = []
    logger.info(f"E8xE8 lattice with is_spin1={is_spin1} and is_spin2={is_spin2} ")
    for pi1 in itertools.product(*ranges1):
        pi1 = np.array(pi1)
        if np.sum(pi1) % 2 != 0:
            continue
        if is_spin1:
            pi1 = pi1 + np.array([0.5]*8)
        lhs1 = np.dot(pi1 - w2*A2_1_value, pi1 - w2*A2_1_value)
        if np.all(pi1 == 0):
            logger.info(f"the LHS with pi1={pi1}: {lhs1}")
        if compare_float_num(lhs1, rhs):
            continue
        for pi2 in itertools.product(*ranges2):
            pi2 = np.array(pi2)
            if np.sum(pi2) % 2 != 0:
                continue
            if is_spin2:
                pi2 = pi2 + np.array([0.5]*8)
            lhs2 = np.dot(pi2 - w2*A2_2_value, pi2 - w2*A2_2_value)
            lhs = lhs1 + lhs2
            if not is_equal_float_num(lhs, rhs):
                continue
            n2 = w2 - np.dot(pi1, A2_1_value) - np.dot(pi2, A2_2_value)
            if is_integer(n2):
                Pi = np.concatenate((pi1, pi2))
                solution = {'w2': w2, 'n2': n2, 'Pi': Pi.tolist(), "rho": calculate_rho(A2, w2, Pi)}
                logger.info(f"solution: {solution}")
                solutions.append(solution)
    return solutions
