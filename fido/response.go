package fido

import (
	"github.com/duo-labs/webauthn/protocol"
)

type ConformanceResponse struct {
	TestCredentialOptions
	Status       string `json:"status"`
	ErrorMessage string `json:"errorMessage"`
}

type TestCredentialOptions struct {
	Challenge              string                            `json:"challenge"`
	RelyingParty           protocol.RelyingPartyEntity       `json:"rp"`
	User                   TestUserEntity                    `json:"user"`
	Parameters             []protocol.CredentialParameter    `json:"pubKeyCredParams,omitempty"`
	AuthenticatorSelection protocol.AuthenticatorSelection   `json:"authenticatorSelection,omitempty"`
	Timeout                int                               `json:"timeout,omitempty"`
	CredentialExcludeList  []protocol.CredentialDescriptor   `json:"excludeCredentials,omitempty"`
	Extensions             protocol.AuthenticationExtensions `json:"extensions,omitempty"`
	Attestation            protocol.ConveyancePreference     `json:"attestation,omitempty"`
}

type TestUserEntity struct {
	protocol.CredentialEntity
	DisplayName string `json:"displayName,omitempty"`
	ID          string `json:"id"`
}

func MarshallTestResponse(opts protocol.PublicKeyCredentialCreationOptions) ConformanceResponse {
	testOpts := TestCredentialOptions{
		RelyingParty:           opts.RelyingParty,
		Parameters:             opts.Parameters,
		AuthenticatorSelection: opts.AuthenticatorSelection,
		Timeout:                opts.Timeout,
		CredentialExcludeList:  opts.CredentialExcludeList,
		Extensions:             opts.Extensions,
		Attestation:            opts.Attestation,
	}

	testUser := TestUserEntity{
		opts.User.CredentialEntity, opts.User.DisplayName, opts.User.ID,
	}
	testOpts.User = testUser
	testOpts.Challenge = opts.Challenge
	return ConformanceResponse{
		testOpts, "ok", "",
	}
}
