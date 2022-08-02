from random import randint
from os import name, system

def clear():
    system('cls' if name in ('nt', 'dos') else 'clear')

def get_values(mat, name):
    for i in range(len(mat)):
        for j in range(len(mat[i])):
            mat[i][j] = "X"
            clear()
            valid = False
            while not valid:
                print(f"{name}:")
                display_matrix(mat)
                user_input = input("Enter the value of X: ")
                if "." in user_input:
                    try:
                        mat[i][j] = float(user_input)
                        valid = True
                    except:
                        clear()
                        print("Error: Value must be an integer or float.")
                else:
                    try:
                        mat[i][j] = int(user_input)
                        valid = True
                    except:
                        clear()
                        print("Error: Value must be an integer or float.")
    return mat

def display_matrix(mat):
    for i in mat:
        print("  ", end="")
        for j in i:
            print(j, end=" ")
        print()

def matrix_multiply(a, b):
    result = [[0 for i in range(len(b[0]))] for j in range(len(a))]
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                result[i][j] += a[i][k]*b[k][j]
    return result

def get_matrix_dimensions(name):
    valid = False
    while not valid:
        valid = True
        mat_dimensions = input(f"Enter {name} dimensions (e.g. 2x2): ").split("x")
        if len(mat_dimensions) != 2:
            clear()
            print("Error: Please input two integers seperated by an x.")
            valid = False
        else:
            try:
                for i in range(len(mat_dimensions)):
                    mat_dimensions[i] = int(mat_dimensions[i])
                    if mat_dimensions[i] <= 0:
                        clear()
                        print("Error: Dimensions must be greater than 0.")
                        valid = False
            except:
                clear()
                print("Error: Please make sure that the inputs are integers.")
                valid = False
    return mat_dimensions

def main():
    mat_a_dimensions, mat_b_dimensions = get_matrix_dimensions("Matrix A"), get_matrix_dimensions("Matrix B")
    mat_a, mat_b = [["_" for i in range(int(mat_a_dimensions[1]))] for j in range(int(mat_a_dimensions[0]))], [["_" for i in range(int(mat_b_dimensions[1]))] for j in range(int(mat_b_dimensions[0]))]

    if len(mat_a[0]) != len(mat_b):
        print("Matrix Multiplication not possible!")

    else:
        mat_a, mat_b = get_values(mat_a, "Matrix A"), get_values(mat_b, "Matrix B")
        result =  matrix_multiply(mat_a, mat_b)
        clear()
        print()
        display_matrix(mat_a)
        print("Multiplied by")
        display_matrix(mat_b)
        print("Equals")
        display_matrix(result)

if __name__ == "__main__":
    main()
