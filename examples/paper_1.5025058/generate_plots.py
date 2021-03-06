# generate_plots.py

# system imports
from multiprocessing import Process

# third party imports

# local imports
import context
import systems
from pibronic.plotting import plotting as pl
from pibronic.data import file_structure as fs


def automate_simple_z_plots(name):
    """ loops over the data sets and different rhos plotting the data for each one """
    systems.assert_system_name_is_valid(name)

    root = context.choose_root_folder()

    # Currently we implement very simple plotting, only plotting the Z_MC
    for id_data in systems.id_dict[name]:
        for id_rho in systems.rho_dict[name][id_data]:
            try:
                FS = fs.FileStructure(root, id_data, id_rho)
                plotObj = pl.plot_Z_test(FS)
                plotObj.load_data()
                plotObj.plot()
                print(f"Finished plotting D{id_data:d} R{id_rho:d}")
            except Exception as e:
                print(e)
                continue
    return


if (__name__ == "__main__"):
    # If you want to speed things up you can split the work across four processes
    # pool is not used because these processes are I/O intensive and we want them to run concurrently
    multiprocessing_flag = True

    if multiprocessing_flag:
        # create a thread for each system
        lst_p = [Process(target=automate_simple_z_plots,
                         args=(name,)
                         ) for name in systems.name_lst
                 ]

        # start the threads
        for p in lst_p:
            p.start()

        # wait until they are all finished
        for p in lst_p:
            p.join()

    else:
        # Sequential, comment out lines if you only need to run for individual models
        automate_simple_z_plots("superimposed")
        automate_simple_z_plots("displaced")
        automate_simple_z_plots("elevated")
        automate_simple_z_plots("jahnteller")

    print("Done plotting")
