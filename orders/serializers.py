from rest_framework import serializers

class GeneratePayLinkSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)