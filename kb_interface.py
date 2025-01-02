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
    Initializes the global ontology and related variables. 
    This function must necessarily be called every time it is desired 
    to initialize the KB and use other methods to interact.
    
    Parameters:
    - backup_number (int, optional): The number indicating which backup file to load, inside the backup folder.
      If not specified, it reads the configuration file to determine the latest backup.

    Global Variables Modified:
    - SAVE_INT: Save interval value read or set.
    - ONTO: The ontology object loaded from the backup.
    - PARSABLE_FORMULA, HUMAN_READABLE_FORMULA, UNIT_OF_MEASURE, DEPENDS_ON,
      OPERATION_CASS, MACHINE_CASS, KPI_CLASS: Specific ontology classes extracted.
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
    Generates a compact, alphanumeric hash code for a given input string.

    Parameters:
    - input_data (str): The input string to generate the hash code from.

    Returns:
    - hash_code (str): A shortened alphanumeric hash code derived from the input data.
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
    Computes similarity between two strings using a chosen method.

    Parameters:
    - a (str): First string to compare.
    - b (str): Second string to compare.
    - method (str, optional): The method to use, default is 'custom'.

    Returns:
    - similarity (float): A value between 0 and 1 indicating similarity.
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
        elif b_suffix is 'sum':
            # If only one string has a suffix, we treat it as completely different
            suffix_similarity = 1e-08
        else:
            suffix_similarity = 0
            
        # Assign higher weight to the main part and lower weight to the suffix part
        total_similarity = (0.85 * main_similarity) + (0.15 * suffix_similarity)

        return total_similarity
    
    else:
        # raise exception if method is not recognized
        raise Exception(f'METHOD NOT FOUND: {method}')

def _backup():
    """
    Creates a backup of the current ontology and manages cleanup of old backups.

    Global Variables Used:
    - SAVE_INT: Determines the naming and management of backups.
    - ONTO: The ontology object being saved.

    File Management:
    - Saves the ontology in RDF/XML format.
    - Deletes older backups based on the fine and coarse grain intervals.
    """
    global SAVE_INT
    coarse_grain = 20  # Defines the coarse-grain interval
    max_fine_b = 10  # Maximum fine-grain backups to keep
    max_coarse_b = 5  # Maximum coarse-grain backups to keep

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
    if isinstance(lab, list):
        return str(lab.first())
    else:
        return str(lab)
   


 
def get_formulas(kpi):
    """
    Retrieves and expands formulas associated with a given KPI.

    This function identifies the formula for a KPI and recursively unrolls any nested KPIs 
    referenced within the formula until all dependencies are fully resolved.

    Parameters:
    - kpi (str): The label of the KPI whose formulas need to be expanded.

    Returns:
    - kpi_formula (dict): A dictionary mapping KPI labels to their formulas.
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
    Finds the formulas associated with a KPI or the closest matching KPI.

    If no formula is found for the given KPI, this function calculates similarity scores between 
    the KPI and other ontology entities, returning formulas for the closest match.

    Parameters:
    - kpi (str): The label of the KPI to search for.
    - method (str, optional): The similarity metric to use (default is 'levenshtein').

    Returns:
    - tuple:
      - formulas (dict): A dictionary mapping KPI labels to their formulas.
      - similarity (float): The similarity score (1 for exact matches).
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
        



def add_kpi(superclass, label, description, unit_of_measure, parsable_computation_formula, 
            human_readable_formula=None, depends_on_machine=False, depends_on_operation=False):
    """
    Adds a new KPI to the ontology.

    This function validates that the KPI's label and superclass are unique and correctly defined. 
    It then creates the KPI and associates the provided attributes, formulas, and dependencies.

    Parameters:
    - superclass (str): The label of the superclass for the KPI.
    - label (str): The unique label for the KPI.
    - description (str): A text description of the KPI.
    - unit_of_measure (str): The measurement unit for the KPI.
    - parsable_computation_formula (str): A machine-readable formula for the KPI.
    - human_readable_formula (str, optional): A user-friendly formula (default is the parsable formula).
    - depends_on_machine (bool, optional): Whether the KPI depends on machines.
    - depends_on_operation (bool, optional): Whether the KPI depends on operations.

    Returns:
    - None: Prints errors or creates the KPI instance.
    """
    if not human_readable_formula:
        human_readable_formula = parsable_computation_formula
    
    # Validate that the KPI label does not already exist.
    if ONTO.search(label=label):
        raise Exception(f'KPI ALREADY EXISTS: {label}')
    
    # Validate that the superclass is defined and unique.
    target = ONTO.search(label=superclass)
    if not target or len(target) > 1:
        raise Exception(f"DOUBLE OR NONE REFERENCED CLASS: {superclass}")
    
    target = target[0]
    
    # Ensure the superclass is valid (either a KPI class or derived from it).
    if not (KPI_CLASS == target or any(KPI_CLASS in cls.ancestors() for cls in target.is_a)):
        raise Exception(f"NOT A VALID SUPERCLASS: {superclass}")
 
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
    Deletes a KPI from the ontology.

    This function checks if the KPI is used in the computation of other KPIs and raises an exception if it is.
    If the KPI is not used, it deletes the KPI and updates the ontology.

    Parameters:
    - label (str): The label of the KPI to delete.

    Returns:
    - None: Prints success message or raises an exception if the KPI is used in other computations.
    """
    # Search for the KPI in the ontology.
    target = ONTO.search(label=label)
    
    # Ensure exactly one match is found; otherwise, report an error.
    if not target or len(target) > 1:
        raise Exception(f"DOUBLE OR NONE REFERENCED KPI: {label}")
    
    target = target[0]  # Select the first result.
    
    # Verify the target is a KPI.
    if not isinstance(target, KPI_CLASS):
        raise Exception(f"IS NOT A VALID KPI: {label}")
    
    # Check if the KPI is used in the computation of other KPIs.
    for kpi in KPI_CLASS.instances():
        if kpi != target:
            matches = re.findall(r'R°[A-Za-z_]+°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', PARSABLE_FORMULA[kpi][0])
            for match in matches:
                kpi_name = re.match(r'R°([A-Za-z_]+)°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', match).group(1)
                if kpi_name == label:
                    raise Exception(f"KPI {label} IS USED IN THE COMPUTATION OF {_extract_label(kpi.label)}")
    
    # Remove the KPI from the ontology.
    or2.destroy_entity(target)
    print(DEPENDS_ON[target])
    
    _backup()  # Save changes.
    print('KPI', label, 'successfully deleted from the ontology!')




def add_process(process_label, process_description, steps_list):
    """
    Adds a new process to the ontology with the given label, description, and steps.
    
    Args:
        process_label (str): The label for the new process.
        process_description (str): A description of the new process.
        steps_list (list of tuples): A list of tuples where each tuple contains a machine label and an operation label.
    Raises:
        Exception: If a process with the same label already exists.
        Exception: If a machine or operation in the steps list is not found or if there are multiple matches.
        Exception: If a machine or operation in the steps list is not of the correct type.
    Returns:
        None
    """
    
    # request validation
    
    # Ensure exactly no match is found
    if ONTO.search(label=process_label):
        raise Exception(f"LABEL ALREADY PRESENT: {process_label}")
    
    entity_pairs = []
    for m, o in steps_list:
        # Search for the machine in the ontology.
        m_target = ONTO.search(label=m)
        # Ensure exactly one match is found; otherwise, report an error.
        if not m_target or len(m_target) > 1:
            raise Exception(f"DOUBLE OR NONE REFERENCED MACHINE: {m}")
        m_target = m_target[0]  # Select the first result.
        # Verify the target is a machine.
        if not isinstance(m_target, MACHINE_CASS):
            raise Exception(f"IS NOT A VALID MACHINE: {m}")
        
        # Search for the operation in the ontology.
        o_target = ONTO.search(label=o)   
        # Ensure exactly one match is found; otherwise, report an error.
        if not o_target or len(o_target) > 1:
            raise Exception(f"DOUBLE OR NONE REFERENCED OPERATION: {o}")   
        o_target = o_target[0]  # Select the first result.
        # Verify the target is an operation.
        if not isinstance(o_target, OPERATION_CLASS):
            raise Exception(f"IS NOT A VALID OPERATION: {o}")
        
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
            
def delete_process(process_label):
    """
    Deletes a process from the ontology.

    Parameters:
    - process_label (str): The label of the process to delete.

    Returns:
    - None: Prints a success message or raises an exception if the process is referenced elsewhere.
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

    
    # Remove all process steps associated with this process.
    steps = PROCESS_STEP[target]
    for step in steps:
        or2.destroy_entity(step)
    
    # Remove the process itself.
    or2.destroy_entity(target)
    
    # Save changes to the ontology.
    _backup()
    print('PROCESS', process_label, 'successfully deleted from the ontology!')




def add_operation(label, description):
    """
    Adds a new operation to the ontology.

    This function validates that the operation's label is unique and correctly defined.
    It then creates the operation and associates the provided label and description.

    Parameters:
    - label (str): The unique label for the operation.
    - description (str): A text description of the operation.

    Returns:
    - None: Prints errors or creates the operation instance.
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
    Deletes an operation from the ontology.

    This function checks if the operation is used in the computation of any KPIs and raises an exception if it is.
    If the operation is not used, it deletes the operation and updates the ontology.

    Parameters:
    - label (str): The label of the operation to delete.

    Returns:
    - None: Prints success message or raises an exception if the operation is used in computations.
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
    print(f"Operation {label} successfully deleted from the ontology!")
    
    _backup()  # Save changes.
    print('OPERATION', label, 'successfully deleted from the ontology!')
    
    


def get_instances(owl_class_label):
    """
    Retrieves all instances of a given OWL class.

    If the input label corresponds to a class, instances of the class and its subclasses are returned.
    If the label corresponds to an individual, it is directly returned.

    Parameters:
    - owl_class_label (str): The label of the OWL class or instance to search for.

    Returns:
    - list: Labels of all matching instances, or an empty list if none are found.
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

def get_closest_class_instances(owl_class_label, istances_type='a', method='custom'):
    
    """
    Retrieves all instances of a given OWL class or individual. If an exact match is not found, 
    searches for the most similar element in the knowledge base (KB).

    Parameters:
    - owl_class_label (str): The label of the class or individual to search for.
    - istances_type (str): The type of instances to return (default is 'a' for all). 
      Options are:
        - 'k' for KPI
        - 'm' for machine
        - 'o' for operation
        - 'p' for process
        - 'a' for all
    - method (str): The similarity method (default is 'levenshtein').

    Returns:
    - tuple:
      - list: Instances of the closest matching class or individual.
      - float: The similarity score of the closest match.
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
        print(max_label)
        return get_instances(max_label), max_val
        



def get_object_properties(owl_label):
    """
    Retrieves all the properties (annotation, object, and data properties) associated with an ontology entity
    based on its label. It also returns information about superclasses, subclasses, and instances if the element
    is a class or individual and entity_type.

    Args:
        owl_label (str): The label of the ontology element (class or individual) whose properties are to be retrieved.

    Returns:
        dict: A dictionary containing the information associated with the entity, including:
            - 'label': The label of the element.
            - 'description': The description annotation property, if available.
            - 'depends_on_other_kpi': A list of KPI labels the element depends on based on the parsable computational formula.
            - 'superclasses': List of superclasses of the element (for classes and individuals).
            - 'subclasses': List of subclasses of the element (for classes).
            - 'instances': List of instances of the element (for classes).
            - 'entity_type': The nature of the referred entity which can be class, istance or property 
            - 'ontology_property_name': List of every entity related to the referenced entoty with the 'ontology_property_name' property
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

    Args:
        owl_label (str): The label of the ontology element whose closest match is to be found.
        method (str): The similarity measure to use for finding the closest match (default: 'levenshtein').

    Returns:
        tuple: A tuple containing:
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
        

