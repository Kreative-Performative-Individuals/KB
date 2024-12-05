# Repository of Topic 1 - KB and KPI Ontology

Version: 1.1.0

Last Update: 05/12/2024

Authors: Giacomo Aru (KB Design, KB Implementation), Simone Marzeddu (KB Design, KPI Selection, KB Population, Documentation)

## Introduction

This is the documentation for the Python interface implemented by Topic 1 to allow interaction with the Knowledge Base.  
The code and ontology in owl format can be found in the GitHub repository at this [link](https://github.com/Kreative-Performative-Individuals/KB).  
A detailed description of the ontology including structure and individuals present, on the other hand, can be found at this [link](https://github.com/Kreative-Performative-Individuals/KB/blob/main/docs/Group%20B_Topic%201%20_Deliverable%201_12-11-2024.pdf).

Please note that the current implementation is only a prototype with basic and fundamental functionality to make the implementation usable.

Below we have the list of KPIs currently in the ontology with a reference to the taxonomic structure:

- **Pure KPIs**:
  - Machine Usage KPIs -> Utilization KPIs -> `time_sum`, `time_avg`, `time_min`, `time_max`
  - Energy KPIs -> Consumption KPIs -> `consumption_sum`, `consumption_avg`, `consumption_min`, `consumption_max`, `power_avg`, `power_min`, `power_max`
  - Production KPIs -> Cycles KPIs -> `cycles_sum`, `cycles_avg`, `cycles_min`, `cycles_max`, `average_cycle_time_avg`
  - Production KPIs -> Efficiency KPIs -> `good_cycles_sum`, `good_cycles_avg`, `good_cycles_min`, `good_cycles_max`, `bad_cycles_sum`, `bad_cycles_avg`, `bad_cycles_min`, `bad_cycles_max`
  - Financial KPIs -> Cost KPIs -> `cost_sum`, `cost_avg`, `cost_min`, `cost_max`

- **Derived KPIs**:
  - Machine Usage KPIs -> Utilization KPIs -> `utilization_rate`, `availability`
  - Machine Usage KPIs -> Downtime KPIs -> `non_operative_time`, `mean_time_between_failures`
  - Energy KPIs -> Consumption KPIs -> `power_cumulative`, `power_mean`, `energy_efficiency`, `total_consumption`, `operative_consumption`
  - Energy KPIs -> Sustainability KPIs -> `total_carbon_footprint`, `carbon_footprint_per_cycle`
  - Production KPIs -> Efficiency KPIs -> `success_rate`, `failure_rate`, `overall_equipment_effectiveness`
  - Financial KPIs -> Cost KPIs -> `cost_per_cycle`, `total_energy_cost`

## Methods and Documentation

### `start(backup_number=1)`

**Description:**  
Initializes the global ontology and related variables. This function must necessarily be called every time it is desired to initialize the KB and use other methods to interact.

**Parameters:**
- `backup_number` (optional, int): The number indicating which backup file to load, inside the backup folder. If not specified, it reads the configuration file to determine the latest backup.

**Global Variables Modified:**
- `SAVE_INT`: Save interval value read or set.
- `ONTO`: The ontology object loaded from the backup.
- `PARSABLE_FORMULA`, `HUMAN_READABLE_FORMULA`, `UNIT_OF_MEASURE`, `DEPENDS_ON`, `OPERATION_CASS`, `MACHINE_CASS`, `KPI_CLASS`: Specific ontology classes extracted.

### Notes
If `backup_number` is not provided, the function will automatically determine the latest backup from the configuration file. Ensure that the backup folder is properly structured and contains valid backup files, and also that the configuration file exists and contains only a numeric value, to avoid errors during initialization.

### Examples
```
>>> start(1)
Ontology successfully initialized!
```


### `get_formulas(kpi)`

**Description:**  
Retrieves and expands formulas associated with a given KPI. This function identifies the formula for a KPI and recursively unrolls any nested KPIs referenced within the formula until all dependencies are fully resolved.

**Parameters:**
- `kpi` (str): The label of the KPI whose formulas need to be expanded.

**Returns:**
- `kpi_formula` (dict): A dictionary mapping KPI labels to their formulas.

### Notes
This function works recursively to resolve all nested KPI references in the formula. It ensures that all dependencies are properly expanded before returning the final formula. If it receives a non-existent label, it returns `None`.

### Examples
```
>>> get_formulas('total_carbon_footprint')
{'total_carbon_footprint': 'A°sum°mo[S°*[ R°total_consumption°T°m°o° ; C°400°]]',
 'total_consumption': 'S°+[ R°consumption_sum°T°M°idle° ; R°consumption_sum°T°M°offline° ; R°consumption_sum°T°M°working° ]',
 'consumption_sum': 'A°sum°mo[ A°sum°t[ D°consumption_sum°t°m°o° ] ]'}

>>> get_formulas('wrong_kpi')
DOUBLE OR NONE REFERENCED KPI
```


### `get_closest_kpi_formulas(kpi, method='levenshtein')`

**Description:**  
Finds the formulas associated with a KPI or the closest matching KPI. If no formula is found for the given KPI, this function calculates similarity scores between the KPI and other ontology entities, returning formulas for the closest match.

**Parameters:**
- `kpi` (str): The label of the KPI to search for.
- `method` (str, optional): The similarity metric to use (default is 'levenshtein').

**Returns:**
- `formulas` (dict): A dictionary mapping KPI labels to their formulas.
- `similarity` (float): The similarity score (1 for exact matches).

### Notes
If no exact match is found for the given KPI, the function will calculate the similarity to other KPIs using the specified method, such as Levenshtein distance, and return the formulas associated with the closest match.  
Currently, only the Levenshtein distance has been implemented, and changing the method will generate an error.

### Examples
```
>>> get_closest_kpi_formulas('total_carbon_footprint')
({'total_carbon_footprint': 'A°sum°mo[S°*[ R°total_consumption°T°m°o° ; C°400°]]',
  'total_consumption': 'S°+[ R°consumption_sum°T°M°idle° ; R°consumption_sum°T°M°offline° ; R°consumption_sum°T°M°working° ]',
  'consumption_sum': 'A°sum°mo[ A°sum°t[ D°consumption_sum°t°m°o° ] ]'},
 1)

>>> get_closest_kpi_formulas('wrong_kpi')
({'operative_consumption': 'S°+[ R°consumption_sum°T°M°idle° ; R°consumption_sum°T°M°working° ]',
  'consumption_sum': 'A°sum°mo[ A°sum°t[ D°consumption_sum°t°m°o° ] ]'},
 0.23809523809523814)
```


### `get_instances(owl_class_label)`

**Description:**  
Retrieves all instances of a given OWL class. If the input label corresponds to a class, instances of the class and its subclasses are returned. If the label corresponds to an individual, it is directly returned.

**Parameters:**
- `owl_class_label` (str): The label of the OWL class or instance to search for.

**Returns:**
- `list`: Labels of all matching instances, or an empty list if none are found.

### Notes
This function was designed to allow not only the expansion of a class into all its individuals, thus giving the possibility of referring to sets of individuals with aggregating terms, but also to disambiguate situations in which it is not known whether a label belongs to an individual or a class.

### Examples
```
>>> get_instances('metal_cutting_machine')
['large_capacity_cutting_machine_2',
 'large_capacity_cutting_machine_1',
 'medium_capacity_cutting_machine_3',
 'medium_capacity_cutting_machine_2',
 'low_capacity_cutting_machine_1',
 'medium_capacity_cutting_machine_1']

>>> get_instances('energy_kpi')
['power_max',
 'power_avg',
 'total_consumption',
 'carbon_footprint_per_cycle',
 'consumption_avg',
 'power_cumulative',
 'total_carbon_footprint',
 'power_min',
 'operative_consumption',
 'consumption_min',
 'consumption_sum',
 'energy_efficiency',
 'consumption_max']

>>> get_instances('wrong_class')
DOUBLE OR NONE REFERENCED KPI
```
