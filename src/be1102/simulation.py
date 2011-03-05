from numpy import  array
from pybv import BVException, assert_reasonable_value, TexturedRaytracer, get_safe_pose
import numpy as np
from pybv.worlds.world_generation import create_random_world
import os
import tables


class RandomPoseGenerator:
    
    def __init__(self, radius, safe_zone):
        self.safe_zone = safe_zone
        self.radius = radius
        
    def set_map(self, world):
        self.raytracer = TexturedRaytracer()
        self.raytracer.set_map(world)
        
    def generate_pose(self):
        return get_safe_pose(
                             raytracer=self.raytracer,
                             world_radius=self.radius,
                             safe_zone=self.safe_zone, num_tries=1000) 

def random_commands_generator(niteration, vehicle): #@UnusedVariable
    ''' Generates commands uniformly between -1 and 1 '''
    ncommands = 3 # XXX
    return  (np.random.rand(ncommands) - 0.5) * 2 #


def simulate_vehicle_random(output, vid, vehicle, num_iterations):
    dir = os.path.join(output, vid, 'logs', 'random_poses')
    filename = os.path.join(dir, 'log.bpi')
    if os.path.exists(filename):
        f = tables.openFile(filename, 'r+')
    else:
        f = tables.openFile(filename, 'w')
        
    vehicle.
    if not f.
    tablename = 
    if ''
    
    
def simulate_vehicle_random_slave(vehicle):
    radius = 10
    num_iterations = 100
    generate_world_every = 5
    seed = 0
    dt = 0.1
    safe_zone = 0.5
    
    def random_world_generator():
        ''' Generates a random world. '''
        return create_random_world(radius=radius,
                                   num_lines=10, num_circles=10)

    
    pose_generator = RandomPoseGenerator(radius, safe_zone)
    world_generator = random_world_generator
    commands_generator = random_commands_generator
    
    observations = random_motion_simulation(
                    vehicle=vehicle,
                    world_generator=world_generator,
                    pose_generator=pose_generator,
                    commands_generator=commands_generator,
                    num_iterations=num_iterations,
                    dt=dt,
                    generate_world_every=generate_world_every)
    
    for observation in observations:
        yield observation


def random_motion_simulation(
    vehicle,
    world_generator,
    pose_generator,
    commands_generator,
    num_iterations,
    dt,
    generate_world_every=5):
    """
    
    world
    vehicle
    random_pose_gen:  lambda iteration -> RigidBodyState
    random_commands_gen:  lambda iteration, vehicle -> castable to float list
    processing_class
    """
    
    current_iteration = 0
    world = None
    while current_iteration < num_iterations:
        # sample a random world
        if  (world is None or  
             current_iteration % generate_world_every == 0):
            world = world_generator()
            # give the map to the pose generator
            pose_generator.set_map(world)
            # sets the map for all sensors
            vehicle.set_map(world)
    
        state1 = pose_generator.generate_pose()
        if state1 is None:
            raise BVException('Could not generate a random pose.')

        commands = commands_generator(current_iteration, vehicle)
        state2 = vehicle.dynamics.evolve_state(state1, commands, dt)
        
        data = vehicle.compute_observations_and_derivatives(state1, state2, dt)
        data.commands = array(commands) 
         
        yield data
