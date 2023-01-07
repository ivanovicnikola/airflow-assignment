from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator

from datetime import datetime
import os
import tarfile

def log_exists():
    if 'log.txt' in os.listdir('/the_logs'):
        return 'extract_data'
    else:
        return None

def extract_ip_address():
    ips = []
    with open('/the_logs/log.txt', 'r') as log:
        for line in log.readlines():
            ip = line.split(' ')[0]
            ips.append(ip)
    
    with open('/the_logs/extracted_data.txt', 'w+') as res:
        for ip in ips:
           res.write(ip + '\n')

def transform_extracted():
    ips = []
    with open('/the_logs/extracted_data.txt', 'r') as extracted:
        for ip in extracted.readlines():
            if ip != '198.46.149.143\n':
                ips.append(ip)

    with open('/the_logs/transformed_data.txt', 'w+') as res:
        for ip in ips:
           res.write(ip)

def export_tar():
    file = tarfile.open('/the_logs/weblog.tar', 'w')
    file.add('/the_logs/transformed_data.txt')
    file.close()

with DAG('process_web_log', start_date = datetime(2023, 1, 1),
    schedule_interval = '@daily', catchup = False) as dag:
        
    scan_for_log = BranchPythonOperator (
            task_id='scan_for_log',
            python_callable= log_exists
        )

    extract_data = PythonOperator (
            task_id='extract_data',
            python_callable= extract_ip_address
        )

    transform_data = PythonOperator (
        task_id = 'transform_data',
        python_callable = transform_extracted
    )

    load_data = PythonOperator (
        task_id = 'load_data',
        python_callable = export_tar
    )
    
    scan_for_log >> [extract_data] >> transform_data >> load_data
