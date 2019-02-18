package fido

import (
	"github.com/duo-labs/webauthn/protocol"
)

type ConformanceResponse struct {
	protocol.PublicKeyCredentialCreationOptions
	Status       string `json:"status"`
	ErrorMessage string `json:"errorMessage"`
}
