import random
import string
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import kb_interface as kbi

def random_modify(s, n):
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



kbi.start()

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




print('Testing get_closest_class_instances correct label')
print('----------------------------------------------------------------------------')
for cl in kbi.ONTO.classes():
    
    ret = kbi.get_closest_kpi_formulas(cl.label.en.first())
    print('Requested:', cl.label.en.first())
    print('Received:', ret)
    print('----------------------------------------------------------------------------')

print('Testing get_closest_class_instances wrong label ({modify_count} modify)')
print('----------------------------------------------------------------------------')
for cl in kbi.ONTO.classes():
    
    ret = kbi.get_closest_kpi_formulas(random_modify(cl.label.en.first(), modify_count))
    print('Requested:', cl.label.en.first())
    print('Received:', ret)
    print('----------------------------------------------------------------------------')




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
print('Deleting generated files')
for f in os.listdir('../backups'): 
    if f != '0.owl' and os.path.isfile(os.path.join('../backups', f)): 
        os.remove(os.path.join('../backups', f)) 
with open('../config.cfg', 'w+') as cfg:
        cfg.write(str(1))