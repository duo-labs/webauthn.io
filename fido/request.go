package fido

import (
	"github.com/duo-labs/webauthn/protocol"
)

type ConformanceRequest struct {
	DisplayName            string                               `json:"displayName"`
	AttestationType        string                               `json:"attestation,omitempty"`
	Username               string                               `json:"username"`
	AuthenticatorSelection protocol.AuthenticatorSelection      `json:"authenticatorSelection"`
	Extensions             protocol.AuthenticationExtensions    `json:"extensions"`
	UserVerification       protocol.UserVerificationRequirement `json:"userVerification"`
}
