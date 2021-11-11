import csv
import io
from datetime import datetime
from userreviews.models import ExportedFile

def save_uploaded_file(f):

    file_path = 'media/import/{}'.format(f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def read_uploaded_csv(csv_file):
    csv_file.seek(0)
    return csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))


def save_data_to_csv(panda_data, name):
    now = datetime.now()
    save_directory = 'media/export/'
    filename = '{}_{}_{}_{}_{}.csv'.format(now.year, now.month, now.day, str(
        now.hour)+str(now.minute)+str(now.second), name.upper())
    filepath = save_directory+filename
    panda_data.to_csv(filepath, index=False)

    #Add record to DB
    _record_exported_file({'name':filename, 'path':filepath})

    print('Success, panda data to csv: {}'.format(filepath))
    return filename

def _record_exported_file(data):
    exportedFile = ExportedFile(name=data['name'], path=data['path'])
    exportedFile.save()