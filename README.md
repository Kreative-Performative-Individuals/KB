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


### `get_closest_class_instances(owl_class_label, method='levenshtein')`

**Description:**  
Retrieves all instances of a given OWL class or individual. If no exact match is found, the function searches for the most similar element in the knowledge base using a similarity method.

**Parameters:**
- `owl_class_label` (str): The label of the class or individual to search for.
- `method` (str): The similarity method (default is 'levenshtein').

**Returns:**
- `list`: Instances of the closest matching class or individual.
- `float`: The similarity score of the closest match.

### Notes
If an exact match for the provided label is not found, this function calculates the similarity between the label and other elements in the knowledge base using the specified method, and returns the correct answer with respect to the entity found.  
Currently only the Levenshtein distance has been implemented, and changing the method will generate an error.

### Examples
```
>>> get_closest_class_instances('testing_machine')
(['testing_machine_3', 'testing_machine_1', 'testing_machine_2'], 1)

>>> get_closest_class_instances('generic_operation')
(['offline', 'working', 'idle', 'independent'], 1)

>>> get_closest_class_instances('wrong_class')
(['good_cycles_sum'], 0.33333333333333337)
```
---


### `get_object_properties(owl_label)`

**Description:**  
Retrieves all the properties (annotation, object, and data properties) associated with an ontology entity based on its label. It also returns information about superclasses, subclasses, and instances if the element is a class or individual, as well as the entity type.

**Parameters:**
- `owl_label` (str): The label of the ontology element (class or individual) whose properties are to be retrieved.

**Returns:**
- `dict`: A dictionary containing the information associated with the entity, including:
  - `label`: The label of the element.
  - `description`: The description annotation property, if available.
  - `depends_on_other_kpi`: A list of KPI labels the element depends on based on the parsable computational formula.
  - `superclasses`: List of superclasses of the element (for classes and individuals).
  - `subclasses`: List of subclasses of the element (for classes).
  - `instances`: List of instances of the element (for classes).
  - `entity_type`: The nature of the referred entity, which can be class, instance, or property.
  - `ontology_property_name`: List of every entity related to the referenced entity with the 'ontology_property_name' property.

### Notes
This function retrieves various properties of an ontology element, such as its description, dependencies, and hierarchical relationships, including its superclasses, subclasses, instances, and entity type. For each property (annotation, object, and datatype), the dictionary contains an element that has as its key the label of the property and as its value the list of values or entities associated through the property itself.

### Examples
```
>>> get_object_properties('depends_on')
{'label': 'depends_on',
 'description': 'This object property defines a dependency relationship between a Key Performance Indicator (KPI) and other entities such as machines or operations. It specifies the contextual elements required for calculating or interpreting a KPI. The domain of this property is KPI, and its range includes classes like Machine and Operation. A KPI may have multiple dependsOn relationships, or none, if it is independent of specific contexts.',
 'entity_type': 'property'}

>>> get_object_properties('working')
{'label': 'working',
 'description': 'The machine is fully operational and actively performing its designated tasks or functions.',
 'superclasses': ['generic_operation'],
 'entity_type': 'instance'}

>>> get_object_properties('energy_kpi')
{'label': 'energy_kpi',
 'description': 'Energy KPIs are metrics used to assess and optimize an organization’s energy consumption, efficiency, and sustainability. These indicators help companies monitor their energy usage, identify areas to reduce waste, lower costs, and minimize their environmental impact.',
 'superclasses': ['kpi'],
 'subclasses': ['energy_efficiency_kpi', 'sustainability_kpi', 'consumption_kpi'],
 'instances': ['power_max', 'power_avg', 'total_consumption', 'carbon_footprint_per_cycle', 'consumption_avg', 'power_cumulative', 'total_carbon_footprint', 'power_min', 'operative_consumption', 'consumption_min', 'consumption_sum', 'energy_efficiency', 'consumption_max'],
 'entity_type': 'class'}

>>> get_object_properties('wrong_label')
DOUBLE OR NONE REFERENCED KPI
```
---


### `get_closest_object_properties(owl_label, method='levenshtein')`

**Description:**  
Apply `get_object_properties` to the entity whose label is the closest match to the given label. The closeness is determined by a similarity measure (default is Levenshtein distance).

**Parameters:**
- `owl_label` (str): The label of the ontology element whose closest match is to be found.
- `method` (str): The similarity measure to use for finding the closest match (default: 'levenshtein').

**Returns:**
- `tuple`: A tuple containing:
  - `dict`: The properties of the closest matching element.
  - `float`: The similarity score (between 0 and 1) of the closest match.

### Notes
If no exact match for the given label is found, the function uses the specified similarity measure (e.g., Levenshtein distance) to find the closest match in the ontology and returns its properties along with the similarity score.  
Currently, only the Levenshtein distance has been implemented and changing the method will generate an error.

### Examples
```
>>> get_closest_object_properties('total_carbon_footprint')
({'label': 'total_carbon_footprint',
  'description': 'This KPI is a sustainability metric that measures the amount of CO2 emissions produced globally for a process, machine, or system. It provides insights into the environmental impact, enabling organizations to track and reduce their carbon emissions.',
  'unit_of_measure': 'CO2 Emissions',
  'human_readable_formula': 'sum_M_O(total_consumption(T,m,o)*estimated_italian_emission_factor(400))',
  'depends_on': ['operation', 'machine'],
  'parsable_computation_formula': 'A°sum°mo[S°*[ R°total_consumption°T°m°o° ; C°400°]]',
  'depends_on_other_kpi': ['total_consumption'],
  'superclasses': ['sustainability_kpi'],
  'entity_type': 'instance'},
 1)

>>> get_closest_object_properties('wrong_label')
({'label': 'testing_machine_2',
  'location': 'floor_2',
  'database_id': 'ast-pu7dfrxjf2ms',
  'superclasses': ['testing_machine'],
  'entity_type': 'instance'},
 0.2941176470588235)
```
---


### `add_kpi(superclass, label, description, unit_of_measure, parsable_computation_formula, human_readable_formula=None, depends_on_machine=False, depends_on_operation=False)`

**Description:**  
Adds a new KPI to the ontology. This function validates that the KPI's label and superclass are unique and correctly defined. It then creates the KPI and associates the provided attributes, formulas, and dependencies.

**Parameters:**
- `superclass` (str): The label of the superclass for the KPI.
- `label` (str): The unique label for the KPI.
- `description` (str): A text description of the KPI.
- `unit_of_measure` (str): The measurement unit for the KPI.
- `parsable_computation_formula` (str): A machine-readable formula for the KPI.
- `human_readable_formula` (str, optional): A user-friendly formula (default is the parsable formula).
- `depends_on_machine` (bool, optional): Whether the KPI depends on machines.
- `depends_on_operation` (bool, optional): Whether the KPI depends on operations.

**Returns:**
- `None`: Prints errors or creates the KPI instance.

### Notes
This function ensures that the KPI's label and superclass are unique within the ontology. It will also handle dependencies on machines and operations if specified.

### Examples
```
>>> new_kpi_inputs = ['utilization_kpi', 
                     'availability', 
                     'Percentage of machine uptime in respect to machine downtime over each machine-operation pairs', 
                     '%', 
                     'S°*[ S°/[ A°sum°m[ R°time_sum°T°m°working° ] ; S°+[ A°sum°m[ R°time_sum°T°m°idle° ] ; A°sum°m[ R°time_sum°T°m°offline° ] ] ] ; C°100° ]',
                     '(sum_M( time_sum(T,m,working)) / ( sum_M(time_sum(T,m,Idle)) + sum_M(time_sum(T,m,offline)) ) )*100',
                     True,
                     True]
>>> add_kpi(*new_kpi_inputs)
KPI availability successfully added to the ontology!

>>> add_kpi(*new_kpi_inputs)
KPI availability ALREADY EXISTS
```
