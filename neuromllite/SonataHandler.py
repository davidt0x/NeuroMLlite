#
#
#   A class to write to the Sonata format...
#
#

from neuromllite.utils import print_v
from neuromllite.DefaultNetworkHandler import DefaultNetworkHandler

import h5py
import numpy as np
from neuromllite.utils import save_to_json_file

class SonataHandler(DefaultNetworkHandler):
        
    positions = {}
    pop_indices = {}
    
    DEFAULT_NODE_GROUP_ID = 0
    pop_type_ids = {}
    node_type_csv_info = {}
        

    def __init__(self):
        print_v("Initiating Sonata handler")


    def handle_document_start(self, id, notes):
            
        print_v("Parsing for Sonata export: %s"%id)
        
        self.config_file_info = {}
        self.config_file_info["network"]="./circuit_config.json"
        self.config_file_info["simulation"]="./simulation_config.json"
        
        self.circuit_file_info = {}
        self.circuit_file_info["manifest"]={}
        self.circuit_file_info["manifest"]['$NETWORK_DIR']='./'
        self.circuit_file_info["manifest"]['$COMPONENT_DIR']='./'
        
        self.circuit_file_info["networks"]={}
        self.circuit_file_info["networks"]["nodes"]=[]
        self.circuit_file_info["networks"]["nodes"].append({})
        
        
    def finalise_document(self):
                
        print_v("Writing file...: %s"%id)
        self.sonata_nodes.close()
        
        node_type_filename = "%s_node_types.csv"%self.network_id
        
        self.circuit_file_info["networks"]["nodes"][0]["node_types_file"] = "$NETWORK_DIR/%s"%node_type_filename
        
        node_type_file = open(node_type_filename, "w")
        header = ''
        for var in self.node_type_csv_info[self.node_type_csv_info.keys()[0]]:
            header+='%s '%var
        node_type_file.write(header+'\n') 
        
        for pop_id in self.node_type_csv_info:
            line = ''
            for var in self.node_type_csv_info[pop_id]:
                line+='%s '%self.node_type_csv_info[pop_id][var]
            node_type_file.write(line+'\n') 
                
        node_type_file.close()
        
        
        save_to_json_file(self.config_file_info, 'config.json', indent=2)
        save_to_json_file(self.circuit_file_info, 'circuit_config.json', indent=2)
        
        

    def handle_network(self, network_id, notes, temperature=None):
            
        print_v("Network: %s"%network_id)
        self.network_id = network_id
        
        if temperature:
            print_v("  Temperature: "+temperature)
        if notes:
            print_v("  Notes: "+notes)
            
        nodes_filename = "%s_nodes.sonata.h5"%network_id
        self.circuit_file_info["networks"]["nodes"][0]["nodes_file"] = "$NETWORK_DIR/%s"%nodes_filename
            
        self.sonata_nodes = h5py.File(nodes_filename, "w")
        self.sonata_nodes.attrs.create('version',[0,1], dtype=np.uint32)
        self.sonata_nodes.attrs.create('magic', np.uint32(0x0A7A))
        

    def handle_population(self, 
                          population_id, 
                          component, size=-1, 
                          component_obj=None, 
                          properties={}):
        
        sizeInfo = " as yet unspecified size"
        if size>=0:
            sizeInfo = ", size: "+ str(size)+ " cells"
        if component_obj:
            compInfo = " (%s)"%component_obj.__class__.__name__
        else:
            compInfo=""
            
        print_v("Population: "+population_id+", component: "+component+compInfo+sizeInfo)
        
        self.sonata_nodes.create_group("nodes/%s"%population_id)
        self.sonata_nodes.create_group("nodes/%s/0"%population_id)
        
        node_type_id = 100+len(self.pop_type_ids)
        self.pop_type_ids[population_id] = node_type_id
        
        self.node_type_csv_info[population_id] = {}
        self.node_type_csv_info[population_id]['node_type_id'] = node_type_id
        self.node_type_csv_info[population_id]['pop_name'] = population_id
        self.node_type_csv_info[population_id]['model_name'] = component
        self.node_type_csv_info[population_id]['location'] = '???'
        self.node_type_csv_info[population_id]['model_template'] = component
        self.node_type_csv_info[population_id]['model_type'] = component
        self.node_type_csv_info[population_id]['dynamics_params'] = 'None'
        
 
    def handle_location(self, id, population_id, component, x, y, z):
        
        if not population_id in self.positions:
            self.positions[population_id] = np.array([[x,y,z]])
            self.pop_indices[population_id] = np.array([id])
        else:
            self.positions[population_id] = np.concatenate((self.positions[population_id], [[x,y,z]]))
            self.pop_indices[population_id] = np.concatenate((self.pop_indices[population_id], [id]))
        
        
    def finalise_population(self, population_id):
        
        self.sonata_nodes.create_dataset("nodes/%s/0/positions"%population_id, data=self.positions[population_id])
        self.sonata_nodes.create_dataset("nodes/%s/node_group_index"%population_id, data=self.pop_indices[population_id])
        self.sonata_nodes.create_dataset("nodes/%s/node_group_id"%population_id, data=[self.DEFAULT_NODE_GROUP_ID for i in self.pop_indices[population_id]])
        self.sonata_nodes.create_dataset("nodes/%s/node_id"%population_id, data=self.pop_indices[population_id])
        
        self.sonata_nodes.create_dataset("nodes/%s/node_type_id"%population_id, data=[self.pop_type_ids[population_id] for i in self.pop_indices[population_id]])

        
            

'''
    def handle_projection(self, projName, prePop, postPop, synapse, hasWeights=False, hasDelays=False, type="projection", synapse_obj=None, pre_synapse_obj=None):

        synInfo=""
        if synapse_obj:
            synInfo += " (syn: %s)"%synapse_obj.__class__.__name__
            
        if pre_synapse_obj:
            synInfo += " (pre comp: %s)"%pre_synapse_obj.__class__.__name__

        print_v("Projection: "+projName+" ("+type+") from "+prePop+" to "+postPop+" with syn: "+synapse+synInfo)
        
        exec('self.projection__%s_conns = []'%(projName))


    #
    #  Should be overridden to handle network connection
    #  
    def handle_connection(self, projName, id, prePop, postPop, synapseType, \
                                                    preCellId, \
                                                    postCellId, \
                                                    preSegId = 0, \
                                                    preFract = 0.5, \
                                                    postSegId = 0, \
                                                    postFract = 0.5, \
                                                    delay = 0, \
                                                    weight = 1):
        
        self.print_connection_information(projName, id, prePop, postPop, synapseType, preCellId, postCellId, weight)
        print_v("Src cell: %d, seg: %f, fract: %f -> Tgt cell %d, seg: %f, fract: %f; weight %s, delay: %s ms" % (preCellId,preSegId,preFract,postCellId,postSegId,postFract, weight, delay))
         
        import random
        exec('self.projection__%s_conns.append((%s,%s,float(%s),float(%s)))'%(projName,preCellId,postCellId,weight,delay))

        
    #
    #  Should be overridden to handle end of network connection
    #  
    def finalise_projection(self, projName, prePop, postPop, synapse=None, type="projection"):
   
        print_v("Projection finalising: "+projName+" from "+prePop+" to "+postPop+" completed")
        
        #exec('print(self.projection__%s_conns)'%projName)
        exec('self.projection__%s_connector = self.sim.FromListConnector(self.projection__%s_conns, column_names=["weight", "delay"])'%(projName,projName))

        exec('self.projections["%s"] = self.sim.Projection(self.populations["%s"],self.populations["%s"], ' % (projName,prePop,postPop) + \
                                                          'connector=self.projection__%s_connector, ' % projName + \
                                                          'synapse_type=self.sim.StaticSynapse(weight=%s, delay=%s), ' % (1,5) + \
                                                          'receptor_type="%s", ' % (self.receptor_types[synapse]) + \
                                                          'label="%s")'%projName)
        
        #exec('print(self.projections["%s"].describe())'%projName)
        

        
    #
    #  Should be overridden to create input source array
    #  
    def handle_input_list(self, inputListId, population_id, component, size, input_comp_obj=None):
        
        self.print_input_information(inputListId, population_id, component, size)
        
        if size<0:
            self.log.error("Error! Need a size attribute in sites element to create spike source!")
            return
             
        self.input_info[inputListId] = (population_id, component)
        
    #
    #  Should be overridden to to connect each input to the target cell
    #  
    def handle_single_input(self, inputListId, id, cellId, segId = 0, fract = 0.5, weight=1):
        
        print_v("Input: %s[%s], cellId: %i, seg: %i, fract: %f, weight: %f" % (inputListId,id,cellId,segId,fract,weight))
        
        population_id, component = self.input_info[inputListId]
        
        #exec('print  self.POP_%s'%(population_id))
        #exec('print  self.POP_%s[%s]'%(population_id,cellId))
       
        exec('self.POP_%s[%s].inject(self.input_sources[component]) '%(population_id,cellId))
        #exec('self.input_sources[component].inject_into(self.populations["%s"])'%(population_id))
        
        #exec('pulse = self.sim.DCSource(amplitude=0.9, start=19, stop=89)')
        #pulse.inject_into(pop_pre)
        #exec('self.populations["pop0"][0].inject(pulse)')

        
    #
    #  Should be overridden to to connect each input to the target cell
    #  
    def finalise_input_source(self, inputName):
        print_v("Input : %s completed" % inputName)
        
'''
