"""Minimal, near-instant GPU device confirmation. No data, no model, no
network access needed -- just asks torch what hardware this session has.
"""

import torch

print("torch.cuda.is_available():", torch.cuda.is_available())
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        print(f"torch.cuda.get_device_name({i}):", torch.cuda.get_device_name(i))
        props = torch.cuda.get_device_properties(i)
        print(f"  compute capability: {props.major}.{props.minor}")
        print(f"  total memory (GB): {props.total_memory / 1e9:.2f}")
else:
    print("No CUDA device available.")
