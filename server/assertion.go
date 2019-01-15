package server

import (
	"errors"
	"net/http"

	log "github.com/duo-labs/webauthn.io/logger"
	"github.com/duo-labs/webauthn.io/models"
	"github.com/gorilla/mux"
	"github.com/jinzhu/gorm"
)

var ErrCredentialCloned = errors.New("The credential appears to have been cloned.")

// GetAssertion - assemble the data we need to make an assertion against
// a given user and authenticator
func (ws *Server) GetAssertion(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	username := vars["name"]
	// TODO: Change these to POST's
	//username := r.FormValue("username")
	if username == "" {
		jsonResponse(w, "No username specified", http.StatusBadRequest)
		return
	}

	user, err := models.GetUserByUsername(username)
	if err == gorm.ErrRecordNotFound {
		log.Errorf("error creating assertion: user doesn't exist: %s", username)
		jsonResponse(w, "User doesn't exist", http.StatusBadRequest)
		return
	}

	assertion, sessionData, err := ws.webauthn.BeginLogin(user)
	if err != nil {
		log.Errorf("error creating assertion: %v", err)
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = ws.store.SaveWebauthnSession("assertion", sessionData, r, w)
	if err != nil {
		log.Errorf("error creating assertion session: error marshaling session: %v", err)
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse(w, assertion, http.StatusOK)
}

// MakeAssertion validates the assertion data provided by the authenticator and
// responds whether or not it was successful alongside the relevant credential.
func (ws *Server) MakeAssertion(w http.ResponseWriter, r *http.Request) {
	sessionData, err := ws.store.GetWebauthnSession("assertion", r)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusBadRequest)
		return
	}
	// Get the user associated with the credential
	user, err := models.GetUser(models.BytesToID(sessionData.UserID))
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	log.Infof("Finishing authentication with user: %#v\n", user)
	cred, err := ws.webauthn.FinishLogin(user, sessionData, r)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	// At this point, we've confirmed the correct authenticator has been
	// provided and it passed the challenge we gave it. We now need to make
	// sure that the sign counter is higher than what we have stored to help
	// give assurance that this credential wasn't cloned.
	if cred.Authenticator.CloneWarning {
		jsonResponse(w, ErrCredentialCloned, http.StatusForbidden)
		return
	}
	// We're logged in!
	// All that's left is to update the sign count with
	// TODO: Set the session indicating that we're logged in
	log.Info("Logged in!")
}
