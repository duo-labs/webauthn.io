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
	CredentialExcludeList  []TestCredentialDescriptor   `json:"excludeCredentials"`
	Extensions             protocol.AuthenticationExtensions `json:"extensions,omitempty"`
	Attestation            protocol.ConveyancePreference     `json:"attestation,omitempty"`
}

type TestCredentialRequestOptions struct {
	Challenge          string                               `json:"challenge"`
	Timeout            int                                  `json:"timeout,omitempty"`
	RelyingPartyID     string                               `json:"rpId,omitempty"`
	AllowedCredentials []TestCredentialDescriptor      `json:"allowCredentials,omitempty"`
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

type TestCredentialDescriptor struct {
	// The valid credential types.
	Type protocol.CredentialType `json:"type"`
	// CredentialID The ID of a credential to allow/disallow
	CredentialID string `json:"id"`
	// The authenticator transports that can be used
	Transport []protocol.AuthenticatorTransport `json:"transports,omitempty"`
}

func MarshallTestCreationResponse(opts protocol.PublicKeyCredentialCreationOptions) ConformanceCreationResponse {
	testOpts := TestCredentialCreationOptions{
		RelyingParty:           opts.RelyingParty,
		Parameters:             opts.Parameters,
		AuthenticatorSelection: opts.AuthenticatorSelection,
		Timeout:                opts.Timeout,
		Extensions:             opts.Extensions,
		Attestation:            opts.Attestation,
	}

	testUser := TestUserEntity{
		opts.User.CredentialEntity, opts.User.DisplayName, base64.RawURLEncoding.EncodeToString(opts.User.ID),
	}
	testOpts.User = testUser
	testOpts.Challenge = base64.RawURLEncoding.EncodeToString(opts.Challenge)

	excludedCredentials := make([]TestCredentialDescriptor, len(opts.CredentialExcludeList))
	for i, credential := range opts.CredentialExcludeList {
		var credentialDescriptor TestCredentialDescriptor
		credentialDescriptor.CredentialID = base64.RawURLEncoding.EncodeToString(credential.CredentialID)
		credentialDescriptor.Type = protocol.PublicKeyCredentialType
		excludedCredentials[i] = credentialDescriptor
	}
	testOpts.CredentialExcludeList = excludedCredentials

	return ConformanceCreationResponse{
		testOpts, "ok", "",
	}
}

func MarshallTestRequestResponse(opts protocol.PublicKeyCredentialRequestOptions) ConformanceRequestResponse {
	response := opts.Response
	testOpts := TestCredentialRequestOptions{
		Challenge:          base64.RawURLEncoding.EncodeToString(response.Challenge),
		Timeout:            response.Timeout,
		RelyingPartyID:     response.RelyingPartyID,
		UserVerification:   response.UserVerification,
		Extensions:         response.Extensions,
	}

	allowedCredentials := make([]TestCredentialDescriptor, len(response.AllowedCredentials))
	for i, credential := range response.AllowedCredentials {
		var credentialDescriptor TestCredentialDescriptor
		credentialDescriptor.CredentialID = base64.RawURLEncoding.EncodeToString(credential.CredentialID)
		credentialDescriptor.Type = protocol.PublicKeyCredentialType
		allowedCredentials[i] = credentialDescriptor
	}
	testOpts.AllowedCredentials = allowedCredentials

	return ConformanceRequestResponse{
		testOpts, "ok", "",
	}
}
