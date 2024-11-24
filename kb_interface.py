import owlready2 as or2
import re
import hashlib
import base64

onto = or2.get_ontology('./KB.owl').load()

PARSABLE_FORMULA = onto.search(label = 'parsable_computation_formula')[0]
HUMAN_READABLE_FORMULA = onto.search(label = 'human_readable_formula')[0]
UNIT_OF_MEASURE = onto.search(label = 'unit_of_measure')[0]
DEPENDS_ON = onto.search(label = 'depends_on')[0]

OPERATION_CASS = onto.search(label = 'operation')[0]
MACHINE_CASS = onto.search(label = 'machine')[0]
KPI_CLASS = onto.search(label = 'kpi')[0]
LABEL = 'label'

def generate_hash_code(input_data):
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

def get_formulas(kpi, onto):
    """
    This function retrieves and unrolls formulas associated with a given KPI label.
    It recursively searches for nested KPIs in the formulas and expands them until
    all formulas are fully unrolled.

    Parameters:
    - kpi (str): The label of the KPI whose formula is to be retrieved and unrolled.
    - onto (Ontology): An ontology object used to search for KPI entities based on their label.

    Returns:
    - f_list (list): A list of all formulas found during the unrolling process, including nested ones.
    - kpi_label_list (list): A list of the original KPI labels (input `kpi` and any nested ones found).
    - kpi_list (list): A list of KPI names corresponding to the formulas in `f_list`.
    """
    
    # Search for the KPI label in the ontology
    target = onto.search(label=kpi)
    
    # Check if there is more than one match for the KPI label
    if not target or len(target) > 1:
        print("DOUBLE OR NONE REFERENCED KPI")  # Print error if multiple references found
        return
    
    # Select the first match from the search result
    target = target[0]
    
    # Initialize lists to store unrolled formulas, KPI names, and labels
    # `to_unroll` will hold formulas to expand, starting with the current KPI's formula
    to_unroll = [PARSABLE_FORMULA[target][0]]
    
    # `f_list` will store all formulas found and unrolled
    f_list = [PARSABLE_FORMULA[target][0]]
    
    # `kpi_list` will store names of the KPIs as they are found
    kpi_list = [target.get_name()]
    
    # `kpi_label_list` will store the original KPI labels
    kpi_label_list = [kpi]
    
    # While there are formulas to unroll, continue expanding
    while to_unroll:
        # Pop the first formula to process and search for KPI references in it
        matches = re.findall(r'R°[A-Za-z_]+°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', to_unroll.pop(0))
        
        # Iterate through all matches found for KPI references in the formula
        for match in matches:
            # Extract the KPI name from the reference using regex
            kpi_name = re.match(r'R°([A-Za-z_]+)°[A-Za-z_]*°[A-Za-z_]*°[A-Za-z_]*°', match).group(1)

            # Search for the KPI name in the ontology
            target = onto.search(label=kpi_name)
            
            # Check if there is more than one match for the KPI name
            if not target or len(target) > 1:
                print("DOUBLE OR NONE REFERENCED KPI")  # Print error if multiple references found
                return
            
            # Select the first match from the search result
            target = target[0]
            
            # Add the formula of the found KPI to the `to_unroll` list for further expansion
            to_unroll.append(PARSABLE_FORMULA[target][0])
            
            # Append the formula, KPI name, and label to their respective lists
            f_list.append(PARSABLE_FORMULA[target][0])
            kpi_list.append(target.get_name())
            kpi_label_list.append(kpi_name)
    
    # Return the list of formulas, KPI labels, and KPI names
    return f_list, kpi_list, kpi_label_list

# TODO: Greatly improve the intelligence of the method
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

    Side Effects:
    - Modifies the ontology to add the new KPI.
    - Updates global mappings (e.g., HUMAN_READABLE_FORMULA, PARSABLE_FORMULA).
    """
    
    # Default the human-readable formula to the parsable computation formula if not provided
    if not human_readable_formula:
        human_readable_formula = parsable_computation_formula
    
    # Step 1: Search for the KPI label in the ontology
    target = onto.search(label=label)
    if target:
        # If the label already exists, print an error and terminate
        print("KPI LABEL ALREADY EXISTS")
        return
    
    # Step 2: Search for the superclass in the ontology
    target = onto.search(label=superclass)
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
        new_el = target(generate_hash_code(label))  # Generate a unique identifier for the KPI
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
