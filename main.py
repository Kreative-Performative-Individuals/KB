from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import kb_interface as kbi

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Inizializza l'ontologia all'avvio dell'app
    kbi.start()

class KPIModel(BaseModel):
    superclass: str
    label: str
    description: str
    unit_of_measure: str
    parsable_computation_formula: str
    human_readable_formula: Optional[str] = None
    depends_on_machine: Optional[bool] = False
    depends_on_operation: Optional[bool] = False

@app.get("/get_formulas/{kpi_label}")
def get_formulas(kpi_label: str):
    try:
        formulas, kpi_labels, kpi_names = kbi.get_formulas(kpi_label)
        return {"formulas": formulas, "kpi_labels": kpi_labels, "kpi_names": kpi_names}
    except exception as e:
        raise httpexception(status_code=404, detail=str(e))

@app.get("/")
def get_formulas():
    return {"message": "knowledge base"}

@app.post("/add_kpi/")
def add_kpi(kpi: KPIModel):
    try:
        kbi.add_kpi(kpi.superclass, kpi.label, kpi.description, kpi.unit_of_measure, 
                    kpi.parsable_computation_formula, kpi.human_readable_formula, 
                    kpi.depends_on_machine, kpi.depends_on_operation)
        return {"message": "KPI added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_onto_path/")
def get_onto_path():
    path = kbi.get_onto_path()
    return {"ontology_path": str(path)}
