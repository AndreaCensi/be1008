from .vehicles_list import vehicles_list_A
from .simulation import simulate_vehicle_random

def main():
    output = 'simulations'
    
    vehicles = dict(vehicles_list_A())
    
    for name, vehicle in vehicles.items():
        simulate_vehicle_random(output, name, vehicle)
    
    
if __name__ == '__main__':
    main()
