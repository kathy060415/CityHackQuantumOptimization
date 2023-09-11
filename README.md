## Container Optimization Problem

The container optimization problem is an optimization problem where given a number of items with respective to base area, we look at the best arrangement of the items to minimize the number of containers needed. In this case, three restrictions are given : 
1. Boxes with the largest base area will be filled
2. If the remaining container base area is smaller than the box base area, fill up the box vertically
3. Volume of the containers shouldn't be surpassed.

### The data(box_data.csv) contains the following columns

Box Type: An identifier for the type of box.
Length, Width, Height: Dimensions of the box.
Base_area: The area of the base of the box (calculated as 
Length
×
Width
Length×Width).
Volume: The volume of the box (calculated as 
Base_area
×
Height
Base_area×Height).
Weight: The weight of the box.
All the columns contain integer values.

### Variables

1. x[i] : A binary variable that represents whether bin \( i \) is used or not.
2. e[i, j] : A binary variable that indicates whether item \( j \) is placed in bin \( i \).

### Objective Function

The objective is to minimize the number of bins used, which is mathematically represented as:

![image](https://github.com/kathy060415/CityHackQuantumOptimization/assets/71390293/cdaa1b5c-6172-49b9-98a4-1292f5269f79)

### Constraints

1. **Every Item Should Be in One Bin**: For each item \( j \), the sum of \( e[i, j] \) across all bins \( i \) should be 1.

   ![image](https://github.com/kathy060415/CityHackQuantumOptimization/assets/71390293/108263b3-5922-4b68-8016-cae746ffa8f7)

2. **Limit Bin Capacity by Area**: The total area of items in each bin \( i \) must not exceed the area \( Q \) of the bin.


   ![image](https://github.com/kathy060415/CityHackQuantumOptimization/assets/71390293/0d174503-3f8d-4dd0-8632-201d3c26790a)

   
3.  **Limit Bin Capacity by Volume**: The total volume of items in each bin \( i \) must not exceed the volume of the bin.


   ![image](https://github.com/kathy060415/CityHackQuantumOptimization/assets/71390293/c75e65e0-5b8a-485c-ab9c-cc0642059df0)


### Translation to Qiskit's Quadratic Program

After constructing this model, the code translates it into a Quadratic Program that can be solved using quantum algorithms like QAOA.

