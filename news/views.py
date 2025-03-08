# news/views.py
import feedparser
from datetime import datetime
import pytz
import re
from html.parser import HTMLParser
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class MLStripper(HTMLParser):
    """Helper class to strip HTML tags"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []
    
    def handle_data(self, d):
        self.fed.append(d)
    
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    """Strip HTML tags from text"""
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class NewsViewSet(viewsets.ViewSet):
    """ViewSet for news-related endpoints"""
    
    @action(detail=False, methods=['get'])
    def agriculture_news(self, request):
        """Get agricultural news from Sandesh RSS feed"""
        category = request.query_params.get('category', 'all')
        
        # Sandesh RSS feed URL for agriculture news
        sandesh_feed_url = 'https://sandesh.com/rss/agriculture.xml'
        
        # Category keywords for classification
        category_keywords = {
            'government': ['યોજના', 'સરકાર', 'સબસિડી', 'સહાય', 'scheme', 'subsidy', 'government', 'policy'],
            'market': ['બજાર', 'ભાવ', 'મંડી', 'વેપાર', 'વેચાણ', 'market', 'price', 'mandi', 'trade'],
            'technology': ['ટેકનોલોજી', 'તકનીક', 'મશીન', 'technology', 'innovation', 'method', 'equipment']
        }
        
        all_news = []
        
        try:
            # Parse the Sandesh RSS feed
            feed = feedparser.parse(sandesh_feed_url)
            
            for entry in feed.entries:
                # Extract image URL from media:content tag if available
                image_url = None
                if hasattr(entry, 'media_content') and entry.media_content:
                    for media in entry.media_content:
                        if 'url' in media:
                            image_url = media['url']
                            break
                
                # If media:content is not available, try to find image in description
                if not image_url and hasattr(entry, 'description'):
                    image_match = re.search(r'<img[^>]+src="([^">]+)"', entry.description)
                    if image_match:
                        image_url = image_match.group(1)
                
                # Clean description (remove HTML tags)
                description = ""
                if hasattr(entry, 'description'):
                    description = strip_tags(entry.description)
                    description = description[:300] + ('...' if len(description) > 300 else '')
                
                # Determine category
                content_text = (entry.title + ' ' + description).lower()
                item_category = 'general'  # Default category
                
                for cat, keywords in category_keywords.items():
                    if any(keyword.lower() in content_text for keyword in keywords):
                        item_category = cat
                        break
                
                # Only include items for the requested category
                if category != 'all' and item_category != category:
                    continue
                
                # Parse date
                pub_date = datetime.now(pytz.UTC)
                if hasattr(entry, 'published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=pytz.UTC)
                
                # Create news item
                news_item = {
                    "title": entry.title,
                    "description": description,
                    "url": entry.link,
                    "source": {"name": "Sandesh"},
                    "publishedAt": pub_date.isoformat(),
                    "urlToImage": image_url,
                    "category": item_category
                }
                
                all_news.append(news_item)
        
        except Exception as e:
            # Log the error but return a fallback response
            print(f"Error parsing Sandesh feed: {str(e)}")
            return Response({
                "error": "Unable to fetch news from Sandesh",
                "message": str(e)
            }, status=500)
        
        # Sort by date (newest first)
        all_news.sort(key=lambda x: x['publishedAt'], reverse=True)
        
        # If no news found, provide a fallback response
        if not all_news:
            all_news = [
                {
                    "title": "કૃષિ સમાચાર ઉપલબ્ધ નથી",
                    "description": "અત્યારે કોઈ કૃષિ સમાચાર ઉપલબ્ધ નથી. કૃપા કરીને થોડા સમય પછી ફરી પ્રયાસ કરો.",
                    "url": "#",
                    "source": {"name": "System"},
                    "publishedAt": datetime.now(pytz.UTC).isoformat(),
                    "urlToImage": None,
                    "category": "all"
                }
            ]
        
        return Response(all_news)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get available news categories"""
        categories = [
            {"id": "all", "name_en": "All News", "name_gu": "બધા સમાચાર"},
            {"id": "government", "name_en": "Government Schemes", "name_gu": "સરકારી યોજનાઓ"},
            {"id": "market", "name_en": "Market Updates", "name_gu": "બજાર અપડેટ"},
            {"id": "technology", "name_en": "Technology", "name_gu": "ટેકનોલોજી"},
            {"id": "general", "name_en": "General", "name_gu": "સામાન્ય"}
        ]
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def resources(self, request):
        """Get important agricultural resources and links"""
        resources = [
            {
                "title": "i-ખેડૂત પોર્ટલ - ગુજરાત સરકાર",
                "url": "https://ikhedut.gujarat.gov.in/",
                "description": "Gujarat government portal for farmers"
            },
            {
                "title": "ખેડૂત પોર્ટલ - ભારત સરકાર",
                "url": "https://farmer.gov.in/",
                "description": "Indian government portal for farmers"
            },
            {
                "title": "એગમાર્કનેટ - કૃષિ બજાર માહિતી",
                "url": "https://www.agmarknet.gov.in/",
                "description": "Agricultural market information"
            }
        ]
        return Response(resources)