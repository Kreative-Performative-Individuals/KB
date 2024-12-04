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
OPERATION_CASS = None  # Ontology class for operations
MACHINE_CASS = None  # Ontology class for machines
KPI_CLASS = None  # Ontology class for Key Performance Indicators (KPIs)

# === FUNCTION DEFINITIONS ===

def start(backup_number=1):
    """
    Initializes the global ontology and related variables.

    Parameters:
    - backup_number (int, optional): The number indicating which backup file to load.
      If not specified, it reads the configuration file to determine the latest backup.

    Global Variables Modified:
    - SAVE_INT: Save interval value read or set.
    - ONTO: The ontology object loaded from the backup.
    - PARSABLE_FORMULA, HUMAN_READABLE_FORMULA, UNIT_OF_MEASURE, DEPENDS_ON,
      OPERATION_CASS, MACHINE_CASS, KPI_CLASS: Specific ontology classes extracted.
    """
    # Declare global variables to ensure they are modified globally
    global SAVE_INT, ONTO, PARSABLE_FORMULA, HUMAN_READABLE_FORMULA
    global UNIT_OF_MEASURE, DEPENDS_ON, OPERATION_CASS, MACHINE_CASS, KPI_CLASS

    if backup_number:
        # Load ontology from the specified backup number
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
    OPERATION_CASS = ONTO.search(label='operation')[0]
    MACHINE_CASS = ONTO.search(label='machine')[0]
    KPI_CLASS = ONTO.search(label='kpi')[0]

    # Set environment variable for Kaggle compatibility
    os.environ["KAGGLE_CONFIG_DIR"] = "./backups"

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

def _get_similarity(a, b, method='w2v'):
    """
    Computes similarity between two strings using a chosen method.

    Parameters:
    - a (str): First string to compare.
    - b (str): Second string to compare.
    - method (str, optional): The method to use, default is 'levenshtein'.

    Returns:
    - similarity (float): A value between 0 and 1 indicating similarity.
    """
    if method == 'levenshtein':
        # Compute Levenshtein distance
        distance = Levenshtein.distance(a, b)
        # Convert distance to a similarity score
        similarity = 1 - distance / max(len(a), len(b))
        return similarity
    else:
        # Print error if method is not recognized
        print('METHOD NOT FOUND')
        return 

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
    coarse_grain = 8  # Defines the coarse-grain interval
    max_fine_b = 3  # Maximum fine-grain backups to keep
    max_coarse_b = 2  # Maximum coarse-grain backups to keep

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
    
def _fix():
    for el in get_instances('kpi'):
        target = ONTO.search(label=el)[0]
        if el in ['energy_efficiency', 'non_operative_time', 'operative_consumption', 'total_consumption', 'total_energy_cost']:
            DEPENDS_ON[target] = [OPERATION_CASS]
        else:
            DEPENDS_ON[target] = [MACHINE_CASS, OPERATION_CASS]

    ONTO.save(file='./new_onto_test.owl', format="rdfxml")


 
 
def get_formulas(kpi):
    """
    Retrieves and expands formulas associated with a given KPI.

    This function identifies the formula for a KPI and recursively unrolls any nested KPIs 
    referenced within the formula until all dependencies are fully resolved.

    Parameters:
    - kpi (str): The label of the KPI whose formulas need to be expanded.

    Returns:
    - kpi_formula (dict): A dictionary mapping KPI labels to their fully unrolled formulas.
    """
    # Search for the KPI in the ontology.
    target = ONTO.search(label=kpi)
    
    # Ensure exactly one match is found; otherwise, report an error.
    if not target or len(target) > 1:
        print("DOUBLE OR NONE REFERENCED KPI")
        return
    
    target = target[0]  # Select the first result.
    
    # Verify the target is a KPI.
    if not any(issubclass(cls, KPI_CLASS) for cls in target.is_a):
        print(kpi + "IS NOT A VALID KPI")
        return
    
    # Initialize lists for formulas to unroll and store resolved formulas.
    to_unroll = [PARSABLE_FORMULA[target][0]]
    kpi_formula = {kpi: PARSABLE_FORMULA[target][0]}
    
    # Expand all formulas by resolving nested KPI references.
    while to_unroll:
        matches = re.findall(r'R°[A-Za-z_]+°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', to_unroll.pop(0))
        
        for match in matches:
            kpi_name = re.match(r'R°([A-Za-z_]+)°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', match).group(1)
            target = ONTO.search(label=kpi_name)
            
            if not target or len(target) > 1:
                print("DOUBLE OR NONE REFERENCED KPI")
                return
            
            target = target[0]
            to_unroll.append(PARSABLE_FORMULA[target][0])
            kpi_formula[kpi_name] = PARSABLE_FORMULA[target][0]
    
    return kpi_formula

def get_closest_kpi_formulas(kpi, method='levenshtein'):
    """
    Finds the formulas associated with a KPI or the closest matching KPI.

    If no formula is found for the given KPI, this function calculates similarity scores between 
    the KPI and other ontology entities, returning formulas for the closest match.

    Parameters:
    - kpi (str): The label of the KPI to search for.
    - method (str, optional): The similarity metric to use (default is 'levenshtein').

    Returns:
    - tuple:
      - formulas (dict): The formulas of the found KPI.
      - similarity (float): The similarity score (1 for exact matches).
    """
    # Attempt to retrieve the exact formulas for the given KPI.
    ret = get_formulas(kpi)
    
    if not ret:
        # Initialize variables to track the closest match and similarity.
        max_val = -math.inf
        max_label = ''
        
        # Compare the KPI with all individuals in the ontology.
        for ind in ONTO.individuals():
            similarity = _get_similarity(kpi, ind.label.en.first(), method)
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()
        
        # Return the formulas for the closest matching label.
        return get_formulas(max_label), max_val
    else:
        return ret, 1  # Return exact match with similarity score of 1.



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
        print("KPI LABEL ALREADY EXISTS")
        return
    
    # Validate that the superclass is defined and unique.
    target = ONTO.search(label=superclass)
    if not target or len(target) > 1:
        print("DOUBLE OR NONE REFERENCED KPI")
        return
    
    target = target[0]
    
    # Ensure the superclass is valid (either a KPI class or derived from it).
    if not (KPI_CLASS == target or any(KPI_CLASS in cls.ancestors() for cls in target.is_a)):
        print("NOT A VALID SUPERCLASS")
        return
    
    # Create the KPI and assign attributes.
    new_el = target(_generate_hash_code(label))
    new_el.label = [or2.locstr(label, lang='en')]
    new_el.description = [or2.locstr(description, lang='en')]
    UNIT_OF_MEASURE[new_el] = [or2.locstr(unit_of_measure, lang='en')]
    HUMAN_READABLE_FORMULA[new_el] = [or2.locstr(human_readable_formula, lang='en')]
    PARSABLE_FORMULA[new_el] = [parsable_computation_formula]
    
    # Define dependencies if specified.
    if depends_on_machine and depends_on_operation:
        DEPENDS_ON[new_el] = [MACHINE_CASS, OPERATION_CASS]
    elif depends_on_operation:
        DEPENDS_ON[new_el] = [OPERATION_CASS]
    elif depends_on_machine:
        DEPENDS_ON[new_el] = [MACHINE_CASS]
    
    _backup()  # Save changes.



def get_instances(owl_class_label):
    """
    Retrieves all instances of a given OWL class or individual.

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
        print("DOUBLE OR NONE REFERENCED KPI")  # Error if none or multiple matches found.
        return
    
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
        print("INPUT IS NEITHER A CLASS NOR AN INSTANCE")
    
    # Return the list of instances found.
    return list(instances)

def get_closest_class_instances(owl_class_label, method='levenshtein'):
    """
    Retrieves all instances of a given OWL class or individual, if not exact match is found search for the
    most similar element in the KB.

    Parameters:
    - owl_class_label (str): The label of the class or individual to search for.
    - method (str): The similarity method (default is 'levenshtein').

    Returns:
    - tuple:
      - list: Instances of the closest matching class or individual.
      - float: The similarity score of the closest match.
    """
    # Attempt to retrieve the instances of the exact class or individual.
    ret = get_instances(owl_class_label)
    
    # If no instances are found, look for the closest match.
    if not ret:
        max_val = -math.inf  # Initialize the highest similarity score.
        max_label = ''  # Initialize the label of the closest match.
        
        # Iterate over all classes in the ontology.
        for ind in ONTO.classes():
            # Compute the similarity between the input and the current class label.
            similarity = _get_similarity(owl_class_label, ind.label.en.first(), method)
            # Update the closest match if the similarity is higher.
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()
        
        # Iterate over all individuals in the ontology.
        for ind in ONTO.individuals():
            # Compute the similarity between the input and the current individual label.
            similarity = _get_similarity(owl_class_label, ind.label.en.first(), method)
            # Update the closest match if the similarity is higher.
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()
        
        # Retrieve the instances of the closest matching label and return them.
        return get_instances(max_label), max_val
    else:
        # If exact match is found, return the instances with similarity score of 1.
        return ret, 1



def get_object_properties(owl_label):
    """
    Retrieves all the properties (annotation, object, and data properties) associated with an ontology entity
    based on its label. It also gathers information about superclasses, subclasses, and instances if the element
    is a class or individual.

    Args:
        owl_label (str): The label of the ontology element (class or individual) whose properties are to be retrieved.

    Returns:
        dict: A dictionary containing the properties associated with the element, including:
            - 'label': The label of the element.
            - 'description': The description annotation property, if available.
            - 'depends_on_other_kpi': A list of KPI names the element depends on (for a specific property).
            - 'superclasses': List of superclasses of the element (for classes and individuals).
            - 'subclasses': List of subclasses of the element (for classes).
            - 'instances': List of instances of the element (for classes).
    """
    # Search for the target element using its label in the ontology.
    target = ONTO.search(label=owl_label)
    
    if not target or len(target) > 1:
        print("DOUBLE OR NONE REFERENCED KPI")
        return
    
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
    
def get_closest_object_properties(owl_label, method='levenshtein'):
    """
    Retrieves the properties of the ontology element that is the closest match to the given label (`owl_label`).
    The closeness is determined by a similarity measure (default is Levenshtein distance), and the function
    returns the properties of the most similar element found.

    Args:
        owl_label (str): The label of the ontology element whose closest match is to be found.
        method (str): The similarity measure to use for finding the closest match (default: 'levenshtein').

    Returns:
        tuple: A tuple containing:
            - dict: The properties of the closest matching element.
            - float: The similarity score (between 0 and 1) of the closest match.
    """
    # Attempt to retrieve properties for the exact match of the owl_label.
    ret = get_object_properties(owl_label)
    
    if not ret:
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
    else:
        return ret, 1  # If the exact match is found, return its properties with a similarity of 1.

