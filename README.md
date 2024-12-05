
# API Documentation

**Version:** 1.1.0  
**Last Updated:** 05/12/2024  
**Authors:**  
- Giacomo Aru (KB Design, KB Implementation)  
- Simone Marzeddu (KB Design, KPI Selection, KB Population, Documentation)

## Introduction

This is the documentation for the Python interface implemented by Topic 1 to allow interaction with the Knowledge Base. The code and ontology in OWL format can be found in the GitHub repository at this [link](https://github.com/Kreative-Performative-Individuals/KB). A detailed description of the ontology, including structure and individuals, can be found [here](https://github.com/Kreative-Performative-Individuals/KB/blob/main/docs/Group%20B_Topic%201%20_Deliverable%201_12-11-2024.pdf).

**Note:** The current implementation is a prototype with basic and fundamental functionality to make the implementation usable.

### KPIs

The list of KPIs currently in the ontology is as follows:

#### Pure KPIs
- **Machine Usage KPIs**  
  - Utilization KPIs: `time_sum`, `time_avg`, `time_min`, `time_max`  
- **Energy KPIs**  
  - Consumption KPIs: `consumption_sum`, `consumption_avg`, `consumption_min`, `consumption_max`, `power_avg`, `power_min`, `power_max`  
- **Production KPIs**  
  - Cycles KPIs: `cycles_sum`, `cycles_avg`, `cycles_min`, `cycles_max`, `average_cycle_time_avg`  
  - Efficiency KPIs: `good_cycles_sum`, `good_cycles_avg`, `good_cycles_min`, `good_cycles_max`, `bad_cycles_sum`, `bad_cycles_avg`, `bad_cycles_min`, `bad_cycles_max`  
- **Financial KPIs**  
  - Cost KPIs: `cost_sum`, `cost_avg`, `cost_min`, `cost_max`  

#### Derived KPIs
- **Machine Usage KPIs**  
  - Utilization KPIs: `utilization_rate`, `availability`  
  - Downtime KPIs: `non_operative_time`, `mean_time_between_failures`  
- **Energy KPIs**  
  - Consumption KPIs: `power_cumulative`, `power_mean`, `energy_efficiency`, `total_consumption`, `operative_consumption`  
  - Sustainability KPIs: `total_carbon_footprint`, `carbon_footprint_per_cycle`  
- **Production KPIs**  
  - Efficiency KPIs: `success_rate`, `failure_rate`, `overall_equipment_effectiveness`  
- **Financial KPIs**  
  - Cost KPIs: `cost_per_cycle`, `total_energy_cost`  

## Methods and Documentation

### `start(backup_number=1)`
**Description:** Initializes the global ontology and related variables.  
**Parameters:**  
- `backup_number` (optional, int): Indicates which backup file to load. Defaults to the latest backup.  

**Global Variables Modified:**  
- `SAVE_INT`, `ONTO`, `PARSABLE_FORMULA`, `HUMAN_READABLE_FORMULA`, `UNIT_OF_MEASURE`, `DEPENDS_ON`, `OPERATION_CASS`, `MACHINE_CASS`, `KPI_CLASS`  

**Examples:**  
```python
>>> start(1)
Ontology successfully initialized!
```

---

### `get_formulas(kpi)`
**Description:** Retrieves and expands formulas associated with a given KPI.  
**Parameters:**  
- `kpi` (str): The label of the KPI.  

**Returns:**  
- `kpi_formula` (dict): A dictionary mapping KPI labels to their formulas.  

**Examples:**  
```python
>>> get_formulas('total_carbon_footprint')
{'total_carbon_footprint': 'A°sum°mo[S°*[ R°total_consumption°T°m°o° ; C°400°]]',
 'total_consumption': 'S°+[ R°consumption_sum°T°M°idle° ; R°consumption_sum°T°M°offline° ; R°consumption_sum°T°M°working° ]',
 'consumption_sum': 'A°sum°mo[ A°sum°t[ D°consumption_sum°t°m°o° ] ]'}
```

---

### `get_closest_kpi_formulas(kpi, method='levenshtein')`
**Description:** Finds formulas for a KPI or the closest matching KPI.  
**Parameters:**  
- `kpi` (str): The KPI label.  
- `method` (str): Similarity metric (default is 'levenshtein').  

**Returns:**  
- `formulas` (dict): Dictionary of formulas for the closest match.  
- `similarity` (float): Similarity score.  

**Examples:**  
```python
>>> get_closest_kpi_formulas('wrong_kpi')
({'operative_consumption': '...', 'consumption_sum': '...'}, 0.238)
```

---

### `get_instances(owl_class_label)`
**Description:** Retrieves all instances of a given OWL class.  
**Parameters:**  
- `owl_class_label` (str): The label of the OWL class.  

**Returns:**  
- `list`: Labels of all matching instances.  

**Examples:**  
```python
>>> get_instances('energy_kpi')
['power_max', 'total_consumption', 'carbon_footprint_per_cycle']
```

---

### `get_closest_class_instances(owl_class_label, method='levenshtein')`
**Description:** Finds instances of the closest matching class.  
**Parameters:**  
- `owl_class_label` (str): The class label.  
- `method` (str): Similarity metric (default is 'levenshtein').  

**Returns:**  
- `list`: Instances of the closest match.  
- `float`: Similarity score.  

**Examples:**  
```python
>>> get_closest_class_instances('wrong_class')
(['good_cycles_sum'], 0.333)
```

---

### `get_object_properties(owl_label)`
**Description:** Retrieves all properties associated with an ontology entity.  
**Parameters:**  
- `owl_label` (str): The label of the ontology element.  

**Returns:**  
- `dict`: Information including properties, superclasses, and subclasses.  

**Examples:**  
```python
>>> get_object_properties('energy_kpi')
{'label': 'energy_kpi', 'description': '...', 'superclasses': ['kpi'], ...}
```

---

### `add_kpi(...)`
**Description:** Adds a new KPI to the ontology.  
**Parameters:**  
- `superclass` (str): The KPI's superclass.  
- `label` (str): Unique KPI label.  
- Additional attributes such as `description`, `unit_of_measure`, and formulas.  

**Examples:**  
```python
>>> add_kpi('utilization_kpi', 'availability', '...', '%', '...', True, True)
KPI availability successfully added!
```

---
