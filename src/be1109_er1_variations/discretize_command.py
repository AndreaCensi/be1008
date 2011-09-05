from procgraph import simple_block
import numpy as np

@simple_block
def discretize_command(x, zero_threshold=0.01):
    if np.abs(x) < zero_threshold:
        return 0
    else:
        return np.sign(x)


@simple_block
def discretize_commands(x, zero_threshold=0.01):
    y = np.empty_like(x)
    for i in range(x.size):
        if np.abs(x[i]) < zero_threshold:
            y[i] = 0
        else:
            y[i] = np.sign(x[i])
    return y
