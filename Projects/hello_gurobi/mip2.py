import gurobipy as gp
from gurobipy import GRB
import numpy as np
import scipy.sparse as sp

try:

    # 创建模型
    m = gp.Model("mip2")

    # 创建变量
    x = m.addMVar(shape=3, vtype=GRB.BINARY , name ="x")  # 长度为3的向量，包含三个0,1变量

    # 更新变量环境
    m.update()

    # 创建目标函数
    obj = np.array([1.0, 1.0, 2.0])
    m.setObjective(obj @ x, GRB.MAXIMIZE)  # 目标函数表达式，目标方向

    # 创建约束条件
    val = np.array([1.0, 2.0, 3.0, -1.0, -1.0])  # 非零值
    row = np.array([0 , 0 , 0 , 1 , 1])  # 非零值行坐标
    col = np.array([0 , 1 , 2 , 0 , 1])  # 非零值列坐标
    A = sp.csr_matrix ((val ,(row ,col )), shape=(2 , 3))  # 构建矩阵

    # Build rhs vector
    rhs = np.array([4.0, -1.0])  # 右侧变量
    # Add constraints
    m.addConstr (A @ x <= rhs , name ="c")  # 约束表达式，"约束名称"

    # 执行线性规划模型
    m.optimize()

    # 输出模型结果
    print("Obj:", m.objVal)
    for v in m.getVars():  # 获取变量，此时v是一个变量
        print(v.varName, end=" : ")  # 输出变量名
        print(v.x)  # 输出变量值

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')
