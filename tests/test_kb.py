import random
import string
import os
import sys
import time
import pathlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import kb_interface as kbi

def random_modify(s, n):
    if n < len(s): 
        n = max(len(s) - 3, 0)
        
    s = list(s)  # Convert the string to a list for easier modification
    for _ in range(n):
        operation = random.choice(['insert', 'replace', 'remove'])
        
        if operation == 'insert':
            position = random.randint(0, len(s))  # Random position to insert the character
            char = random.choice(string.ascii_letters + string.digits)  # Random character
            s.insert(position, char)
        
        elif operation == 'replace':
            if s:  # If the list is not empty
                position = random.randint(0, len(s) - 1)
                char = random.choice(string.ascii_letters + string.digits)
                s[position] = char
        
        elif operation == 'remove':
            if s:  # If the list is not empty
                position = random.randint(0, len(s) - 1)
                del s[position]
    
    return ''.join(s)  # Return the modified string

modify_count = 7
#to_test = ['get_closest_object_properties']
to_test = ['add_delete_kpi', 'add_delete_operation', 'add_delete_process']

random.seed(69)

kbi.start()

if 'get_closest_kpi_formulas' in to_test:
    print('Testing get_closest_kpi_formulas correct label')
    print('----------------------------------------------------------------------------')
    for lab in kbi.ONTO.search(label='kpi')[0].instances():
        
        ret = kbi.get_closest_kpi_formulas(lab.label.en.first())
        print('Requested:', lab.label.en.first())
        print('Received:',ret)
        print('----------------------------------------------------------------------------')

    print('Testing get_closest_kpi_formulas wrong label ({modify_count} modify)')
    print('----------------------------------------------------------------------------')
    for lab in kbi.ONTO.search(label='kpi')[0].instances():
        
        ret = kbi.get_closest_kpi_formulas(random_modify(lab.label.en.first(), modify_count))
        print('Requested:', lab.label.en.first())
        print('Received:',ret)
        print('----------------------------------------------------------------------------')



if 'get_closest_class_instances' in to_test:
    print('Testing get_closest_class_instances correct label')
    print('----------------------------------------------------------------------------')
    for cl in kbi.ONTO.classes():
        print(cl.label)
        ret = kbi.get_closest_class_instances(cl.label.en.first())
        print('Requested:', cl.label.en.first())
        print('Received:', ret)
        print('----------------------------------------------------------------------------')

    print('Testing get_closest_class_instances wrong label ({modify_count} modify)')
    print('----------------------------------------------------------------------------')
    for cl in kbi.ONTO.classes():
        
        ret = kbi.get_closest_class_instances(random_modify(cl.label.en.first(), modify_count))
        print('Requested:', cl.label.en.first())
        print('Received:', ret)
        print('----------------------------------------------------------------------------')

    for cl in kbi.ONTO.individuals():
        
        ret = kbi.get_closest_class_instances(random_modify(cl.label.en.first(), modify_count))
        print('Requested:', cl.label.en.first())
        print('Received:', ret)
        print('----------------------------------------------------------------------------')



if 'get_closest_object_properties' in to_test:
    print('Testing get_closest_object_properties wrong label ({modify_count} modify)')
    print('----------------------------------------------------------------------------')
    for cl in kbi.ONTO.classes():
       
        print('Requested:', cl.label.en.first()) 
        ret = kbi.get_closest_object_properties(random_modify(cl.label.en.first(), modify_count))

        print('Received:', ret)
        print('----------------------------------------------------------------------------')

    for cl in kbi.ONTO.individuals():
        
        print('Requested:', cl.label.en.first())
        ret = kbi.get_closest_object_properties(random_modify(cl.label.en.first(), modify_count))

        print('Received:', ret)
        print('----------------------------------------------------------------------------')
        
    for cl in kbi.ONTO.object_properties():
        
        print('Requested:', cl.label.en.first())
        ret = kbi.get_closest_object_properties(random_modify(cl.label.en.first(), modify_count))

        print('Received:', ret)
        print('----------------------------------------------------------------------------')
        
    for cl in kbi.ONTO.data_properties():
        
        print('Requested:', cl.label.en.first())
        ret = kbi.get_closest_object_properties(random_modify(cl.label.en.first(), modify_count))
        
        print('Received:', ret)
        print('----------------------------------------------------------------------------')
        
    for cl in kbi.ONTO.annotation_properties():
        if cl.label.en.first() != None:
            print('Requested:', cl.label.en.first())
            ret = kbi.get_closest_object_properties(random_modify(cl.label.en.first(), modify_count))

            print('Received:', ret)
            print('----------------------------------------------------------------------------')



if 'add_delete_kpi' in to_test:

    print('Testing add_kpi')
    for i in range(200):
        kbi.add_kpi(*['downtime_kpi', 'kpi' + str(i), 'desc','unit', 'form'])

    time.sleep(2)
            
    print('Testing delete_kpi')
    for i in range(200):
        kbi.delete_kpi('kpi' + str(i))

    time.sleep(2)
        

if 'add_delete_operation' in to_test:

    print('Testing add_operation')
    for i in range(200):
        kbi.add_operation(*['op' + str(i), 'desc'])

    time.sleep(2)
            
    print('Testing delete_operation')
    for i in range(200):
        kbi.delete_operation('op' + str(i))

    time.sleep(2)      
    
if 'add_delete_process' in to_test:
    op = ['working',
   'visual_inspection',
   'aerodynamic_testing',
   'riveting',
   'final_assembly',
   'welding_parts',
   'metal_cutting',
   'assembly',
   'idle',
   'rough_cutting',
   'precision_cutting',
   'final_welding',
   'riveting_assembly',
   'edge_welding',
   'pre_assembly',
   'parts_welding',
   'offline',
   'material_cutting',
   'stress_testing',
   'functional_testing',
   'quality_testing']
    for o in op:
        try:
            kbi.add_operation(o, 'desc')
        except:
            pass
        
    mach = ['testing_machine_3',
   'low_capacity_cutting_machine_1',
   'riveting_machine_1',
   'assembly_machine_2',
   'medium_capacity_cutting_machine_2',
   'medium_capacity_cutting_machine_1',
   'laser_welding_machine_1',
   'large_capacity_cutting_machine_2',
   'testing_machine_2',
   'laser_cutter',
   'assembly_machine_1',
   'assembly_machine_3',
   'testing_machine_1',
   'large_capacity_cutting_machine_1',
   'medium_capacity_cutting_machine_3',
   'laser_welding_machine_2']
    
    print('Testing add_process')
    for i in range(50):
        kbi.add_process(*['pr' + str(i), 'desc', [(random.choice(mach), random.choice(op)) for _ in range(random.randint(1, 10))]])

    time.sleep(2)
            
    print('Testing delete_process')
    for i in range(50):
        kbi.delete_process('pr' + str(i))

    time.sleep(2)     
        
print('Test ended')
