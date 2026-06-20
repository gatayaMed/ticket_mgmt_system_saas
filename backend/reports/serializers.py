from rest_framework import serializers


class ReportRequestSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    project_id = serializers.IntegerField(required=False)
    format = serializers.ChoiceField(choices=['json', 'csv'], default='json')


class ExportRequestSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=['json', 'csv'], default='json')
    data = serializers.JSONField(required=True)
