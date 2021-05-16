from rest_framework import serializers
from tutorials.models import Tutorial
from tutorials.models import FileDetails


class TutorialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tutorial
        fields = ('id',
                  'title',
                  'description',
                  'published')


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileDetails
        fields = ('id',
                  'fileName',
                  'coordinates',
                  'timestamp')
