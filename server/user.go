package server

import "net/http"

// CreateNewUser - hitting this endpoint with a new user will add it to the db
func (ws *Server) CreateNewUser(w http.ResponseWriter, r *http.Request) {}

// GetUser - get a user from the db
func (ws *Server) GetUser(w http.ResponseWriter, r *http.Request) {}
