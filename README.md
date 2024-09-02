# Netbox Scripts
Netbox Scripts is an automation tool used to chunk Netbox addition. This exists due to Netbox file addition feature being synchronous, causing addition of large files to result in HTTP timeout.

### Requirements
This script requires a GNU/Linux environment to execute. Additionally, it also requires:
1. Python 3.12
2. Pynetbox (Ver. 7.4.0)
3. Pandas (Ver. 2.2.2)
4. Netbox API (Ver. 4.0)

### Installation
This script requires no installation. Allow execution of script using
```
./chmod +x run.py
```

### Usage
This script is cli based, show list of commands using
```
./run.py -h
```

### Notable Features
- Device, Interface, and Address addition

## Credits
> [MuhamadAjiW](https://github.com/MuhamadAjiW) <br/>
> [akmaldika](https://github.com/akmaldika)