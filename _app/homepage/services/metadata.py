from webauthn.helpers.structs import CredentialDeviceType


class MetadataService:
    # Pulled from https://github.com/passkeydeveloper/passkey-authenticator-aaguids/ on 2024-01-03
    aaguid_json = {
        "ea9b8d66-4d01-1d21-3ce4-b6b48cb575d4": {"name": "Google Password Manager"},
        "adce0002-35bc-c60a-648b-0b25f1f05503": {"name": "Chrome on Mac"},
        "08987058-cadc-4b81-b6e1-30de50dcbe96": {"name": "Windows Hello"},
        "9ddd1817-af5a-4672-a2b9-3e3dd95000a9": {"name": "Windows Hello"},
        "6028b017-b1d4-4c02-b4b3-afcdafc96bb2": {"name": "Windows Hello"},
        "dd4ec289-e01d-41c9-bb89-70fa845d4bf2": {"name": "iCloud Keychain (Managed)"},
        "531126d6-e717-415c-9320-3d9aa6981239": {"name": "Dashlane"},
        "bada5566-a7aa-401f-bd96-45619a55120d": {"name": "1Password"},
        "b84e4048-15dc-4dd0-8640-f4f60813c8af": {"name": "NordPass"},
        "0ea242b4-43c4-4a1b-8b17-dd6d0b6baec6": {"name": "Keeper"},
        "f3809540-7f14-49c1-a8b3-8f813b225541": {"name": "Enpass"},
        "b5397666-4885-aa6b-cebf-e52262a439a2": {"name": "Chromium Browser"},
        "771b48fd-d3d4-4f74-9232-fc157ab0507a": {"name": "Edge on Mac"},
        "39a5647e-1853-446c-a1f6-a79bae9f5bc7": {"name": "IDmelon"},
        "d548826e-79b4-db40-a3d8-11116f7e8349": {"name": "Bitwarden"},
        "fbfc3007-154e-4ecc-8c0b-6e020557d7bd": {"name": "iCloud Keychain"},
        "53414d53-554e-4700-0000-000000000000": {"name": "Samsung Pass"},
        "66a0ccb3-bd6a-191f-ee06-e375c50b9846": {"name": "Thales Bio iOS SDK"},
        "8836336a-f590-0921-301d-46427531eee6": {"name": "Thales Bio Android SDK"},
        "cd69adb5-3c7a-deb9-3177-6800ea6cb72a": {"name": "Thales PIN Android SDK"},
        "17290f1e-c212-34d0-1423-365d729f09d9": {"name": "Thales PIN iOS SDK"},
    }

    def get_provider_name(self, *, aaguid: str, device_type: CredentialDeviceType) -> str:
        """
        Try to map the provided AAGUID to a human-friendly provider name
        """
        default_name = ""

        if not aaguid:
            return default_name

        provider_metadata = self.aaguid_json.get(aaguid, {})
        provider_name = provider_metadata.get("name", None)

        # Return the name if we could look one up
        if provider_name is not None:
            return provider_name

        # Try to derive the provider name
        if (
            aaguid == "00000000-0000-0000-0000-000000000000"
            and device_type == CredentialDeviceType.MULTI_DEVICE
        ):
            return "iCloud Keychain"

        # When all else fails, provide a default name
        return default_name
