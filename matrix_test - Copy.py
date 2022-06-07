mat_a = [[0,1,2,3],
        [4,5,6,7],
        [8,9,10,11],
        [12,13,14,15]]
mat_b = [[0],
        [1],
        [2],
        [3]]

def matrix_multiply(a, b):
    #print("a is", len(a), "x", len(a[0]), "and b is", len(b), "x", len(b[0]))
    if len(a[0]) != len(b):
        return [], False
    result = [[0 for i in range(len(b[0]))] for j in range(len(a))]
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                result[i][j] += a[i][k]*b[k][j]
    return result, True

result, success =  matrix_multiply(mat_a, mat_b)
if success:
    for i in result:
        print(i)
else:
    print("Not possible")
