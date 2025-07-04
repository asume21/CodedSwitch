import torch

obj = torch.load('backups/slim_backup', map_location='cpu')
with open('slim_backup_info.txt', 'w') as f:
    f.write(f'Type: {type(obj)}\n')
    if hasattr(obj, 'keys'):
        f.write(f'Keys: {list(obj.keys())}\n')
    else:
        f.write(f'Attributes: {dir(obj)}\n') 