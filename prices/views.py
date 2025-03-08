from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, date, timedelta
from django.db.models import Avg, Max, Min
from django.db import connection
from .models import Price
from .serializers import PriceSerializer

class PriceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    search_fields = ['commodity', 'market', 'district']
    ordering_fields = ['arrival_date', 'modal_price', 'min_price', 'max_price']

    @action(detail=False, methods=['get'])
    def districts(self, request):
        """Get list of all districts"""
        districts = Price.objects.values_list('district', flat=True).distinct()
        return Response(sorted(list(districts)))

    @action(detail=False, methods=['get'])
    def markets_by_district(self, request):
        """Get markets in a specific district"""
        district = request.query_params.get('district')
        if not district:
            return Response(
                {'error': 'Please provide a district parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        markets = Price.objects.filter(
            district=district
        ).values_list('market', flat=True).distinct()
        
        return Response(sorted(list(markets)))

    @action(detail=False, methods=['get'])
    def market_prices(self, request):
        """Get today's and yesterday's prices for a specific market"""
        market = request.query_params.get('market')
        if not market:
            return Response(
                {'error': 'Please provide a market parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        today = date.today()
        yesterday = today - timedelta(days=3)

        prices = Price.objects.filter(
            market=market,
            arrival_date__in=[today, yesterday]
        ).order_by('commodity', '-arrival_date')

        serializer = self.get_serializer(prices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest_prices(self, request):
        """Get latest prices"""
        prices = self.queryset.order_by('-arrival_date')[:10]
        serializer = self.get_serializer(prices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def debug_data(self, request):
        """Get sample data for debugging"""
        sample = Price.objects.first()
        
        district_samples = Price.objects.values_list('district', flat=True).distinct()[:5]
        market_samples = Price.objects.values_list('market', flat=True).distinct()[:5]
        
        return Response({
            "sample_record": {
                "district": sample.district,
                "market": sample.market,
                "commodity": sample.commodity
            },
            "sample_districts": list(district_samples),
            "sample_markets": list(market_samples)
        })

    @action(detail=False, methods=['get'])
    def test_connection(self, request):
        """Test database connection"""
        count = Price.objects.count()
        return Response({"message": f"Connected successfully. Found {count} records in database."})