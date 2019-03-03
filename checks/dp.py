import aiohttp
from urllib.parse import urljoin

class DPCheck:

    def __init__(self, server_url, token, unti_id) -> None:
        super().__init__()
        self.server_url = server_url
        self.token = token
        self.unti_id = unti_id
        
    
    async def _set_competence(self):
        self._competence_uuid = "9e605f7b-9ffe-44f3-996e-58e545e466c2"
        self._competence_value = 101


    async def _set_user_data(self):
        await self._set_competence()

        async with aiohttp.ClientSession() as session:
            url = urljoin(self.server_url, f'/api/v1/user_meta/{self.unti_id}?app_token={self.token}')
            body = [{
                "competence": self._competence_uuid,
                "value": self._competence_value 
            }]
            async with session.post(url, json=body) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    if json and json.get("status", None) == 0:
                        return True
                    else:
                        return False
                else:
                    return False


    async def get_user_data(self):
        async with aiohttp.ClientSession() as session:
            url = urljoin(self.server_url, f'/api/v1/user/{self.unti_id}?app_token={self.token}')
            async with session.get(url) as resp:
                if resp.status == 200:
                    elements = await resp.json()
                    filtered = [ elem for elem in elements if elem.get('uuid', None) == self._competence_uuid ]
                    if len(filtered) == 1 and filtered[0].get("value", None) == str(self._competence_value):
                        return True
                    else:
                        return False
                else:
                    return False
    
    
    async def check(self):
        return (await self._set_user_data()) and (await self.get_user_data())
