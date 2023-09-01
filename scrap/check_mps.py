import torch

def check_mps_availability():
    return torch.backends.mps.is_available()

if __name__ == "__main__":
    print(check_mps_availability())