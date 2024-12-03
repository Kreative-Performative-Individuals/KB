from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import kb_interface as kbi

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    kbi.start()

class KPIData(BaseModel):
    superclass: str
    label: str
    description: str
    unit_of_measure: str
    parsable_computation_formula: str
    human_readable_formula: Optional[str] = None  # Optional field, can be None
    depends_on_machine: bool = False  # Default value set to False
    depends_on_operation: bool = False  # Default value set to False

@app.get("/")
def root():
    return {"message": "knowledge base"}

@app.get("/get_formulas/")
def get_formulas(kpi_label: str = None):
    try:
        result = kbi.get_formulas(kpi_label)

        if kpi_label:
            return result

        return result

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_all_formulas/")
def get_all_formulas():
    try:
        result = []
        for lab in kbi.ONTO.search(label='kpi')[0].instances():
            ret = kbi.get_formulas(lab.label[0][:])
            result.append(ret)
        
        return {"formulas": result}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_kpi/")
def add_kpi(kpi: KPIData):
    try:
        kbi.add_kpi(kpi.superclass, kpi.label, kpi.description, kpi.unit_of_measure, 
                    kpi.parsable_computation_formula, kpi.human_readable_formula, 
                    kpi.depends_on_machine, kpi.depends_on_operation)
        return {"message": "kpi added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_onto_path/")
def get_onto_path():
    path = kbi.get_onto_path()
    return {"ontology_path": str(path)}

@app.get("/api/kpi-formulas")
async def get_kpi_formulas(
    kpi: str = Query(..., description="The label of the KPI to retrieve formulas for"),
    method: Optional[str] = Query("levenshtein", description="The similarity method to use")
):
    """
    Endpoint to find formulas associated with a KPI or the closest matching KPI.

    Parameters:
    - kpi (str): The label of the KPI to search for.
    - method (str, optional): The similarity method to use (default is 'levenshtein').

    Returns:
    - JSON containing:
      - formulas (dict): The formulas of the found KPI.
      - similarity (float): The similarity score.
    """
    try:
        formulas, similarity = kbi.get_closest_kpi_formulas(kpi, method)
        if not formulas:
            raise HTTPException(status_code=404, detail="No matching KPI formulas found.")
        return {"formulas": formulas, "similarity": similarity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/class-instances")
async def get_class_instances(
    owl_class_label: str = Query(..., description="The label of the OWL class or instance to search for"),
    method: Optional[str] = Query("levenshtein", description="The similarity method to use for comparison")
):
    """
    Endpoint to find instances of the closest matching class or individual based on label similarity.

    Parameters:
    - owl_class_label (str): The label of the class or individual to search for.
    - method (str, optional): The similarity method (default is 'levenshtein').

    Returns:
    - JSON containing:
      - instances (list): Instances of the closest matching class or individual.
      - similarity (float): The similarity score of the closest match.
    """
    try:
        instances, similarity = kbi.get_closest_class_instances(owl_class_label, method)
        if not instances:
            raise HTTPException(status_code=404, detail="No matching class or individual instances found.")
        return {"instances": instances, "similarity": similarity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status":"ok"}
