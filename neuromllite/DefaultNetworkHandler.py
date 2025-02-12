#
#
#   A class to handle events from the NeuroMLHdf5Parser, etc.
#   This should be overridden by simulator specific implementations.
#   Parsing classes, e.g. NetworkBuilder should call the appropriate
#   function here when a cell location, connection, etc. is encountered.
#
#   Use of this handler class should mean that the network setup is
#   independent of the source of the network info (XML or HDF5 based NeuroML
#   files for example) and the instantiator of the network objects (NetManagerNEURON
#   or PyNN based setup class)
#
#   Author: Padraig Gleeson
#
#   This file has been developed as part of the neuroConstruct project
#   This work has been funded by the Medical Research Council & Wellcome Trust
#
#

from neuromllite.utils import print_v


class DefaultNetworkHandler:

    #
    #  Internal info method, can be reused in overriding classes for debugging
    #
    def print_location_information(self, id, population_id, component, x, y, z):
        position = "(%s, %s, %s)" % (x, y, z)
        print_v(
            "  Location "
            + str(id)
            + " of population: "
            + population_id
            + ", component: "
            + component
            + ": "
            + position
        )

    #
    #  Internal info method, can be reused in overriding classes for debugging
    #
    def print_connection_information(
        self, projName, id, prePop, postPop, synapseType, preCellId, postCellId, weight
    ):
        print_v(
            "  Connection "
            + str(id)
            + " of: "
            + projName
            + ": cell "
            + str(preCellId)
            + " in "
            + prePop
            + " -> cell "
            + str(postCellId)
            + " in "
            + postPop
            + ", syn: "
            + str(synapseType)
            + ", weight: "
            + str(weight)
        )

    #
    #  Internal info method, can be reused in overriding classes for debugging
    #
    def print_input_information(self, inputName, population_id, component, size=-1):
        sizeInfo = " size: " + str(size) + " cells"
        print_v(
            "Input Source: "
            + inputName
            + ", on population: "
            + population_id
            + sizeInfo
            + " with component: "
            + component
        )

    #
    #  Should be overridden
    #
    def handle_document_start(self, id, notes):

        print_v("Document: %s started..." % id)
        if notes:
            print_v("  Notes: " + notes)

    #
    #  Should be overridden
    #
    def finalise_document(self):

        print_v("Document ended...")

    #
    #  Should be overridden to create network
    #
    def handle_network(self, network_id, notes, temperature=None):

        print_v("Network: %s" % network_id)
        if temperature:
            print_v("  Temperature: " + temperature)
        if notes:
            print_v("  Notes: " + notes)

    #
    #  Should be overridden to create population array
    #
    def handle_population(
        self, population_id, component, size=-1, component_obj=None, properties={}
    ):
        sizeInfo = " as yet unspecified size"
        if size >= 0:
            sizeInfo = " size: " + str(size) + " cells"
        if component_obj:
            compInfo = " (%s)" % component_obj.__class__.__name__
        else:
            compInfo = ""
        propsInfo = ""
        if properties and len(properties) > 0:
            propsInfo += "; %s" % properties

        print_v(
            "Population: "
            + population_id
            + ", component: "
            + component
            + compInfo
            + sizeInfo
            + propsInfo
        )

    #
    #  Should be overridden to create specific cell instance
    #
    def handle_location(self, id, population_id, component, x, y, z):
        self.print_location_information(id, population_id, component, x, y, z)

    def finalise_population(self, population_id):

        pass

    #
    #  Should be overridden to create population array
    #
    def handle_projection(
        self,
        projName,
        prePop,
        postPop,
        synapse,
        hasWeights=False,
        hasDelays=False,
        type="projection",
        synapse_obj=None,
        pre_synapse_obj=None,
    ):

        synInfo = ""
        if synapse_obj:
            synInfo += " (syn: %s)" % synapse_obj.__class__.__name__

        if pre_synapse_obj:
            synInfo += " (pre comp: %s)" % pre_synapse_obj.__class__.__name__

        print_v(
            "Projection: "
            + projName
            + " ("
            + type
            + ") from "
            + prePop
            + " to "
            + postPop
            + " with syn: "
            + synapse
            + synInfo
        )

    #
    #  Should be overridden to handle network connection
    #
    def handle_connection(
        self,
        projName,
        id,
        prePop,
        postPop,
        synapseType,
        preCellId,
        postCellId,
        preSegId=0,
        preFract=0.5,
        postSegId=0,
        postFract=0.5,
        delay=0,
        weight=1,
    ):

        self.print_connection_information(
            projName, id, prePop, postPop, synapseType, preCellId, postCellId, weight
        )
        if preSegId != 0 or postSegId != 0 or preFract != 0.5 or postFract != 0.5:
            print_v(
                "Src cell: %d, seg: %f, fract: %f -> Tgt cell %d, seg: %f, fract: %f; weight %s, delay: %s ms"
                % (
                    preCellId,
                    preSegId,
                    preFract,
                    postCellId,
                    postSegId,
                    postFract,
                    weight,
                    delay,
                )
            )

    #
    #  Should be overridden to handle end of network connection
    #
    def finalise_projection(
        self, projName, prePop, postPop, synapse=None, type="projection"
    ):

        print_v(
            "Projection: "
            + projName
            + " from "
            + prePop
            + " to "
            + postPop
            + " completed"
        )

    #
    #  Should be overridden to create input source array
    #
    def handle_input_list(
        self, inputListId, population_id, component, size, input_comp_obj=None
    ):

        self.print_input_information(inputListId, population_id, component, size)

        if size < 0:
            self.log.error(
                "Error! Need a size attribute in sites element to create spike source!"
            )
            return

    #
    #  Should be overridden to to connect each input to the target cell
    #
    def handle_single_input(
        self, inputListId, id, cellId, segId=0, fract=0.5, weight=1
    ):

        print_v(
            "  Input: %s[%s], cellId: %i, seg: %i, fract: %f, weight: %f"
            % (inputListId, id, cellId, segId, fract, weight)
        )

    #
    #  Should be overridden to to connect each input to the target cell
    #
    def finalise_input_source(self, inputName):
        print_v("Input : %s completed" % inputName)
