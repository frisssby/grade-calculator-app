from __future__ import annotations
from typing import Any, List
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetsApiHandler:
    def __init__(self, sheets_service, drive_service) -> None:
        self.sheets_service = sheets_service
        self.drive_service = drive_service

    @staticmethod
    def from_creds_file(creads_file: str) -> GoogleSheetsApiHandler:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            creads_file,
            ['https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive']
        )
        httpAuth = credentials.authorize(httplib2.Http())
        sheets_service = apiclient.discovery.build(
            'sheets', 'v4', http=httpAuth)
        drive_service = apiclient.discovery.build('drive', 'v3', http=httpAuth)
        return GoogleSheetsApiHandler(sheets_service, drive_service)

    def create_spreadsheet(self, title) -> Any:
        # creating empty spreadsheet with given title
        body = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = self.sheets_service.spreadsheets().create(body=body).execute()
        # giving permission to change spreadsheet
        shareRes = self.drive_service.permissions().create(
            fileId=spreadsheet['spreadsheetId'],
            body={'type': 'anyone', 'role': 'writer'},
            fields='id'
        ).execute()
        return spreadsheet

    def write_formula(
        self,
        spreadsheet,
        names: List[str],
        weights: List[float],
        marks: List[float]
    ) -> None:
        assert(len(names) == len(weights))
        sheet_name = 'Sheet1'
        cell_range = 'B2'

        # making formula for grade in Google Sheets format
        expression = '='
        for i in range(len(weights)):
            expression += f'C{2 + i}*{str(weights[i])}'
            if (i != len(weights) - 1):
                expression += '+'
        names.append('Итог')
        marks.append(expression)

        values = (
            names,
            marks
        )
        
        body = {
            'majorDimension': 'COLUMNS',
            'values': values
        }

        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet['spreadsheetId'],
            valueInputOption='USER_ENTERED',
            range=sheet_name + '!' + cell_range,
            body=body
        ).execute()
