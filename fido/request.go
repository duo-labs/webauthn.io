package fido

type ConformanceRequest struct {
	DisplayName     string `json:"displayName"`
	AttestationType string `json:"attestation,omitempty"`
	Username        string `json:"username"`
}
