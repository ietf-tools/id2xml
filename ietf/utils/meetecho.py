# Copyright The IETF Trust 2021, All Rights Reserved
#
"""Meetecho interim meeting scheduling API

Implements the v1 API described in email from alex@meetecho.com
on 2021-12-09.

API methods return Python objects equivalent to the JSON structures
specified in the API documentation. Times and durations are represented
in the Python API by datetime and timedelta objects, respectively.
"""
import requests

from datetime import datetime, timedelta
from json import JSONDecodeError
from typing import Sequence
from urllib.parse import urljoin


class MeetechoAPI:
    def __init__(self, api_base: str, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._session = requests.Session()
        self.api_base = api_base

    def _request(self, method, url, api_token=None, json=None):
        """Execute an API request"""
        headers = {}
        if api_token is not None:
            headers['Authorization'] = f'bearer {api_token}'

        try:
            response = self._session.request(
                method,
                urljoin(self.api_base, url),
                headers=headers,
                json=json,
                timeout=3.01,  # python-requests doc recommend slightly > a multiple of 3 seconds
            )
        except requests.RequestException as err:
            raise MeetechoAPIError(str(err)) from err
        if response.status_code != 200:
            raise MeetechoAPIError(f'API request failed (HTTP status code = {response.status_code})')

        try:
            return response.json()
        except JSONDecodeError as err:
            raise MeetechoAPIError('Error decoding response as JSON') from err

    def _deserialize_time(self, s: str) -> datetime:
        return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

    def _serialize_time(self, dt: datetime) -> str:
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _deserialize_duration(self, minutes: int) -> timedelta:
        return timedelta(minutes=minutes)

    def _serialize_duration(self, td: timedelta) -> int:
        return int(td.total_seconds() // 60)

    def _deserialize_meetings_response(self, response):
        """In-place deserialization of response data structure

        Deserializes data in the structure where needed (currently, that's time-related structures)
        """
        for session_data in response['rooms'].values():
            session_data['room']['start_time'] = self._deserialize_time(session_data['room']['start_time'])
            session_data['room']['duration'] = self._deserialize_duration(session_data['room']['duration'])
        return response

    def retrieve_wg_tokens(self, acronyms: Sequence[str]):
        """Retrieve API tokens for one or more WGs"""
        return self._request(
            'POST', 'auth/ietfservice/tokens',
            json={
                'client': self.client_id,
                'secret': self.client_secret,
                'wgs': acronyms,
            }
        )

    def schedule_meeting(self, wg_token: str, description: str, start_time: datetime, duration: timedelta,
                         extrainfo=''):
        """Schedule a meeting session"""
        return self._deserialize_meetings_response(
            self._request(
                'POST', 'meeting/interim/createRoom',
                api_token=wg_token,
                json={
                    'description': description,
                    'start_time': self._serialize_time(start_time),
                    'duration': self._serialize_duration(duration),
                    'extrainfo': extrainfo,
                },
            )
        )

    def fetch_meetings(self, wg_token: str):
        return self._deserialize_meetings_response(
            self._request('GET', 'meeting/interim/fetchRooms', api_token=wg_token)
        )

    def delete_meeting(self, deletion_token: str):
        return self._request('POST', 'meeting/interim/deleteRoom', api_token=deletion_token)


class MeetechoAPIError(Exception):
    """Base class for MeetechoAPI exceptions"""
