from base64 import b64decode
from typing import Any, Union
import requests

from core.tools.entities.tool_entities import ToolInvokeMessage, ToolParameter
from core.tools.tool.builtin_tool import BuiltinTool


class PDF2MDTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) \
        -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
        """
        mode = tool_parameters.get('mode', 'image')
        if mode == 'base64':
            file_base64 = tool_parameters['file_base64']
            if not file_base64:
                self.create_text_message('Please input file_base64')
        else:
            image_id = tool_parameters.get('image_id', '')
            if not image_id:
                return self.create_text_message('Please create image')
            file_base64 = self.get_variable_file(self.VARIABLE_KEY.IMAGE)
            if not file_base64:
                self.create_text_message('Image empty')

        timeout = tool_parameters.get('timeout', 60)

        response = self.pdf2md_respnse(
            app_id=self.runtime.credentials.get('intsig_app_id'), 
            secret_code=self.runtime.credentials.get('intsig_secret_code'), 
            file_base64=file_base64, 
            timeout=timeout)

        if response.status_code != 200:
            raise Exception(f'Error {response.status_code}: {response.text}')
        
        return [
            self.create_text_message(response.json()["result"]["markdown"])
        ]
    
    @staticmethod
    def pdf2md_respnse(app_id, secret_code, file_base64, timeout):
        url = 'https://api.textin.com/ai/service/v1/pdf_to_markdown?page_count=999&apply_document_tree=1'
        headers = {
            'x-ti-app-id': app_id,
            'x-ti-secret-code': secret_code
        }

        response = requests.post(
            url,
            headers=headers,
            data=b64decode(file_base64),
            timeout=timeout
        )

        return response

    def get_runtime_parameters(self) -> list[ToolParameter]:
        """
        override the runtime parameters
        """
        return [
            ToolParameter.get_simple_instance(
                name='image_id',
                llm_description=f'the image id that you want to vectorize, \
                    and the image id should be specified in \
                        {[i.name for i in self.list_default_image_variables()]}',
                type=ToolParameter.ToolParameterType.SELECT,
                required=True,
                options=[i.name for i in self.list_default_image_variables()]
            )
        ]
    
    def is_tool_available(self) -> bool:
        return len(self.list_default_image_variables()) > 0
