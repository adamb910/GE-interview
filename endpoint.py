from flask import Flask, jsonify, request
from datetime import date
import json

app = Flask(__name__)

# Could be refractored in to classes to clean code, depends on amount of different units..........
def ConvertUnits(valueQuantity):
    unit = valueQuantity['unit']
    
        #length
    if unit == 'mm':
        valueQuantity['unit'] = "m"
        valueQuantity['value'] *= 1000
    if unit == 'cm':
        valueQuantity['unit'] = "m"
        valueQuantity['value'] *= 100
    #temperature
    if unit == '[degF]':
        valueQuantity['unit'] = "Cel"
        valueQuantity['value'] = (valueQuantity['value'] - 32) * 5/9 
    return valueQuantity

def GetComponentEntries(component, observationBaseData):
    observationId = observationBaseData['observationId']
    patientId = observationBaseData['patientId']
    performerId = observationBaseData['performerId']
    effectiveDateTime = observationBaseData['effectiveDateTime']

    measurementCoding = []
    for coding in component['code']['coding']:
        measurementCoding.append(coding)
        #added function, to convert units on the whole structure
        valueQuantity = ConvertUnits(component['valueQuantity'])
        measurementValue = valueQuantity['value']
        measurementUnit = valueQuantity['unit']
        meausrementDate = effectiveDateTime
        dataFetched = date.today().strftime("%d/%m/%Y %H:%M:%S")
    
    #build the dictionary
    observation = {}
    #for the references, grab the substring after '/', if no '/' this is still safe, result is 0
    observation['observationId'] = observationId[observationId.index('/')+1:len(observationId)]
    observation['patientId'] = patientId[patientId.index('/')+1:len(patientId)]
    observation['performerId'] = performerId[performerId.index('/')+1:len(performerId)]
    observation['measurementCoding'] = measurementCoding
    observation['measurementValue'] = measurementValue
    observation['measurementUnit'] = measurementUnit
    observation['meausrementDate'] = meausrementDate
    observation['dataFetched'] = dataFetched
    return observation

def MapEntriesToObservations(content):
    observations = []
    failedMappings = 0
    for entry in content['entry']:
        try:
            resource = entry['resource']
            if resource['resourceType'] != "Observation":
                continue
            observationId = resource['encounter']['reference']
            patientId = resource['subject']['reference']
            # as the output observation format implies only a single performer
            performerId = resource['performer'][0]['reference']
            #build collected data so far in to a dictionary for ease of passing
            observationBaseData = {}
            observationBaseData['observationId'] = observationId
            observationBaseData['patientId'] = patientId
            observationBaseData['performerId'] = performerId
            observationBaseData['effectiveDateTime'] = resource['effectiveDateTime']



            # iterate through components, if there are multiple, it will create multiple Observation objects
            if 'component' in resource:                
                for component in resource['component']:
                    observation = GetComponentEntries(component,observationBaseData)
                    observations.append(observation)
            else:
                observation = GetComponentEntries(component, observationBaseData)
                observations.append(observation) 
        except:
            failedMappings = failedMappings + 1
    print("Number of failed mappings:")
    print(failedMappings)
    return json.dumps(observations)
    
        

# Opening JSON file
# f = open('input_observations.json')
  
# # returns JSON object as 
# # a dictionary
# data = json.load(f)
# MapEntriesToObservations(data)
  
@app.route('/remapentries',methods = ['POST', 'GET'])
def MapEntriesToObservationsEndPoint():
    content = request.json
    return MapEntriesToObservations(content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=91)