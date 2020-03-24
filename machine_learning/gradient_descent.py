import matplotlib.pyplot as plt


def g(xx, yy):
    """This is the function g(x,y) = (x + y - 2)**2"""
    return (xx + yy - 2)**2


def partial_deriv_x(x_, y_):
    return 2*(x_ + y_ - 2)


def partial_deriv_y(x_, y_):
    return 2*(x_ + y_ - 2)


learning_rate = 0.1
termination_cond = 2**-32

x_val = 0
y_val = 0
g_val = g(x_val, y_val)

g_val_list = [g_val]
x_val_list = [x_val]
y_val_list = [y_val]

while True:
    partial_x = partial_deriv_x(x_val, y_val)
    partial_y = partial_deriv_y(x_val, y_val)
    x_val -= partial_x * learning_rate
    y_val -= partial_y * learning_rate

    new_g = g(x_val, y_val)
    g_val_list.append(new_g)
    x_val_list.append(x_val)
    y_val_list.append(y_val)

    if abs(abs(new_g) - abs(g_val)) < termination_cond:  # Termination condition
        break
    else:
        g_val = new_g

# Let's make the graphs
plt.subplot(3, 1, 1)
plt.scatter([i for i in range(len(g_val_list))], g_val_list)
plt.title('Iteration vs g(x,y)')
plt.xlabel('Iteration')
plt.ylabel('g(x,y)')

plt.subplot(3, 1, 2)
plt.scatter([i for i in range(len(x_val_list))], x_val_list)
plt.title('Iteration vs x')
plt.xlabel('Iteration')
plt.ylabel('x')

plt.subplot(3, 1, 3)
plt.scatter([i for i in range(len(y_val_list))], y_val_list)
plt.title('Iteration vs y')
plt.xlabel('Iteration')
plt.ylabel('y')

plt.tight_layout()
plt.show()
