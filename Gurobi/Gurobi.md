# 基础过程

## 导入

```python
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import scipy.sparse as sp
```

## 创建模型

```python
m = gp.Model("model_name")
```

## 创建变量

```python
addVar(lb=0.0, ub=float(’inf’), obj=0.0, vtype=GRB.CONTINUOUS, name="", column=None)
# lb是变量下界，默认是0.0
# ub是变量上界，默认浮点数无穷
# obj是变量的目标系数，默认0.0
# vtype是变量类型，有GRB.CONTINUOUS: 连续性，GRB.BINARY: 0-1型,GRB.INTEGER: 整数型
# vtype还有GRB.SEMICONT: 半连续型和GRB.SEMIINT: 半整数型，还不了解，应该用不到
# name是变量名字，必须是ASCII，并且不包含空格
# column是变量的约束系数，也是默认没有

x = model.addVar() # all default arguments
y = model.addVar(vtype=GRB.INTEGER, obj=1.0, name="y") # arguments by name
z = model.addVar(0.0, 1.0, 1.0, GRB.BINARY, "z") # arguments by position
```

```python
addVars(*indices, lb=0.0, ub=float(’inf’), obj=0.0, vtype=GRB.CONTINUOUS, name="")
# 第一个参数indices用于描述变量的索引，有多种使用方法
# 在最简单的定义方法中，可以指定一个整数或多个整数，以创建一个等效的多维数组变量(x1)
# 也可以通过给出各轴的索引(x2)，以及给定特定变量索引来创建变量(x3)
# 各轴的索引的type需要保持一致
# lb是变量上界，可以给定一个标量，从而给出所有变量的上界，也可以利用Python字典给定lb
# 如果indices是一个list，可以给定lb一个对应的list来规定上界
# name和前面保持一致就行了，多的整不明白，总之各个变量会以x1[0, 1], x2[3, 'c']出现

x1 = model.addVars(2, 3)  # 创建一个两行三列共六个变量
x2 = model.addVars([3, 7], [’a’, ’b’, ’c’])  # 同样创建一个两行三列共六个变量，不过访问方式不同，如x2[7, 'c']才能访问7c变量
x3 = model.addVars([(3,’a’), (3,’b’), (7,’b’), (7,’c’)])  # 通过给予变量索引来创建变量，这通常用于稀疏变量，可以看出x3只有四个变量
l = tuplelist([(1, 2), (1, 3), (2, 3)])
x4 = model.addVars(l, ub=[1, 2, 3])  # 利用list给定变量规模，利用list规定上界
```

## 更新环境

```python
model.update()  # Process any pending model modifications.
```

## 创建目标

```python
setObjective(expr, sense=None)
# expr是目标函数的表达式，当然可以通过变量的obj来确定目标函数，再次使用本函数会更新目标函数
# expr可以是线性或二次型的
# LinExpr是线性表达式，quicksum可以代替sum
# LinExpr()用以构建表达式，可以有效提高效率; LinExpr() > addTerms > quicksum
# Optimization sense (GRB.MINIMIZE for minimization, GRB.MAXIMIZE for maximization)

model.setObjective(x1 + x2, GRB.MINIMIZE)  # 目标函数表达式，目标方向
```

## 创建约束

```python
addConstr(constr, name="")
# constr是约束表达式，需要一个TempConstr

model.addConstr(x + y <= 2.0, "c1")
model.addConstr(x*x + y*y <= 4.0, "qc0")
model.addConstr(x + y + z == [1, 2], "rgc0")
model.addConstr(A @ t >= b)
model.addConstr(z == and_(x, y, w), "gc0")
model.addConstr(z == min_(x, y), "gc1")
model.addConstr((w == 1) >> (x + y <= 1), "ic0")
```

```python
addConstrs(generator, name="")
# 增加多个约束，利用Python generator(生成器)
# 第一个generator是Python生成器，每次迭代生成后，生成一条新的约束
# 利用addConstrs创造一组约束name = c，每条约束的名字由c[i]表示
# 生成器中的i必须是标量值，生成器必须放在括号内

model.addConstrs(x.sum(i, ’*’) <= capacity[i] for i in range(5))  # 对第二个维度求和
model.addConstrs(x[i] + x[j] <= 1 for i in range(5) for j in range(5))
model.addConstrs(x[i]*x[i] + y[i]*y[i] <= 1 for i in range(5))
model.addConstrs(x.sum(i, ’*’) == [0, 2] for i in [1, 2, 4])
model.addConstrs(z[i] == max_(x[i], y[i]) for i in range(5))
model.addConstrs((x[i] == 1) >> (y[i] + z[i] <= 5) for i in range(5))
```

## 执行模型

```python
model.optimize()
```

## 输出结果

```python
print("Obj:", m.objVal)  # 输出结果

for v in m.getVars():  # 获取变量，此时v是一个变量
    print(v.varName, end=" : ")  # 输出变量名
    print(v.x)  # 输出变量值
```

# 附录

## MLinExpr

Gurobi利用`MLinExpr`来表达线性矩阵表达式。其中矩阵是`NumPy`的矩阵或`SciPy`的稀疏矩阵，Gurobi的变量，以及对应维度的常量。如$Ax=b$。

利用矩阵乘法`@`将矩阵与变量相乘，构建表达式，注意形状兼容。`A @ x`中，一定要保持A是二维数组，x是一维数组，且A的第二个维度的长度与x的长度相同。

常数是例外，常数可以广播到所有列。

```python
model.addConstr(A @ x <= b)
```

## TempConstr

Gurobi利用临时约束`TempConstr`构建模型约束，他由变量，表达式，不等号等组成，他有一下几种分类：

```python
# Linear Constraint: 线性约束
model.addConstr(x + y == 1)

# Ranged Linear Constraint: 框约束
model.addConstr(x + y == [1, 2])

# Quadratic Constraint: 二次约束
model.addConstr(x*x + y*y <= 1)

# Linear Matrix Constraint: 线性矩阵约束，需要Expr1和Expr2都是MLinExpr对象
model.addConstr(A @ x <= 1)
model.addConstr(A @ x == B @ y)

# Quadratic Matrix Constraint: 二次矩阵约束
model.addConstr(x @ A @ x <= 1)

# Absolute Value Constraint: 绝对值约束
model.addConstr(x @ A @ x <= 1)

# Logical Constraint: 逻辑约束，都是布尔变量，使用or或者and
model.addConstr(x == or_(y, z))

# Min or Max Constraint: 最小最大约束
model.addConstr(x == max_(y, z))

# Indicator Constraint: 指标约束，由>>构成，当>>前的部分成立时，>>后的部分必须成立。
model.addConstr((x == 1) >> (y + z <= 5))
```









### 模型参数

1. 停止参数：控制停止条件
2. 容差参数：最有或可行的精度
3. 单纯性参数
4. 内点法参数
5. MIP混合整数参数：控制混合整数规划的算法
6. MIP Cuts割平面参数：控制割平面算法的强度
7. Tuning调参参数：控制调参工具
8. Multiple Solutions多解参数：尝试寻找多个解

**设置方法**

setParam/model.Params.xxx

如 model.Params.TimeLimit = 600

MIPFocus：设定MIP求解侧重点：0默认均衡1侧重可行2侧重最有3侧重界的提升

Method：求解方法，内点法单纯形法对偶单纯形法等

### 属性

1. 模型属性：ModelSense：模型优化方向；ObjVal：当前目标函数值
2. 变量属性
3. 线性约束属性
4. SOS约束属性
5. 二次约束属性
6. 广义约束属性
7. 解质量属性
8. 多目标属性

**设置方法**

setAttr(attrname, newval)



约束

优化器参数

环境