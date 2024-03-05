import csv
import time
import random
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import mysql.connector

url = 'https://portal.linx.net/api/public/stats/snmp/lans?period=week&metric=bitrate'
# Time to wait between each scraping iteration (in seconds)

def send_email(subject, body):

    sender_email = "#####"
    receiver_email = "####"
    password = "####"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.outlook365.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)
    except Exception as e:
        error_message = 'An error occurred while sending the email: ' + str(e)

def timestamp_to_datetime(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def scrape_website():
    try:

        mysql_connection = mysql.connector.connect(
            host="#####",
            user="#####",
            password="#####",
            database="####"
        )
  
        session = requests.Session()
        response = session.get(url)
        json_data = response.json()

        # Parse and interpret the JSON data
        aggregate = json_data['aggregate']
        throughput_data = json_data['throughput']['aggregate']['in']['data']

        # Find the latest common timestamp across all regions
        latest_common_timestamp = None
        if throughput_data is not None:
            for timestamp, bitrate in throughput_data:
                if latest_common_timestamp is None or timestamp > latest_common_timestamp:
                    latest_common_timestamp = timestamp
                    
        else:
            print("No throughput data available")
            return

        region_data = {}


        for region in aggregate:
            region_data[region] = None
            region_region_data = json_data['throughput'][region]['in']['data']
            if region_region_data is not None:
                for timestamp, bitrate in region_region_data:
                    if isinstance(timestamp, (int, float)) and isinstance(bitrate, (int, float)):
                        if timestamp == latest_common_timestamp:
                            region_data[region] = (timestamp, bitrate)
                            break
            else:
                continue
        

        cursor = None
        cursor = mysql_connection.cursor()
        for region, data in region_data.items():
            timestamp, value = data
            time = timestamp_to_datetime(timestamp)

            query = "SELECT * FROM region_data WHERE region = %s AND timestamp = %s"
            cursor.execute(query, (region, time))
            result = cursor.fetchone()
            if result is None:
                query = "INSERT INTO region_data (region, timestamp, bitrate) VALUES (%s, %s, %s)"
                cursor.execute(query, (region, time, value))
                mysql_connection.commit()
            unit = "bps"
            print(f"Region: {region}, Value: {value} {unit}, Timestamp: {timestamp}, Time: {time}")
            print("Data scraped successfully")
    
        csv_file_path = "#####/file.csv"
        try:
            with open(csv_file_path, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                if cursor.description:
                    csv_writer.writerow([i[0] for i in cursor.description])  
                    cursor.execute("SELECT * FROM region_data")
                    csv_writer.writerows(cursor)
                print("Data exported to CSV successfully")
        except Exception as e:
            error_message = 'An error occurred while exporting data to CSV: ' + str(e)
            print(error_message)
            send_email("Error occurred during data export", error_message)

    except Exception as e:
        error_message = 'An error occurred during scraping: ' + str(e)
        print(error_message)
        send_email("Error occurred during scraping", error_message)
        scrape_website()

    finally:
        session.close()
        cursor.close()
        mysql_connection.close()

while True:
    scrape_website()
    wait_time = random.randint(0,9) * 10
    time.sleep(wait_time)
