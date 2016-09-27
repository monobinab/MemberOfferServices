from gcloud import datastore
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def index(request):
    return render(request, 'index.html')


bucket = 'campaign-bucket-backend'
project_id = 'campaign-backend-arun'
client = datastore.Client(project_id)


@csrf_exempt
@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        try:
            str_response = request.body.decode('utf-8')
            data = json.loads(str_response)
            username = data.get('username')
            password = data.get('password')
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
            else:
                user = User.objects.get(username=username)
            login(request, user)
            token = Token.objects.get_or_create(user=user)
            # print(token[0])
            response_data = {'token': str(token[0]),
                             'message': 'User logged in successfully!!!',
                             'user_id': request.user.id,
                             'username': request.user.username,
                             'email': request.user.username}
            return Response(data={'data': response_data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            response_data = {'message': 'Something went wrong. Please try later'}
            return Response(data=response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['POST'])
def logout_view(request):
    try:
        if request.user.is_authenticated():
            request.user.auth_token.delete()
            logout(request)
            response_data = {'message': 'Logged out successfully!!!'}
            return Response(data=response_data, status=status.HTTP_200_OK)
        else:
            return Response(data={'message': "Session is invalid."},
                            status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(str(e))
        return Response(data={'message': 'Something went wrong. Please try again.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# {
# 	"offer_details": {
#       "offer_id":"1",
# 		"max_value": "100",
# 		"member_issuance": "2 per week",
# 		"min_value": "20",
# 		"offer_type": "Liquidly Injection",
# 		"valid_till": "2016-09-26"
# 	},
# 	"campaign_details": {
#       "campaign_id":"1",
# 		"category": "Approval",
# 		"conversion_ratio": "5",
# 		"money": "500",
# 		"name": "Campaign up 1",
# 		"period": "2 Weeks"
# 	}
# }


def get_campaign_list(limit=10, cursor=None):
    query = client.query(kind='Campaign', order=['name'])
    it = query.fetch(limit=limit, start_cursor=cursor)
    entities, more_results, cursor = it.next_page()
    return entities, cursor.decode('utf-8') if len(entities) == limit else None


def get_campaign(campaign_id, entities):
    result = []
    for each in entities:
        if each is not None and str(each[0].key.id) == str(campaign_id):
            result.append(each)
    return result


@csrf_exempt
@api_view(['GET', 'POST', 'PUT'])
def campaign(request, campaign_id=None):
    try:
        if request.method == 'GET':
            campaign_list = get_campaign_list()
            if campaign_id is not None:
                campaign_list = get_campaign(campaign_id, campaign_list)
            result = list()
            for each_result in campaign_list:
                if each_result is not None and len(each_result) > 0:
                    for entity in each_result:
                        each_dict = dict()
                        campaign_dict = dict()
                        if entity is not None:
                            campaign_dict['name'] = entity['name']
                            campaign_dict['campaign_id'] = entity.key.id
                            campaign_dict['category'] = entity['category']
                            campaign_dict['period'] = entity['period']
                            campaign_dict['money'] = entity['money']
                            campaign_dict['conversion_ratio'] = entity['conversion_ratio']

                            offer_dict = dict()
                            offer_dict['offer_id'] = entity.key.id
                            offer_dict['offer_type'] = entity['offer_type']
                            offer_dict['member_issuance'] = entity['member_issuance']
                            offer_dict['max_value'] = entity['max_value']
                            offer_dict['min_value'] = entity['min_value']
                            offer_dict['valid_till'] = entity['valid_till']
                            each_dict['campaign_details'] = campaign_dict
                            each_dict['offer_details'] = offer_dict
                            result.append(each_dict)
            return Response(data={'data': result,
                                  'message': 'Campaigns fetched successfully!!!'},
                            status=status.HTTP_200_OK)
        elif request.method == 'POST':
            str_response = request.body.decode('utf-8')
            data = json.loads(str_response)
            key = client.key('Campaign')
            task = datastore.Entity(key=key, exclude_from_indexes=['description'])
            campaign_data = dict(data.get('campaign_details').items() + data.get('offer_details').items())
            task.update(campaign_data)
            client.put(task)
            return Response(data={'message': 'Campaign has been created successfully!!!'},
                            status=status.HTTP_201_CREATED)
        elif request.method == 'PUT':
            str_response = request.body.decode('utf-8')
            data = json.loads(str_response)
            # print data.get('campaign_details').get('campaign_id')
            key = client.key('Campaign', data.get('campaign_details').get('campaign_id'))
            client.delete(key=key)
            task = datastore.Entity(key=key, exclude_from_indexes=['description'])
            campaign_data = dict(data.get('campaign_details').items() + data.get('offer_details').items())
            campaign_data.pop('campaign_id', None)
            campaign_data.pop('offer_id', None)

            task.update(campaign_data)
            client.put(task)
            return Response(data={'message': 'Campaign has been updated successfully!!!'},
                            status=status.HTTP_202_ACCEPTED)
        else:
            Response(data={'message': 'Method not allowed'},
                     status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        print(str(e))
        return Response(data={'message': 'Something went wrong. Please try again.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)