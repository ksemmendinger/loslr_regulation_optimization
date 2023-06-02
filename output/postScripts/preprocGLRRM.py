import sys
import dill as pickle 
from pathlib import Path

GLRRM_ONTARIO = "C:\\Users\\GervasiN\\Documents\\GLRRM-Ontario"

sys.path.append(GLRRM_ONTARIO)

from glrrm.util.config_utils import read_config, SimulationInfo
from glrrm.handler import databank as db
from glrrm.handler import databank_io as dbio
from glrrm.ontario.simulate import Simulation

def get_solution(cfg_pth):
    # read the GLRRM-Ontario configuration file   
    cfgparser = read_config(cfg_pth)
    sim_info = SimulationInfo.from_configparser(cfgparser)
    
    solution = sim_info.get('solutions', 'solns', obj_type="list")
    
    if len(solution) > 1:
        raise ValueError(
            "Only one solution permitted when running GLRRM within the optimization framework."    
        )
    elif len(solution) == 0:
        raise ValueError(
            f"solution not specified in {cfg_pth}."
        )
    else:
        solution = solution[0]
    inp_pth = sim_info.get(solution, 'config', obj_type='string')
    return solution, inp_pth, sim_info

def pre_process(start, end, cfg_pth, out_pth):

    solution, inp_pth, sim_info = get_solution(cfg_pth)
    
    # !!! hard-coded for now...
    intvl = 'qm48'

    # read and parse the config file with the list of input files
    cfgparser = read_config(inp_pth)
    inp_info = SimulationInfo.from_configparser(cfgparser)
    inp_list = inp_info.get('inputs', 'list', obj_type='list')
    
    fname_vault = 'vault.pkl'
    fname_sim_data = 'sim_data.pkl'
    
    vault = db.DataVault()
    
    # read all inputs and deposit into vault object
    for inp in inp_list:
        filename = Path(inp_info['input_files'][inp])
        ds = dbio.read_file(filename=filename)
        if ds.dataInterval != intvl:
            ds.change_qm_notation(intvl)
        if ds:
            vault.deposit(ds)
            print(f"{filename} deposited")
    
    # write the vault to file
    dbio.write_vault(
        vault=vault,
        out_path=out_pth,
        file_format='binary',
        key_list=vault.contents, 
        group=True,
        fname=fname_vault
    )
    
    # instantiate a GLRRM-Ontario solution
    sim = Simulation(
        vault=vault, 
        tstart=start, 
        tend=end, 
        sim_info=sim_info,
        solution_template=solution,
        inputs_from_cfg=False,
    )
    
    # write out the GLRRM-Ontario initial conditions and spin-up data 
    # (contained within a sim_data object)
    with open(Path(out_pth+'/'+fname_sim_data), 'wb') as p:
        pickle.dump(sim.sim_data, p)


if __name__ == '__main__':
    
    cfg_pth = "C:\\Users\\GervasiN\\Documents\\GLRRM-Ontario\\glrrm\\config\\ontario\\ontario.ini"
    out_pth = "C:\\Users\\GervasiN\\Documents\\GLRRM-Ontario\\data\\data_out\\"
    
    pre_process(
        start='1900-01-01', 
        end='2008-12-31', 
        cfg_pth=cfg_pth, 
        out_pth=out_pth
    )