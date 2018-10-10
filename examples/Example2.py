from neuromllite import RandomLayout, Cell, Synapse, InputSource, Input, RectangularRegion
from neuromllite.NetworkGenerator import generate_network
from neuromllite.NetworkGenerator import generate_neuroml2_from_network
from neuromllite.DefaultNetworkHandler import DefaultNetworkHandler
from neuromllite.utils import load_network_json

################################################################################
###   Reuse network from Example1

filename = 'Example1_TestNetwork.json'
net = load_network_json(filename)

net.notes = "A simple network with 2 populations & projection between them. "+ \
            "Cells are specified to be NeuroML 2 HH cell models & pre population " \
            "is given a spiking input."


################################################################################
###   Add some elements to the network & save new JSON

r1 = RectangularRegion(id='region1', x=0,y=0,z=0,width=1000,height=100,depth=1000)
r2 = RectangularRegion(id='region2', x=0,y=200,z=0,width=1000,height=100,depth=1000)
net.regions.append(r1)
net.regions.append(r2)

del net.populations[0].fields['unstructured']
del net.populations[1].fields['unstructured']
net.populations[0].random_layout = RandomLayout(size=5, region=r1.id)
net.populations[1].random_layout = RandomLayout(size=10, region=r2.id)

net.populations[0].component = 'hhcell'
net.populations[1].component = 'hhcell'

net.cells.append(Cell(id='hhcell', neuroml2_source_file='test_files/hhcell.cell.nml'))
net.synapses.append(Synapse(id='ampa', neuroml2_source_file='test_files/ampa.synapse.nml'))

input_source = InputSource(id='poissonFiringSyn', neuroml2_source_file='test_files/inputs.nml')
net.input_sources.append(input_source)

net.inputs.append(Input(id='stim_%s'%net.populations[0].id,
                            input_source=input_source.id,
                            population=net.populations[0].id,
                            percentage=80))

print(net.to_json())
new_file = net.to_json_file('Example2_%s.json'%net.id)


################################################################################
###   Export to some formats
###   Try:
###        python Example2.py -nml

from neuromllite.NetworkGenerator import check_to_generate_or_run
from neuromllite import Simulation
import sys

check_to_generate_or_run(sys.argv, Simulation(id='SimExample2',network=new_file))
                               