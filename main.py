# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 12:01:12 2020

@author: Keinan Marks

"""




#Internal Libraries
import json
import requests
from datetime import date, timedelta, datetime
import os


#External Dependencies
import arcgis
from arcgis.gis import GIS
from arcgis import features
from arcgis.geocoding import Geocoder,batch_geocode
from arcgis.features import FeatureLayerCollection


#This is an overwrought function to geocode an array from a list of geocoding services.
#If you aren't using more than one geocoder, probably better to just use the built in batch_geocode or geocode_from_file
#But this should still work fine
#Defined as used in credentials.json


#Basically uses batch_geocode for a pass via the primary and the geocode function to fill in the gaps moving down the list.
#Some additional logic that was written specifically for city of los angeles bureau of engineering services, ie take match >85 with zip
#Take match >95 without zip
def collect_and_geocode_addresses_batch(array1,address_index,gis,geocoder_list = [],pass_nan = True,lat_index = False, sr = 4326, batch_size = 1000,lat_name = 'Latitude',long_name = 'longitude',match_address_name = 'Match_Addr'):
    import copy
    array = array1
    array[0].extend(lat_name,long_name,match_address_name)
    batches = int(len(array)/batch_size) + 2
    from arcgis.gis import GIS
    from arcgis.geocoding import batch_geocode, Geocoder, geocode
    address_list = []
    inter_dict = {}
    for address in array:
        address_list.append(address[address_index])
        inter_dict[address[address_index]] = ['NaN', 'NaN','NaN']
    geocoder = Geocoder(geocoder_list[0],gis=gis)
    try:
        del results
    except:
        pass
    for r in range(1,batches):
        #print(r)
        start = batch_size * (r - 1)
        end = batch_size * r

        try:
            results.extend(batch_geocode(address_list[start:end],geocoder = geocoder,out_sr = sr))
        except Exception as e:
            #print(e)
            results = batch_geocode(address_list[start:end],geocoder = geocoder,out_sr = sr)
        #print(results)
    for r_vals in results:
        inter_dict[r_vals['address']] = [r_vals['location']['x'],r_vals['location']['y'],str(value['attributes']['Match_addr']).replace(',','')]
        
    for geocoders in geocoder_list[1:]:
        geocoder = Geocoder(geocoders,gis = gis)
        for address, vals in inter_dict.items():
            if inter_dict[address] == ['NaN', 'NaN','NaN']:
                try:
                    r_vals = geocode(address, geocoder = geocoder,out_sr = sr)
                except:
                    continue
                #print(r_vals)
                try:
                    inter_dict[address] = [r_vals[0]['location']['x'],r_vals[0]['location']['y'],str(value['attributes']['Match_addr']).replace(',','')]
                except:
                    
                    pass
    
    
    return_array = []

    
    for row in array:
        
        new_row = []
        addy = inter_dict[row[address_index]][:2]
        #print(addy,' || ', row)
        new_row.extend(copy.copy(row))
        new_row.extend(copy.copy(addy))
        return_array.append(new_row)
    #print(return_array)
    return return_array

#returns the index of a value in a list in a list\array
def find_index_value(array,value,header_index = 0):
    for index,val in enumerate(array[header_index]):
        if val == value:
            return index

    return ''



#overwrites a feature layer with passed item_id (must have same schema as original service)
#If no item_id is passed, creates a new feature service named from the credentials file
def overwrite_feature_layer(csv_file,feature_layer_id,username,password,gis,updates=[],mappings = {}, parameters = {},item_props = {}):
    from arcgis.gis import GIS
    from arcgis import features
    from arcgis.features import FeatureLayerCollection
    from arcgis.gis import ContentManager
    import datetime

    #add csv to portal
    if feature_layer_id == '' or None:
        print('Creating New Feature Service')
        csv_item = gis.content.add(item_properties=item_props,data = csv_file)

        #publish portal csv to feature layer with pass params

        csv_lyr = csv_item.publish(publish_parameters = parameters)
        #csv_item.delete()
        #might consider writing item id to credentials?
        return 'New Service Created, item id ' + str(csv_lyr.id)
    else:
        print('Beginning Update Process')
        try:
            date = datetime.datetime.now()

            inspections_feature_layer = gis.content.get(feature_layer_id)
            inspections_flayer_collection = FeatureLayerCollection.fromitem(inspections_feature_layer)
            response_1 = inspections_flayer_collection.manager.overwrite(csv_file)
            #response = inspections_flayer_collection.manager.overwrite(csv_path)
            updates.append(str(response_1) + ' - ' + str(date))
            #print(updates[-1])

        except Exception as e:
            print('Failed to update feature layer')
            print(e)
            pass
        return updates


#dump array to csv
def dump_to_csv(array, out_path = 'out.csv'):
    import csv
    with open(out_path, 'w+', newline='\n') as csvfile:
        listwriter = csv.writer(csvfile)
        listwriter.writerows(array)
    return out_path
def json_to_csv(json_data,name):

    import csv
    data = json.loads(json_data.text)
    #print(data[0])
    with open(name + '.csv', 'w', newline='') as csvfile:
        w = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)


        w.writerow(data[0].keys())
        for r in data:
            try:
                w.writerow(r.values())
            except:
                out = []
                for val in r.values():
                    try:
                        out.append(val.encode('ascii', 'ignore'))
                    except:
                        out.append(val)
                    w.writerow(out)
    return name + '.csv'

#This is a super hacky, temporary way to format the top level of a json into an array
#Needs better handling
def json_to_array(json_data):
    data = json.loads(json_data.text)

    output_array = []

    headers = []
    for header,value in data[0].items():
        headers.append(header)
    output_array.append(headers)
#This could be handled much better
#Attempt to clean it up to point where numerics are resolved
#and it is still standard csv compliant
#Will rewrite to appropriately type and convert fields at some point
    for vals in data:
        row = []
        for k,v in vals.items():
            
            try:
                row.append(float(v))
            except:
                
                #Wild encodings going on
                try:
                    
                    #v = v.replace('\u200b','').replace('\u2011','').replace('\ufeff','').replace('\u25cf','')
                    v = str(ascii(v)).strip("'")
                    #v = str(v,'utf-8')
                    row.append(v.replace(',',';'))
                except Exception as e:
                    print(e)
                    #wild encodings
                    try:
                        
                        row.append(v.encode('ascii','ignore').replace(',', ';'))
                    except:
                        try:
                            row.append(';'.join(v))
                        except:
                            row.append('')
                            pass
        output_array.append(row)
    return output_array

#Body
if __name__ == '__main__':

    #then = datetime.today()
    #then = then - timedelta(microseconds=then.microsecond)
    #print("\nInitiating script at", then, "\n")


    #Collect all paramters from config json
    credentials_json = r"credentials.json"
    try:
        with open(credentials_json, 'r') as f:
            print("Loading Environment Variables...")
            credentials = json.load(f)
            #either arcgis online portal or hosted enterprise
            arcgis_portal = credentials['arcgis_portal']

            #agol or portal username. for domain use DOMAIN\\USERNAME eg SAN\\388560
            username = credentials['username']
            password = credentials['password']
            json_source = credentials['json_source']
            geocoder_list = credentials['geocoder_list']
            geocoding = credentials['geocoding']
            lat = credentials['latitude_field_name']
            lng = credentials['longitude_field_name']
            address = credentials['address_field_name']
            feature_layer_id = credentials['item_id']
            new_service_name = credentials['new_service_name']
            proxy_bypass = credentials['proxy_bypass']


            #This helps resolve hitting internal arcgis enterprise servers behind a proxy
            if proxy_bypass != '':
                os.environ['NO_PROXY'] = proxy_bypass

            response = requests.get(json_source)

    except Exception as e:
        print(e)
        print('Missing Values in Credentials json')



    
    #Create GIS object from defined portal, username and password
    gis = GIS(arcgis_portal,username,password)
    array = json_to_array(response)
    #Add lat and long to each array row is geocoding flag != no
    if geocoding.upper() != 'NO':
        #get the index of the address to pass to the geocoder
        address_index = find_index_value(array,address)
        array = collect_and_geocode_addresses_batch(array,address_index,gis,geocoder_list = geocoder_list)
        #change passed lat long headers to those assigned by the bonkers function
        lat = 'Latitude'
        lng = 'Longitude'

    #dir_path = os.path.dirname(os.path.realpath(__file__))

    #Assumed xy
    #publish params docs available here: https://developers.arcgis.com/rest/users-groups-and-items/publish-item.htm
    params = {'locationType' : 'coordinates', 'latitudeFieldName' : lat, 'longitudeFieldName' : lng, 'name' : new_service_name}
    mapping = {}
    #output csv to script directory
    
    csv_object = dump_to_csv(array, out_path = new_service_name + '.csv')
    #push csv to portal
    #item_props = {'title' : new_service_name}
    overwrite_feature_layer(csv_object,feature_layer_id,username,password,gis,mappings = mapping, parameters = params)
    sys.exit('Complete')
