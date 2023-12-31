import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from docplex.mp.model import Model

from qiskit import BasicAer
from qiskit.algorithms import QAOA, NumPyMinimumEigensolver
from qiskit_optimization.algorithms import CplexOptimizer, MinimumEigenOptimizer
from qiskit_optimization.algorithms.admm_optimizer import ADMMParameters, ADMMOptimizer
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.translators import from_docplex_mp
from qiskit_optimization.converters import InequalityToEquality, IntegerToBinary, LinearEqualityToPenalty

##================##
df = pd.read_csv('box_data.csv').set_index('Box Type')
cargo_list = []
base_area_list = []
volume_list = []

# Iterate over each row
for index, rows in df.iterrows():
    # Create list for the current row
    my_list =[rows.Length, rows.Width, rows.Height, rows.Base_area, rows.Volume, rows.Weight]
    base_area = rows.Base_area
    volume = rows.Volume

    # append the list to the final list
    cargo_list.append(my_list)
    base_area_list.append(base_area)
    volume_list.append(volume)

base_area_list.sort(reverse=True)
volume_list.sort(reverse=True)

print(cargo_list)
print(base_area_list)
print(volume_list)

##================##
n = 2 # number of bins

m = len(cargo_list) # number of items

container_base_area =  2000  # container

# wj = np.amax(base_area_list) #  picking the maximum base area

container_volume = container_base_area * 200

# Construct model using docplex
mdl = Model("BinPacking")

x = mdl.binary_var_list([f"x{i}" for i in range(n)]) # list of variables that represent the bins
e =  mdl.binary_var_list([f"e{i//m},{i%m}" for i in range(n*m)]) # variables that represent the boxes
objective = mdl.sum([x[i] for i in range(n)])
mdl.minimize(objective)

#1. A model named "BinPacking" is created using docplex.
#2. Binary variables x[i] are defined to represent whether each bin i is used.
#3. Binary variables e[i,j] are defined to represent whether each item j is in bin i.
#4. The objective function is set to minimize the sum of x[i], which represents minimizing the number of bins used

##===================##
# Additional Variables
##===================##
ver = mdl.continuous_var_list([f"Ver{j}" for j in range(m)], lb=0, ub=volume_list[0])  # volume of each cargo
base = mdl.continuous_var_list([f"base{j}" for j in range(m)], lb=0, ub=base_area_list[0])  # base area of each cargo
counter = mdl.integer_var(lb=0, name="counter")  # number of cargos placed
sn = mdl.continuous_var(lb=0, ub=1, name="Sn")  # space utilization

# To track remaining base & volume
remaining_base = mdl.continuous_var_list([f"remaining_base{i}" for i in range(n)], lb=0, ub=container_base_area)  # Bounded
remaining_volume = mdl.continuous_var_list([f"remaining_volume{i}" for i in range(n)], lb=0, ub=container_volume)  # Bounded


##==============##
# Constraints
for i in range(n):
    # Second set of constraints: sum of box area < container area
    constraint1 = mdl.sum(base_area_list[j] for j in range(m))
    mdl.add_constraint(constraint1 <= container_base_area, f"cons1,{i}")

for i in range(n):
    constraint2 = mdl.sum(volume_list[i] for i in range(m))
    mdl.add_constraint(constraint2 <= container_volume, f"cons2,{i}")

##===================##
# Additional Constraints
##===================##

# Initial Constraints to set the remaining_base and remaining_volume to the maximum capacity initially
for i in range(n):
    mdl.add_constraint(remaining_base[i] == container_base_area, f"InitialBase{i}")  # Assuming Q is the maximum base area of each bin
    mdl.add_constraint(remaining_volume[i] == container_volume, f"InitialVolume{i}")  # Assuming V is the maximum volume of each bin

# Constraints to update remaining_base and remaining_volume based on the items placed in each bin
for i in range(n):
    for j in range(m):
        # Update remaining base area if e[i, j] = 1 (i.e., if item j is placed in bin i)
        mdl.add_constraint(remaining_base[i] >= container_base_area - mdl.sum(e[i*m+j] * base_area_list[j] for j in range(m)), f"UpdateRemainingBase{i}{j}")

         # Update remaining volume if e[i, j] = 1 (i.e., if item j is placed in bin i)
        mdl.add_constraint(remaining_volume[i] >= container_volume - mdl.sum(e[i*m+j] * volume_list[j] for j in range(m)), f"UpdateRemainingVolume{i}{j}")


# Constraint: Cargo volume should be less than or equal to container volume
for j in range(m):
    mdl.add_constraint(ver[j] <= container_volume, f"VolumeConstraint{j}")

# Corrected Constraints: Compare base[j] and ver[j] with remaining_base[i] and remaining_volume[i] for each bin i
for i in range(n):
    for j in range(m):
        
        # Assuming remaining_base is a variable that keeps track of remaining base area in the container
        # Constraint: Base area of each cargo j should be less than remaining base area in the container
        mdl.add_constraint(base[j] <= remaining_base[i], f"BaseAreaConstraint{i}{j}")

        # Constraint: Volume of each cargo j should be less than remaining volume in the container
        # Assuming remaining_volume is a variable that keeps track of remaining volume in the container
        mdl.add_constraint(ver[j] <= remaining_volume[i], f"RemainingVolumeConstraint{i}{j}")


##=============##
# Solving Quadratic Program using CPLEX
#qp = QuadraticProgam() will be automatically executed within from_docplex_mp
qp = from_docplex_mp(mdl)

cplex = CplexOptimizer()
result = cplex.solve(qp)
print(result)
print(qp.prettyprint())

ineq2eq = InequalityToEquality()
qp_eq = ineq2eq.convert(qp)
print(qp_eq.export_as_lp_string())
print(f"The number of variables is {qp_eq.get_num_vars()}")

int2bin = IntegerToBinary()
qp_eq_bin = int2bin.convert(qp_eq)
print(qp_eq_bin.export_as_lp_string())
print(f"The number of variables is {qp_eq_bin.get_num_vars()}")

lineq2penalty = LinearEqualityToPenalty()
qubo = lineq2penalty.convert(qp_eq_bin)
print(f"The number of variables is {qp_eq_bin.get_num_vars()}")
print(qubo.export_as_lp_string())

result = cplex.solve(qubo)
print(result)

##=================##
# Solving Quadratic program using QAOA
from qiskit import Aer
backend = Aer.get_backend("qasm_simulator")
qaoa = MinimumEigenOptimizer(QAOA(reps=1, quantum_instance=backend))
result_qaoa = qaoa.solve(qubo)
print(result_qaoa)

##==================##
# Calculate and print the space utilization
##==================##

# Define a function to calculate space utilization for a given result
def calculate_space_utilization(result, n, m, volume_list):
    # Initialize an empty dictionary to store total volume for each bin
    total_volume_of_bin = {i: 0 for i in range(n)}
    space_utilization_of_bin = {i: 0 for i in range(n)}

    # Extract optimized variable values
    optimized_values = result.x
    e_values = optimized_values[len(total_volume_of_bin):]  # Assuming e starts after x in the variable list

    # Calculate the total volume for each bin
    for i in range(n):
        for j in range(m):
            #If the value is greater than or equal to 0.5, it is likely that the optimal integer solution would have this variable set to 1.
            if e_values[i * m + j] >= 0.5:
                total_volume_of_bin[i] += volume_list[j]

    # Calculate space utilization for each bin
    for i in range(n):
        if total_volume_of_bin[i] > 0:  # To avoid division by zero
            space_utilization_of_bin[i] = total_volume_of_bin[i] / container_volume

    return space_utilization_of_bin

# Calculate space utilization based on CPLEX result
space_utilization_cplex = calculate_space_utilization(result, n, m, volume_list)
print("Space Utilization (CPLEX):", space_utilization_cplex)

# Calculate space utilization based on QAOA result
space_utilization_qaoa = calculate_space_utilization(result_qaoa, n, m, volume_list)
print("Space Utilization (QAOA):", space_utilization_qaoa)

