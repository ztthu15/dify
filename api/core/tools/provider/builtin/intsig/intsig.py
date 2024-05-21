from typing import Any

from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.provider.builtin.intsig.tools.intsig_pdf2md import PDF2MDTool
from core.tools.provider.builtin_tool_provider import BuiltinToolProviderController


class PDF2MDProvider(BuiltinToolProviderController):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            if "intsig_app_id" not in credentials or not credentials.get("intsig_app_id"):
                raise ToolProviderCredentialValidationError("x-ti-app-id is required.")
            if "intsig_secret_code" not in credentials or not credentials.get("intsig_secret_code"):
                raise ToolProviderCredentialValidationError("x-ti-secret-code is required.")
            
            intsig_app_id = credentials.get("intsig_app_id")
            intsig_secret_code = credentials.get("intsig_secret_code")

            # 验证 APIKey
            response = PDF2MDTool.pdf2md_respnse(app_id=intsig_app_id, secret_code=intsig_secret_code, file_base64='', timeout=60)
            if response.status_code == 40305 or response.status_code == 200:
                pass
            else:
                raise ToolProviderCredentialValidationError(
                    f'{response.status_code}: {response.text}'
                )
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))