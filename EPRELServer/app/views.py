import json
from django.http import JsonResponse, HttpResponseBadRequest
from .models import MyModel
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from django.http import Http404
import pandas as pd
import traceback
import io


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
            elif manufacturer and not model_number:
                data = MyModel.objects.filter(manufacturer__startswith=manufacturer.split()[0])
            elif model_number and not manufacturer:
                data = MyModel.objects.filter(model_number=model_number)
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
                else:
                    data = data.values()

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
    

@require_GET
def data_view(request):
    # actually give the option to download the data from this library 
    if request.method == 'GET':
        try:
            print('gets over here...')
            data = MyModel.objects.all()
            response = JsonResponse(data)

            # Set the CORS headers
        #    response["Access-Control-Allow-Origin"] = "localhost:8000"
        #    response["Access-Control-Allow-Methods"] = "GET, POST"
         #   response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
            # Process the data if needed
            return response
        except Exception as e:
            return JsonResponse({'error': str(e)})


@require_POST
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
def home(request):
    try:
        if request.method == 'GET':
            response = render(request,'libraryInterface.html', context = None, content_type=None, using=None)
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

#for any other url request 


@require_GET
def anyOtherRequest(request, undefined_path):
    raise Http404()







    







