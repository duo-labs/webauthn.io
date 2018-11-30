package server

import (
	"fmt"
	"net/http"
)

// Index renders the dashboard index page.
func (ws *Server) Index(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "hello!")
}

// Login renders the dashboard login page.
func (ws *Server) Login(w http.ResponseWriter, r *http.Request) {
	renderTemplate(w, "login.html", nil)
}
