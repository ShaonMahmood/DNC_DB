Welcome to DNC DB!
===================

Hey! This is a webhook project. An Web Api for receiving and sending data information.

----------

Documentation
-------------
DNC DB stores data information in a database received from external sources and send this stored data to Other external sources

#### Project Requirements:

- python version >= 3.4
- postgresql >=  9.3

#### Project Setup:

> - Clone or Download the project.
> - Create A DataBase according to settings (recommended POSTGRES).
> - Install the requirements via the command, pip install -r requirements.txt (recommended to use virtualenvironment).
> - Migrate using command python manage.py migrate.

#### API Configuration:

> - **URL** : "http://domain/api/{provider}/{provider_no}/",
> - **AUTHENTICATION** : username and password will be provided
> - Currently this api supports two providers, vicidial and xencall

#### Accepted Data Format :

1.  Accepts both get and post json data.

2. **Required Fields for xencall :**
> - source
> - result
> - leadid
> - phone1
> - phone2

3. **Required Fields for vicidial :**
> - phone_number
> - phone_code
> - listID
> - leadID
> - dispo
> - talk_time

4. For fields hook_sms_sent and hook_email_sent the values must be from these sets,
> - **accepted_set** :{"DNC", "dnc", "Dnc", "Do Not Call",}





#### Example :

> A typical post data may contain these fields(vicidial):
>>	{
>>        "phone_number": "3435566777",
>>        "phone_code": "1",
>>        "listID": "23",
>>        "leadID": "44",
>>        "dispo": "DNC",
>>        "talk_time": "454",

>>    }

> A typical post data may contain these fields(xencall):
>>	{
>>        "source": "xrc",
>>        "result": "DNC",
>>        "leadid": "44",
>>        "phone1": "9458794585",
>>        "phone2": "7548484574",

>>    }

