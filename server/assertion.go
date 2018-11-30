package server

import "net/http"

// MakeAssertion - Validate the Assertion Data provided by the authenticator and
// resond whether or not it was successful alongside the relevant credential.
func (ws *Server) MakeAssertion(w http.ResponseWriter, r *http.Request) {}

// GetAssertion - assemble the data we need to make an assertion against
// a given user and authenticator
func (ws *Server) GetAssertion(w http.ResponseWriter, r *http.Request) {}
