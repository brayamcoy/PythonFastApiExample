from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Text
from datetime import datetime
from uuid import uuid4 as uuid
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput
from hubspot.crm.contacts.exceptions import ApiException
from models import ContactCreateSchema, ContactBodySchema, ApiCallCreate
from database import ApiCall, session
import requests
import json

import uvicorn

# Clients definition
app = FastAPI()
api_client = HubSpot(access_token='pat-na1-bfa3f0c0-426b-4f0e-b514-89b20832c96a')
api_key= "pk_3182376_Q233NZDZ8AVULEGGCHLKG2HFXWD6MJLC"
list_id = "900200532843"


@app.get('/')
def read_root():
    return {"welcome": "Welcome to my ORBIDI API"}

@app.post('/contacts/hubspot')
def create_contact(contact_data: ContactCreateSchema):
    try:
        data={
            "email": contact_data.email,
            "firstname": contact_data.firstname,
            "lastname": contact_data.lastname,
            "phone": contact_data.phone,
            "website": contact_data.website,
            "estadoclickup": contact_data.estadoclickup
        }
        simple_public_object_input = SimplePublicObjectInput(
            properties=data
        )
        api_response = api_client.crm.contacts.basic_api.create(
            simple_public_object_input=simple_public_object_input
        )
        api_call_data={
            "endpoint":"/contacts/hubspot",
            "parameters": "Success",
            "result":"Success"
        }
        #TODO Implement database integration
    except ApiException as e:
        print("Exception when creating contact: %s\n" % e)

@app.post('/contacts/syncronize')
async def syncronize_contacts(background_tasks: BackgroundTasks):
    # Get hubspot contacts
    hubspot_contacts = api_client.crm.contacts.get_all()

    # Sincronize each contact in background
    for contact in hubspot_contacts:
        background_tasks.add_task(sync_contact, contact)
    return {"message": "Contact synchronization initiated"}

def sync_contact(contact: ContactBodySchema):
    try:
      # Validate hs state
       if hasattr(contact, 'estadoclickup'):
            #Validate if is string is not null
        if contact.estadoclickup is not None and contact.estadoclickup.strip():
            return

        url = "https://api.clickup.com/api/v2/list/" + list_id + "/task"

        payload = {
            "name": "New Task Name",
            "description": "New Task Description",
            "assignees": [
                183
            ],
            "tags": [
                "tag name 1"
            ],
            "status": "Open",
            "priority": 3,
            "due_date": 1508369194377,
            "due_date_time": False,
            "time_estimate": 8640000,
            "start_date": 1567780450202,
            "start_date_time": False,
            "notify_all": True,
            "parent": None,
            "links_to": None,
            "check_required_custom_fields": True,
            "custom_fields": [
                {
                "id": "0a52c486-5f05-403b-b4fd-c512ff05131c",
                "value": "This is a string of text added to a Custom Field.",
                }
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": api_key
        }
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        print(data) 
        # update_contact
        update_contact(contact.id, "ok")
    except Exception as e:
        # Print the error message
        print(f"Error syncronizing contact: {str(e)}")


def update_contact(contact_id: str, estadoclickup: str):
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    headers = {
        'Authorization': f"Bearer pat-na1-bfa3f0c0-426b-4f0e-b514-89b20832c96a",
        'Content-Type': 'application/json'
    }
    data = {
        'properties': {
            'estadoclickup': estadoclickup
        }
    }

    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle error
        raise HTTPException(status_code=500, detail='Error trying to update')


def create_api_call(api_call):
    new_api_call = ApiCall(
        endpoint=api_call['endpoint'],
        parameters=api_call['parameters'],
        result=api_call['result']
    )
    session.add(new_api_call)
    session.commit()
    return {"message": "API call created successfully"}