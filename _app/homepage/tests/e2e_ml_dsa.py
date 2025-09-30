from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from webauthn.helpers import base64url_to_bytes

from homepage.services import AuthenticationService, CredentialService, RegistrationService


class TestE2EMLDSA(TestCase):
    """
    End-to-end tests of support for authenticators using ML-DSA algorithms
    """

    def setUp(self):
        settings.RP_ID = "webauthn.io"
        settings.RP_EXPECTED_ORIGIN = "https://webauthn.io"
        self.authentication_service = AuthenticationService()
        self.credential_service = CredentialService()
        self.registration_service = RegistrationService()
        # Initialize a session
        self.client.get(reverse("index"))

    def test_supports_ml_dsa_44(self):
        username = "mmiller"
        # Generate registration options
        self.client.post(
            reverse("registration-options"),
            {
                "username": username,
                "user_verification": "preferred",
                "attestation": "direct",
                "attachment": "platform",
                "algorithms": ["mldsa44"],
                "discoverable_credential": "required",
            },
            content_type="application/json",
        )

        # Set an expected challenge
        options = self.registration_service._get_options(username)
        assert options
        options.challenge = base64url_to_bytes(
            "4l8disV6VitGCg_EJvCNx7V92QLtBn_RYq9tTBEZ7j4B5hZI9kijJ2InLxQNRYVlgLROF3nfj80Yi7MPhXQwjw"
        )
        self.registration_service._save_options(username, options)

        # Verify registration response
        reg_response = self.client.post(
            reverse("registration-verification"),
            {
                "username": "mmiller",
                "response": {
                    "id": "-EM9FDFIdFVeqWdTycRjoZVN2ZS4vnVE-MBpg7k0pl4jpuqj4GnMCW3Wqlm2WWI2PQ",
                    "rawId": "-EM9FDFIdFVeqWdTycRjoZVN2ZS4vnVE-MBpg7k0pl4jpuqj4GnMCW3Wqlm2WWI2PQ",
                    "response": {
                        "attestationObject": "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YVkFoHSm6pITyZwvdLIkkrMgz0AmKpTBqVCgOX8pJQtghB7wxQAAAAQAAAAAAAAAAAAAAAAAAAAAADH4Qz0UMUh0VV6pZ1PJxGOhlU3ZlLi-dUT4wGmDuTSmXiOm6qPgacwJbdaqWbZZYjY9owEHAzgvIFkFIC4AIUrgARve17AEk0W30POluaL08p91eLXkktSjmAlmZdNTWhtUFj3wkseZEt4xpmWarG28Za86i7yq-B4df3uOuq3zQVTKOQUWJLWGJ3-wUUuyywPtkdgSqzQdcli6xMgwnVqh9r6FVL9Xp7x3kgjUVDqhux_k1D2d4ts2zqi1rUrSF6FNX139g3dd1VnUNQrMLdrwohR9CmE0fZ6Am4Df_OV2JxOrUEPzMFi5SeBcrU1oSj2lX_91gY179PO0wIOtTa1KzWvwOYa_KjOj9Ow16AtmsXrcpL-jYW4_bFn4kpT9G-vDG4qPFDpint62g0DDjEt7JrF288aIZXOpsbVmnjw2_O_5pFFvFpH32gD7_NdmvE6PSymNxPcTCnMzY3xv5wJXiEDhO21E85n78Oay4k7PzWHvzQxlJldIYw-9TfKZXqZa6sIbE-LyZj_Y2FV1Owd4WLvKCNcO-IIP3XFcZ7__XPZtAsBTJ5Z5w18jRnlMNKTygva-F2Ec65tA2skED9PnVyS_WjtZN5VjbhuU-D9DIDXEgUjitdcXWbCruDjxaBwjuDFXOI9cYdp4n-KWCZGJdX9QFHDGkvX6zDXupFrFV1q1JeKCayuMJjL3Z44AMF2UtjNODzhlviE8neX5NSfXdf36FWGFER6D6YCGGvooW8EBCx8OLPRNGGwoKBrEflr_ISYIdyw8-rDkAG0-bka_ulzfg8uTY8BXNu0HhqsteUPni4HlhUXMb0yI1DbLi5hTTkpBEBfmjzTJ8JMDe9sOOaqU2PrOzvIs5c7fx_VBqQZbF6amei2Y41okZJWwW0LWNvL2JQ_Yj9deHMczichCHWVX3uCL-SfPL3AaLeWLPjTAejU-H1Lnn2jWQeHtiRxBL1eleZNmJVqFbrgclcMXirM6rrmPrsbFe41fDF3Hm1KgcKkpZMPSICijfDCT4csVeLDxmsg9aDYwboxigOVHZa-zAmePLBZrPJIWDNEHNBG9CdEG-RfeshvnRbPerB1zLzA9jP-Jj55_Xd4igau4FEc7dLWgyn2b2Q3aMAaDnKCzEScd301WeuZtutm6flzqDPCUTJnoniUHuO__bALWkzIxe5rHW6wQ_wPBEX32bQNN-gtI6_yiw-UTwu3egro3tDp7ZzHkMSslF9FHD7divbmeEzsE8N4iOwO5kWFt2jY9VpjGXAhyCcGZtWU68SzllOpWzvuacFjlE5KZ_c4nHhYdaphJAjXvbkog-vGUwjffCXe9gQhIliwPzREtccZdgyLKiBAlypp0pwVKe6disU9-2kflk_BXPRf1PkBEqO41ySFZWLb6eSij9FrIXtPAo4RFmeKPLoYT-ce3gi8_XftVv7MDl9s0hoFlgh5vTh1xMdpxEt-6BxdesEF3zJycxNY4QFVkUKE78geXogQFz2QE7kW4ncTXjq4IydHOKX9Bp2P8uGcCJ6dzW3PFE-Zurf1klV-rkvT7xE-Tds7CPeWkrRr_Ckhn6rQ2Z3-Sjz5bgIRHiBnd0iZfm6ZgD77nVHY7ztaSmUQ7JWbeFSz0eoYExgXi7HfSdV77DlHxIjcNlrSh58SGWfkSwUVboOUJKy_B3EbBDeweqn1pf7QIjAJnYL7WiogmAku2UxEBQijtPAusmyhLf0_aTEFFc3zdGutHim3dzAKfJucy2aBm8ViQxY_U1N26WVO6sfui7dZVhqkQniZLCq8N_xqEMqWV6utksRHOvITvB_SqmeDacy2ZfiSogU8K5G2ha2NyZWRQcm90ZWN0Ag",
                        "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiNGw4ZGlzVjZWaXRHQ2dfRUp2Q054N1Y5MlFMdEJuX1JZcTl0VEJFWjdqNEI1aFpJOWtpakoySW5MeFFOUllWbGdMUk9GM25majgwWWk3TVBoWFF3anciLCJvcmlnaW4iOiJodHRwczovL3dlYmF1dGhuLmlvIiwiY3Jvc3NPcmlnaW4iOmZhbHNlfQ",
                    },
                    "type": "public-key",
                    "clientExtensionResults": {},
                },
            },
            content_type="application/json",
        )

        self.assertEquals(reg_response.json(), {"verified": True})

        # Request authentication options
        self.client.post(
            reverse("authentication-options"),
            {
                "username": username,
                "user_verification": "preferred",
            },
            content_type="application/json",
        )

        # Set an expected challenge
        options = self.authentication_service._get_options(
            cache_key=self.client.session.session_key,
        )
        assert options
        options.challenge = base64url_to_bytes(
            "Ji15971jSESa9haCUYb7s_pMhV8DNNwYT8Wb5zbEo151Ab7s_MuT-_MIjnousfaF2Q3emFAx7GkpXkTUmMicTQ"
        )
        self.authentication_service._save_options(
            cache_key=self.client.session.session_key,
            options=options,
        )

        # Verify authentication response
        auth_response = self.client.post(
            reverse("authentication-verification"),
            {
                "username": username,
                "response": {
                    "id": "-EM9FDFIdFVeqWdTycRjoZVN2ZS4vnVE-MBpg7k0pl4jpuqj4GnMCW3Wqlm2WWI2PQ",
                    "rawId": "-EM9FDFIdFVeqWdTycRjoZVN2ZS4vnVE-MBpg7k0pl4jpuqj4GnMCW3Wqlm2WWI2PQ",
                    "response": {
                        "authenticatorData": "dKbqkhPJnC90siSSsyDPQCYqlMGpUKA5fyklC2CEHvAFAAAACA",
                        "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uZ2V0IiwiY2hhbGxlbmdlIjoiSmkxNTk3MWpTRVNhOWhhQ1VZYjdzX3BNaFY4RE5Od1lUOFdiNXpiRW8xNTFBYjdzX011VC1fTUlqbm91c2ZhRjJRM2VtRkF4N0drcFhrVFVtTWljVFEiLCJvcmlnaW4iOiJodHRwczovL3dlYmF1dGhuLmlvIiwiY3Jvc3NPcmlnaW4iOmZhbHNlLCJvdGhlcl9rZXlzX2Nhbl9iZV9hZGRlZF9oZXJlIjoiZG8gbm90IGNvbXBhcmUgY2xpZW50RGF0YUpTT04gYWdhaW5zdCBhIHRlbXBsYXRlLiBTZWUgaHR0cHM6Ly9nb28uZ2wveWFiUGV4In0",
                        "signature": "e7L-Xli-2lj9ZlP2s26sbrvFGLkVrz74BZnDsLW-7HOhj7AcEl5Zgtm3VLvLtcrfqyKE0PTuFrswsikm7t6ddhxXphxWcSo4ggarl6ODQk8NdPCYoFhoK8qwpqKZKmJAl9xDsJE1HAudrWLgq_747JV4QmGLizK0_oJgGM7WLd5xVYvKsl14odBFjU_ZBCrjB0UHIMg8aAq1727yZnY1eiNeF_sEmci_pigYCo-MbxbHmQWPp-U75sGSPPfK0soN2-29_aIxRO4Fg8P37WrwVUrEFdG2PFNgAhcM-ljjyv3mkCfsLUiQNuS-a0cn6MeygREc2HBwE6ChS351-dpNTbkfnb-o1fA6suP1sh3-i7YZrEn9e2J7UZxIAEJPpmuKxYFA4Fj0lAGUhi3lvnkWPOnS8BUjPr5q5z5iEbyL4MokDP75G723Tyy-5L8u1pLmlSLiuwvuW5MBkEhjVVj0RpVSnCoqzwE9A9ZmqZx5wv5gQEi4hAA64mSoXGdUZ5EGkPGrrIDjGyIOrLjuHOSZ6hjyioZvMA1nCQJ76oaL5-Pn1FR1VTurI5ccTWrDAo5sHuo8uGjx9bsyy_aMT3Nzosu29PArTm0AkJFd7INXky0L9itCmhujSnali9zTO8UuwV0G8sZeB2BG4VZN2nkjT1Ib8VeBnSMTlIFVOI2JHlD9kePZuV3nCuAvK8j5qH5OPJoEeJzuxGHP2k7f0941kzyW9sjBaD90HEusVGGgST0qWigEKU3kKaO_Du5ZngcqlmKnnFVKXQk5mEV5nFs9ia76sKe9FKYUp_ZxsVFATcjXETW5GuXF1qIj0ZTCSmhn8V_cqEH29fQWyy9qxNa6kkKc4koZUP36B-h5yVawIDdfyjl-VueUvUyEunPv1EyqXQaf9bo-WThxD_5v3Bd2sYTOI__0PIsUvCASjZJMQU4jpwyXoR2EsLWDRD4fsAxLmdao0iXNxdlH0Ys2MqkXkkMbIylccEHkFjbm_VB5tPYQkFRqqRX13KUyYqqTpaT6MdD8IpltlzJxcNLd9mazUvOfSaf5ho2FFtv8TMubekKU8b92MoPQpjeS1DJ9y2pvMrtIiZP0Lm0WTeniN6luRfUN-4v5GU6FPajkOPLNV9OXJKLREhrA_SvbDldSF9RtWZOqIk1WeTlbnEWlejtwWFoLSScCSfExu6bu_vv9NKK-E8mTWF8_f4bCvlZQp58BEsTHrZuBiQzH34Z5wPeOZuuQlqbAquIS4_W6z_XmNW-d4FhIp2U3y9sYC7wpo1M7N7MB3HKwAliPVgsNHBRI4ZLZ-dL3FCyCMThKJqQMNrMcRif_Mm5Du--Atjn1UH2u2gAxiBA6IY7uSlSn-OJEO-m8qeif8zsdvVhXtJMxNAWZHhQ4QuRFgjuDgxy1nVuhGHdmXi6tseiiC2NQ9iqGuBRetexfz84R93RVSbKMkYlvBU1KPe8ARVf_N52C1KC9F2b3Uo5To9iD2lXShcsGkQkcAX5gjmhy4jrmTv5-pUJYAHa6A9Vorr59D7-Y-CVvVX59YJB9-kMT8wzHQdj2XimbcLKnS5Z4BKsMMEIt01LVkdHcBP9tKBQ20e-Kmf25wsUr9TqFa7ukQEhfLwgflIBbobAJoGKFC2_3fIKaEBuoAOoErASxPClLNAbBqG1JAdrAq9Ki3WC46aN4b-Q6ykfbk2azLAxOzFftJuhLWGLLCkOxbxjfaUrRJ51h8Dwrpy2xBT1qWurNnfFTrzScouK-R8G4SfsyaSiejiaLYLsWZVCcpeH_S8cqQuBFCMpQfxiPn2reOgMFhSzbdSDkzwUTQsjGq94QTs7bdS0LlyRb4OUa0s3szGSIa7n4vQ10uc9gzHlDxEqgaKSpPlVDyvZs58GC3PCZ2HJiiVbuc508_rV1xuydd7asPlyaOAMXImKPxp7d6rAGLbDOQOKS4U9sr6wKQVPnfPqg7TvmtuXTJS5Y_M6mutU7Bn8y6qmbjt5EtoETTSORHfx71ySMLZ8zxveJdsaNow6lfjvI0myk8oSDIucRar1j9G2m13B3K2Kr0URBweH6JkJz3Z7mYFTe09B6GMzIOcPoaYzzJP_PSrpuAfvb6V0AwVCX_HixF2qkCvcdrLyvGaGkkkYh32T2Renu7QWj8Wz06MvimWYCA4pB8SPJpjyw8mNZHOWJXgkI8hgD90O_rDF8mhEIMbDtfTZdOPjekS1a7-LNUGM6ajWLzDehU5YQBzTuGwgoPd2RV0E68iYR6QplHTmhh5vToa7eHvbQrYn8NUzJ6CP5YXcoxl7H9HsQ3AXDHmCtZ3e5p4FLV-Lz64_hVJWaTLOgHecFGAFqXMmnp1BtoKlzwbMnXaFMVaT1T7CkC_XZsoggQA1WFO3vFuXpnw4D6BPNGTmEZrEmINmfBVeFHB4SHDPJXDYX4wwTK8kgUpCHSI8ozIYFy0nw4uJqhkAYjXnvbEeCPsPkf7SPGS7xujgIdlYbtizeg-op2ZyI020Jt-hx2GogXRD_bsNcHaToWZ90fTI8M_Y1-F8iMJG4OnxinHlHnTj7R6wRuM2AZ4-Ov_yhd9w6yXenoKh56RReHCbYAvGCt3aDDyOrcX9WX7VePrBHH3C9ubCwj3PNcuP16or5ho6XRNlXC1s63J99dgi42FWatXeYdUvvcmK7fKxFZWSCXko-cArTT1KqgucxXg8wMk7gaGSwfb2j3pNt1hf4y5MOJQ-HbS0uhuywUbBiHBe8ns6FzUJpM4T8sNXAfbslBk1nIYU9BCMn1Veqw8puCYcwkjWJgxrKU_d2Jx0b8DKpIbbdFKkrdR4vAGRTJ74IgWPuk7wZTSWCddJAB4Q1PU1nbXO3MsxxzlQrWXY1jD9Zp3E69NEUss4qMTT6u5W-RG6RB6ge6sOt47l40v3IO-1LgsCwJtFyQzks0msArf0MSSQ9HreubNnjYqaMOqgUleX4-a0P8BhQwOhwt7C6zyGCnbcBiQx0RWAs0mvf-k5mgqn9Ij5mpGoGVV5L4OhBdY6pm51h7v02bgoWlzUzZHImgBhQtkx0jlBM9XeCIo4t8EQ4ZbqGmLsbj3CTu7KZbc9uQJkWyXSov2WWMvzZfOgCHbizXOGazd47v44BDRMXIiUmJzI1ZXiFkqPB0NftBw80ZnCHlpeq1Nzq8_QQHiM2R1SEsc_T1QQcSlJTVmBpdnqesbv9AAAAAAAAAAAAAAAAAAAAAAAAAAAAABMhLDo",
                        "userHandle": "d2ViYXV0aG5pby1tbC1kc2EtNDQ",
                    },
                    "type": "public-key",
                    "clientExtensionResults": {},
                },
            },
            content_type="application/json",
        )

        self.assertEquals(auth_response.json(), {"verified": True})

        # Clean up
        self.credential_service.delete_credential_by_id(
            credential_id="-EM9FDFIdFVeqWdTycRjoZVN2ZS4vnVE-MBpg7k0pl4jpuqj4GnMCW3Wqlm2WWI2PQ"
        )
