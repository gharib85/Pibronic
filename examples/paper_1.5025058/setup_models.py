# setup_models.py - creates all the directories and copies in the necessary files

# system imports
import shutil
import time
import glob
import sys
# import os
from os.path import join, abspath, dirname

# third party imports

# local imports
import context
import systems
from pibronic.vibronic import vIO, VMK
import pibronic.data.file_structure as fs
sys.path.insert(1, abspath(__file__))  # TODO - fix this import in the future
from submit_jobs_to_server import iterative_method_wrapper


def parse_input_mctdh_files_into_directories(FS, system_name):
    """ fill the directories with the appropriate data so we can run simulations
    starts from MCTDH *.op files and creates the relevant *.json files """

    # where the MCTDH input files for each model are stored
    dir_src = join(abspath(dirname(__file__)), "input_mctdh")

    path_src = join(dir_src, f"{system_name:s}_{FS.id_data%10:d}.op")
    path_dst = shutil.copy(path_src, FS.path_es)

    # create the coupled_model.json file from the system_[1-6].op file
    # this is not necessary since we know what the *.json files will look like,
    # but simulating the full procedure is fine
    vIO.create_coupling_from_op_file(FS, path_dst)
    vIO.create_harmonic_model(FS)
    # this basic sampling model is simply the diagonal of the Hamiltonian
    vIO.create_basic_diagonal_model(FS)
    return


def copy_input_json_files_into_directories(FS, system_name):
    """ fill the directories with the appropriate data so we can run simulations
    starts from the preconstructed *.json file"""

    # where the .json input files for each model are stored
    dir_src = join(abspath(dirname(__file__)), "input_json")

    path_src = join(dir_src, f"{system_name:s}_{FS.id_data%10:d}.json")

    # copy the .json file into the appropriate directory
    shutil.copy(path_src, FS.path_vib_model)
    # this basic sampling model is simply the diagonal of the Hamiltonian
    print(FS.path_rho_params)
    vIO.create_basic_diagonal_model(FS)
    return


def copy_alternate_rhos_into_directories(FS, system_name):
    """ scan files in root/alternate_rhos/ directory
    make directories for and copy in all relevant files """

    # where the .json input files for each sampling distribution are stored
    dir_src = join(abspath(dirname(__file__)), "alternate_rhos")

    # collect all possible alternative rho's
    globPath = join(dir_src, f"{system_name:s}_D{FS.id_data%10:d}_R*.json")
    lst_files = [file for file in glob.glob(globPath)]

    for file in lst_files:
        # extract the id
        id_rho = int(file.split("_R")[1].split(".json")[0])
        # create the directories
        FS.change_rho(id_rho)
        # copy the file over
        shutil.copy(file, FS.path_rho_model)

    return


def prepare_paper_model(system_name, id_data=0, root=None):
    """ wrapper function """
    systems.assert_id_data_is_valid(id_data)

    if root is None:
        root = context.choose_root_folder()

    # instantiate the FileStructure object which creates the directories
    FS = fs.FileStructure(root, id_data, 0)

    # either way will work
    if True:
        copy_input_json_files_into_directories(FS, system_name)
    else:
        parse_input_mctdh_files_into_directories(FS, system_name)

    # create all possible rho's
    # which are the diagonal of the transformed Hamiltonian (id_rho = 0)
    # and the improved models presented in the paper (id_rho = 1)
    # (jahn-teller only) the more improved model presented in the paper (id_rho = 2)
    copy_alternate_rhos_into_directories(FS, system_name)
    return


def setup_weight_corrected_iterative_model(FS):
    """ x """
    FS.change_rho(systems.iterative_model_id_rho)
    iterative_method_wrapper(id_data=FS.id_data)
    time.sleep(2)  # hopefully fixes a race condition, which I encountered one time, possibly due to timing of the Slurm scheduler
    vIO.recalculate_energy_values_of_diagonal_model(FS, FS.path_iter_model)
    shutil.copy(FS.path_iter_model, FS.path_rho_model)


def prepare_paper_model_plus_iterative_method(system_name, id_data=0, root=None):
    """ wrapper function """

    # first call the simple setup
    prepare_paper_model(system_name, id_data=id_data, root=root)

    if root is None:
        root = context.choose_root_folder()

    # instantiate the FileStructure object which creates the directories
    FS = fs.FileStructure(root, id_data, 0)

    # creates the additional rho
    # the weight corrected iterative method (id_rho = 11)
    setup_weight_corrected_iterative_model(FS)
    return


def automate_prepare_model():
    """ convenience/wrapper function
    loops over all the models we want to prepare
    """
    for name in systems.name_lst:
        for id_data in systems.id_dict[name]:
            prepare_paper_model(name, id_data=id_data)
    return


def main():
    automate_prepare_model()


if (__name__ == "__main__"):
    main()
