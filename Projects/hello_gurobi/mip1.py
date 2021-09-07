import gurobipy as gp
from gurobipy import GRB

try:

    # 创建模型
    m = gp.Model("mip1")

    # 创建变量
    X = m.addVar(vtype=GRB.BINARY, name="X")
    Y = m.addVar(vtype=GRB.BINARY, name="Y")
    Z = m.addVar(vtype=GRB.BINARY, name="Z")

    # 更新变量环境
    m.update()

    # 创建目标函数
    m.setObjective(X + Y + 2 * Z, GRB.MINIMIZE)

    # 创建约束条件
    m.addConstr(X + 2 * Y + 3 * Z <= 4, "c0")
    m.addConstr(X + Y >= 1, "c1")

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
