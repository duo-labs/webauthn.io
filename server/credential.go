package server

import "net/http"

// RequestNewCredential begins a Credential Registration Request when
// MakeNewCredential gets hit
func (ws *Server) RequestNewCredential(w http.ResponseWriter, r *http.Request) {}

// MakeNewCredential attempts to make a new credential given an authenticator's response
func (ws *Server) MakeNewCredential(w http.ResponseWriter, r *http.Request) {}

// GetCredentials gets a user's credentials from the db
func (ws *Server) GetCredentials(w http.ResponseWriter, r *http.Request) {}

// DeleteCredential deletes a credential from the db
func (ws *Server) DeleteCredential(w http.ResponseWriter, r *http.Request) {}
