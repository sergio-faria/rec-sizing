![alt text](figures/logo_Enershare.png)
```
  ____   _____  ____   ____   _       _               
 |  _ \ | ____|/ ___| / ___| (_) ____(_) _ __    __ _ 
 | |_) ||  _| | |     \___ \ | ||_  /| || '_ \  / _` |
 |  _ < | |___| |___   ___) || | / / | || | | || (_| |
 |_| \_\|_____|\____| |____/ |_|/___||_||_| |_| \__, |
                                                |___/ 
```

# Documentation

The *REC Sizing* use case aims to provide an **optimal investment plan** for Renewable Energy Communities (REC) and 
Citizen Energy Communities (CEC) under the *Enershare* project. 

To that end, a library was implemented, named ***rec_sizing*** (**R**enewable **E**nergy **C**ommunities **Sizing**), 
that provides the user with several options for running a MILP optimization aimed at **minimizing the collective 
operation and investment costs** of the whole community. The MILP formulation not only schedules all controllable 
assets (namely batteries) and the optimal internal exchanges that should be established within the REC 
(a thorough explanation of the algorithms implemented is published [here](https://www.mdpi.com/1996-1073/16/3/1143)), 
but also the optimal investments in new RES generation and/or storage capacities.

**Notes**:
- The optimization is perfomed over the individual meters in the REC, defined by the user in the request.
- In the current version, the only option available is to run a collective MILP, where the local energy market (LEM) 
established within the REC is organized as a pool (i.e., bilateral transactions are not considered). The pricing 
mechanism for the market is one of the suggested outputs and is calculated according to the dual approach presented 
[here](https://ieeexplore.ieee.org/abstract/document/10161899)
- Any suggested investment is limited to the meters defined in the request. This means that the tool will not suggest 
the inclusion of additional meters. If that option is to be considered, one or more "empty" meters can be explicitly 
included in the request. 
- Any investment is applicable to the whole optimization period. This means that if the optimal solution requires 
installing additional RES or storage capacity behind a given meter, that capacity is considered to be operational from 
the beginning of the optimization horizon (defined by the user).

## Main optimization functions overview
Under ```rec_sizing_tools.optimization_functions``` the user can find:

```run_pre_collective_pool_milp``` 
- run a purely collective pre-delivery MILP, considering a *pool* LEM structure

## Install guide: use it as a library

The tool is implemented as a Python library. To install the library in, for example, a virtual environment, one must:
- download this repository
- change the working directory to the root folder of the repository:
    ```shell
    % cd /path/to/root_folder
    ```
- create the wheel file that will allow you to install the repository as a Python library 
(make sure you have previously installed Python ~= 3.10 in your local computer / server);

    ```shell
    % python setup.py bdist_wheel
    ``` 
- after creating your virtual environment with and activating it
    (see [this](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment)
    example for conda environments), enter the newly created ```dist``` folder, copy the name of the ```.whl``` file and 
install the library by using:
    ```shell
    % pip install wheel_file_name.whl
    ```
- (optional) return to the root folder path and run the tests provided to assert everything is working as it should:
    ```shell
    % python setup.py pytest
    ```
- to import the library use:
    ```shell
    from rec_sizing.optimization_functions import run_pre_collective_pool_milp as sizing
    ```