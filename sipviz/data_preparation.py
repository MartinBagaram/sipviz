import xmltodict
import os
import numpy as np
import pandas as pd

#FOLDER = os.path.dirname(__file__)

class ResultsData:
    """ Creates and prepare the data needed for the visualization of scenarios
        in all iterations. And the final results after all the iterations are complete.
        By default, the class uses data stored in a folder named as <code> sample_data/</code>
        Files of the solutions during iterations should be named following the convention:
        <code> solution_[iteration]_[scenario].sol</code>. The extension of the files are the 
        default xml extentions of solutions files from <b> cplex</b> <br>
        The filal result shoub be named with the name starting with the word <i>final</i>
    """
    def __init__(self, data_folder):
        FOLDER = os.getcwd() # os.path.join(FOLDER, os.pardir())
        self.FOLDER_DATA = os.path.join(FOLDER, data_folder)
        self.stands, self.stages = self._get_number_of_stands_and_stages()
    
    def _get_number_of_stands_and_stages(self):
        """ Returns the number of stands on which the optimization is run and the number of stages.
            One must notice the difference between the number of stages and the number of periods.
            We consider here the <i> do-nothing</i> as a stage (<b> Stage 0</b>)

        """
        periods = 0
        stands = 0
        for file in os.listdir(self.FOLDER_DATA):
            if file.startswith('solution'):
                with open(os.path.join(self.FOLDER_DATA, file)) as fd:
                    sol = xmltodict.parse(fd.read())
                var_sol = sol['CPLEXSolution']['variables']['variable']
                for i in range(len(var_sol)):
                    one_sol = var_sol[i]
                    x = one_sol['@name']
                    if x.startswith('X') or x.startswith('x'):
                        _,s,p = x.split('_')
                        s = int(s)
                        p = int(p)
                        periods = max(periods, p)
                        stands = max(stands, s)
                break
        return stands, periods+1

    def _results_of_one_scenario(self, filename):
        """ Returns the solution of actions to do for a single scenario
        """
        with open(os.path.join(self.FOLDER_DATA, filename)) as fd:
            sol = xmltodict.parse(fd.read())
        var_sol = sol['CPLEXSolution']['variables']['variable']
        results = np.zeros(self.stands, dtype=int)
        for i in range(len(var_sol)):
            one_sol = var_sol[i]
            x = one_sol['@name']
            if x.startswith('X') or x.startswith('x'):
                _,s,p = x.split('_')
                s = int(s) - 1
                p = int(p)
                if int(float(one_sol['@value'])) == 1: # stand to harvest in period p
                    results[s] = p
        return results

    def process_solutions_to_dictionary(self):
        """ Computes all solutions for all iteration before the final solution from the reduced MIP

            Returns
            --------------------
            dictionary_all_soluions: dict dictionary of iteration, scenario, solution for each stand
        """
        dict_all_data = dict()
        for file in os.listdir(self.FOLDER_DATA):
            if file.startswith('sol'):
                _,it,scen_ext = file.split('_')
                scen, _ = scen_ext.split('.')
                if int(it) not in dict_all_data:
                    dict_all_data[int(it)] = {}
                dict_all_data[int(it)][int(scen)] = self._results_of_one_scenario(file)
        return dict_all_data

    def get_final_result_data(self):
        """ Computes the final solution from the progressive hedging variable
            fixing algorithm. It gives the solution for all the sceanrios and the 
            expected volume harvested in each period for each scenario. The only thing hard wired 
            is the name of the file containing the final solution. It should be named <strong>final.sol</strong>
            
            Parameters
            ---------------
            #n_stands: int number of stands that the problem is run on
            #n_periods: int number of periods in which there is expected to have harverst
            
            Note that both variables can be computed by a private function included in this software
            
            Returns
            ---------------
            final_sol_dict: dictionary of scenarios as keys and a list of stands as value where the period at which
                            the stand is harvested is used in place of the stand id. The index of the list is used 
                            as the id of the stand
            volumes_dict: dictionary of scenarios as keys and the list of periods as values. The index of the list is 
                            as the period - 1 in which the volume is harversted. The value in the list is the actual 
                            volumes
        """
        with open(os.path.join(self.FOLDER_DATA, 'final.sol')) as fd:
                    final = xmltodict.parse(fd.read())
        solutions = final['CPLEXSolution']['variables']['variable']
        final_sol_dict = {}
        volumes_dict = {}
        n_periods = self.stages - 1
        for i in range(len(solutions)):
            one_sol_row = solutions[i]
            one_sol = one_sol_row['@name']
            if one_sol.startswith('x') or one_sol.startswith('X'):
                _,s,w,p = one_sol.split('_')
                w = int(w); s = int(s); p = int(p)
                if int(float(one_sol_row['@value'])) == 1:
                    if w not in final_sol_dict: # create the scenario if not exist
                        final_sol_dict[w] = np.zeros(self.stands, dtype=int)
                    final_sol_dict[w][s - 1] = p
            elif one_sol.startswith('s') or one_sol.startswith('S'):
                _,w,p = one_sol.split('_')
                w = int(w); p = int(p)
                if w not in volumes_dict:
                    volumes_dict[w] = np.zeros(n_periods, dtype=float)
                volumes_dict[w][p - 1] = float(one_sol_row['@value'])
        return final_sol_dict, volumes_dict