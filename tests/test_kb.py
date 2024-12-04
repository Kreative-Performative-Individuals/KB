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
to_test = ['get_closest_kpi_formulas', 'get_closest_class_instances', 'get_closest_object_properties', 'add_kpi']
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



if 'add_kpi' in to_test:
    test_create = [['downtime_kpi', 
                    'mean_time_between_failures', 
                    'Mean time between failures cumulative over machine-opertion pairs', 
                    's', 
                    'A°sum°mo[S°/[ R°bad_cycles_sum°T°m°o° ; R°time_sum°T°m°o° ]]',
                    'sum_M_O(bad_cycles_sum(T,m,o)/time_sum(T,m,o))',
                    True,
                    True], 
                
                ['utilization_kpi', 
                    'availability', 
                    'Percentage of machine uptime in respect to machine downtime over each machine-operation pairs', 
                    '%', 
                    'S°*[ S°/[ A°sum°m[ R°time_sum°T°m°working° ] ; S°+[ A°sum°m[ R°time_sum°T°m°idle° ] ; A°sum°m[ R°time_sum°T°m°offline° ] ] ] ; C°100° ]',
                    '(sum_M( time_sum(T,m,working)) / ( sum_M(time_sum(T,m,Idle)) + sum_M(time_sum(T,m,offline)) ) )*100',
                    True,
                    False]]

    print('Testing add_kpi and backups')
    for i in range(200):
        kbi.add_kpi(*['downtime_kpi', str(i), 'desc','unit', 'form'])

    time.sleep(2)
            
    # Definisci il percorso della cartella
    folder = pathlib.Path('backups')

    # Verifica che la cartella esista
    if folder.exists() and folder.is_dir():
        # Elimina tutti i file nella cartella, eccetto 0.owl
        for file in folder.iterdir():
            if file.is_file() and file.name != '0.owl':
                file.unlink()  # Rimuove il file
                
    with open('config.cfg', 'w+') as cfg:
        cfg.write(str(1)) 
        
print('Test ended')