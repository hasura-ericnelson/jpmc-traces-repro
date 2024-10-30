from hasura_ndc import start
from hasura_ndc.instrumentation import with_active_span
from opentelemetry.trace import get_tracer
from hasura_ndc.function_connector import FunctionConnector
import asyncio
from hasura_ndc.errors import UnprocessableContent
import requests
from pydantic import BaseModel, validator, ValidationError, model_validator
from typing import Optional
from datetime import date, datetime

connector = FunctionConnector()
TOKEN = "eyJhbGciOiJFZERTQSIsImtpZCI6IjlkX2JMaEVGbWpSelMwanpxajlOSk15Vmt4TUpDZGpJeVkweFZxMFpWNlEiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiI0OWM2MGEzZS04YWU2LTRiODQtYjdjZC0zNGQxOWMyZWRiYTUiLCJleHAiOjE3MzAyMTE1MzgsImlhdCI6MTczMDIwNzkzOCwiaXNzIjoiaHR0cHM6Ly9hdXRoLnByby5oYXN1cmEuaW8vZGRuL3Rva2VuIiwic3ViIjoiYWUwODk4NDgtY2MxMy00NDY5LWJhM2MtMTUzYTE1MGJkNWM3In0.3SH_JaWnyNp_KbeQUeCP5PkT0cl1LV0APjttJZ1_R3xV53thbGDEGiQ-xlVriHaCMkWSpoeFhyLUNej2caqbCQ"
headers = {'Content-Type': 'application/json', 'x-hasura-ddn-token': TOKEN}
GQL_ENDPOINT = "https://in-macaque-4009-786500d79c.ddn.hasura.app/graphql"


class TransactionQueryParams(BaseModel):
    arn: int
    crn: Optional[int] = None
    account_activity_start_date: Optional[str] = None
    account_activity_end_date: Optional[str] = None
    etu_standard_transaction_type_code: Optional[str] = None
    card_number: Optional[str] = None
    etu_standard_expense_category_code: Optional[str] = None

    @model_validator(mode='before')
    def check_date_and_arn(cls, values):
        arn = values.get('arn')
        start_date = values.get('account_activity_start_date')
        end_date = values.get('account_activity_end_date')
        if arn is None:
            raise ValueError("ARN is required")
        if (start_date is None) != (end_date is None):
            raise ValueError("Both Start and End Date must be provided")
        return values


@connector.register_query  # This is how you register a query
async def postedtxn(params: TransactionQueryParams):
    print('help me')
    if params.crn:
        query = """
        query ($arn: Int8!, $crn: Int8!) {
            cardPostedTxn (where: {arn:{_eq:$arn}, crn: {_eq:$crn}}) {
                arn
                crn
                pstDt
                pstTm
                cardPan
                txnAm
                crdb
                txnDt
                txnTypCd
                expnseCat
                authDt
                authTm
                authHigh
                authLow
                txnRefNb
                featrTypCd
                poiTyp
                toknRqstNb
                toknRqstId
                disptTypCd
                fraudTypCd
                sicCd
                mcc
                mrchDba
                mrchCity
                mrchState
                mrchPstCd
                mrchCntryCd
                mrchPoNb
              }
        }
        """
        variables = {"arn": params.arn, "crn": params.crn}
    elif params.account_activity_start_date and params.account_activity_end_date:
        query = """
        query ($arn: Int8!, $startdate: Date!, $enddate: Date!) {
            cardPostedTxn (where: {arn:{_eq:$arn},pstDt: {_gte: $startdate, _lte: $enddate}}) {
            arn
            crn
            pstDt
            pstTm
            cardPan
            txnAm
            crdb
            txnDt
            txnTypCd
            expnseCat
            authDt
            authTm
            authHigh
            authLow
            txnRefNb
            featrTypCd
            poiTyp
            toknRqstNb
            toknRqstId
            disptTypCd
            fraudTypCd
            sicCd
            mcc
            mrchDba
            mrchCity
            mrchState
            mrchPstCd
            mrchCntryCd
            mrchPoNb
          }
        }
        """
        variables = {
            "arn": params.arn,
            "startdate": params.account_activity_start_date,
            "enddate": params.account_activity_end_date
        }
    elif params.etu_standard_transaction_type_code:
        query = """
        query ($arn: Int8!, $txnTypCd: Varchar!) {
            cardPostedTxn (where: {arn:{_eq:$arn},txnTypCd: {_eq: $txnTypCd}}) {
            arn
            crn
            pstDt
            pstTm
            cardPan
            txnAm
            crdb
            txnDt
            txnTypCd
            expnseCat
            authDt
            authTm
            authHigh
            authLow
            txnRefNb
            featrTypCd
            poiTyp
            toknRqstNb
            toknRqstId
            disptTypCd
            fraudTypCd
            sicCd
            mcc
            mrchDba
            mrchCity
            mrchState
            mrchPstCd
            mrchCntryCd
            mrchPoNb
          }
        }
        """
        variables = {"arn": params.arn,
                     "txnTypCd": params.etu_standard_transaction_type_code
                     }
    elif params.card_number:
        query = """
        query ($arn: Int8!, $cardPan: Varchar!) {
            cardPostedTxn (where: {arn:{_eq:$arn}, cardPan: {_eq: $cardPan}}) {
            arn
            crn
            pstDt
            pstTm
            cardPan
            txnAm
            crdb
            txnDt
            txnTypCd
            expnseCat
            authDt
            authTm
            authHigh
            authLow
            txnRefNb
            featrTypCd
            poiTyp
            toknRqstNb
            toknRqstId
            disptTypCd
            fraudTypCd
            sicCd
            mcc
            mrchDba
            mrchCity
            mrchState
            mrchPstCd
            mrchCntryCd
            mrchPoNb
          }
        }
        """
        variables = {"arn": params.arn,
                     "cardPan": params.card_number
                     }
    elif params.etu_standard_expense_category_code:
        query = """
        query ($arn: Int8!, $expnseCat: Varchar!) {
            cardPostedTxn (where: {arn:{_eq:$arn}, expnseCat: {_eq: $expnseCat}}) {
            arn
            crn
            pstDt
            pstTm
            cardPan
            txnAm
            crdb
            txnDt
            txnTypCd
            expnseCat
            authDt
            authTm
            authHigh
            authLow
            txnRefNb
            featrTypCd
            poiTyp
            toknRqstNb
            toknRqstId
            disptTypCd
            fraudTypCd
            sicCd
            mcc
            mrchDba
            mrchCity
            mrchState
            mrchPstCd
            mrchCntryCd
            mrchPoNb
          }
        }
        """
        variables = {"arn": params.arn,
                     "expnseCat": params.etu_standard_expense_category_code
                     }
    else:
        query = """
        query ($arn: Int8!) {
            cardPostedTxn (where: {arn:{_eq:$arn}}) {
            arn
            crn
            pstDt
            pstTm
            cardPan
            txnAm
            crdb
            txnDt
            txnTypCd
            expnseCat
            authDt
            authTm
            authHigh
            authLow
            txnRefNb
            featrTypCd
            poiTyp
            toknRqstNb
            toknRqstId
            disptTypCd
            fraudTypCd
            sicCd
            mcc
            mrchDba
            mrchCity
            mrchState
            mrchPstCd
            mrchCntryCd
            mrchPoNb
          }
        }
        """
        variables = {"arn": params.arn
                     }

    response = requests.post(
        GQL_ENDPOINT,
        json={'query': query, 'variables': variables},
        headers=headers
    )

    return response.json()


if __name__ == "__main__":
    start(connector)
