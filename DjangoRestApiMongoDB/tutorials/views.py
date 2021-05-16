import os

from django.db import connections
from tutorials.models import FileDetails
from django.shortcuts import render

from django.http.response import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.core import serializers
from rest_framework import status

from tutorials.models import Tutorial
from tutorials.serializers import TutorialSerializer
from tutorials.serializers import FileSerializer
from rest_framework.decorators import api_view
from django.core.files.storage import FileSystemStorage
import xml.etree.ElementTree as ET
import cv2
import numpy as np
import json
import csv


@api_view(['GET', 'POST', 'DELETE'])
def tutorial_list(request):
    if request.method == 'GET':
        tutorials = Tutorial.objects.all()

        title = request.GET.get('title', None)
        if title is not None:
            tutorials = tutorials.filter(title__icontains=title)

        tutorials_serializer = TutorialSerializer(tutorials, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = TutorialSerializer(data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Tutorial.objects.all().delete()
        return JsonResponse({'message': '{} Tutorials were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def tutorial_detail(request, pk):
    try:
        tutorial = Tutorial.objects.get(pk=pk)
    except Tutorial.DoesNotExist:
        return JsonResponse({'message': 'The tutorial does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        tutorial_serializer = TutorialSerializer(tutorial)
        return JsonResponse(tutorial_serializer.data)

    elif request.method == 'PUT':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = TutorialSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        tutorial.delete()
        return JsonResponse({'message': 'Tutorial was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def tutorial_list_published(request):
    tutorials = Tutorial.objects.filter(published=True)

    if request.method == 'GET':
        tutorials_serializer = TutorialSerializer(tutorials, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)


@api_view(['GET'])
def file_list(request):
    files = FileDetails.objects.all()
    # file_serializer = FileSerializer(files, many=True)
    # return JsonResponse(file_serializer.data, safe=False)

    # response = HttpResponse(content_type='text/csv')
    # response['Content-Disposition'] = 'attachment;filename=result.csv'
    response = HttpResponse(content_type='text/csv')  
    response['Content-Disposition'] = 'attachment; filename="file.csv"'  
    writer = csv.writer(response)
    writer.writerow(['Image Name', 'Object Name',
                    'X Min', 'Y Min', 'X Max', 'Y Max', 'date'])

    for row in files:
        # data = JSONParser().parse(row.coordinates)
        data = json.loads(row.coordinates)
        # print(row.coordinates)
        for obj in data:
            print(obj)
            object_name = obj["object_name"]  # getattr(obj, "object_name")
            xmin = obj["xmin"]
            ymin = obj["ymin"]
            xmax = obj["xmax"]
            ymax = obj["ymax"]

        writer.writerow([row.fileName, object_name, xmin,
                        ymin, xmax, ymax, row.timestamp])

    return response


@api_view(['POST'])
def upload(request):
    folder = 'media/'
    if request.method == 'POST' and request.FILES['image'] and request.FILES['xml']:
        image = request.FILES['image']
        xml = request.FILES['xml']

        numPyImage = cv2.imdecode(np.fromstring(
            image.read(), np.uint8), cv2.IMREAD_UNCHANGED)

        file_name, object_details = read_content(xml)

        createBoundingBox(numPyImage, file_name, object_details)
        manipulated_image = open(os.path.join("media/", file_name), "rb")
        serialized_obj = json.dumps(object_details)

        data_dict = {"fileName": file_name, "coordinates": serialized_obj}

        file_serializer = FileSerializer(data=data_dict)
        if file_serializer.is_valid():
            file_serializer.save()
            return HttpResponse(manipulated_image, content_type="image/png")
        else:
            return JsonResponse(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def createBoundingBox(img, file_name, objects):
    i = 0
    for row in objects:
        print(row)
        object = row
        # object = JSONParser().parse(row)
        # print(object)
        label = object["object_name"]
        x_min = object["xmin"]
        y_min = object["ymin"]
        box_width = object["xmax"]
        box_height = object["ymax"]
        print(x_min, y_min, box_width, box_height)
        cv2.rectangle(img, (x_min, y_min),
                      (box_width, box_height),
                      (0, 255, 0), 3)

        # Putting text with Label on the current BGR frame
        cv2.putText(img, label, (x_min-2, y_min-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        i += 1

    cv2.imwrite(os.path.join("media/", file_name), img)
    return img


def read_content(xml_file: str):

    tree = ET.parse(xml_file)
    root = tree.getroot()

    object_list = []

    for boxes in root.iter('object'):

        filename = root.find('filename').text
        object_name = str(boxes.find("name").text)

        ymin, xmin, ymax, xmax = None, None, None, None

        ymin = int(boxes.find("bndbox/ymin").text)
        xmin = int(boxes.find("bndbox/xmin").text)
        ymax = int(boxes.find("bndbox/ymax").text)
        xmax = int(boxes.find("bndbox/xmax").text)

        object_details = {"object_name": object_name,
                          "xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
        object_list.append(object_details)

    return filename, object_list
