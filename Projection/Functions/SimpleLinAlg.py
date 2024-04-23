import math

def cross(A, B):
    c = [A[1] * B[2] - A[2] * B[1],
         A[2] * B[0] - A[0] * B[2],
         A[0] * B[1] - A[1] * B[0]]

    return c

# https://stackoverflow.com/a/39881366
def transposeMatrix(m):
    return list(map(list,zip(*m)))

def getMatrixMinor(m,i,j):
    return [row[:j] + row[j+1:] for row in (m[:i]+m[i+1:])]

def getMatrixDeternminant(m):
    #base case for 2x2 matrix
    if len(m) == 2:
        return m[0][0]*m[1][1]-m[0][1]*m[1][0]

    determinant = 0
    for c in range(len(m)):
        determinant += ((-1)**c)*m[0][c]*getMatrixDeternminant(getMatrixMinor(m,0,c))
    return determinant

def getMatrixInverse(m):
    determinant = getMatrixDeternminant(m)
    #special case for 2x2 matrix:
    if len(m) == 2:
        return [[m[1][1]/determinant, -1*m[0][1]/determinant],
                [-1*m[1][0]/determinant, m[0][0]/determinant]]

    #find matrix of cofactors
    cofactors = []
    for r in range(len(m)):
        cofactorRow = []
        for c in range(len(m)):
            minor = getMatrixMinor(m,r,c)
            cofactorRow.append(((-1)**(r+c)) * getMatrixDeternminant(minor))
        cofactors.append(cofactorRow)
    cofactors = transposeMatrix(cofactors)
    for r in range(len(cofactors)):
        for c in range(len(cofactors)):
            cofactors[r][c] = cofactors[r][c]/determinant
    return cofactors

def vecMatMul(v, m):
    result = []
    for row in m:
        result.append(sum(vecMul(row, v)))
    return result  

def matmul(x, y):
    return  [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*y)] for X_row in x]

def dotProd(a, b):
    dot = sum(a[i] * b[i] for i in range(len(a)))
    return dot

def vecAdd(a, b):
    return [a[i] + b[i] for i in range(len(a))]

def vecSub(a, b):
    return [a[i] - b[i] for i in range(len(a))]

def vecMul(a, b):
    return [a[i] * b[i] for i in range(len(a))]

def scaleVecMul(s, v):
    return [x*s for x in v]

def normalize_vector(vector: list[float]) -> list[float]:
    """
    Normalize a vector
    """
    # sqrt( x^2 + y^2 + z^2 ) = length
    magnitude = math.sqrt((vector[0] ** 2) + (vector[1] ** 2) + (vector[2] ** 2))
    return scaleVecMul(1/magnitude, vector)

def four_to_three_dim(point):
    """
    Given a point with dimensions 4 x 1, returns it as 3x1
    """
    return [point[0], point[1], point[2]]

def four_to_three_dim_list(points):
    """
    Given a list of points each with dimensions 4 x 1, returns them as 3x1s
    """
    for i, point in enumerate(points):
        points[i] = point[0], point[1], point[2]
    return points

def is_point_on_plane(point: list[float], plane_point: list[float], plane_normal: list[float]) -> bool:
    """
    Returns whether a point lies on a plane
    """
    points_vector = vecSub(point, plane_point)
    dot = dotProd(points_vector, plane_normal) # different depending on whether or not the normal is normalized?
    if math.isclose(dot, 0, abs_tol=1e-9): # Should be true? abs tol might fix it maybe TODO check that
        return True
    return False

def get_plane_normal(plane: list[list[float]]):
    """
    Given three points on a plane, returns the normal of that plane
    """
    if len(plane[0]) > 3:
        plane[0] = four_to_three_dim(plane[0])
    if len(plane[1]) > 3:
        plane[1] = four_to_three_dim(plane[1])
    if len(plane[2]) > 3:
        plane[2] = four_to_three_dim(plane[2])

    vector_1 = vecSub(plane[0], plane[1])
    vector_2 = vecSub(plane[0], plane[2])
    normal = cross(vector_1, vector_2)
    normal = normalize_vector(normal)
    return normal

def is_point_infront_of_plane(plane: list[list[float]], point: list[float]) -> bool:
    """
    Takes in a plane defined as three points and a point (3x1).
    The points have dimensions of 3/4x1
    Returns True if the point is in front / on a plane
    Returns False if the point is outside a plane
    Taken from here:
    https://math.stackexchange.com/questions/214187/point-on-the-left-or-right-side-of-a-plane-in-3d-space/214194#214194
    """
    a = plane[0]
    if len(a) == 4:
        a = four_to_three_dim(a)

    b = plane[1]
    if len(b) == 4:
        b = four_to_three_dim(b)

    c = plane[2]
    if len(c) == 4:
        c = four_to_three_dim(c)
        
    x = point
    if len(x) == 4:
        x = four_to_three_dim(x)

    b_p = vecSub(b, a)
    c_p = vecSub(c, a)
    x_p = vecSub(x, a)

    new_mat = [
        b_p, c_p, x_p
    ]
    
    det = getMatrixDeternminant(new_mat)

    if det >= 0 or math.isclose(det, 0, rel_tol=1e-9, abs_tol=1e-9):
        return True
    return False

def get_line_plane_intersect_point(line: list[list[float]], plane_point: list[float], plane_normal: list[float]):
    """
    Takes in a line (2 points) and a plane, returns a 3x1 vector of their intersection, or None if there is none.
    Taken from https://stackoverflow.com/questions/5666222/3d-line-plane-intersection
    """

    epsilon = 1e-6
    point_1 = line[0]
    point_1 = four_to_three_dim(point_1)

    point_2 = line[1]
    point_2 = four_to_three_dim(point_2)

    u = vecSub(point_2, point_1)
    dot = dotProd(plane_normal, u)

    if abs(dot) > epsilon:
        w = vecSub(point_1, plane_point)
        fac = -dotProd(plane_normal, w) / dot
        u = scaleVecMul(fac, u)

        intersect_point = vecAdd(point_1, u)
        return intersect_point
    
    # Line is parallel to plane
    return None

def mean(values: list[float]):
    """Returns the mean value of all the numbers in a list"""
    sum = 0
    for value in values:
        sum += value
    return sum / len(values)

def mean_of_points(points: list):
    """Returns the average of 3 points"""
    x_values = []
    y_values = []
    z_values = []

    for point in points:
        x_values.append(point[0])
        y_values.append(point[1])
        z_values.append(point[2])

    mean_x = mean(x_values)
    mean_y = mean(y_values)
    mean_z = mean(z_values)

    return [mean_x, mean_y, mean_z]

def intersect_planes(normal_1, normal_2):
    direction = cross(normal_1, normal_2)
    return direction