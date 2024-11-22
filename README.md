# Repository of Topic 1 - KB and KPI Ontology

Version: 1.1.9

Authors: Giacomo Aru (KB Design, KB Implementation) Simone Marzeddu (KB Design, KPI Selection, KB Population, Documentation)

## Description

This repository contains the code developed for Topic 1 and the ontology in OWL format.
The code is used to query the Knowledge Base (KB) to retrieve specific information and to add or modify individuals in the KB.

At present, KPIs (pure and derived) have been defined and will be included in the Knowledge Base by the final version of the product. The list of these KPIs is available  [here](https://docs.google.com/document/d/1RMJVM6Xd4dcazlPhCdCzNqwm6lIBSvDHMgVil6wiLNI/edit?tab=t.0#heading=h.equ5lulcmq18)

Please note that the current Knowledge Base prototype currently only supports the following KPIs:

* Pure KPIs:
  * Machine Usage KPIs -> Utilization KPIs -> `time_sum`, `time_avg`, `time_min`, `time_max`
  * Energy KPIs -> Consumption KPIs -> `consumption_sum`, `consumption_avg`, `consumption_min`, `consumption_max`, `power_sum`
  * Production KPIs -> Cycles KPIs -> `cycles_sum`, `cycles_avg`, `cycles_min`, `cycles_max`, `average_cycle_time_avg`
  * Production KPIs -> Efficiency KPIs -> `good_cycles_sum`, `good_cycles_avg`, `good_cycles_min`, `good_cycles_max`, `bad_cycles_sum`, `bad_cycles_avg`, `bad_cycles_min`, `bad_cycles_max`
  * Financial KPIs -> Cost KPIs -> `cost_sum`

 
* Derived KPIs:
  * Machine Usage KPIs -> Downtime KPIs -> `non_operative_time`
  * Energy KPIs -> Consumption KPIs -> `power_cumulative`, `power_mean`
  * Production KPIs -> Efficiency KPIs -> `success_rate`
  * Financial KPIs -> Cost KPIs -> `cost_per_cycle`

## Methods and Documentation
