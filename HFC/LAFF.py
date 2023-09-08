import time
import pandas as pd

df = pd.read_csv('box_data.csv').set_index('Box Type')

cargo_list = []
base_area_list = []

# Iterate over each row
for index, rows in df.iterrows():
    # Create list for the current row
    my_list =[rows.Length, rows.Width, rows.Height, rows.Base_area, rows.Volume, rows.Weight]
    base_area = rows.Base_area

    # append the list to the final list
    cargo_list.append(my_list)
    base_area_list.append(base_area)


# print list
print(cargo_list)

base_area_list.sort()
print(base_area_list)
df.head()
df.dtypes

def calculate_space_efficiency(container_dimensions, cargo_list):
    # Calculate volume of container vc
    vc = container_dimensions[0] * container_dimensions[1] * container_dimensions[2]

    # Initialize variables

    cargo_counter = 0  # queue number of the cargo
    remaining_base = container_dimensions[0]
    remaining_volume = vc
    loaded_cargos = []

    # While all cargos are placed
    while cargo_counter < len(cargo_list):
        cargo = cargo_list[cargo_counter]

        # start measuring the time
        start_time = time.time()

        # Calculate volume of cargo, vcr
        vcr = cargo[0] * cargo[1] * cargo[2]

        # If cargo dimensions = container dimensions
        if cargo[0] == container_dimensions[0] and cargo[1] == container_dimensions[1] and cargo[2] == \
                container_dimensions[2]:
            loaded_cargos.append(cargo)
            remaining_volume -= vcr
            cargo_counter += 1
            continue

        # Choose cargo with widest base
        if cargo[0] >= cargo[1] and cargo[0] >= cargo[2]:
            cargobase = cargo[0]
            cargobase_idx = 0
        elif cargo[1] >= cargo[0] and cargo[1] >= cargo[2]:
            cargobase = cargo[1]
            cargobase_idx = 1
        else:
            cargobase = cargo[2]
            cargobase_idx = 2

        # If volume of cargo > container, skip cargo
        if vcr > vc:
            cargo_counter += 1
            continue

        #  Add cargo to list
        loaded_cargos.append(cargo)

        # Add volume of cargo
        remaining_volume -= vcr

        # Increment the cargo counter
        cargo_counter += 1

        # If remaining base > cargo base, place cargo along with base and add cargo volume again
        if remaining_base >= cargobase:
            remaining_base -= cargobase

            # Place cargo along height & add cargo volume
            remaining_volume -= vcr
        else:
            # else place along width and add volume
            remaining_volume -= vcr

        # If remaining volume < cargo volume, add cargo to new container
        if remaining_volume < vcr:
            # Calculate space utilization for this container
            space_utilization = (vc - remaining_volume) / vc

            # Step 15: Add cargo to new container
            new_container_space_utilization = calculate_space_efficiency(container_dimensions,
                                                                         cargo_list[cargo_counter:])

            # Step 16: Calculate total space utilization, su
            su = space_utilization + new_container_space_utilization

            return su

    # Calculate space utilization
    space_utilization = (vc - remaining_volume) / vc
    su = space_utilization

    return su


# sample input
container_dimensions = (70, 70, 70)

# Record the start time
start_time = time.time()

space_utilization = calculate_space_efficiency(container_dimensions, cargo_list)

# Record the end time
end_time = time.time()
running_time = end_time - start_time

print(f"Space utilization: {space_utilization:.3f}")
print(f"Running time: {running_time:.10f} seconds")
