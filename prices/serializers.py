from rest_framework import serializers
from .models import Price

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['id', 'commodity', 'market', 'district', 'state',
                 'min_price', 'max_price', 'modal_price', 'arrival_date']