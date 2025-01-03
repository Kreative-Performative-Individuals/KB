import owlready2 as or2  # Library for working with OWL ontologies
import re  # Regular expressions for string pattern matching
import hashlib  # For generating secure hash codes
import base64  # For encoding hash values
import pathlib as pl  # For handling file paths
import math  # Mathematical operations
import os  # Operating system utilities

import Levenshtein  # Library for calculating Levenshtein distance (string similarity)

# === GLOBAL VARIABLES ===
# Directory for ontology backup files
MAIN_DIR = pl.Path('./backups')

# List containing paths to ontology files
ONTO_PATH = ['KB_original']

# Path to the configuration file
CONFIG_PATH = pl.Path('./config.cfg')

# === ONTOLOGY RELATED GLOBAL VARIABLES ===
# These variables store ontology objects or classes extracted during initialization
ONTO = None  # The global ontology object
SAVE_INT = None  # Save interval for backups
PARSABLE_FORMULA = None  # Ontology class for parsable computation formulas
HUMAN_READABLE_FORMULA = None  # Ontology class for human-readable formulas
UNIT_OF_MEASURE = None  # Ontology class for units of measurement
DEPENDS_ON = None  # Ontology class for entity dependencies
OPERATION_CLASS = None  # Ontology class for operations
MACHINE_CASS = None  # Ontology class for machines
KPI_CLASS = None  # Ontology class for Key Performance Indicators (KPIs)

PROCESS_CLASS = None # Ontology class for processes
MACHINE_OPERATION_CLASS = None # Ontology class for couple machine operation
ASSOCIATED_MACHINE = None # Ontology property of machine_operation_class
ASSOCIATED_OPERATION = None # Ontology property of machine_operation_class
PROCESS_STEP_POSITION = None # Ontology property of machine_operation_class
PROCESS_STEP = None # Ontology property of process

# === FUNCTION DEFINITIONS ===

def start(backup_number=1):
    """
    Initialize the Ontology and Global Variables
    -----------------------------
    
    This function loads an ontology from a specified backup number or defaults to the latest save interval.
    It also assigns specific ontology classes and related data structures to global variables, making them available for further processing and operations.

    -----------------------------
    Args:
    -----------------------------
    - backup_number (int, optional): 
        The backup number to load the ontology from. Defaults to 1 if not provided.

    -----------------------------
    Side Effects:
    -----------------------------
    Modifies the following global variables:
        SAVE_INT: The save interval setting.
        ONTO: The main ontology object.
        PARSABLE_FORMULA: The class containing machine-readable formulas for KPIs.
        HUMAN_READABLE_FORMULA: The class containing user-friendly formulas for KPIs.
        UNIT_OF_MEASURE: The class mapping KPIs to their respective units of measure.
        DEPENDS_ON: The class indicating dependencies between KPIs and other entities.
        OPERATION_CLASS: The class representing operations in the ontology.
        MACHINE_CASS: The class representing machines in the ontology.
        KPI_CLASS: The class representing KPIs in the ontology.
        PROCESS_CLASS: The class representing processes in the ontology.
        MACHINE_OPERATION_CLASS: The class representing machine operations in the ontology.
        ASSOCIATED_MACHINE: The class linking machine operations to specific machines.
        ASSOCIATED_OPERATION: The class linking machine operations to specific operations.
        PROCESS_STEP_POSITION: The class mapping process steps to their order in a process.
        PROCESS_STEP: The class mapping processes to their respective steps.

    -----------------------------
    Prints:
    -----------------------------
    "Ontology successfully initialized!" 
        upon successful initialization of the ontology and global variables.
    """


    
    # Declare global variables to ensure they are modified globally
    global SAVE_INT, ONTO, PARSABLE_FORMULA, HUMAN_READABLE_FORMULA
    global UNIT_OF_MEASURE, DEPENDS_ON, OPERATION_CLASS, MACHINE_CASS, KPI_CLASS
    global PROCESS_CLASS, MACHINE_OPERATION_CLASS, ASSOCIATED_MACHINE, ASSOCIATED_OPERATION, PROCESS_STEP_POSITION, PROCESS_STEP
    
    if backup_number:
        # Load ontology with the specified backup number
        ONTO = or2.get_ontology(str(MAIN_DIR / (str(backup_number - 1) + '.owl'))).load()
        SAVE_INT = backup_number
        # Update the configuration file with the new backup number
        with open(CONFIG_PATH, 'w+') as cfg:
            cfg.write(str(backup_number))
    else:
        # Read the latest save interval from the configuration file
        with open(CONFIG_PATH, 'r') as cfg:
            SAVE_INT = int(cfg.read())
        # Load ontology corresponding to the latest save interval
        ONTO = or2.get_ontology(str(MAIN_DIR / (str(SAVE_INT - 1) + '.owl'))).load()

    # Search and assign specific ontology classes by their labels
    PARSABLE_FORMULA = ONTO.search(label='parsable_computation_formula')[0]
    HUMAN_READABLE_FORMULA = ONTO.search(label='human_readable_formula')[0]
    UNIT_OF_MEASURE = ONTO.search(label='unit_of_measure')[0]
    
    DEPENDS_ON = ONTO.search(label='depends_on')[0]
    
    OPERATION_CLASS = ONTO.search(label='operation')[0]
    MACHINE_CASS = ONTO.search(label='machine')[0]
    KPI_CLASS = ONTO.search(label='kpi')[0]
    
    PROCESS_CLASS = ONTO.search(label='process')[0]
    MACHINE_OPERATION_CLASS = ONTO.search(label='machine_operation')[0]
    ASSOCIATED_MACHINE = ONTO.search(label='associated_machine')[0]
    ASSOCIATED_OPERATION = ONTO.search(label='associated_operation')[0]
    PROCESS_STEP_POSITION = ONTO.search(label='process_step_position')[0]
    PROCESS_STEP = ONTO.search(label='process_step')[0]
    
    # Print success message
    print("Ontology successfully initialized!")

def _generate_hash_code(input_data):
    """
    Generate a Truncated, URL-safe Base64 Encoded SHA-256 Hash
    -----------------------------
    
    This function computes the SHA-256 hash of a given input string, encodes it using 
    URL-safe Base64, and truncates the output to 22 characters for brevity.

    -----------------------------
    Args:
    -----------------------------
    - input_data (str): 
        The input string to be hashed.

    -----------------------------
    Returns:
    -----------------------------
    - str: 
        A 22-character truncated, URL-safe Base64 encoded SHA-256 hash of the input string.
    """
    
    # Compute a SHA-256 hash of the input string
    hash_obj = hashlib.sha256(input_data.encode())
    # Convert the hash to a URL-safe Base64 encoded string
    hash_b64 = base64.urlsafe_b64encode(hash_obj.digest()).decode()
    # Clean up unwanted characters ('-' and '_')
    hash_b64_clean = hash_b64.replace('-', '').replace('_', '')
    # Truncate the hash to 22 characters for brevity
    hash_code = hash_b64_clean[:22]
    return hash_code

def _get_similarity(a, b, method='custom'):
    """
    Compute Similarity Between Two Strings
    -----------------------------
    
    This function calculates the similarity between two strings using the specified method. 
    It supports both 'levenshtein' and a custom similarity method that factors in suffixes.

    -----------------------------
    Args:
    -----------------------------
    - a (str): 
        The first string for comparison.
    - b (str): 
        The second string for comparison.
    - method (str, optional): 
        The method to compute similarity. Defaults to 'custom'. Available options are:
        - 'levenshtein': Computes similarity based on Levenshtein distance.
        - 'custom': Separates main parts and suffixes for weighted similarity calculation.

    -----------------------------
    Returns:
    -----------------------------
    - float: 
        A similarity score between 0 and 1. A score of 1 indicates identical strings, 
        while 0 indicates completely dissimilar strings.

    -----------------------------
    Raises:
    -----------------------------
    ValueError: 
    - If an unsupported method is specified.
    """
    
    if method == 'levenshtein':
        # Compute Levenshtein distance
        distance = Levenshtein.distance(a, b)
        # Convert distance to a similarity score
        similarity = 1 - distance / max(len(a), len(b))
        return similarity
    
    elif method == 'custom':
        # Define suffixes to be treated separately
        deleted_suffixes = ['sum', 'min', 'max', 'avg', 'mean', 'tot', 'count', 'var']
        
        # Separate main parts and suffixes
        a_main_part = a
        b_main_part = b
        a_suffix = None
        b_suffix = None
        
        # Check and capture the deleted suffix from both strings
        for suffix in deleted_suffixes:
            if a.endswith(f"_{suffix}"):
                a_suffix = suffix
                a_main_part = a[:-(len(suffix) + 1)]  # Remove the suffix
                break
        for suffix in deleted_suffixes:      
            if b.endswith(f"_{suffix}"):
                b_suffix = suffix
                b_main_part = b[:-(len(suffix) + 1)]  # Remove the suffix
                break
        
        # Remove spaces and underscores from the main part and suffix
        a_main_part = a_main_part.replace("_", "").replace(" ", "")
        b_main_part = b_main_part.replace("_", "").replace(" ", "")
        
        # Handle cases where the main parts are empty
        if not a_main_part or not b_main_part:
            main_similarity = 0  # Treat empty main parts as having no similarity
        else:
            # Compute Levenshtein distance for the main parts (first parts of the strings)
            main_distance = Levenshtein.distance(a_main_part, b_main_part)
            main_similarity = 1 - main_distance / max(len(a_main_part), len(b_main_part))

        # Handle cases where the suffixes are empty
        if not a_suffix and not b_suffix:
            suffix_similarity = 1  # Both strings have no suffix, so they are identical
        elif a_suffix and b_suffix:
            # Compute Levenshtein distance for the suffixes (second parts of the strings)
            suffix_distance = Levenshtein.distance(a_suffix, b_suffix)
            suffix_similarity = 1 - suffix_distance / max(len(a_suffix), len(b_suffix))
        elif b_suffix == 'sum':
            # If only one string has a suffix, we treat it as completely different
            suffix_similarity = 1e-08
        else:
            suffix_similarity = 0
            
        # Assign higher weight to the main part and lower weight to the suffix part
        total_similarity = (0.85 * main_similarity) + (0.15 * suffix_similarity)

        return total_similarity
    
    else:
        # Raise a more specific exception with detailed information
        raise ValueError(f"Unrecognized method '{method}' encountered. Please check the method name or ensure it is properly defined.")


def _backup():
    """
    Create Ontology Backup and Manage Old Backups
    -----------------------------
    
    This function saves the current ontology as a backup file and deletes older backups 
    based on fine-grain and coarse-grain intervals to conserve storage space.

    -----------------------------
    Side Effects:
    -----------------------------
    - Saves the ontology to the `MAIN_DIR` directory in RDF/XML format.
    - Deletes old backup files according to defined intervals.
    - Updates the `SAVE_INT` global variable and writes it to the configuration file.

    -----------------------------
    Global Variables Used:
    -----------------------------
    - SAVE_INT: Determines the naming and management of backups.
    - ONTO: The ontology object being saved.
    """
    global SAVE_INT
    coarse_grain = 100  # Defines the coarse-grain interval
    max_fine_b = 15  # Maximum fine-grain backups to keep
    max_coarse_b = 10  # Maximum coarse-grain backups to keep

    # Save the current ontology
    ONTO.save(file=str(MAIN_DIR / (str(SAVE_INT) + '.owl')), format="rdfxml")

    # Delete old backups based on the fine-grain interval
    if (SAVE_INT - max_fine_b) % coarse_grain == 0:
        # Delete the corresponding coarse-grain backup if it exceeds limits
        if (SAVE_INT - max_fine_b) / coarse_grain - max_coarse_b > 0:
            os.remove(str(MAIN_DIR / (str(SAVE_INT - max_fine_b - max_coarse_b * coarse_grain) + '.owl')))
    else:        
        # Delete excess fine-grain backups
        if SAVE_INT - max_fine_b > 0:
            os.remove(str(MAIN_DIR / (str(SAVE_INT - max_fine_b) + '.owl')))

    # Increment the save interval and update the configuration file
    SAVE_INT += 1
    with open(CONFIG_PATH, 'w+') as cfg:
        cfg.write(str(SAVE_INT))
    
def _extract_label(lab):
    """
    Extract Label from Ontology Entities
    -----------------------------
    
    This helper function retrieves the string label from an ontology entity, 
    handling cases where the label is a list or a direct string.

    -----------------------------
    Args:
    -----------------------------
    - lab (Union[str, list]): 
        The label to extract, which could be a string or a list of strings.

    -----------------------------
    Returns:
    -----------------------------
    - str: 
        The extracted label as a string.
    """
    if isinstance(lab, list):
        return str(lab.first())
    else:
        return str(lab)
   



def add_kpi(superclass, label, description, unit_of_measure, parsable_computation_formula, 
            human_readable_formula=None, depends_on_machine=False, depends_on_operation=False):
    """
    Add a New Key Performance Indicator (KPI) to the Ontology
    -----------------------------
    
    This function validates and creates a new KPI in the ontology. It checks for duplicate labels, 
    validates the superclass, and associates attributes, formulas, and dependencies with the KPI.

    -----------------------------
    Args:
    -----------------------------
    - superclass (str): 
        The label of the KPI's superclass, which must be unique and valid.
    - label (str): 
        A unique label for the new KPI.
    - description (str): 
        A descriptive text for the KPI.
    - unit_of_measure (str): 
        The unit of measurement for the KPI (e.g., 'kg', 'hours').
    - parsable_computation_formula (str): 
        A machine-readable formula to calculate the KPI's value.
    - human_readable_formula (str, optional): 
        A user-friendly version of the computation formula. Defaults to the parsable formula.
    - depends_on_machine (bool, optional): 
        Whether the KPI is dependent on machines. Defaults to False.
    - depends_on_operation (bool, optional): 
        Whether the KPI is dependent on operations. Defaults to False.

    -----------------------------
    Raises:
    -----------------------------
    ValueError: 
    - If the KPI label already exists in the ontology.
    - If the superclass is undefined or referenced multiple times.

    TypeError: 
    - If the superclass is not a valid KPI class or derived from it.

    -----------------------------
    Side Effects:
    -----------------------------
    - Adds the KPI to the ontology.
    - Updates global mappings for units of measure, formulas, and dependencies.
    - Saves changes to the ontology via the `_backup` function.

    -----------------------------
    Prints:
    -----------------------------
    "KPI {label} successfully added to the ontology!" 
        upon successful addition of the KPI.
    """
    if not human_readable_formula:
        human_readable_formula = parsable_computation_formula
    
    # Validate that the KPI label does not already exist.
    if ONTO.search(label=label):
        raise ValueError(f"KPI '{label}' already exists in the ontology. Please choose a unique label.")

    # Validate that the superclass is defined and unique.
    target = ONTO.search(label=superclass)
    if not target or len(target) > 1:
        raise ValueError(f"The superclass '{superclass}' is either missing or referenced multiple times. Ensure there is only one unique reference.")

    target = target[0]

    # Ensure the superclass is valid (either a KPI class or derived from it).
    if not (KPI_CLASS == target or any(KPI_CLASS in cls.ancestors() for cls in target.is_a)):
        raise TypeError(f"The specified superclass '{superclass}' is not valid. It must be either the KPI class or derived from it.")

 
    # Create the KPI and assign attributes.
    new_el = target(_generate_hash_code(label))
    new_el.label = [or2.locstr(label, lang='en')]
    new_el.description = [or2.locstr(description, lang='en')]
    UNIT_OF_MEASURE[new_el] = [or2.locstr(unit_of_measure, lang='en')]
    HUMAN_READABLE_FORMULA[new_el] = [or2.locstr(human_readable_formula, lang='en')]
    PARSABLE_FORMULA[new_el] = [parsable_computation_formula]
    
    dependencies = []
    if depends_on_machine:
        dependencies.append(MACHINE_CASS)
    if depends_on_operation:
        dependencies.append(OPERATION_CLASS)
    if dependencies:
        DEPENDS_ON[new_el] = dependencies
    
    _backup()  # Save changes.
    print('KPI', label, 'successfully added to the ontology!')
    
def delete_kpi(label):
    """
    Delete a Key Performance Indicator (KPI) from the Ontology
    -----------------------------
    
    This function removes a KPI from the ontology after verifying it is not referenced by other KPIs.

    -----------------------------
    Args:
    -----------------------------
    - label (str): 
        The label of the KPI to be deleted.

    -----------------------------
    Raises:
    -----------------------------
    ValueError: 
    - If more than one or no KPI is found for the given label.
    - If the KPI is used in the computation of other KPIs.
    
    TypeError: 
    - If the target is not a valid KPI (not an instance of KPI_CLASS).


    -----------------------------
    Side Effects:
    -----------------------------
    - Deletes the KPI entity from the ontology.
    - Saves changes to the ontology via the `_backup` function.

    -----------------------------
    Prints:
    -----------------------------
    "KPI {label} successfully deleted from the ontology!" 
        upon successful deletion of the KPI.
    """
    # Search for the KPI in the ontology.
    target = ONTO.search(label=label)
    
    # Ensure exactly one match is found; otherwise, report an error.
    if not target or len(target) > 1:
        raise ValueError(f"More than one or no KPI found for label: {label}")

    target = target[0]  # Select the first result.

    # Verify the target is a KPI.
    if not isinstance(target, KPI_CLASS):
        raise TypeError(f"The lable {label} refer to an entity that is not an instance of KPI_CLASS.")

    # Check if the KPI is used in the computation of other KPIs.
    for kpi in KPI_CLASS.instances():
        if kpi != target:
            matches = re.findall(r'R°[A-Za-z_]+°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', PARSABLE_FORMULA[kpi][0])
            for match in matches:
                kpi_name = re.match(r'R°([A-Za-z_]+)°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', match).group(1)
                if kpi_name == label:
                    raise ValueError(f"KPI {label} is already used in the computation of {_extract_label(kpi.label)}")

    
    # Remove the KPI from the ontology.
    or2.destroy_entity(target)
    
    _backup()  # Save changes.
    print('KPI', label, 'successfully deleted from the ontology!')




def add_process(process_label, process_description, steps_list):
    """
    Add a New Process to the Ontology
    -----------------------------
    
    This function creates a new process in the ontology by associating the given label, 
    description, and a sequence of steps (machine-operation pairs).

    -----------------------------
    Args:
    -----------------------------
    - process_label (str): 
        A unique label for the process.
    - process_description (str): 
        A descriptive text for the process.
    - steps_list (list of tuples): 
        A sequence of steps, where each step is a tuple of (machine_label, operation_label).

    -----------------------------
    Raises:
    -----------------------------
    ValueError:
    - If the process label already exists in the ontology.
    - If any machine or operation in the steps list is not unique, missing, or has multiple references.
    
    TypeError:
    - If a machine or operation in the steps list does not match the expected type.


    -----------------------------
    Side Effects:
    -----------------------------
    - Adds the process and its associated steps to the ontology.
    - Updates mappings for machines, operations, and step positions.
    - Saves changes to the ontology via the `_backup` function.

    -----------------------------
    Prints:
    -----------------------------
    "Process {process_label} successfully added to the ontology!" 
        upon successful addition of the process.
    """
    
    # request validation
    
    # Ensure exactly no match is found
    if ONTO.search(label=process_label):
        raise ValueError(f"The process label '{process_label}' already exists in the ontology. Please choose a different label.")

    entity_pairs = []
    for m, o in steps_list:
        # Search for the machine in the ontology.
        m_target = ONTO.search(label=m)
        # Ensure exactly one match is found; otherwise, report an error.
        if not m_target or len(m_target) > 1:
            raise ValueError(f"The machine label '{m}' is either not referenced or has multiple matches in the ontology. Please ensure it is unique and defined correctly.")
        m_target = m_target[0]  # Select the first result.
        # Verify the target is a machine.
        if not isinstance(m_target, MACHINE_CASS):
            raise TypeError(f"The label '{m}' refers to an invalid machine type. Expected instance of '{MACHINE_CASS}', found '{type(m_target)}'.")
        
        # Search for the operation in the ontology.
        o_target = ONTO.search(label=o)
        # Ensure exactly one match is found; otherwise, report an error.
        if not o_target or len(o_target) > 1:
            raise ValueError(f"The operation label '{o}' is either not referenced or has multiple matches in the ontology. Please ensure it is unique and defined correctly.")
        o_target = o_target[0]  # Select the first result.
        # Verify the target is an operation.
        if not isinstance(o_target, OPERATION_CLASS):
            raise TypeError(f"The label '{o}' refers to an invalid operation type. Expected instance of '{OPERATION_CLASS}', found '{type(o_target)}'.")
        
        entity_pairs.append((m_target, o_target))

    
    # creating the process
    steps = []
    for i, (m, o) in enumerate(steps_list):
        new_el_label = process_label + '_' + str(i + 1) + '_' + m + '_' + o
        new_el = MACHINE_OPERATION_CLASS(_generate_hash_code(new_el_label))
        steps.append(new_el)
        
        new_el.label = [or2.locstr(new_el_label, lang='en')]
        new_el.description = [or2.locstr(f'step {i + 1} of the process {process_label}', lang='en')]
        
        ASSOCIATED_MACHINE[new_el] = [entity_pairs[i][0]]
        ASSOCIATED_OPERATION[new_el] = [entity_pairs[i][1]]
        PROCESS_STEP_POSITION[new_el] = [i + 1]

    new_process = PROCESS_CLASS(_generate_hash_code(process_label))
    new_process.label = [or2.locstr(process_label, lang='en')]
    new_process.description = [or2.locstr(process_description, lang='en')]
    PROCESS_STEP[new_process] = steps
    
    _backup()
    print('Process', process_label, 'successfully added to the ontology!')

def delete_process(process_label):
    """
    Delete a Process from the Ontology
    -----------------------------
    
    This function removes a process and its associated steps from the ontology.

    -----------------------------
    Args:
    -----------------------------
    - process_label (str): 
        The label of the process to be deleted.

    -----------------------------
    Raises:
    -----------------------------
    ValueError: 
    - If the process is either missing or referenced multiple times, ensuring there is only one unique reference for the process.
    
    TypeError: 
    - If the target is not a valid process or not an instance of the `PROCESS_CLASS`, meaning the target must be a valid process.


    -----------------------------
    Side Effects:
    -----------------------------
    - Deletes all steps associated with the process.
    - Removes the process entity from the ontology.
    - Saves changes to the ontology via the `_backup` function.

    -----------------------------
    Prints:
    -----------------------------
    "Process {process_label} successfully deleted from the ontology!" 
        upon successful deletion of the process.
    """
    # Search for the process in the ontology.
    target = ONTO.search(label=process_label)
    
    # Ensure exactly one match is found; otherwise, report an error.
    if not target or len(target) > 1:
        raise ValueError(f"The process '{process_label}' is either missing or referenced multiple times. Ensure there is only one unique reference.")

    target = target[0]  # Select the first result.

    # Verify the target is a process.
    if not isinstance(target, PROCESS_CLASS):
        raise TypeError(f"The specified target '{process_label}' is not a valid process. It must be an instance of the PROCESS_CLASS.")

    
    # Remove all process steps associated with this process.
    steps = PROCESS_STEP[target]
    for step in steps:
        or2.destroy_entity(step)
    
    # Remove the process itself.
    or2.destroy_entity(target)
    
    # Save changes to the ontology.
    _backup()
    print('Process', process_label, 'successfully deleted from the ontology!')




def add_operation(label, description):
    """
    Add a New Operation to the Ontology
    -----------------------------
    
    This function validates and creates a new operation in the ontology. It ensures the operation label is unique 
    and assigns the provided label and description.

    -----------------------------
    Args:
    -----------------------------
    - label (str): 
        A unique label for the operation.
    - description (str): 
        A descriptive text for the operation.

    -----------------------------
    Raises:
    -----------------------------
    Exception: 
        - If the operation label already exists.

    -----------------------------
    Side Effects:
    -----------------------------
    - Adds the operation to the ontology.
    - Saves changes to the ontology via the `_backup` function.

    -----------------------------
    Prints:
    -----------------------------
    "Operation {label} successfully added to the ontology!" 
        upon successful addition of the operation.
    """
    # Validate that the operation label does not already exist.
    if ONTO.search(label=label):
        raise Exception(f'OPERATION ALREADY EXISTS: {label}')
    
    # Create the operation and assign attributes.
    new_el = OPERATION_CLASS(_generate_hash_code(label))
    new_el.label = [or2.locstr(label, lang='en')]
    new_el.description = [or2.locstr(description, lang='en')]
    
    # Optionally, if you need any additional associations or attributes, they can be added here
    
    _backup()  # Save changes.
    print('Operation', label, 'successfully added to the ontology!')

def delete_operation(label):
    """
    Delete an Operation from the Ontology
    -----------------------------
    
    This function removes an operation from the ontology after ensuring it is not used in any process steps.

    -----------------------------
    Args:
    -----------------------------
    - label (str): 
        The label of the operation to be deleted.

    -----------------------------
    Raises:
    -----------------------------
    Exception: 
        - If the operation is undefined or not unique.
        - If the target is not a valid operation.
        - If the operation is used in process steps.

    -----------------------------
    Side Effects:
    -----------------------------
    - Deletes the operation entity from the ontology.
    - Saves changes to the ontology via the `_backup` function.

    -----------------------------
    Prints:
    -----------------------------
    "Operation {label} successfully deleted from the ontology!" 
        upon successful deletion of the operation.
    """
    # Search for the operation in the ontology.
    target = ONTO.search(label=label)
    
    # Ensure exactly one match is found; otherwise, report an error.
    if not target or len(target) > 1:
        raise Exception(f"DOUBLE OR NONE REFERENCED OPERATION: {label}")
    
    target = target[0]  # Select the first result.
    
    # Verify the target is an operation.
    if not isinstance(target, OPERATION_CLASS):
        raise Exception(f"IS NOT A VALID OPERATION: {label}")
    
    # Check if the KPI is used in the computation of other KPIs.
    for mo in MACHINE_OPERATION_CLASS.instances():
        if target in ASSOCIATED_OPERATION[mo]:
            raise Exception(f"OPERATION {label} IS USED IN THE PROCESS_STEP {_extract_label(mo.label)}")
                
    # Remove the operation from the ontology.
    or2.destroy_entity(target)
    
    _backup()  # Save changes.
    print('Operation', label, 'successfully deleted from the ontology!')
    



def get_formulas(kpi):
    """
    Retrieve and Expand Formulas for a KPI
    -----------------------------
    
    This function retrieves the formula associated with a KPI and recursively resolves any nested KPI references 
    to provide fully expanded formulas.

    -----------------------------
    Args:
    -----------------------------
    - kpi (str): 
        The label of the KPI whose formulas are to be retrieved.

    -----------------------------
    Returns:
    -----------------------------
    - dict: 
        A dictionary mapping KPI labels to their expanded formulas.

    -----------------------------
    Raises:
    -----------------------------
    Exception: 
        - If the KPI is undefined or not unique.
        - If the KPI label is invalid.
        - If a referenced KPI in the formula is undefined or invalid.

    -----------------------------
    Side Effects:
    -----------------------------
    - Traverses the ontology to resolve all nested KPI references.

    -----------------------------
    Notes:
    -----------------------------
    The function recursively unrolls all dependencies until no further nested KPIs remain.
    """
    # Search for the KPI in the ontology.
    target = ONTO.search(label=kpi)
    
    # Ensure exactly one match is found; otherwise, report an error.
    if not target or len(target) > 1:
        raise Exception(f"DOUBLE OR NONE REFERENCED KPI: {kpi}")
    
    target = target[0]  # Select the first result.
    
    # Verify the target is a KPI.
    if not any(issubclass(cls, KPI_CLASS) for cls in target.is_a):
        raise Exception(f"IS NOT A VALID KPI: {kpi}")
    
    # Initialize lists for formulas to unroll and store resolved formulas.
    to_unroll = [PARSABLE_FORMULA[target][0]]
    kpi_formula = {kpi: PARSABLE_FORMULA[target][0]}
    
    # Expand all formulas by resolving nested KPI references.
    while to_unroll:
        # Match every KPI reference contained in the formula to_unroll[0]
        matches = re.findall(r'R°[A-Za-z_]+°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', to_unroll.pop(0))
        
        for match in matches:
            # For every macth append the kpi to to_unroll and save the data to be returnedù
            # And recursively match KPI references
            kpi_name = re.match(r'R°([A-Za-z_]+)°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', match).group(1)
            target = ONTO.search(label=kpi_name)
            
            if not target or len(target) > 1:
                # this exception is raised only if some formula is wrong
                raise Exception(f"DOUBLE OR NONE REFERENCED KPI: {kpi_name}")
            
            target = target[0]
            to_unroll.append(PARSABLE_FORMULA[target][0])
            kpi_formula[kpi_name] = PARSABLE_FORMULA[target][0]
    
    return kpi_formula

def get_closest_kpi_formulas(kpi, method='custom'):
    """
    Find the Formulas for a KPI or Closest Matching KPI
    -----------------------------
    
    This function retrieves formulas for a given KPI. If the KPI is not found, it calculates similarity scores 
    to identify the closest matching KPI and returns its formulas.

    -----------------------------
    Args:
    -----------------------------
    - kpi (str): 
        The label of the KPI to search for.
    - method (str, optional): 
        The similarity metric to use for matching (default is 'custom').

    -----------------------------
    Returns:
    -----------------------------
    - tuple: 
        - dict: A dictionary mapping KPI labels to their formulas.
        - float: The similarity score (1 for exact matches).

    -----------------------------
    Raises:
    -----------------------------
    None directly. It handles missing KPIs by searching for the closest match.

    -----------------------------
    Side Effects:
    -----------------------------
    - Uses a similarity metric to compare the given KPI with other ontology entities.
    - Returns the formulas for the closest match if an exact match is not found.

    -----------------------------
    Notes:
    -----------------------------
    - The function uses `get_formulas` to retrieve formulas for the closest match.
    - Similarity calculation methods can be extended as needed.
    """
    # Attempt to retrieve the exact formulas for the given KPI.
    try:
        ret = get_formulas(kpi)
        
        return ret, 1  # Return exact match with similarity score of 1.
    except:
        # Initialize variables to track the closest match and similarity.
        max_val = -math.inf
        max_label = ''
        
        # Compare the KPI with all individuals in the KPI class.
        for ind in KPI_CLASS.instances():
            similarity = _get_similarity(kpi, ind.label.en.first(), method)
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()
        
        # Return the formulas for the closest matching label.
        return get_formulas(max_label), max_val
        



def get_instances(owl_class_label):
    """
    Retrieve all instances of a given OWL class or individual.
    -----------------------------
    
    This function checks if the provided label corresponds to a class or an individual, 
    and then retrieves all instances of that class, including instances of its subclasses. 
    If the label corresponds to an individual, it directly returns that individual.

    -----------------------------
    Args:
    -----------------------------
    - owl_class_label (str): 
        The label of the OWL class or individual to search for.

    -----------------------------
    Returns:
    -----------------------------
    - list: 
        A list containing labels of all instances of the given class or individual, 
        or an empty list if no instances are found.

    -----------------------------
    Raises:
    -----------------------------
    Exception: 
        If no matches or multiple matches are found for the provided label.
        If the input is neither a class nor an individual.
    """
    # Search for the class or individual in the ontology using the provided label.
    target = ONTO.search(label=owl_class_label)
    
    # Validate that the search returned a unique result.
    if not target or len(target) > 1:
        # Error if none or multiple matches found.
        raise Exception(f"DOUBLE OR NONE REFERENCED ENTITY: {owl_class_label}")
    
    target = target[0]  # Extract the single match.
    instances = set()  # Initialize a set to store the instances.
    
    # Check if the target is an OWL class.
    if isinstance(target, or2.ThingClass):
        # Start with the target class and explore all its subclasses.
        classes_to_process = [target]
        while classes_to_process:
            current_class = classes_to_process.pop()
            
            # Add all instances of the current class to the set.
            instances.update(i.label.en.first() for i in current_class.instances())
            
            # Add subclasses of the current class to the processing queue.
            classes_to_process.extend(current_class.subclasses())
    # If the target is an individual, add it directly to the set of instances.
    elif isinstance(target, or2.Thing):
        instances.add(owl_class_label)
    else:
        # If the input is neither a class nor an individual, print an error message.
        raise Exception(f"INPUT IS NEITHER A CLASS NOR AN INSTANCE: {owl_class_label}")
    
    # Return the list of instances found.
    return list(instances)

def get_closest_class_instances(owl_class_label, istances_type='a', method='levenshtein'):
    """
    Retrieve instances of the closest matching OWL class or individual.
    -----------------------------
    
    This function tries to find an exact match for the provided class or individual label.
    If no exact match is found, it searches for the most similar element using a similarity method 
    (Levenshtein by default). It also allows filtering instances by type (e.g., KPI, machine, etc.).

    -----------------------------
    Args:
    -----------------------------
    - owl_class_label (str): 
        The label of the OWL class or individual to search for.
    
    - istances_type (str, optional): 
        The type of instances to return. Defaults to 'a' for all types.
        Valid options are:
            - 'k' for KPI
            - 'm' for machine
            - 'o' for operation
            - 'p' for process
            - 'a' for all types.
    
    - method (str, optional): 
        The similarity method to use. Defaults to 'levenshtein'.

    -----------------------------
    Returns:
    -----------------------------
    - tuple: 
        - list: Instances of the closest matching class or individual.
        - float: Similarity score of the closest match.

    -----------------------------
    Raises:
    -----------------------------
    Exception: 
        If no instances are found or if the similarity computation fails.
    """
    
    # Attempt to retrieve the instances of the exact class or individual.
    try:
        ret = get_instances(owl_class_label)
        
        # If exact match is found, return the instances with similarity score of 1.
        return ret, 1
    
    except Exception:
    # If no instances are found, look for the closest match.
        max_val = -math.inf  # Initialize the highest similarity score.
        max_label = ''  # Initialize the label of the closest match.


        if istances_type == 'a':
            # not machine_operation because are subordinated to process
            class_to_check = [KPI_CLASS, MACHINE_CASS, OPERATION_CLASS, PROCESS_CLASS]
            instaces_to_check = list(KPI_CLASS.instances()) + list(MACHINE_CASS.instances()) + \
                        list(OPERATION_CLASS.instances()) + list(PROCESS_CLASS.instances())
        elif istances_type == 'k':
            class_to_check = [KPI_CLASS]
            instaces_to_check = list(KPI_CLASS.instances())
        elif istances_type == 'm':
            class_to_check = [MACHINE_CASS]
            instaces_to_check = list(MACHINE_CASS.instances())
        elif istances_type == 'o':
            class_to_check = [OPERATION_CLASS]
            instaces_to_check = list(OPERATION_CLASS.instances())
        elif istances_type == 'p':
            class_to_check = [PROCESS_CLASS]
            instaces_to_check = list(PROCESS_CLASS.instances())
        
        # Iterate over all classes in class_to_check.
        for cl in class_to_check:
            # Compute the similarity between the input and the current class label.
            similarity = _get_similarity(owl_class_label, _extract_label(cl.label), method)
            # Update the closest match if the similarity is higher.
            if max_val < similarity:
                max_val = similarity
                max_label = _extract_label(cl.label)
        
        # Iterate over all istances in instaces_to_check.
        for ind in instaces_to_check:
            # Compute the similarity between the input and the current individual label.
            similarity = _get_similarity(owl_class_label, _extract_label(ind.label), method)
            # Update the closest match if the similarity is higher.
            if max_val < similarity:
                max_val = similarity
                max_label = _extract_label(ind.label)
        
        # Retrieve the instances of the closest matching label and return them.
        return get_instances(max_label), max_val
        



def get_object_properties(owl_label):
    """
    Retrieves all the properties (annotation, object, and data properties) associated with an ontology entity
    based on its label. It also returns information about superclasses, subclasses, and instances if the element
    is a class or individual and entity_type.

    -----------------------------
    Args:
    -----------------------------
    - owl_label (str): 
        The label of the ontology element (class or individual) whose properties are to be retrieved.

    -----------------------------
    Returns:
    -----------------------------
    dict: 
        A dictionary containing the information associated with the entity, including:
        - 'label': The label of the element.
        - 'description': The description annotation property, if available.
        - 'depends_on_other_kpi': A list of KPI labels the element depends on based on the parsable computational formula.
        - 'superclasses': List of superclasses of the element (for classes and individuals).
        - 'subclasses': List of subclasses of the element (for classes).
        - 'instances': List of instances of the element (for classes).
        - 'entity_type': The nature of the referred entity which can be class, instance or property.
        - 'ontology_property_name': List of every entity related to the referenced entity with the 'ontology_property_name' property.
    """
    # Search for the target element using its label in the ontology.
    target = ONTO.search(label=owl_label)
    
    if not target or len(target) > 1:
        raise Exception(f"DOUBLE OR NONE REFERENCED KPI: {owl_label}")
    
    target = target[0]  # Extract the single matching element.
    
    properties = {'label': _extract_label(target.label)}  # Initialize properties dictionary with the label.
    
    # Iterate over annotation properties to gather description and other annotations.
    for prop in ONTO.annotation_properties():
        references = prop[target]
        if references:
            if prop._name == 'description':
                properties['description'] = _extract_label(prop[target])  # Handle description property
            else:
                properties[_extract_label(prop.label)] = _extract_label(prop[target])  # Handle other annotations
    
    # Iterate over object properties to gather object property values.
    for prop in ONTO.object_properties():
        references = prop[target]
        if references:
            properties[_extract_label(prop.label)] = [_extract_label(x.label) for x in references]  # List of related objects
    
    # Iterate over data properties to gather data property values.
    for prop in ONTO.data_properties():
        references = prop[target]
        if references:
            properties[_extract_label(prop.label)] = _extract_label(references)  # Single data property value
            
            # Special handling for PARSABLE_FORMULA, extracting dependencies.
            if prop == PARSABLE_FORMULA:
                depends_on_kpi = []
                matches = re.findall(r'R°[A-Za-z_]+°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', references[0])  
                for match in matches:
                    kpi_name = re.match(r'R°([A-Za-z_]+)°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', match).group(1)
                    depends_on_kpi.append(kpi_name)
                properties['depends_on_other_kpi'] = depends_on_kpi

    # Check if the target is a class (ThingClass) and retrieve its superclass and subclass information.
    if isinstance(target, or2.ThingClass):
        properties['superclasses'] = [_extract_label(superclass.label) for superclass in target.is_a if 
                                      isinstance(superclass, or2.ThingClass) and 
                                      _extract_label(superclass.label) != 'None']
        properties['subclasses'] = [_extract_label(subclass.label) for subclass in target.subclasses()]
        properties['instances'] = get_instances(_extract_label(target.label))
        properties['entity_type'] = 'class'
        
    # Check if the target is an individual (Thing) and retrieve its superclass information.
    elif isinstance(target, or2.Thing):
        properties['superclasses'] = [_extract_label(superclass.label) for superclass in target.is_a if 
                                      isinstance(superclass, or2.ThingClass) and 
                                      _extract_label(superclass.label) != 'None']
        properties['entity_type'] = 'instance'
    else:
        properties['entity_type'] = 'property'

    return properties
    
def get_closest_object_properties(owl_label, method='custom'):
    """
    Apply get_object_properties to the entity whose label is the closest match to the given label.
    The closeness is determined by a similarity measure (default is Levenshtein distance).

    -----------------------------
    Args:
    -----------------------------
    - owl_label (str): 
        The label of the ontology element whose closest match is to be found.
    
    - method (str, optional): 
        The similarity measure to use for finding the closest match (default: 'levenshtein').

    -----------------------------
    Returns:
    -----------------------------
    - tuple: 
        A tuple containing:
        - dict: The properties of the closest matching element.
        - float: The similarity score (between 0 and 1) of the closest match.
    """
    # Attempt to retrieve properties for the exact match of the owl_label.
    try:
        ret = get_object_properties(owl_label)
        
        return ret, 1  # If the exact match is found, return its properties with a similarity of 1.
    
    except Exception:
        max_val = -math.inf  # Initialize a variable to track the maximum similarity score.
        max_label = ''  # Initialize a variable to store the label of the closest match.

        # Check similarity with all classes in the ontology.
        for ind in ONTO.classes():
            similarity = _get_similarity(owl_label, ind.label.en.first(), method)
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()

        # Check similarity with all individuals in the ontology.
        for ind in ONTO.individuals():
            similarity = _get_similarity(owl_label, ind.label.en.first(), method)
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()

        # Check similarity with all object properties in the ontology.
        for ind in ONTO.object_properties():
            similarity = _get_similarity(owl_label, _extract_label(ind.label), method)
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()

        # Check similarity with all data properties in the ontology.
        for ind in ONTO.data_properties():
            similarity = _get_similarity(owl_label, _extract_label(ind.label), method)
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()

        # Check similarity with all annotation properties in the ontology.
        for ind in ONTO.annotation_properties():
            similarity = _get_similarity(owl_label, _extract_label(ind.label), method)
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()

        # Return the properties of the closest match along with the similarity score.
        return get_object_properties(max_label), max_val
        



def get_steps(process_label):
    """
    Retrieve the steps associated with a given process label from the ontology.
    -----------------------------
    
    -----------------------------
    Args:
    -----------------------------
    - process_label (str): The label of the process to search for in the ontology.
        
    -----------------------------
    Returns:
    -----------------------------
    - list of tuple: A list of tuples where each tuple contains:
        - The position of the step in the process.
        - The label of the associated machine.
        - The label of the associated operation.
    
    -----------------------------
    Raises:
    -----------------------------
    Exception: 
        - If no process or more than one process is found with the given label.
        - If the found target is not a valid process.
    """
    
    
    # Search for the process in the ontology.
    target = ONTO.search(label=process_label)
    
    # Ensure exactly one match is found; otherwise, report an error.
    if not target or len(target) > 1:
        raise Exception(f"DOUBLE OR NONE REFERENCED PROCESS: {process_label}")
    
    target = target[0]  # Select the first result.
    
    # Verify the target is a process.
    if not isinstance(target, PROCESS_CLASS):
        raise Exception(f"IS NOT A VALID PROCESS: {process_label}")
    
    steps = []
    for s in PROCESS_STEP[target]:
        steps.append((PROCESS_STEP_POSITION[s][0], _extract_label(ASSOCIATED_MACHINE[s][0].label), _extract_label(ASSOCIATED_OPERATION[s][0].label)))

    return steps

def get_closest_process_steps(process_label, method='levenshtein'):
    """
    Finds the steps associated with a process or the closest matching process.
    -----------------------------
    
    If no process is found for the given label, this function calculates similarity scores between 
    the process and other ontology entities, returning steps for the closest match.

    -----------------------------
    Parameters:
    -----------------------------
    - process_label (str): The label of the process to search for.
    - method (str, optional): The similarity metric to use (default is 'levenshtein').

    -----------------------------
    Returns:
    -----------------------------
    - tuple:
      - list: Steps of the closest matching process.
      - float: The similarity score (1 for exact matches).
    """
    # Attempt to retrieve the steps of the exact process.
    try:
        ret = get_steps(process_label)
        
        return ret, 1  # Return exact match with similarity score of 1.
    except:
        # Initialize variables to track the closest match and similarity.
        max_val = -math.inf
        max_label = ''
        
        # Compare the process with all individuals in the PROCESS_CLASS.
        for ind in PROCESS_CLASS.instances():
            similarity = _get_similarity(process_label, ind.label.en.first(), method)
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()
        
        # Return the steps for the closest matching label.
        return get_steps(max_label), max_val