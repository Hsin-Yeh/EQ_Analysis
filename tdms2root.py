#!/usr/bin/env python
import numpy as np
import pytdms
import ROOT
from ROOT import TTree
import yaml
import sys
from array import array

if len(sys.argv) != 2:
    print ("USAGE: %s <input file>" %(sys.argv[0]))
    sys.exit(1)

tdmsFileName = sys.argv[1]
rootFileName = "data/%s.root" %((tdmsFileName.rsplit('/',1)[1]).split('.')[0])
print ("convert", tdmsFileName, "to", rootFileName)

(objects,rawdata) = pytdms.read(tdmsFileName)


# Read headers
Name              = objects[b'/'][3][b'name'][1].decode('utf-8')
Events            = int(objects[b'/'][3][b'Total Events'][1].decode('utf-8'))
Operator          = objects[b'/'][3][b'Operator'][1].decode('utf-8')
StartT            = objects[b'/'][3][b'Start Time'][1].decode('utf-8')
VerticalRange     = float(objects[b'/'][3][b'vertical range'][1].decode('utf-8'))
VerticalOffset    = float(objects[b'/'][3][b'vertical offset'][1].decode('utf-8'))
MaxInpFreq        = float(objects[b'/'][3][b'maximum input frequency'][1].decode('utf-8'))
SampleRate        = float(objects[b'/'][3][b'actual sample rate'][1].decode('utf-8'))
RecordLength      = int(objects[b'/'][3][b'record length'][1].decode('utf-8'))
TriggerSource     = objects[b'/'][3][b'trigger source'][1].decode('utf-8')
TriggerSlope      = bool(objects[b'/'][3][b'trigger slope'][1].decode('utf-8'))
TriggerLevel      = float(objects[b'/'][3][b'trigger level'][1].decode('utf-8'))
TriggerDelay      = float(objects[b'/'][3][b'trigger delay'][1].decode('utf-8'))
ReferencePosition = float(objects[b'/'][3][b'reference position'][1].decode('utf-8'))
EndT              = objects[b'/'][3][b'End Time'][1].decode('utf-8')

a_dict = {}
for variable in ["Name", "Events", "Operator", "StartT", "EndT", "VerticalRange", "VerticalOffset", "MaxInpFreq", "SampleRate", "RecordLength", "TriggerSource",
                 "TriggerSlope", "TriggerLevel", "TriggerDelay", "ReferencePosition"]:
    a_dict[variable] = eval(variable)

with open(r'yaml/%s.yaml' %((tdmsFileName.rsplit('/',1)[1]).split('.')[0]), 'w') as file:
    documents = yaml.dump(a_dict, file, default_flow_style=False, sort_keys=False)

slicedarray0 = array( 'f', [ 0 ] * RecordLength )
slicedarray1 = array( 'f', [ 0 ] * RecordLength )
t = ROOT.TTree("detector_A", "detector_A")
t.Branch('ch0',slicedarray0,"slicedarray0[%d]/F" %(RecordLength))
t.Branch('ch1',slicedarray1,"slicedarray1[%d]/F" %(RecordLength))

for index in range (Events):
    start_index = index * RecordLength
    end_index = (index + 1) * RecordLength
    # slicedarray0 = array( 'f', rawdata[b"/'ADC Readout Channels'/'ch0'"][start_index:end_index])
    for idx, val in enumerate(range(start_index, end_index)):
        slicedarray0[idx] = rawdata[b"/'ADC Readout Channels'/'ch0'"][val]
        slicedarray1[idx] = rawdata[b"/'ADC Readout Channels'/'ch1'"][val]
    t.Fill()

outHistFile = ROOT.TFile.Open(rootFileName,"RECREATE")
outHistFile.cd()
t.Write()
outHistFile.Close()
