import json
from django.http import JsonResponse, HttpResponseBadRequest
from .models import MyModel
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.http import Http404
import pandas as pd
import traceback
import io
import mysql.connector
from datetime import datetime
import requests
from django.conf import settings

@csrf_exempt
@require_POST 
def apiEndpoint(request):
    if request.method == 'POST':
        try:
            dataAPI = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    
        location = dataAPI['location'].lower()
        day = dataAPI['day'].lower()

        day_dictionary = {'monday': 2, 'tuesday': 3, 'wednesday': 4, 'thursday': 5, 'friday': 6, 'saturday': 7, 'sunday': 1 }
        try:
            day_value = day_dictionary[day]
        except:
            return JsonResponse({'error': 'Invalid day'}, status=400)
        
        location_dictionary = {'middle east': 'jed1', 'wales': 'car1', 'london': 'lon1', 'manchester': 'man1', 
                               'scotland': 'sco1', 'north america': 'nva1', 'nairobi': 'nai1', 'general': 'general', 'the middle east': 'jed1'}
        try:
            locationReq = location_dictionary[location]
        except:
            return JsonResponse({'error': 'Invalid location'}, status=400)
        
        agent_string = dataAPI['tv_agent_string']
        if agent_string != 'null':
            agent_string = agent_string.replace('/', ' ')
            agent_string = agent_string.replace('-', ' ')
            agent_string = agent_string.replace('(', ' ')
            agent_string = agent_string.replace(')', ' ')
            agent_string = agent_string.replace(',', ' ')
            agent_string = agent_string.replace(';', ' ')
            mysql_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password=settings.DATABASES['default']['PASSWORD'],
                database="EPREL"
            )
            sql_query = (
            f"SELECT manufacturer from new_energyLibrary GROUP BY manufacturer;"
            )
            cursor = mysql_connection.cursor(dictionary=True)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            brands = set()

            foundBrand = False

            for result in results:
                if result['manufacturer'] is None:
                    #for some reason the continue keyword here caused the program to break... 
                    break
                elif len(result['manufacturer'].split()) > 1:
                    main_brand = result['manufacturer'].split()[0]
                    brands.add(main_brand)
                else:
                    main_brand = result['manufacturer']

            brand_in_agent_string = None

            agent_string = agent_string.split()
            
            for word in agent_string:
                try:
                    if word.upper() in brands:
                        brand_in_agent_string = word.upper()
                        foundBrand = True
                
                except(AttributeError):
                    print(word)
            
    
            agent_string_response = {}
            if foundBrand:
                while(foundBrand):
                    for word in agent_string:
                        data = MyModel.objects.filter(
                            manufacturer__startswith=brand_in_agent_string,
                            model_number=word
                        )
                        data = list(data.values('energy_class', 'energy_class_sdr', 'energy_class_hdr'))
                        if len(data) > 0:
                            agent_string_response['agent-string_data'] = data
                            foundBrand = False
                    foundBrand = False
            
        else:
            agent_string_response = {}
            agent_string_response['agent-string_data'] = []

        TV_data = {}

        if dataAPI['model'] != 'null' and dataAPI['brand'] != 'null':
            TV_model = dataAPI['model']
            TV_brand = dataAPI['brand'].upper()

            data = MyModel.objects.filter(
                manufacturer__startswith= TV_brand,
                model_number = TV_model
                )

            data = data.values('energy_class', 'energy_class_sdr', 'energy_class_hdr')
            TV_data['energy data'] = list(data)
            if len(data) == 0:
                TV_data['energy data'] = 'No TV corresponds with brand and model sent in API request'
        
        mysql_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="#Carlosknox1",
            database="LINX"
        )

        if location and location != 'general':
            cursor = mysql_connection.cursor()
            sql_query = (
                f"SELECT "
                f"DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') AS hour, "
                f"AVG(bitrate) AS average_hourly_traffic "
                f"FROM region_data "
                f"WHERE timestamp BETWEEN '2023-11-14 00:00:00' - INTERVAL 2 MONTH AND '2023-11-14 00:00:00' - INTERVAL 1 DAY "
                f"AND region = '{locationReq}' "
                f"AND DAYOFWEEK(timestamp) = {day_value} "
                f"GROUP BY hour "
                f"ORDER BY hour;"
            )

            cursor.execute(sql_query)
            result = cursor.fetchall()
            peakTime = findPeak(result)
            response = {"peak": peakTime, "energy data": TV_data, "agent_string_data": agent_string_response}
            return JsonResponse(response)

        elif location == 'general':
            cursor = mysql_connection.cursor()
            sql_query = (
                f"SELECT "
                f"DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') AS hour, "
                f"AVG(bitrate) AS average_hourly_traffic "
                f"FROM region_data "
                f"WHERE timestamp BETWEEN '2023-11-14 00:00:00' - INTERVAL 1 MONTH AND '2023-11-14 00:00:00' - INTERVAL 1 DAY "
                f"AND DAYOFWEEK(timestamp) = {day_value} "
                f"GROUP BY hour "
                f"ORDER BY hour;"
            )
            cursor.execute(sql_query)
            result = cursor.fetchall()
            peakTime = findPeak(result)
            response = {"peak": peakTime, "energy data": TV_data, "agent_string_data": agent_string_response}
            return JsonResponse(response)
        else:
            return JsonResponse({'error': 'Error, refer to API page on website'}, status=400)

def findPeak(results):
 
    result_dictionary = dict()

    for result in results:
        parsed_time = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        hour = parsed_time.strftime("%H:%M:%S")

        if hour not in result_dictionary:
            result_dictionary[hour] = [result[1]]
        else:
            result_dictionary[hour].append(result[1])

   
    for key in result_dictionary.keys():
        allValuesForTime = result_dictionary[key]
        result_dictionary[key] = sum(allValuesForTime) / len(allValuesForTime)

  
    highest = 0
    peakTime = 0
    for key in result_dictionary.keys():
        if result_dictionary[key] > highest:
            highest = result_dictionary[key]
            peakTime = key

    return str(peakTime) + ' UTC'

@require_POST
def search(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        manufacturer = data.get('manufacturer')
        model_number = data.get('model_number')
        filter_enabled = data.get('filter')
        manufacturer = manufacturer.upper()

        try:
            if manufacturer and model_number:
                data = MyModel.objects.filter(
                    manufacturer__startswith=manufacturer.split()[0],
                    model_number=model_number
                )
                if(len(data) == 0):
                    return JsonResponse(data)

            elif manufacturer and not model_number:
                data = MyModel.objects.filter(manufacturer__startswith=manufacturer.split()[0])
                if(len(data) == 0):
                    return JsonResponse(data)
            elif model_number and not manufacturer:
                data = MyModel.objects.filter(model_number=model_number)
                if(len(data) == 0):
                    return JsonResponse(data)
            else:
                data = MyModel.objects.all()

            if filter_enabled:
                if filter_enabled == 'Overall Energy Class':
                    data = data.values('manufacturer', 'model_number', 'energy_class')
                elif filter_enabled == 'Energy Class SDR':
                    data = data.values('manufacturer', 'model_number', 'energy_class_sdr')
                elif filter_enabled == 'Energy Class HDR':
                    data = data.values('manufacturer', 'model_number', 'energy_class_hdr')
                elif filter_enabled == 'Standard Dynamic Range':
                    data = data.values('manufacturer', 'model_number', 'power_on_mode_sdr')
                elif filter_enabled == 'High Dynamic Range':
                    data = data.values('manufacturer', 'model_number', 'power_on_mode_hdr')
              
            response_data = {
                'message': 'Data received successfully.',
                'filter-enabled': filter_enabled,
                'data': list(data),
            }
        except Exception as e:
            response_data = {
                'error': str(e),
            }

        response = JsonResponse(response_data)

        response["Access-Control-Allow-Origin"] = "localhost:8000"
        response["Access-Control-Allow-Methods"] = "GET, POST"
        response["Access-Control-Allow-Headers"] = "Accept, Content-Type"

        return response
    else:
        return HttpResponseBadRequest("Invalid request method")
    
def parse_excel(request):
    try:
        if request.method == 'POST' and request.FILES.get('file'):
            file = request.FILES['file']
            df = pd.read_excel(file)
            model_data = MyModel.objects.all()

            # Create a DataFrame from the model_data
            model_df = pd.DataFrame(list(model_data.values()), columns=['manufacturer', 'model_number', 'power_on_mode_sdr', 'power_on_mode_hdr', 'energy_class', 'energy_class_sdr', 'energy_class_hdr'])
    
            # Split the values, extract the first word, and convert to uppercase
            model_df['manufacturer'] = model_df['manufacturer'].str.split().str[0]
            df.columns = df.columns.str.strip()
            df['device_brand'] = df['device_brand'].str.split().str[0].str.upper()

            # Trim whitespace from all values in 'df'
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            # Convert all values in the DataFrame to uppercase
            df = df.apply(lambda x: x.str.upper() if x.dtype == "object" else x)

            # Rename the columns in 'df'
            df.rename(columns={'device_brand': 'manufacturer', 'device_model': 'model_number'}, inplace=True)
            
            merged_df = pd.merge(df, model_df, on=['manufacturer', 'model_number'], how='left')

            merged_df.fillna('N/A', inplace=True)

            merged_df.dropna(subset=['power_on_mode_sdr', 'power_on_mode_hdr', 'energy_class', 'energy_class_sdr', 'energy_class_hdr'], inplace=True)

            excel_file = io.BytesIO()
            with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                merged_df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=output.xlsx'
            
            excel_file.seek(0)
            response.write(excel_file.getvalue())

                # Set the CORS headers
          #  response["Access-Control-Allow-Origin"] = "localhost:8000"
          #  response["Access-Control-Allow-Methods"] = "GET, POST"
         #   response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
            return response
    except Exception as e:
        traceback.print_exc()  
        return HttpResponse(f"An error occurred: {str(e)}", status=500)

    return HttpResponse("Invalid request", status=400)


@require_GET
def searchLibrary(request):
    try:

        if request.method == 'GET':
            response = render(request,'searchLibrary.html', context = None, content_type=None, using=None)
          # response["Access-Control-Allow-Origin"] = "localhost:8000"
          #  response["Access-Control-Allow-Methods"] = "GET, POST"
           # response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
            return response
            
    except Exception as e:
        traceback.print_exc() 
        print(e)
        return HttpResponse("Invalid request", status=400)

@require_GET
def show_DataAnalytics_page(request):
    try:

        if request.method == 'GET':
            response = render(request,'dataAnalytics.html', context = None, content_type=None, using=None)
          #  response["Access-Control-Allow-Origin"] = "localhost:8000/doc"
          #  response["Access-Control-Allow-Methods"] = "GET, POST"
          #  response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
            return response

    except Exception as e:
            traceback.print_exc() 
            print(e)
            return HttpResponse("Invalid request", status=400)

@require_GET
def showAPI(request):
    try:
        if request.method == 'GET':
            response = render(request,'API.html', context = None, content_type=None, using=None)
            #  response["Access-Control-Allow-Origin"] = "localhost:8000/doc"
            #  response["Access-Control-Allow-Methods"] = "GET, POST"
            #  response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
            return response

    except Exception as e:
        traceback.print_exc() 
        print(e)
        return HttpResponse("Invalid request", status=400)

@require_GET
def showLiveDashboardMonthly(request):
    try:
        if request.method == 'GET':
            response = render(request,'liveDashboardPage.html', context = None, content_type=None, using=None)
            #  response["Access-Control-Allow-Origin"] = "localhost:8000/doc"
            #  response["Access-Control-Allow-Methods"] = "GET, POST"
            #  response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
            return response

    except Exception as e:
        traceback.print_exc() 
        print(e)
        return HttpResponse("Invalid request", status=400)
    

@require_GET
def displayHomePage(request):
    try:
        if request.method == 'GET':
            response = render(request,'home.html', context = None, content_type=None, using=None)
            #  response["Access-Control-Allow-Origin"] = "localhost:8000/doc"
            #  response["Access-Control-Allow-Methods"] = "GET, POST"
            #  response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
            return response

    except Exception as e:
        traceback.print_exc() 
        print(e)
        return HttpResponse("Invalid request", status=400)


@require_GET
def display404(request, undefined_path):
    try:
        if undefined_path:
            response = render(request,'404.html', context = None, content_type=None, using=None)
            #  response["Access-Control-Allow-Origin"] = "localhost:8000/doc"
            #  response["Access-Control-Allow-Methods"] = "GET, POST"
            #  response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
            return response

    except Exception as e:
        traceback.print_exc() 
        print(e)
        return HttpResponse("Invalid request", status=400)








    







