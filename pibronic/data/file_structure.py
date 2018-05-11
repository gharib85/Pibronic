"""
Bookkeeping provided by FileStucture class

keeps directory structure consistant over the many modules if changes need to be made
"""

# system imports
import os
from os.path import join
# from pathlib import Path  # should eventually make use of this

# third party imports

# local imports
from . import file_name
from ..log_conf import log


# the names of the sub directories
# TODO - clean this up
list_sub_dirs = [
    "parameters/",
    "results/",
    "execution_output/",
    "plots/",
    ]


class FileStructure:
    """handles creation and verification of default file structure storing data from/to jobs"""
    template_vib = "data_set_{:d}/"
    template_rho = template_vib + "rho_{:d}/"
    template_vib_params = template_vib + "parameters/"
    template_vib_results = template_vib + "results/"
    template_vib_output = template_vib + "execution_output/"
    template_vib_plots = template_vib + "plots/"
    template_rho_params = template_rho + "parameters/"
    template_rho_results = template_rho + "results/"
    template_rho_output = template_rho + "execution_output/"
    template_rho_plots = template_rho + "plots/"

    # TODO - make sure all the old output files are not needed or have been converted to new file names
    """
    template_pimc_suffix = "D{D:d}_R{R:d}_P{P:d}_T{T:.2f}_J*_data_points.npz"
    template_jackknife_suffix = "D{D:d}_R{R:d}_P{P:d}_T{T:.2f}_X{X:d}_thermo"
    template_sos_suffix = "sos_B{B:d}.json"
    """

    # template_pimc_suffix = file_name.pimc
    # template_jackknife_suffix = file_name.jackknife
    # template_sos_suffix = file_name.sos

    @classmethod
    def from_boxdata(cls, path_root, data):
        """constructor wrapper that takes a data object from minimal.py"""
        return cls(path_root, data.id_data, data.id_rho)

    def __init__(self, path_root, id_data, id_rho=0):
        """x"""
        # assert type(path_root) is str, "did not provide a path in str format"

        self.id_rho = id_rho
        self.id_data = id_data
        assert os.path.exists(path_root), "the path_root does not exist"
        assert os.path.isdir(path_root), "the path_root is not a directory"
        self.path_root = os.path.abspath(path_root)
        # main directories
        self.path_data = join(self.path_root, self.template_vib.format(id_data))
        self.path_rho = join(self.path_root, self.template_rho.format(id_data, id_rho))
        # special
        self.path_es = join(self.path_data, "electronic_structure")
        # sub directories
        self.path_vib_params = join(path_root, self.template_vib_params.format(id_data))
        self.path_vib_results = join(path_root, self.template_vib_results.format(id_data))
        self.path_vib_output = join(path_root, self.template_vib_output.format(id_data))
        self.path_vib_plots = join(path_root, self.template_vib_plots.format(id_data))
        self.path_rho_params = join(path_root, self.template_rho_params.format(id_data, id_rho))
        self.path_rho_results = join(path_root, self.template_rho_results.format(id_data, id_rho))
        self.path_rho_output = join(path_root, self.template_rho_output.format(id_data, id_rho))
        self.path_rho_plots = join(path_root, self.template_rho_plots.format(id_data, id_rho))

        # root_suffix = "D{:d}_R{:d}_".format(id_data, id_rho)
        # self.pimc_suffix = root_suffix + "P{P:d}_T{T:.2f}_J*_data_points.npz"
        # self.jackknife_suffix = root_suffix + "P{P:d}_T{T:.2f}_X{X:d}_thermo"

        # can't use os.path.join on these because they are format strings that haven't been fully resolved yet
        self.template_pimc = self.path_rho_results + file_name.pimc(J="{J:s}")
        self.template_jackknife = self.path_rho_results + file_name.jackknife()
        self.template_sos_rho = self.path_rho_params + file_name.sos()
        self.template_sos_vib = self.path_vib_params + file_name.sos()

        # TODO - should we factor this out into the file_name module?
        # self.template_pimc = file_name.pimc
        # self.pimc_suffix = "P{P:d}_T{T:.2f}_J*_data_points.npz"
        # self.jackknife_suffix = self.template_jackknife_suffix

        self.dir_list = [a for a in dir(self) if a.startswith('path_')]

        # print(self.dir_list, '\n\n')
        # self.dir_list = [self.path_data, self.path_es]
        # self.dir_list.extend([self.path_data + x for x in list_sub_dirs])
        # self.dir_list.extend([self.path_rho + x for x in list_sub_dirs])

        """ TODO - possibly rename the sampling and coupled paths?
        they are paths but shouldn't be in the dir_list
        """
        self.path_vib_model = join(self.path_vib_params, file_name.coupled_model)
        self.path_har_model = join(self.path_vib_params, file_name.harmonic_model)
        self.path_rho_model = join(self.path_rho_params, file_name.sampling_model)

        # if not self.directories_exist():
        self.make_directories()
        return

    def directories_exist(self):
        """x"""
        if False in map(os.path.isdir, self.dir_list):
            return False
        return True

    def make_directories(self):
        """x"""
        for directory in self.dir_list:
            path = getattr(self, directory)
            log.flow(path)
            os.makedirs(path, exist_ok=True)
        return

    def make_rho_directories(self, id_rho):
        """x"""
        if id_rho == self.id_rho:
            self.make_directories()
            return

        directories = [self.path_data + self.dir_rho.format(id_rho) + x for x in list_sub_dirs]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        return

    def verify_directories_exists(self, id_data, path_root=None):
        """ if directory structure exists does nothing, creates the file structure otherwise"""

        # assume default
        if path_root is None:
            raise Exception("NO DEFAULT ROOT!?")
            # path_root = path_default_root # fix this ?

        files = FileStructure(path_root, id_data)
        if files.directories_exist():
            return

        files.make_directories()
        return
