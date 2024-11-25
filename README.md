# Repository of Topic 1 - KB and KPI Ontology

Version: 1.0.1

Last Update: 24/11/2024

Authors: Giacomo Aru (KB Design, KB Implementation), Simone Marzeddu (KB Design, KPI Selection, KB Population, Documentation)

## Description

This repository contains the code developed for Topic 1 and the ontology in OWL format.
The code is used to query the Knowledge Base (KB) to retrieve specific information and to add or modify individuals in the KB.

At present, KPIs (pure and derived) have been defined and will be included in the Knowledge Base by the final version of the product. The list of these KPIs is available  [here](https://docs.google.com/document/d/1RMJVM6Xd4dcazlPhCdCzNqwm6lIBSvDHMgVil6wiLNI/edit?tab=t.0#heading=h.equ5lulcmq18)

Please note that the current Knowledge Base prototype currently only supports the following KPIs:

* <strong>Pure KPIs</strong>:
  * Machine Usage KPIs -> Utilization KPIs -> `time_sum`, `time_avg`, `time_min`, `time_max`
  * Energy KPIs -> Consumption KPIs -> `consumption_sum`, `consumption_avg`, `consumption_min`, `consumption_max`, `power_sum`
  * Production KPIs -> Cycles KPIs -> `cycles_sum`, `cycles_avg`, `cycles_min`, `cycles_max`, `average_cycle_time_avg`
  * Production KPIs -> Efficiency KPIs -> `good_cycles_sum`, `good_cycles_avg`, `good_cycles_min`, `good_cycles_max`, `bad_cycles_sum`, `bad_cycles_avg`, `bad_cycles_min`, `bad_cycles_max`
  * Financial KPIs -> Cost KPIs -> `cost_sum`

 
* <strong>Derived KPIs</strong>:
  * Machine Usage KPIs -> Downtime KPIs -> `non_operative_time`
  * Energy KPIs -> Consumption KPIs -> `power_cumulative`, `power_mean`
  * Production KPIs -> Efficiency KPIs -> `success_rate`
  * Financial KPIs -> Cost KPIs -> `cost_per_cycle`

## Methods and Documentation
The Phyton implementation offers a library of methods for interaction with the Knowledge Base, with additional methods for other relevant operations. Documentation of the methods offered follows:

* <strong>"start"</strong>:
  * Description: Initializes the global ontology and related variables.
    This function reads a configuration file to determine the most recent ontology backup, 
    loads the corresponding ontology file, and extracts key elements for computation and reasoning.
   
  * Global Variables Modified:
    * `SAVE_INT` (int): The save interval read from the configuration file.
    * `ONTO` (Ontology): The ontology object loaded from the specified backup file.
    * `PARSABLE_FORMULA` (OntologyClass): The ontology class representing parsable computation formulas.
    * `HUMAN_READABLE_FORMULA` (OntologyClass): The ontology class for human-readable formulas.
    * `UNIT_OF_MEASURE` (OntologyClass): The ontology class defining units of measurement.
    * `DEPENDS_ON` (OntologyClass): The ontology class describing dependencies between entities.
    * `OPERATION_CASS` (OntologyClass): The ontology class representing operations.
    * `MACHINE_CASS` (OntologyClass): The ontology class representing machines.
    * `KPI_CLASS` (OntologyClass): The ontology class representing Key Performance Indicators (KPIs).
  * Output:
      * `None`
      
 * <strong>"get_formulas"</strong>:
   * Description: This function retrieves and unrolls formulas associated with a given KPI label.
     It recursively searches for nested KPIs in the formulas and expands them until
     all formulas are fully unrolled
   * Input Parameters: 
      * `kpi` (str): The label of the KPI whose formula is to be retrieved and unrolled.
      * `onto` (Ontology): An ontology object used to search for KPI entities based on their label.
   * Output:
      * `f_list` (list): A list of all formulas found during the unrolling process, including nested ones.
      * `kpi_label_list` (list): A list of the original KPI labels (input `kpi` and any nested ones found).
      * `kpi_list` (list): A list of KPI names corresponding to the formulas in `f_list`.
        
 * <strong>"add_kpi"</strong>:
     * Description: Adds a new KPI (Key Performance Indicator) to the ontology if it meets the specified criteria.
       The function ensures that the KPI label does not already exist, validates the superclass, and 
       associates formulas and dependencies with the new KPI.
     * Input Parameters:
        * `superclass` (str): The label of the superclass to which this KPI belongs.
        * `label` (str): The unique label for the new KPI.
        * `description` (str): A descriptive text explaining the KPI.
        * `unit_of_measure` (str): The unit in which this KPI is measured.
        * `parsable_computation_formula` (str): A machine-parsable formula for computing the KPI.
        * `human_readable_formula` (str, optional): A human-readable formula for computing the KPI. Defaults to `parsable_computation_formula` if not provided.
        * `depends_on_machine` (bool, optional): Indicates if the KPI depends on the machine. Defaults to False.
        * `depends_on_operation` (bool, optional): Indicates if the KPI depends on the operation. Defaults to False.
      * Output:
        * `None`: Prints error messages or completes the KPI creation process.
      * Side Effects:
        * Modifies the ontology to add the new KPI.
        * Updates global mappings (e.g., HUMAN_READABLE_FORMULA, PARSABLE_FORMULA).

 * <strong>"get_onto_path"</strong>:
      * Description: Constructs and returns the file path to the last ontology backup file.
      * Output:
        * `pathlib.Path`: The full file path to the ontology file, as a `Path` object.

