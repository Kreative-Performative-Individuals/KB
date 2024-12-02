import owlready2 as or2
import re
import hashlib
import base64
import pathlib as pl
import math
import os

import Levenshtein

MAIN_DIR = pl.Path('./backups')
ONTO_PATH = ['KB_original']
CONFIG_PATH = pl.Path('./config.cfg')

ONTO = None
SAVE_INT = None
PARSABLE_FORMULA = None
HUMAN_READABLE_FORMULA = None
UNIT_OF_MEASURE = None
DEPENDS_ON = None
OPERATION_CASS = None
MACHINE_CASS = None
KPI_CLASS = None

def start():
    """
    Initializes the global ontology and related variables.
    This function reads a configuration file to determine the most recent ontology backup, 
    loads the corresponding ontology file, and extracts key elements for computation and reasoning.

    Global Variables Modified:
    - SAVE_INT (int): The save interval read from the configuration file.
    - ONTO (Ontology): The ontology object loaded from the specified backup file.
    - PARSABLE_FORMULA (OntologyClass): The ontology class representing parsable computation formulas.
    - HUMAN_READABLE_FORMULA (OntologyClass): The ontology class for human-readable formulas.
    - UNIT_OF_MEASURE (OntologyClass): The ontology class defining units of measurement.
    - DEPENDS_ON (OntologyClass): The ontology class describing dependencies between entities.
    - OPERATION_CASS (OntologyClass): The ontology class representing operations.
    - MACHINE_CASS (OntologyClass): The ontology class representing machines.
    - KPI_CLASS (OntologyClass): The ontology class representing Key Performance Indicators (KPIs).
    """
    # Declare global variables to ensure modifications affect the global namespace
    global SAVE_INT, ONTO, PARSABLE_FORMULA, HUMAN_READABLE_FORMULA
    global UNIT_OF_MEASURE, DEPENDS_ON, OPERATION_CASS, MACHINE_CASS, KPI_CLASS

    # Step 1: Read the configuration file to determine the save interval
    with open(CONFIG_PATH, 'r') as cfg:
        SAVE_INT = int(cfg.read())

    # Step 2: Load the ontology file corresponding to the most recent backup
    ONTO = or2.get_ontology(str(MAIN_DIR / (str(SAVE_INT - 1) + '.owl'))).load()

    # Step 3: Extract specific ontology classes by their labels
    PARSABLE_FORMULA = ONTO.search(label='parsable_computation_formula')[0]
    HUMAN_READABLE_FORMULA = ONTO.search(label='human_readable_formula')[0]
    UNIT_OF_MEASURE = ONTO.search(label='unit_of_measure')[0]
    DEPENDS_ON = ONTO.search(label='depends_on')[0]

    # Extract ontology classes for operations, machines, and KPIs
    OPERATION_CASS = ONTO.search(label='operation')[0]
    MACHINE_CASS = ONTO.search(label='machine')[0]
    KPI_CLASS = ONTO.search(label='kpi')[0]

    import os
    os.environ["KAGGLE_CONFIG_DIR"] = "./backups"

    # Confirm successful initialization
    print("Ontology successfully initialized!")

        
def _generate_hash_code(input_data):
    """
    Generates a compact, alphanumeric hash code for a given input string.
    The function uses a secure SHA-256 hash algorithm and ensures no '-' or '_'
    characters appear in the output.
    
    Parameters:
    - input_data (str): The input string to generate the hash code from.

    Returns:
    - hash_code (str): A shortened alphanumeric hash code derived from the input data.
    """
    # Create a SHA-256 hash object and compute the hash of the input string
    hash_obj = hashlib.sha256(input_data.encode())
    
    # Encode the binary hash digest into a URL-safe Base64 string
    hash_b64 = base64.urlsafe_b64encode(hash_obj.digest()).decode()
    
    # Remove '-' and '_' by replacing them (optional, can just use hexadecimal)
    hash_b64_clean = hash_b64.replace('-', '').replace('_', '')
    
    # Truncate the clean Base64 string to 22 characters for compactness
    hash_code = hash_b64_clean[:22]
    
    return hash_code

def _get_similarity(a, b, method='w2v'):
    """
    Calculates the similarity between two strings using the specified method.
    The function can use either Word2Vec (w2v) or Levenshtein distance to compute the similarity.

    Parameters:
    - a (str): The first string to compare.
    - b (str): The second string to compare.
    - method (str, optional): The method used to compute similarity. Can be 'levenshtein' for Levenshtein distance.

    Returns:
    - similarity (float): A similarity score between 0 and 1. A score of 1 indicates identical strings.
    """
    
    # Check if the method chosen is 'levenshtein' for Levenshtein distance
    if method == 'levenshtein':
        # Compute the Levenshtein distance between the two strings
        distance = Levenshtein.distance(a, b)
        
        # Calculate the similarity as 1 - (distance / max length of the two strings)
        # This converts the distance into a similarity score between 0 and 1
        similarity = 1 - distance / max(len(a), len(b))
        
        return similarity
    else:
        print('METHOD NOT FOUND')
        return 

def _backup():
    global SAVE_INT
    coarse_grain = 8
    max_fine_b = 3
    max_coarse_b = 2
    
    ONTO.save(file=str(MAIN_DIR / (str(SAVE_INT) + '.owl')), format="rdfxml")
    
    if (SAVE_INT - max_fine_b)%coarse_grain == 0:
        if (SAVE_INT - max_fine_b)/coarse_grain - max_coarse_b > 0:
            os.remove(str(MAIN_DIR / (str(SAVE_INT - max_fine_b - max_coarse_b*coarse_grain) + '.owl')))
    else:        
        if SAVE_INT - max_fine_b > 0:
            os.remove(str(MAIN_DIR / (str(SAVE_INT - max_fine_b) + '.owl')))

    
    SAVE_INT = SAVE_INT + 1
    with open(CONFIG_PATH, 'w+') as cfg:
        cfg.write(str(SAVE_INT))
    
        
        
def get_formulas(kpi):
    """
    This function retrieves and unrolls formulas associated with a given KPI label.
    It recursively searches for nested KPIs in the formulas and expands them until
    all formulas are fully unrolled.

    Parameters:
    - kpi (str): The label of the KPI whose formula is to be retrieved and unrolled.
    - onto (Ontology): An ontology object used to search for KPI entities based on their label.

    Returns:
    - kpi_formula (dict): A dictionary containing all formulas found during the unrolling process, including nested ones.
    """
    
    # Search for the KPI label in the ontology
    target = ONTO.search(label=kpi)
    
    # Check if there is more than one match for the KPI label
    if not target or len(target) > 1:
        print("DOUBLE OR NONE REFERENCED KPI")  # Print error if multiple references found
        return
    
    # Select the first match from the search result
    target = target[0]
    
    # Initialize lists to store unrolled formulas, KPI names, and labels
    # `to_unroll` will hold formulas to expand, starting with the current KPI's formula
    to_unroll = [PARSABLE_FORMULA[target][0]]
    
    # `kpi_formula` will store all formulas found and unrolled
    kpi_formula = {kpi:PARSABLE_FORMULA[target][0]}
    
    # While there are formulas to unroll, continue expanding
    while to_unroll:
        # Pop the first formula to process and search for KPI references in it
        matches = re.findall(r'R°[A-Za-z_]+°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', to_unroll.pop(0))
        
        # Iterate through all matches found for KPI references in the formula
        for match in matches:
            # Extract the KPI name from the reference using regex
            kpi_name = re.match(r'R°([A-Za-z_]+)°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', match).group(1)

            # Search for the KPI name in the ontology
            target = ONTO.search(label=kpi_name)
            
            # Check if there is more than one match for the KPI name
            if not target or len(target) > 1:
                print("DOUBLE OR NONE REFERENCED KPI")  # Print error if multiple references found
                return
            
            # Select the first match from the search result
            target = target[0]
            
            # Add the formula of the found KPI to the `to_unroll` list for further expansion
            to_unroll.append(PARSABLE_FORMULA[target][0])
            
            # Append the formula, KPI name, and label to their respective lists
            kpi_formula[kpi_name] = PARSABLE_FORMULA[target][0]

    # Return the list of formulas, KPI labels, and KPI names
    return kpi_formula

def get_closest_kpi_formulas(kpi, method='levenshtein'):
    """
    Retrieves the closest Key Performance Indicator (KPI) formulas by comparing the given KPI
    with available formulas or instances, based on the selected similarity method.
    
    The function first attempts to retrieve existing formulas for the given KPI. If no formulas are found,
    it calculates the similarity between the KPI and other instances, and returns the formulas 
    associated with the closest instance.

    Parameters:
    - kpi (str): The Key Performance Indicator (KPI) whose formulas are to be found.
    - method (str, optional): The similarity method to use for comparison. Defaults to 'levenshtein'.
    
    Returns:
    - formulas (list): The list of formulas associated with the closest KPI, or formulas related to the given KPI.
    - similarity (float): The similarity score between the KPI and the closest instance (if applicable).
    """
    
    # Attempt to retrieve formulas associated with the given KPI
    ret = get_formulas(kpi)
    
    # If no formulas are found for the given KPI, compute the similarity with other instances
    if not ret:
        # Initialize variables to track the maximum similarity value and corresponding label
        max_val = -math.inf
        max_label = ''
        
        # Iterate through all available instances to find the closest match based on similarity
        for ind in ONTO.individuals():
            # Compute the similarity between the given KPI and the instance's label
            similarity = _get_similarity(kpi, ind.label.en.first(), method)
            
            # Update the maximum similarity and label if a closer match is found
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()
        
        # Return the formulas associated with the closest label, along with the similarity value
        return get_formulas(max_label), max_val
    
    else:
        # If formulas are found, return them with a perfect similarity score (1)
        return ret, 1


def add_kpi(superclass, label, description, unit_of_measure, parsable_computation_formula, 
            human_readable_formula=None, 
            depends_on_machine=False, 
            depends_on_operation=False):
    """
    Adds a new KPI (Key Performance Indicator) to the ontology if it meets the specified criteria.
    The function ensures that the KPI label does not already exist, validates the superclass, and 
    associates formulas and dependencies with the new KPI.

    Parameters:
    - superclass (str): The label of the superclass to which this KPI belongs.
    - label (str): The unique label for the new KPI.
    - description (str): A descriptive text explaining the KPI.
    - unit_of_measure (str): The unit in which this KPI is measured.
    - parsable_computation_formula (str): A machine-parsable formula for computing the KPI.
    - human_readable_formula (str, optional): A human-readable formula for computing the KPI.
      Defaults to `parsable_computation_formula` if not provided.
    - depends_on_machine (bool, optional): Indicates if the KPI depends on the machine. Defaults to False.
    - depends_on_operation (bool, optional): Indicates if the KPI depends on the operation. Defaults to False.

    Returns:
    - None: Prints error messages or completes the KPI creation process.
    """
    
    # Default the human-readable formula to the parsable computation formula if not provided
    if not human_readable_formula:
        human_readable_formula = parsable_computation_formula
    
    # Step 1: Search for the KPI label in the ontology
    target = ONTO.search(label=label)
    if target:
        # If the label already exists, print an error and terminate
        print("KPI LABEL ALREADY EXISTS")
        return
    
    # Step 2: Search for the superclass in the ontology
    target = ONTO.search(label=superclass)
    if not target or len(target) > 1:
        # If there is no match or multiple matches for the superclass, print an error and terminate
        print("DOUBLE OR NONE REFERENCED KPI")
        return
    
    # Use the first match as the valid superclass
    target = target[0]
    
    # Step 3: Validate that the found superclass is derived from or is the base KPI class
    valid_superclass = any(KPI_CLASS in cls.ancestors() for cls in target.is_a) or KPI_CLASS == target
    if not valid_superclass:
        # If the superclass is not valid, print an error and terminate
        print("NOT A VALID SUPERCLASS")
        return
    else:
        # Step 4: Create the new KPI instance
        new_el = target(_generate_hash_code(label))  # Generate a unique identifier for the KPI
        new_el.label = [ or2.locstr(label, lang='en')]                       # Set the KPI label
        new_el.description = [or2.locstr(description, lang='en')]          # Set the KPI description
        
        UNIT_OF_MEASURE[new_el] = [or2.locstr(unit_of_measure, lang='en')] # Set the KPI's unit of measurement
        
        # Step 5: Store the formulas in the global formula dictionaries
        HUMAN_READABLE_FORMULA[new_el] = [or2.locstr(human_readable_formula, lang='en')]
        PARSABLE_FORMULA[new_el] = [parsable_computation_formula]
        
        
        # Step 6: Add dependencies if specified
        if depends_on_machine and depends_on_operation:
            DEPENDS_ON[new_el] = [MACHINE_CASS, OPERATION_CASS]      # Associate with machine and operation if applicable
        elif depends_on_operation:
            DEPENDS_ON[new_el] = [OPERATION_CASS]    # Associate with operation if applicable
        elif depends_on_machine:
            DEPENDS_ON[new_el] = [MACHINE_CASS]    # Associate with machine if applicable
            
        _backup()

def get_onto_path():
    """
    Constructs and returns the file path to the last ontology backup file.

    Returns:
    - pathlib.Path: The full file path to the ontology file, as a `Path` object.
    """
    return MAIN_DIR / (str(SAVE_INT - 1) + '.owl')


def get_instances(owl_class_label):
    """
    Retrieves all instances of an OWL class based on the provided label. 
    The function searches the ontology for a class or instance matching the given label.
    If the target is a class, it collects all instances, including those of its subclasses.
    If the target is an individual instance, the function returns the label of that instance.
    If no match or multiple matches are found, an error message is printed, and the function exits.

    Parameters:
    - owl_class_label (str): The label of the OWL class or instance to search for.

    Returns:
    - list: A list of labels for the instances associated with the provided OWL class or instance.
            If no valid instances are found or the input is invalid, an empty list is returned.
    """
    
    # Step 1: Search for the OWL class or instance based on the provided label
    target = ONTO.search(label=owl_class_label)
    
    if not target or len(target) > 1:
        # If no match or multiple matches are found, print an error and terminate
        print("DOUBLE OR NONE REFERENCED KPI")
        return
    
    # Use the first match as the valid target
    target = target[0]

    print(target)
    
    # Initialize a set to store instances (avoids duplicates)
    instances = set()
    
    # Step 2: Check if the target is a class (ThingClass) or an individual instance (Thing)
    if isinstance(target, or2.ThingClass):
        # If the target is a class, process the class and its subclasses
        classes_to_process = [target]

        while classes_to_process:
            current_class = classes_to_process.pop()
            
            # Add all instances of the current class to the set
            for i in current_class.instances():
                instances.add(i.label.en.first())
                
            # Add all subclasses of the current class to the list of classes to process
            classes_to_process.extend(current_class.subclasses())
            
    elif isinstance(target, or2.Thing):
        # If the target is an individual instance, add it directly to the set
        instances.add(owl_class_label)
        
    else:
        # If the target is neither a class nor an instance, print an error message
        print("INPUT IS NEITHER A CLASS NOR A INSTANCE")
    
    # Step 3: Return the instances as a list (to make it more user-friendly)
    return list(instances)

def get_closest_class_instances(owl_class_label, method='levenshtein'):
    """
    Retrieves the closest matching instances for a given OWL class label based on a similarity method.
    This function first tries to find instances based on the exact label. If no matches are found,
    it computes the similarity between the provided label and the labels of all available classes
    and individuals in the ontology, selecting the one with the highest similarity.

    Parameters:
    - owl_class_label (str): The label of the OWL class or instance to search for.
    - method (str): The method used to calculate similarity between labels. Default is 'levenshtein'.

    Returns:
    - tuple: A tuple containing:
        - A list of labels for the instances closest to the provided OWL class or instance.
        - The similarity score of the closest match (1 if an exact match is found).
    """

    # Step 1: Try to get the instances of the provided OWL class label
    ret = get_instances(owl_class_label)
    
    if not ret:
        # Step 2: If no exact match is found, we need to calculate the similarity between the provided label and
        # the labels of all available classes and individuals in the ontology.
        
        max_val = -math.inf  # Initialize the maximum similarity score to negative infinity.
        max_label = ''  # Initialize an empty string to store the label of the closest match.
        
        # Step 3: Compare the input label with all the class labels in the ontology.
        for ind in ONTO.classes():
            similarity = _get_similarity(owl_class_label, ind.label.en.first(), method)  # Compute similarity.
            
            # If the current similarity is higher than the previous max, update max_val and max_label.
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()
        
        # Step 4: If no match was found in the classes, check among individuals.
        for ind in ONTO.individuals():
            similarity = _get_similarity(owl_class_label, ind.label.en.first(), method)  # Compute similarity.
            
            # If the current similarity is higher than the previous max, update max_val and max_label.
            if max_val < similarity:
                max_val = similarity
                max_label = ind.label.en.first()

        # Step 5: Print and return the closest match's instances and similarity score.
        return get_instances(max_label), max_val
    
    else:
        # Step 6: If exact instances were found in the first step, return them along with a similarity score of 1 (exact match).
        return ret, 1
