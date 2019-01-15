package server

import (
	"fmt"
	"net/http"

	log "github.com/duo-labs/webauthn.io/logger"
	"github.com/duo-labs/webauthn.io/models"
	"github.com/gorilla/mux"
)

// Index renders the dashboard index page.
func (ws *Server) Index(w http.ResponseWriter, r *http.Request) {
	// TODO: Right now this is just a placeholder handler. In the future, it
	// needs to get the authenticated user from the session, look up their
	// credentials, and render the dashboard page.
	vars := mux.Vars(r)
	username := vars["username"]

	if username == "" {
		username = models.PlaceholderUsername
	}

	user, err := models.GetUserByUsername(fmt.Sprintf("%s@%s", username, "example.com"))
	if err != nil {
		log.Errorf("error retrieving user for dashboard: %s", err)
		jsonResponse(w, "Error retrieving user", http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "Found user %#v", user)
}

// Login renders the login/registration page.
func (ws *Server) Login(w http.ResponseWriter, r *http.Request) {
	renderTemplate(w, "login.html", nil)
}
