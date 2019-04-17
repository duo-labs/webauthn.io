package fido

import (
	"encoding/base64"

	"github.com/duo-labs/webauthn/protocol"
)

type ConformanceCreationResponse struct {
	TestCredentialCreationOptions
	Status       string `json:"status"`
	ErrorMessage string `json:"errorMessage"`
}

type ConformanceRequestResponse struct {
	TestCredentialRequestOptions
	Status       string `json:"status"`
	ErrorMessage string `json:"errorMessage"`
}

type TestCredentialCreationOptions struct {
	Challenge              string                            `json:"challenge"`
	RelyingParty           protocol.RelyingPartyEntity       `json:"rp"`
	User                   TestUserEntity                    `json:"user"`
	Parameters             []protocol.CredentialParameter    `json:"pubKeyCredParams,omitempty"`
	AuthenticatorSelection protocol.AuthenticatorSelection   `json:"authenticatorSelection,omitempty"`
	Timeout                int                               `json:"timeout,omitempty"`
	CredentialExcludeList  []protocol.CredentialDescriptor   `json:"excludeCredentials"`
	Extensions             protocol.AuthenticationExtensions `json:"extensions,omitempty"`
	Attestation            protocol.ConveyancePreference     `json:"attestation,omitempty"`
}

type TestCredentialRequestOptions struct {
	Challenge          string                               `json:"challenge"`
	Timeout            int                                  `json:"timeout,omitempty"`
	RelyingPartyID     string                               `json:"rpId,omitempty"`
	AllowedCredentials []protocol.CredentialDescriptor      `json:"allowCredentials,omitempty"`
	UserVerification   protocol.UserVerificationRequirement `json:"userVerification,omitempty"` // Default is "preferred"
	Extensions         protocol.AuthenticationExtensions    `json:"extensions,omitempty"`
	Status             protocol.ServerResponseStatus        `json:"status"`
	Message            string                               `json:"errorMessage"`
}

type TestUserEntity struct {
	protocol.CredentialEntity
	DisplayName string `json:"displayName,omitempty"`
	ID          string `json:"id"`
}

func MarshallTestCreationResponse(opts protocol.PublicKeyCredentialCreationOptions) ConformanceCreationResponse {
	testOpts := TestCredentialCreationOptions{
		RelyingParty:           opts.RelyingParty,
		Parameters:             opts.Parameters,
		AuthenticatorSelection: opts.AuthenticatorSelection,
		Timeout:                opts.Timeout,
		CredentialExcludeList:  opts.CredentialExcludeList,
		Extensions:             opts.Extensions,
		Attestation:            opts.Attestation,
	}

	testUser := TestUserEntity{
		opts.User.CredentialEntity, opts.User.DisplayName, base64.RawURLEncoding.EncodeToString(opts.User.ID),
	}
	testOpts.User = testUser
	testOpts.Challenge = base64.RawURLEncoding.EncodeToString(opts.Challenge)
	return ConformanceCreationResponse{
		testOpts, "ok", "",
	}
}

func MarshallTestRequestResponse(opts protocol.CredentialAssertion) ConformanceRequestResponse {
	testOpts := TestCredentialRequestOptions{
		Challenge:          base64.RawURLEncoding.EncodeToString(opts.Response.Challenge),
		Timeout:            opts.Response.Timeout,
		RelyingPartyID:     opts.Response.RelyingPartyID,
		AllowedCredentials: opts.Response.AllowedCredentials,
		UserVerification:   opts.Response.UserVerification,
		Extensions:         opts.Response.Extensions,
	}

	return ConformanceRequestResponse{
		testOpts, "ok", "",
	}
}
