def attention(q, k, v):
    return softmax(q @ k.T / scale) @ v
