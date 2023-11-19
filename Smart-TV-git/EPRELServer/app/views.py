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

@csrf_exempt
@require_POST 
def apiEndpoint(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    
        location = data['location'].lower()
        day = data['day'].lower()

        day_dictionary = {'monday': 2, 'tuesday': 3, 'wednesday': 4, 'thursday': 5, 'friday': 6, 'saturday': 7, 'sunday': 1 }
        try:
            day_value = day_dictionary[day]
        except:
            return JsonResponse({'error': 'Invalid day'}, status=400)
        
        location_dictionary = {'middle east': 'jed1', 'wales': 'car1', 'inner london': 'lon1', 'outer london': 'lon2', 'manchester': 'man1', 
                               'scotland': 'sco1', 'north america': 'nva1', 'nairobi': 'nai1', 'general': 'general', 'the middle east': 'jed1'}
        try:
            locationReq = location_dictionary[location]
        except:
            return JsonResponse({'error': 'Invalid location'}, status=400)
        
        TV_data = {}

        if data['model'] != 'null' and data['brand'] != 'null':
            TV_model = data['model']
            TV_brand = data['brand'].upper()
            data = MyModel.objects.filter(
                    manufacturer__startswith= TV_brand,
                    model_number= TV_model
                )
            data = data.values('energy_class', 'energy_class_sdr', 'energy_class_hdr')
            TV_data['energy data'] = list(data)
            if len(data) == 0:
                TV_data['energy data'] = 'No TV corresponds with TV sent in API request'
        
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

            # timestamp BETWEEN CURRENT_DATE - INTERVAL 1 MONTH AND CURRENT_DATE - INTERVAL 1 DAY AND
            cursor.execute(sql_query)
            result = cursor.fetchall()
            peakTime = findPeak(result)
            response = {"peak": peakTime, "energy data": TV_data}
            return JsonResponse(response)

            # find the current time and state how long in the response until peak time 
            # if time is within an hour of peak time --> state what you need to do
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
            response = {"peak": peakTime, "energy data": TV_data}
            return JsonResponse(response)
        else:
            return JsonResponse({'error': 'Error, refer to API page on website'}, status=400)

def findPeak(results):
    # making a dictionary that associates keys with the average total minutes of the month 
    result_dictionary = dict()

    for result in results:
        parsed_time = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        hour = parsed_time.strftime("%H:%M:%S")

        if hour not in result_dictionary:
            result_dictionary[hour] = [result[1]]
        else:
            result_dictionary[hour].append(result[1])

    # now need to find the averages associated with each array
    for key in result_dictionary.keys():
        allValuesForTime = result_dictionary[key]
        result_dictionary[key] = sum(allValuesForTime) / len(allValuesForTime)

    # find the hour with the highest average data traffic 
    highest = 0
    peakTime = 0
    for key in result_dictionary.keys():
        if result_dictionary[key] > highest:
            highest = result_dictionary[key]
            peakTime = key

    return str(peakTime) + ' GMT'

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

        # Set the CORS headers
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
            
            # Merge 'df' with 'model_df' based on 'manufacturer' and 'model_number'
            merged_df = pd.merge(df, model_df, on=['manufacturer', 'model_number'], how='left')

            # Fill NaN values in the merged columns with a specific value (e.g., 'N/A')
            merged_df.fillna('N/A', inplace=True)

            # Drop rows where values are not present in both databases
            merged_df.dropna(subset=['power_on_mode_sdr', 'power_on_mode_hdr', 'energy_class', 'energy_class_sdr', 'energy_class_hdr'], inplace=True)

            # Rename the columns in 'df'

           # df.rename(columns={'manufacturer': 'device_brand', 'model_number': 'device_model'}, inplace=True)
           # df.rename(columns={'power_on_mode_sdr': 'Standard dynamic Range (Watts)', 'power_on_mode_hdr': 'High Dynamic Range (Watts)'}, inplace=True)
            #df.rename(columns={'energy_class': 'energy_class (A-G)', 'energy_class_sdr': 'energy_class_sdr (A-G)', 'energy_class_hdr': 'energy_class_hdr (A-G)'}, inplace=True)
            
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
def show_documentation(request):
    try:
        if request.method == 'GET':
            response = render(request,'documentation.html', context = None, content_type=None, using=None)
          #  response["Access-Control-Allow-Origin"] = "localhost:8000/doc"
          #  response["Access-Control-Allow-Methods"] = "GET, POST"
          #  response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
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
def getDashboardDaily(request):
    try:
        if request.method == 'GET':
            response = render(request,'liveDashboardDailyPage.html', context = None, content_type=None, using=None)
            return response
    
    except Exception as e:
        traceback.print_exc() 
        print(e)
        return HttpResponse("Invalid request", status=400)
    
@require_GET 
def getDashboardParsed(request):
    try:
        if request.method == 'GET':
            response = render(request,'liveDashboardParserPage.html', context = None, content_type=None, using=None)
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
def showExplanation(request):

    try:
        if request.method == 'GET':
            print('gets here!')
            response = render(request,'', context = None, content_type=None, using=None)
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








    







