from fastapi import FastAPI, HTTPException
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
def get_formulas():
    return {"message": "knowledge base"}

@app.get("/get_formulas/{kpi_label}")
def get_formulas(kpi_label: str):
    try:
        formulas, kpi_labels, kpi_names = kbi.get_formulas(kpi_label)
        return {"formulas": formulas, "kpi_labels": kpi_labels, "kpi_names": kpi_names}
    except exception as e:
        raise httpexception(status_code=404, detail=str(e))

@app.get("/get_all_formulas/")
def get_all_formulas():
    try:
        result = []
        for lab in kbi.ONTO.search(label='kpi')[0].instances():
            ret = kbi.get_formulas(lab.label[0][:])
            result.append([lab.label[0][:], ret])
        
        return {"result": result}
    except:
        raise httpexception(status_code=500, detail=str(e))

@app.get("/get_formulas/{kpi_label}")
def get_formulas(kpi_label: str):
    try:
        formulas, kpi_labels, kpi_names = kbi.get_formulas(kpi_label)
        return {"formulas": formulas, "kpi_labels": kpi_labels, "kpi_names": kpi_names}
    except exception as e:
        raise httpexception(status_code=404, detail=str(e))

@app.post("/add_kpi/")
def add_kpi(kpi: KPIData):
    try:
        kbi.add_kpi(kpi.superclass, kpi.label, kpi.description, kpi.unit_of_measure, 
                    kpi.parsable_computation_formula, kpi.human_readable_formula, 
                    kpi.depends_on_machine, kpi.depends_on_operation)
        return {"message": "kpi added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_onto_path/")
def get_onto_path():
    path = kbi.get_onto_path()
    return {"ontology_path": str(path)}
