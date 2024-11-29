import os
import azure.functions as func
import logging
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from pydantic import BaseModel
import json

class EventBase(BaseModel):
    id: str
    source: str
    type: str
    time: str
    userid: str
    isadmin: bool

# Pydantic model for PingEvent
class PingEvent(EventBase):
    type: str = "ping"

# Pydantic model for LogoutEvent
class LogoutEvent(EventBase):
    type: str = "logout"

# Pydantic model for LoginEvent
class LoginEvent(EventBase):
    type: str = "login"

# Event Type Dictionary to handle the different event types
EVENT_TYPE_MAP = {
    "ping": PingEvent,
    "logout": LogoutEvent,
    "login": LoginEvent
}

app = func.FunctionApp()

# Fetch the Event Hub and storage configuration from environment variables
source_event_hub_name = os.getenv("SourceEventHubName")
destination_event_hub_name = os.getenv("DestinationEventHubName")
destination_event_hub_connection_string = os.getenv("DestinationEventHubConnectionString")

@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name=source_event_hub_name,
                               connection="SourceEventHubConnectionString",
                               consumer_group="default2")
async def eventhub_trigger(azeventhub: func.EventHubEvent):    
    logging.info('destination_event_hub_connection_string')
    logging.info(destination_event_hub_connection_string)

    # Create the Event Hub producer client
    producer = EventHubProducerClient.from_connection_string(
        conn_str=destination_event_hub_connection_string, eventhub_name=destination_event_hub_name
    )
    
    # Prepare the body and properties
    message_body = azeventhub.get_body().decode('utf-8')
    event_data_dict = json.loads(message_body)
    try:
        # Parse the incoming JSON as an EventBase (base model) to get type
        event_data_dict = json.loads(message_body)
        event_type = event_data_dict.get("type", "none")  # Default to "none" if type is not present
        
        if event_type not in EVENT_TYPE_MAP:
            logging.warning(f"Unknown type: {event_type}. Setting default type.")
            # Optionally, you could return here or just continue with a default event type

        # Parse into the correct model based on type
        event_model = EVENT_TYPE_MAP.get(event_type, EventBase)  # Use EventBase for default
        event_data = event_model.parse_raw(message_body)
        
        logging.info(f"Processed {event_type} event for id: {event_data.id}")

    except Exception as e:
        logging.error(f"Failed to parse event: {e}")
        return
    event_data = EventData(message_body)
    
    logging.info('EventHub Input trigger received an event: %s', message_body)
    
    # Set custom properties on the EventData object
    event_data.properties = {
        "Table": event_type,  # Set the "Table" property to the type value (default is "none")
        f"property_key_{event_type}": f"value_{event_type}"  # Dynamically generate properties
    }
    
    # Send the event to the destination Event Hub
    async with producer:
        # Create a batch.
        event_data_batch = await producer.create_batch()
        
        # Add events to the batch.
        event_data_batch.add(event_data)
        
        # Send the batch of events to the event hub.
        await producer.send_batch(event_data_batch)
        
        logging.info('EventHub Output pushed to Destination Manually')
