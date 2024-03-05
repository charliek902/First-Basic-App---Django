import csv
import random
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import mysql.connector

url = 'https://portal.linx.net/api/public/stats/flow/lans?period=week&metric=bitrate'
randomTime = random.randint(0, 9)
wait_time = 10 * randomTime  # Time to wait between each scraping iteration (in seconds)

def send_email(subject, body):
    sender_email = "#####"
    receiver_email = "#####"
    password = "#####"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp-mail.outlook.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(message)
    except Exception as e:
        error_message = 'An error occurred while sending the email: ' + str(e)
        print(error_message)

def timestamp_to_datetime(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def scrape_website():
    # Set up the MySQL connection
    mysql_connection = mysql.connector.connect(
        host="####",
        user="####",
        password="#####",
        database="####"
    )

    cursor = None  # Initialize the cursor variable

    try:
        session = requests.Session()

        response = session.get(url)
        json_data = response.json()

        aggregate = json_data['aggregate']
        throughput_data = json_data['throughput']['aggregate']['in']['ipv4']['data']

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
            region_throughput_data = json_data['throughput'][region]['in']['ipv4']['data']
            if region_throughput_data is not None:
                for timestamp, bitrate in region_throughput_data:
                    if isinstance(timestamp, (int, float)) and isinstance(bitrate, (int, float)):
                        if timestamp == latest_common_timestamp:
                            region_data[region] = (timestamp, bitrate)
                            break
            else:
                continue

        cursor = mysql_connection.cursor()
        try:
            for region, data in region_data.items():
                if data is None:
                    continue

                timestamp, value = data
                time = timestamp_to_datetime(timestamp)

                query = "SELECT * FROM region_data WHERE region = %s AND timestamp = %s"
                cursor.execute(query, (region, time))
                result = cursor.fetchone()
                if result is None:
                    # Insert the data into the database
                    query = "INSERT INTO region_data (region, timestamp, bitrate) VALUES (%s, %s, %s)"
                    cursor.execute(query, (region, time, value))
                    mysql_connection.commit()

                    unit = "bps"
                    print(f"Region: {region}, Value: {value} {unit}, Timestamp: {timestamp}, Time: {time}")

            print("Data scraped successfully")

            csv_file_path = "/#####/flowFile.csv"
            try:
                with open(csv_file_path, "a", newline="") as csvfile:
                    csv_writer = csv.writer(csvfile)
                    if cursor.description:
                        csv_writer.writerow([i[0] for i in cursor.description])  # Write the column headers
                        cursor.execute("SELECT * FROM region_data")
                        csv_writer.writerows(cursor)
                print("Data exported to CSV successfully")
            except Exception as e:
                error_message = 'An error occurred while exporting data to CSV: ' + str(e)
                print(error_message)
                send_email("Error occurred during data export", error_message)

        except Exception as e:
            error_message = 'An error occurred during database operation: ' + str(e)
            print(error_message)
            send_email("Error occurred during database operation", error_message)

        finally:
            cursor.close()

    except Exception as e:
        error_message = 'An error occurred during scraping: ' + str(e)
        print(error_message)
        send_email("Error occurred during scraping", error_message)
        scrape_website()


    finally:
        session.close()
        if cursor:
            cursor.close()
        mysql_connection.close()

while True:
    scrape_website()
    time.sleep(wait_time)
