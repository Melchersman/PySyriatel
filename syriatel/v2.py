"""Clients for Syriatel Cash API v2; accounts represent Akrab Elik logins."""
import asyncio
import re
from urllib.parse import quote
from .client import SyriatelAPI, SyriatelAPISync


class SyriatelV2:
    def __init__(self, api_token='', base_url='https://api.melchersman.com/syr-cash/v2', timeout=30, session=None):
        self._transport=SyriatelAPI(api_token,base_url=base_url,timeout=timeout,session=session)

    async def __aenter__(self):return self
    async def __aexit__(self,*args):await self.close()
    async def close(self):await self._transport.close()

    def _selector(self,gsm,pay_code):
        if bool(gsm)==bool(pay_code):raise ValueError('Provide exactly one of gsm or pay_code')
        if gsm:
            value=self._transport._normalize_number(str(gsm))
            if not re.fullmatch(r'09[0-9]{8}',value):raise ValueError('Invalid GSM')
            return [('gsm',value)]
        return [('pay_code',str(pay_code))]

    def _number(self,account_id,gsm):
        if not re.fullmatch(r'akrab_[1-9][0-9]*',account_id):raise ValueError('Use an Akrab Elik account ID')
        value=self._transport._normalize_number(str(gsm))
        if not re.fullmatch(r'09[0-9]{8}',value):raise ValueError('Invalid GSM')
        return '/accounts/'+quote(account_id,safe='')+'/numbers/'+quote(value,safe='')

    def _digits(self,value,length):
        if not isinstance(value,str) or not re.fullmatch(r'[0-9]{'+str(length)+'}',value):raise ValueError('Use a string of exactly '+str(length)+' digits')
        return value

    async def incoming_transactions(self,*,gsm=None,pay_code=None,start_at=None,end_at=None,transaction_ids=None,limit=20,page=1):
        if type(limit) is not int or not 1<=limit<=200 or type(page) is not int or not 1<=page<=10000:raise ValueError('Invalid limit or page')
        params=self._selector(gsm,pay_code)+[('limit',limit),('page',page)]
        if start_at is not None:params.append(('start_at',start_at))
        if end_at is not None:params.append(('end_at',end_at))
        if transaction_ids:
            params.extend(('transaction_ids',str(value)) for value in transaction_ids)
        return await self._transport._request('GET','/transactions/incoming',params=params)

    async def get_balance(self,*,gsm=None,pay_code=None):
        return await self._transport._request('GET','/balance',params=self._selector(gsm,pay_code))

    async def list_accounts(self):
        return (await self._transport._request('GET','/accounts'))['accounts']

    async def list_numbers(self,account_id):
        return (await self._transport._request('GET','/accounts/'+quote(account_id,safe='')+'/numbers'))['numbers']

    async def remove_account(self,account_id):
        return await self._transport._request('DELETE','/accounts/'+quote(account_id,safe=''))

    async def get_plans(self):return await self._transport._request('GET','/plans')
    async def wallet_balance(self):return await self._transport._request('GET','/wallet')
    async def get_status(self):return await self._transport._request('GET','/status')

    async def create_link_session(self,gsm,password,*,idempotency_key):
        return await self._transport._request('POST','/link-sessions',body={'gsm':self._transport._normalize_number(str(gsm)),'password':password},idempotency_key=idempotency_key)

    async def get_link_session(self,session_id):
        return await self._transport._request('GET','/link-sessions/'+quote(session_id,safe=''))

    async def verify_link_session(self,session_id,code):
        return await self._transport._request('POST','/link-sessions/'+quote(session_id,safe='')+'/verify',body={'code':self._digits(code,6)})

    async def verify_pin(self,account_id,gsm,pin):
        return await self._transport._request('POST',self._number(account_id,gsm)+'/pin',body={'pin':self._digits(pin,4)})

    async def subscribe(self,account_id,gsm,*,idempotency_key,plan_id='monthly',periods=1):
        if type(periods) is not int or not 1<=periods<=12:raise ValueError('periods must be 1 to 12')
        return await self._transport._request('POST',self._number(account_id,gsm)+'/subscription',body={'plan_id':plan_id,'periods':periods},idempotency_key=idempotency_key)

    async def start_trial(self,account_id,gsm,*,idempotency_key):
        return await self._transport._request('POST',self._number(account_id,gsm)+'/trial',body={},idempotency_key=idempotency_key)

    async def set_auto_renew(self,account_id,gsm,enabled):
        if type(enabled) is not bool:raise ValueError('enabled must be a boolean')
        return await self._transport._request('PATCH',self._number(account_id,gsm)+'/subscription',body={'auto_renew':enabled})


class SyriatelV2Sync:
    def __init__(self,api_token='',base_url='https://api.melchersman.com/syr-cash/v2',timeout=30):
        self._loop=asyncio.new_event_loop()
        self._async_client=SyriatelV2(api_token,base_url,timeout)
    _run_async=SyriatelAPISync._run_async
    close=SyriatelAPISync.close
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def incoming_transactions(self,**kwargs):return self._run_async(self._async_client.incoming_transactions(**kwargs))
    def get_balance(self,**kwargs):return self._run_async(self._async_client.get_balance(**kwargs))
    def list_accounts(self):return self._run_async(self._async_client.list_accounts())
    def list_numbers(self,account_id):return self._run_async(self._async_client.list_numbers(account_id))
    def remove_account(self,account_id):return self._run_async(self._async_client.remove_account(account_id))
    def get_plans(self):return self._run_async(self._async_client.get_plans())
    def wallet_balance(self):return self._run_async(self._async_client.wallet_balance())
    def get_status(self):return self._run_async(self._async_client.get_status())
    def create_link_session(self,gsm,password,*,idempotency_key):return self._run_async(self._async_client.create_link_session(gsm,password,idempotency_key=idempotency_key))
    def get_link_session(self,session_id):return self._run_async(self._async_client.get_link_session(session_id))
    def verify_link_session(self,session_id,code):return self._run_async(self._async_client.verify_link_session(session_id,code))
    def verify_pin(self,account_id,gsm,pin):return self._run_async(self._async_client.verify_pin(account_id,gsm,pin))
    def subscribe(self,account_id,gsm,**kwargs):return self._run_async(self._async_client.subscribe(account_id,gsm,**kwargs))
    def start_trial(self,account_id,gsm,*,idempotency_key):return self._run_async(self._async_client.start_trial(account_id,gsm,idempotency_key=idempotency_key))
    def set_auto_renew(self,account_id,gsm,enabled):return self._run_async(self._async_client.set_auto_renew(account_id,gsm,enabled))
