import asyncio
import logging
import websockets
from datetime import datetime
from ocpp.v16 import call
from ocpp.v16.enums import AuthorizationStatus
from ocpp.v16 import ChargePoint as cp

logging.basicConfig(level=logging.INFO)


# get local machine name


# connection to hostname on the port.


class ChargePoint(cp):

   async def authorize(self):
       r=call.AuthorizePayload(id_tag="test_cp34")
       response1 = await self.call(r)

       if response1.id_tag_info['status'] == 'Accepted' :
           print("authorized.")

           sdadd=call.StartTransactionPayload(connector_id= 6,
           id_tag = "test_cp3", meter_start = 200, timestamp = datetime.utcnow().isoformat())

           response12 = await self.call(sdadd)
           if response12.id_tag_info['status'] == 'Accepted':
               print("Charging now")
               tid=response12.transaction_id
               for j in range(0,7):
                   await asyncio.sleep(2)
                   print("Charging now")

               sdadd2 = call.StopTransactionPayload(meter_stop = 1200,timestamp= datetime.utcnow().isoformat(),transaction_id= tid)
               response123 = await self.call(sdadd2)


           else:
               print('transaction failed')


       else:
           print("Not Authorized")






   async def send_boot_notification(self):
       request = call.BootNotificationPayload(
           charge_point_model="CPF50", charge_point_vendor="ChargePoint INC"
       )
       response = await self.call(request)

       if response.status == 'Accepted':
           print("Boot confirmed.")



async def main():
   async with websockets.connect(
       'ws://localhost:9005/CP_4',
        subprotocols=['ocpp1.6']
   ) as ws:


       try:
           cp = ChargePoint('CP_4', ws)
           await asyncio.gather(cp.start(), cp.authorize(), cp.send_boot_notification())


       except:

           pass
           print('Chargepoint not authorized')








asyncio.run(main())


